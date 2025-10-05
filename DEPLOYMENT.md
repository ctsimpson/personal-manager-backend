# Personal Manager Backend Deployment Guide

This guide covers deploying the Personal Manager Backend in a production environment using Docker. This deployment connects to an external MongoDB instance running on localhost:27017.

## Prerequisites

- External MongoDB instance running on localhost:27017
- Docker and Docker Compose installed
- Access credentials for the MongoDB instance

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <your-repo-url>
   cd personal-manager-backend
   ```

2. **Configure environment**:
   ```bash
   cp .env.production.template .env.production
   # Edit .env.production with your MongoDB credentials and other values
   ```

3. **Deploy**:
   ```bash
   ./deploy.sh deploy
   ```

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- At least 2GB RAM
- 10GB disk space

## Environment Configuration

### Required Environment Variables

Create `.env.production` with these variables:

```bash
# Security (REQUIRED)
SECRET_KEY=your-super-secret-key-minimum-32-characters
MONGODB_PASSWORD=your-mongodb-password

# Database
DATABASE_NAME=personal_manager
MONGODB_USER=admin

# Google API (if using Google Calendar integration)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Application
ALLOWED_ORIGINS_STR=https://yourdomain.com,https://www.yourdomain.com
```

### Optional Variables

```bash
# Timezone
SCHEDULER_TIMEZONE=America/Los_Angeles
```

## Deployment Options

### Simplified Deployment

```bash
# Deploy the application (recommended)
./deploy.sh deploy
```

This starts:
- Personal Manager API (connects to external MongoDB on localhost:27017)

### Alternative: Development Mode

For staging environments with hot-reload:

```bash
# Use development target
docker-compose -f docker-compose.prod.yml --env-file .env.production build --target development
docker-compose -f docker-compose.prod.yml --env-file .env.production up -d
```

## File Structure for Deployment

```
personal-manager-backend/
├── Dockerfile                    # Multi-stage production Dockerfile
├── docker-compose.prod.yml       # Production compose configuration
├── .env.production              # Production environment variables
├── .env.production.template     # Template for environment variables
├── deploy.sh                   # Deployment script
├── data/                       # Persistent data (Google credentials, etc.)
├── logs/                       # Application logs
└── uploads/                    # User uploads
```

## Management Commands

```bash
# Deploy/Update application
./deploy.sh deploy

# Start services
./deploy.sh start

# Stop services
./deploy.sh stop

# Restart services
./deploy.sh restart

# View logs
./deploy.sh logs

# View specific service logs
./deploy.sh logs personal-manager-api

# Check status
./deploy.sh status

# Clean up unused Docker resources
./deploy.sh cleanup
```

## Monitoring and Maintenance

### Health Checks

The application includes built-in health checks:

```bash
# Check API health
curl http://localhost:8000/

# Check via Docker
docker ps  # Should show (healthy) status
```

### Logs

```bash
# Application logs
./deploy.sh logs personal-manager-api

# Database logs
./deploy.sh logs mongodb

# All logs
./deploy.sh logs
```

### Database Backup

```bash
# Backup MongoDB
docker exec personal-manager-mongodb mongodump --out /tmp/backup
docker cp personal-manager-mongodb:/tmp/backup ./backup-$(date +%Y%m%d)
```

### Updates

```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
./deploy.sh deploy
```

## SSL/HTTPS Setup

### External Load Balancer/Proxy

Since this deployment doesn't include Nginx, configure your external load balancer or reverse proxy to handle SSL and proxy requests to port 8000:

- **AWS Application Load Balancer (ALB)**: Configure SSL termination and target group pointing to port 8000
- **Cloudflare**: Enable SSL/TLS encryption and proxy to your server's port 8000
- **Nginx (External)**: Set up a separate Nginx instance with SSL certificates
- **Traefik**: Use Traefik for automatic SSL certificate management
- **Caddy**: Simple reverse proxy with automatic HTTPS

## Scaling

### Horizontal Scaling

```bash
# Scale API instances
docker-compose -f docker-compose.prod.yml up -d --scale personal-manager-api=3
```

### Vertical Scaling

Edit `docker-compose.prod.yml` to add resource limits:

```yaml
services:
  personal-manager-api:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

## Troubleshooting

### Common Issues

1. **API not starting**:
   ```bash
   ./deploy.sh logs personal-manager-api
   ```

2. **Database connection issues**:
   ```bash
   # Check MongoDB is running
   docker ps | grep mongodb
   
   # Check MongoDB logs
   ./deploy.sh logs mongodb
   ```

3. **Port conflicts**:
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   
   # Change port in .env.production
   PORT=8001
   ```

4. **Permission issues**:
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER data logs uploads
   ```

### Performance Issues

1. **Check resource usage**:
   ```bash
   docker stats
   ```

2. **Monitor logs for errors**:
   ```bash
   ./deploy.sh logs | grep ERROR
   ```

3. **Check database performance**:
   ```bash
   # Connect to MongoDB
   docker exec -it personal-manager-mongodb mongosh
   ```

## Security Considerations

### Production Checklist

- [ ] Change default passwords in `.env.production`
- [ ] Use strong `SECRET_KEY` (32+ characters)
- [ ] Set specific `ALLOWED_ORIGINS_STR` (not `*`)
- [ ] Enable SSL/HTTPS
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity
- [ ] Backup data regularly
- [ ] Use non-root user in containers (already configured)

### Network Security

- [ ] Use Docker networks (already configured)
- [ ] Don't expose database ports publicly
- [ ] Use firewall rules
- [ ] Consider VPN for admin access

## Support

For issues and questions:

1. Check the logs first: `./deploy.sh logs`
2. Review this documentation
3. Check GitHub issues
4. Contact support team

---

**Note**: This deployment setup is production-ready but should be customized based on your specific infrastructure and security requirements.