#!/bin/bash

# Personal Manager Backend - Production Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="personal-manager-backend"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if .env.prod exists
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "Production environment file ($ENV_FILE) not found."
        log_info "Please copy .env.prod.example to .env.prod and configure it."
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Build and deploy
deploy() {
    log_info "Starting deployment of $PROJECT_NAME..."
    
    # Load environment variables
    export $(grep -v '^#' $ENV_FILE | xargs)
    
    # Build and start services
    log_info "Building Docker images..."
    docker compose -f $COMPOSE_FILE build
    
    log_info "Starting services..."
    docker compose -f $COMPOSE_FILE up -d
    
    log_info "Waiting for services to be healthy..."
    sleep 10
    
    # Check service health
    if docker compose -f $COMPOSE_FILE ps | grep -q "healthy\|Up"; then
        log_success "Deployment completed successfully!"
        log_info "API is available at: http://localhost:8000"
        log_info "API Documentation: http://localhost:8000/docs"
        log_info "Health check: http://localhost:8000/"
    else
        log_error "Some services failed to start properly"
        docker compose -f $COMPOSE_FILE logs --tail=50
        exit 1
    fi
}

# Stop services
stop() {
    log_info "Stopping services..."
    docker compose -f $COMPOSE_FILE down
    log_success "Services stopped"
}

# Update deployment
update() {
    log_info "Updating deployment..."
    
    # Pull latest changes (if using git)
    if [ -d ".git" ]; then
        log_info "Pulling latest changes from git..."
        git pull
    fi
    
    # Rebuild and restart
    log_info "Rebuilding services..."
    docker compose -f $COMPOSE_FILE down
    docker compose -f $COMPOSE_FILE build --no-cache
    docker compose -f $COMPOSE_FILE up -d
    
    log_success "Update completed"
}

# Show logs
logs() {
    docker compose -f $COMPOSE_FILE logs -f "${2:-personal-manager-api}"
}

# Show status
status() {
    log_info "Service Status:"
    docker compose -f $COMPOSE_FILE ps
    
    log_info "Container Resource Usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.PIDs}}"
}

# Backup data
backup() {
    BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    log_info "Creating backup in $BACKUP_DIR..."
    
    # Backup MongoDB
    docker compose -f $COMPOSE_FILE exec -T mongodb mongodump --archive > "$BACKUP_DIR/mongodb_backup.archive"
    
    # Backup data directory
    if [ -d "data" ]; then
        cp -r data "$BACKUP_DIR/"
    fi
    
    log_success "Backup created: $BACKUP_DIR"
}

# Main script
case "$1" in
    "deploy"|"start")
        check_prerequisites
        deploy
        ;;
    "stop")
        stop
        ;;
    "restart")
        stop
        sleep 5
        check_prerequisites
        deploy
        ;;
    "update")
        update
        ;;
    "logs")
        logs "$@"
        ;;
    "status")
        status
        ;;
    "backup")
        backup
        ;;
    "help"|*)
        echo "Personal Manager Backend - Deployment Script"
        echo ""
        echo "Usage: $0 {deploy|start|stop|restart|update|logs|status|backup|help}"
        echo ""
        echo "Commands:"
        echo "  deploy/start  - Deploy the application"
        echo "  stop          - Stop all services"
        echo "  restart       - Restart all services"
        echo "  update        - Update and redeploy"
        echo "  logs [service]- Show logs (default: personal-manager-api)"
        echo "  status        - Show service status and resource usage"
        echo "  backup        - Create data backup"
        echo "  help          - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 deploy               # Deploy the application"
        echo "  $0 logs                 # Show API logs"
        echo "  $0 logs mongodb         # Show MongoDB logs"
        echo "  $0 status               # Check status"
        echo ""
        ;;
esac