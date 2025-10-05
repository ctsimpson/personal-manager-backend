# Production Deployment Checklist

## Pre-Deployment

### Security
- [ ] Generate strong `SECRET_KEY` (32+ characters, random)
- [ ] Set strong `MONGODB_PASSWORD` 
- [ ] Configure specific `ALLOWED_ORIGINS_STR` (not `*`)
- [ ] Review and set all required environment variables in `.env.production`

### Infrastructure
- [ ] Docker and Docker Compose installed on server
- [ ] Sufficient resources (2GB+ RAM, 10GB+ disk)
- [ ] Firewall configured (allow ports 80, 443, optionally 8000)
- [ ] Domain name configured (if using custom domain)
- [ ] SSL certificates ready (if using HTTPS)

### Application Files
- [ ] Google API credentials file in `./data/credentials.json` (if using Google Calendar)
- [ ] Environment file `.env.production` configured
- [ ] MongoDB initialization script reviewed

## Deployment Steps

1. **Initial Setup**:
   ```bash
   # Clone repository
   git clone <your-repo-url>
   cd personal-manager-backend
   
   # Copy and configure environment
   cp .env.production.template .env.production
   # Edit .env.production with your values
   ```

2. **First Deployment**:
   ```bash
   # Make deployment script executable
   chmod +x deploy.sh
   
   # Deploy application
   ./deploy.sh deploy
   ```

3. **Verify Deployment**:
   ```bash
   # Check service status
   ./deploy.sh status
   
   # Test API endpoint
   curl http://localhost:8000/
   
   # Check logs if needed
   ./deploy.sh logs
   ```

## Post-Deployment

### Verification
- [ ] API responds at http://localhost:8000/
- [ ] Health check passes: `curl http://localhost:8000/`
- [ ] Database connection working (check logs)
- [ ] All services showing as "healthy" in `docker ps`

### Monitoring Setup
- [ ] Set up log monitoring
- [ ] Configure backup strategy for MongoDB
- [ ] Set up alerting for service failures
- [ ] Monitor resource usage

### SSL Configuration (Optional)
- [ ] Configure external reverse proxy/load balancer for SSL
- [ ] Test SSL configuration with external proxy
- [ ] Enable automatic certificate renewal (if using Let's Encrypt)

## Maintenance

### Regular Tasks
- [ ] Monitor application logs: `./deploy.sh logs`
- [ ] Check system resources: `docker stats`
- [ ] Update application: `git pull && ./deploy.sh deploy`
- [ ] Backup database regularly
- [ ] Update dependencies and security patches

### Emergency Procedures
- [ ] Restart application: `./deploy.sh restart`
- [ ] View specific service logs: `./deploy.sh logs [service-name]`
- [ ] Scale services: `docker-compose up -d --scale personal-manager-api=3`
- [ ] Rollback: Deploy previous version from git

## Common Commands

```bash
# Full deployment
./deploy.sh deploy

# Check status
./deploy.sh status

# View logs
./deploy.sh logs
./deploy.sh logs personal-manager-api

# Restart services
./deploy.sh restart

# Stop services
./deploy.sh stop

# Cleanup unused resources
./deploy.sh cleanup
```

## Environment Variables Reference

### Required
```bash
SECRET_KEY=                    # Strong random key (32+ chars)
MONGODB_PASSWORD=              # Database password
DATABASE_NAME=personal_manager # Database name
```

### Authentication & API
```bash
GOOGLE_CLIENT_ID=              # Google OAuth client ID
GOOGLE_CLIENT_SECRET=          # Google OAuth secret
ALLOWED_ORIGINS_STR=          # Comma-separated list of allowed origins
```

### Optional
```bash
SCHEDULER_TIMEZONE=            # Application timezone
```

## Troubleshooting

### Application Won't Start
1. Check logs: `./deploy.sh logs personal-manager-api`
2. Verify environment variables in `.env.production`
3. Check port conflicts: `lsof -i :8000`
4. Verify Docker resources: `docker system df`

### Database Issues
1. Check MongoDB logs: `./deploy.sh logs mongodb`
2. Verify MongoDB is healthy: `docker ps`
3. Test connection manually:
   ```bash
   docker exec -it personal-manager-mongodb mongosh
   ```

### Performance Issues
1. Monitor resources: `docker stats`
2. Check for errors in logs
3. Consider scaling: `docker-compose up -d --scale personal-manager-api=2`

## Security Notes

- Never commit `.env.production` to version control
- Regularly update Docker images and dependencies
- Monitor logs for suspicious activity
- Use strong, unique passwords for all services
- Enable HTTPS in production environments
- Regularly backup your data
- Consider using Docker secrets for sensitive data in production

---

**Ready for Production**: Once all items are checked and verified, your Personal Manager Backend is ready for production use! 🚀