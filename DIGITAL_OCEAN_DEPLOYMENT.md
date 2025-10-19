# Digital Ocean Deployment Guide

This guide covers deploying the Personal Manager Backend on Digital Ocean using different deployment options.

## Deployment Options

### Option 1: Digital Ocean App Platform (Recommended for Beginners)

**Pros:**
- Fully managed, auto-scaling
- Built-in SSL/HTTPS
- Automatic deployments from Git
- No server management needed

**Cons:**
- More expensive than Droplets
- Less control over infrastructure
- Volume mounts don't work the same way

#### Setup Steps:

1. **Prepare your repository:**
   - Ensure Dockerfile is in the root
   - Push to GitHub/GitLab

2. **Create App Platform app:**
   - Go to Digital Ocean Dashboard → App Platform → Create App
   - Connect your GitHub repository
   - Digital Ocean will auto-detect the Dockerfile

3. **Configure environment variables in DO Dashboard:**
   ```
   ENVIRONMENT=production
   DEBUG=false
   HOST=0.0.0.0
   PORT=8000
   MONGODB_HOST=<your-managed-db-host>
   MONGODB_PORT=27017
   MONGODB_USER=<your-db-user>
   MONGODB_PASSWORD=<your-db-password>
   MONGODB_AUTH_SOURCE=admin
   DATABASE_NAME=personal_manager
   SECRET_KEY=<generate-strong-32+-char-key>
   ALLOWED_ORIGINS_STR=https://yourdomain.com
   GOOGLE_CLIENT_ID=<your-client-id>
   GOOGLE_CLIENT_SECRET=<your-client-secret>
   SCHEDULER_TIMEZONE=America/Los_Angeles
   ```

4. **Database setup:**
   - Create a Digital Ocean Managed MongoDB database
   - Or use MongoDB Atlas (recommended)
   - Get connection string and add to environment variables

5. **File storage:**
   - For uploads: Use Digital Ocean Spaces (S3-compatible)
   - For Google credentials: Store in environment variables or Spaces
   - Remove volume mounts from your deployment

6. **Deploy:**
   - Click "Deploy" in App Platform
   - App Platform will build from Dockerfile and deploy

#### App Platform Specific Changes Needed:

**Create `.do/app.yaml` (optional but recommended):**
```yaml
name: personal-manager-backend
services:
- name: api
  dockerfile_path: Dockerfile
  github:
    repo: your-username/personal-manager-backend
    branch: main
    deploy_on_push: true
  health_check:
    http_path: /
  http_port: 8000
  instance_count: 1
  instance_size_slug: basic-xxs
  routes:
  - path: /
  envs:
  - key: ENVIRONMENT
    value: production
  - key: DEBUG
    value: "false"
  - key: PORT
    value: "8000"
  # Add other environment variables here or in DO dashboard
```

---

### Option 2: Digital Ocean Droplet (VPS) with Docker

**Pros:**
- Full control over infrastructure
- More cost-effective
- Can use docker-compose
- Volume mounts work normally

**Cons:**
- You manage the server
- Manual SSL setup required
- Manual scaling

#### Setup Steps:

1. **Create a Droplet:**
   - Ubuntu 22.04 LTS (recommended)
   - At least 2GB RAM
   - Enable monitoring

2. **Initial server setup:**
   ```bash
   # SSH into your droplet
   ssh root@your-droplet-ip

   # Update system
   apt update && apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh

   # Install Docker Compose
   apt install docker-compose-plugin -y

   # Create non-root user
   adduser deploy
   usermod -aG docker deploy
   usermod -aG sudo deploy

   # Switch to deploy user
   su - deploy
   ```

3. **Clone and setup application:**
   ```bash
   git clone https://github.com/your-username/personal-manager-backend.git
   cd personal-manager-backend

   # Create production environment file
   cp .env.production.template .env.production
   nano .env.production  # Edit with your values
   ```

4. **Setup MongoDB:**
   
   **Option A: External MongoDB (Recommended)**
   - Use MongoDB Atlas or Digital Ocean Managed Database
   - Update MONGODB_HOST in .env.production with external host
   - Remove `host.docker.internal` references

   **Option B: MongoDB on same Droplet**
   - Add MongoDB service to docker-compose.prod.yml
   - Use service name as MONGODB_HOST

5. **Fix docker-compose.prod.yml for Droplet:**

   If using external MongoDB, update:
   ```yaml
   environment:
     - MONGODB_HOST=your-external-mongodb-host.com  # Not host.docker.internal
   # Remove these lines:
   # network_mode: bridge
   # extra_hosts:
   #   - "host.docker.internal:host-gateway"
   ```

6. **Deploy:**
   ```bash
   ./deploy.sh deploy
   ```

7. **Setup Nginx reverse proxy with SSL:**
   ```bash
   # Install Nginx
   sudo apt install nginx certbot python3-certbot-nginx -y

   # Create Nginx config
   sudo nano /etc/nginx/sites-available/personal-manager
   ```

   Add this configuration:
   ```nginx
   server {
       server_name yourdomain.com www.yourdomain.com;

       location / {
           proxy_pass http://localhost:8000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

   ```bash
   # Enable site
   sudo ln -s /etc/nginx/sites-available/personal-manager /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx

   # Get SSL certificate
   sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
   ```

8. **Setup firewall:**
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

---

## Current Issues with Your Setup for Digital Ocean

### 1. ✅ FIXED: Environment Variables
- Changed `ENVIRONMENT=development` to `production`
- Changed `DEBUG=true` to `false`

### 2. ⚠️ MongoDB Connection (Needs Manual Fix)

**Current (won't work on DO):**
```yaml
MONGODB_HOST=host.docker.internal
network_mode: bridge
extra_hosts:
  - "host.docker.internal:host-gateway"
```

**For App Platform:**
- Use managed database connection string
- Remove network_mode and extra_hosts

**For Droplet with external MongoDB:**
```yaml
MONGODB_HOST=your-mongodb-atlas-host.mongodb.net
# Remove network_mode and extra_hosts lines
```

**For Droplet with MongoDB container:**
```yaml
# Add MongoDB service to docker-compose.prod.yml
services:
  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - mongodb_data:/data/db
    restart: unless-stopped

  personal-manager-api:
    environment:
      - MONGODB_HOST=mongodb  # Use service name
    depends_on:
      - mongodb

volumes:
  mongodb_data:
```

### 3. ⚠️ File Storage (Needs Redesign for App Platform)

**Current (works on Droplet, not App Platform):**
```yaml
volumes:
  - ./data:/app/data:ro
  - ./uploads:/app/uploads
  - ./logs:/app/logs
```

**For App Platform:**
- Use Digital Ocean Spaces for uploads
- Store credentials in environment variables
- Use DO logging instead of file logs

**For Droplet:**
- Current setup works fine
- Ensure directories exist and have correct permissions

---

## Recommended Approach

### For Quick Start (Easiest):
1. Use **Digital Ocean App Platform**
2. Use **MongoDB Atlas** (free tier available)
3. Store files in **Digital Ocean Spaces**
4. Let App Platform handle SSL/scaling

### For Cost Optimization:
1. Use **Digital Ocean Droplet** ($6-12/month)
2. Use **MongoDB Atlas** free tier or self-hosted
3. Setup **Nginx + Let's Encrypt** for SSL
4. Use current docker-compose setup with fixes

---

## Next Steps

1. **Choose your deployment method** (App Platform or Droplet)
2. **Setup MongoDB** (Atlas or Managed Database)
3. **Update docker-compose.prod.yml** based on your choice
4. **Configure environment variables**
5. **Deploy and test**

## Support

- Digital Ocean Documentation: https://docs.digitalocean.com/
- MongoDB Atlas: https://www.mongodb.com/cloud/atlas
- Let's Encrypt: https://letsencrypt.org/
