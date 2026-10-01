# EMS Docker Setup Guide

Complete guide to run the EMS (Equipment Management System) application using Docker.

## 📋 Prerequisites

- Docker Engine 20.10+ ([Install Docker](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ (comes with Docker Desktop)
- Git (for cloning the repository)

## 🚀 Quick Start

### 1. Clone and Navigate to Project

```bash
cd d:\Zohaib\webapps\ems\ems
```

### 2. Create Environment File

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` file with your settings:

```env
DEBUG=False
SECRET_KEY=your-secret-key-here-change-this-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com

DB_NAME=ems
DB_USER=zohaib
DB_PASSWORD=abcd@1234
DB_HOST=db
DB_PORT=5432
```

### 3. Build and Run

**Option A: With Nginx (Recommended for Production)**

```bash
docker-compose up -d --build
```

**Option B: Django Only (Development)**

```bash
docker-compose up -d --build db web
```

### 4. Access the Application

- **With Nginx**: http://localhost
- **Without Nginx**: http://localhost:8000
- **Admin Panel**: http://localhost/admin

### 5. Create Superuser (Optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

## 📦 What Gets Created

### Services

1. **db** (PostgreSQL 15)
   - Port: 5432
   - Data persisted in Docker volume `postgres_data`

2. **web** (Django + Gunicorn)
   - Port: 8000
   - Runs with 4 workers
   - Auto-migrates database on startup
   - Collects static files automatically

3. **nginx** (Nginx Alpine)
   - Port: 80 (HTTP)
   - Port: 443 (HTTPS - when configured)
   - Serves static/media files
   - Reverse proxy to Django

### Volumes

- `postgres_data`: Persistent PostgreSQL database
- `./staticfiles`: Django static files
- `./media`: User-uploaded files
- `./logs`: Application logs

## 🛠️ Common Commands

### Start Services

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d web

# View logs while starting
docker-compose up
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes database)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
docker-compose logs -f nginx

# Last 100 lines
docker-compose logs --tail=100 web
```

### Execute Commands in Container

```bash
# Django shell
docker-compose exec web python manage.py shell

# Database migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Access PostgreSQL
docker-compose exec db psql -U zohaib -d ems
```

### Rebuild Containers

```bash
# Rebuild all containers
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build web

# Force rebuild (no cache)
docker-compose build --no-cache
docker-compose up -d
```

## 🔧 Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is ready
docker-compose exec db pg_isready -U zohaib

# Restart database
docker-compose restart db

# Check database logs
docker-compose logs db
```

### Permission Issues

```bash
# Fix permissions for media/static directories
sudo chown -R $USER:$USER staticfiles media logs
chmod -R 755 staticfiles media logs
```

### Port Already in Use

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Changed from 8000:8000
```

### Container Won't Start

```bash
# Check container status
docker-compose ps

# Inspect container
docker-compose logs web

# Remove and rebuild
docker-compose down
docker-compose up -d --build
```

### Database Migration Errors

```bash
# Reset migrations (⚠️ only for development)
docker-compose exec web python manage.py migrate --fake core zero
docker-compose exec web python manage.py migrate

# Or reset database completely
docker-compose down -v
docker-compose up -d
```

## 📊 Monitoring

### Check Service Health

```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Nginx health check
curl http://localhost/health/
```

### View Application Logs

```bash
# Django application logs
docker-compose exec web tail -f /app/logs/ems.log

# Nginx access logs
docker-compose logs nginx | grep "GET"

# PostgreSQL logs
docker-compose logs db
```

## 🔒 Production Deployment

### 1. Security Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=False`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Use strong database password
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up firewall rules
- [ ] Configure backup strategy

### 2. SSL/HTTPS Setup

Get SSL certificates (Let's Encrypt):

```bash
# Create ssl directory
mkdir ssl

# Get certificates (using certbot)
docker run -it --rm \
  -v $(pwd)/ssl:/etc/letsencrypt \
  certbot/certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com
```

Uncomment HTTPS section in `nginx.conf` and update domain name.

### 3. Environment Variables

Update `.env` for production:

```env
DEBUG=False
SECRET_KEY=<generate-strong-secret-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Use strong passwords
DB_PASSWORD=<strong-password>
```

### 4. Backup Database

```bash
# Backup
docker-compose exec db pg_dump -U zohaib ems > backup_$(date +%Y%m%d).sql

# Restore
docker-compose exec -T db psql -U zohaib ems < backup_20250127.sql
```

## 🔄 Updates and Maintenance

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build web

# Run migrations
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### Update Docker Images

```bash
# Pull latest base images
docker-compose pull

# Rebuild
docker-compose up -d --build
```

## 📈 Scaling

### Increase Gunicorn Workers

Edit `docker-compose.yml`:

```yaml
web:
  command: gunicorn --bind 0.0.0.0:8000 --workers 8 --timeout 120 ems.wsgi:application
```

### Multiple Web Containers

```bash
# Scale web service to 3 instances
docker-compose up -d --scale web=3
```

Note: You'll need a load balancer (nginx upstream) for this.

## 🗑️ Cleanup

### Remove Stopped Containers

```bash
docker-compose down
```

### Remove Everything (Including Volumes)

```bash
# ⚠️ This deletes ALL data
docker-compose down -v
docker system prune -a
```

### Remove Only Unused Images

```bash
docker image prune -a
```

## 📞 Support

For issues or questions:

1. Check logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Check Docker/Docker Compose versions
4. Review this guide's troubleshooting section

## 📝 File Structure

```
ems/
├── docker-compose.yml      # Docker services configuration
├── Dockerfile             # Django application image
├── .dockerignore          # Files to exclude from image
├── entrypoint.sh          # Container startup script
├── nginx.conf             # Nginx configuration
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create from .env.example)
├── .env.example           # Example environment variables
├── manage.py              # Django management script
├── ems/                   # Django project settings
├── core/                  # Core Django app
├── User/                  # User Django app
├── maintenance/           # Maintenance Django app
├── staticfiles/           # Collected static files (created on build)
├── media/                 # User uploads (created on build)
└── logs/                  # Application logs (created on build)
```

## ✅ Success Indicators

Your setup is working correctly when:

- ✅ All containers are running: `docker-compose ps` shows "Up"
- ✅ Database is accessible: `docker-compose exec db pg_isready`
- ✅ Application responds: `curl http://localhost/health/` returns "healthy"
- ✅ Static files load correctly
- ✅ Admin panel is accessible at `/admin`
- ✅ No errors in logs: `docker-compose logs --tail=50`

---

**Last Updated**: January 27, 2026
**Docker Version**: 20.10+
**Docker Compose Version**: 2.0+
