# Personal Development App - Deployment Guide

## Overview

This guide covers deploying the Personal Development App to various hosting platforms. The app consists of:
- **Backend**: Django REST API (Python 3.13+)
- **Frontend**: React + Vite (Node.js 18+)
- **Database**: SQLite (dev) / PostgreSQL (production)

---

## Quick Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (`pytest backend/ -q`)
- [ ] Environment variables configured
- [ ] SECRET_KEY changed for production
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured
- [ ] Database migrations applied
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] CORS origins configured for production domain

### Security
- [ ] Change SECRET_KEY in production
- [ ] Set DEBUG=False
- [ ] Configure ALLOWED_HOSTS
- [ ] Enable HTTPS/SSL
- [ ] Secure database credentials
- [ ] Configure CSRF/CORS properly

---

## Environment Setup

### 1. Backend Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cd backend
cp .env.example .env
```

Edit `.env`:
```ini
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# PostgreSQL for production
DB_ENGINE=django.db.backends.postgresql
DB_NAME=personal_dev_app
DB_USER=postgres
DB_PASSWORD=your-secure-password
DB_HOST=db.example.com
DB_PORT=5432

CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. Frontend Environment Variables

```bash
cd frontend
cp .env.example .env
```

Edit `.env`:
```ini
VITE_API_URL=https://api.yourdomain.com/api
VITE_ENV=production
```

---

## Deployment Options

### Option 1: Railway (Recommended for MVP)

**Backend (Django API)**

1. Create `railway.json`:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python manage.py migrate && gunicorn config.wsgi:application",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

2. Create `Procfile`:
```
web: python manage.py migrate && gunicorn config.wsgi:application
```

3. Install Gunicorn:
```bash
pip install gunicorn
pip freeze > requirements.txt
```

4. Deploy:
- Connect GitHub repo to Railway
- Add PostgreSQL database
- Set environment variables
- Deploy

**Frontend (React)**

1. Update `package.json`:
```json
{
  "scripts": {
    "build": "vite build",
    "preview": "vite preview --host --port $PORT"
  }
}
```

2. Deploy to Railway or Vercel

---

### Option 2: Heroku

**Backend**

1. Create `Procfile`:
```
web: gunicorn config.wsgi
release: python manage.py migrate
```

2. Create `runtime.txt`:
```
python-3.13.1
```

3. Update `settings.py` for Heroku:
```python
import os
import dj_database_url

# Heroku database configuration
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True
    )
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Middleware for WhiteNoise
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
```

4. Install dependencies:
```bash
pip install gunicorn dj-database-url whitenoise psycopg2-binary
pip freeze > requirements.txt
```

5. Deploy:
```bash
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set DEBUG=False
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

**Frontend**

Deploy to Vercel or Netlify:
```bash
npm run build
# Deploy dist/ folder
```

---

### Option 3: DigitalOcean / AWS EC2

**1. Server Setup (Ubuntu 22.04)**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.13
sudo apt install python3.13 python3.13-venv python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

**2. Backend Setup**

```bash
# Create app user
sudo useradd -m -s /bin/bash appuser
sudo su - appuser

# Clone repo
git clone https://github.com/yourusername/personal-dev-app.git
cd personal-dev-app/backend

# Create virtual environment
python3.13 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Configure environment
cp .env.example .env
nano .env  # Edit with production values

# Run migrations
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

**3. Systemd Service**

Create `/etc/systemd/system/django-app.service`:
```ini
[Unit]
Description=Django Application
After=network.target

[Service]
Type=notify
User=appuser
WorkingDirectory=/home/appuser/personal-dev-app/backend
Environment="PATH=/home/appuser/personal-dev-app/backend/venv/bin"
ExecStart=/home/appuser/personal-dev-app/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/appuser/personal-dev-app/backend/app.sock \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl start django-app
sudo systemctl enable django-app
```

**4. Nginx Configuration**

Create `/etc/nginx/sites-available/django-app`:
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://unix:/home/appuser/personal-dev-app/backend/app.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /home/appuser/personal-dev-app/backend/staticfiles/;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/django-app /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**5. SSL with Let's Encrypt**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
```

**6. Frontend Build**

```bash
cd ../frontend
npm install
npm run build

# Serve with Nginx
sudo cp -r dist/* /var/www/html/
```

Create `/etc/nginx/sites-available/frontend`:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

---

## Database Setup (PostgreSQL)

### Local PostgreSQL

```bash
# Create database
sudo -u postgres psql
CREATE DATABASE personal_dev_app;
CREATE USER appuser WITH PASSWORD 'your-password';
ALTER ROLE appuser SET client_encoding TO 'utf8';
ALTER ROLE appuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE appuser SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE personal_dev_app TO appuser;
\q
```

### Managed Database (Recommended)

Use managed PostgreSQL from:
- **Railway**: Built-in PostgreSQL
- **Heroku**: Heroku Postgres
- **DigitalOcean**: Managed Databases
- **AWS**: RDS PostgreSQL

---

## Post-Deployment

### 1. Verify Deployment

```bash
# Test API
curl https://api.yourdomain.com/api/auth/auth/signup/ -X POST

# Test frontend
curl https://yourdomain.com
```

### 2. Create Admin User

```bash
python manage.py createsuperuser
# Access: https://api.yourdomain.com/admin/
```

### 3. Monitor Logs

```bash
# Systemd logs
sudo journalctl -u django-app -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 4. Setup Error Monitoring (Optional)

Install Sentry:
```bash
pip install sentry-sdk
```

Add to `settings.py`:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

if not DEBUG:
    sentry_sdk.init(
        dsn=os.getenv('SENTRY_DSN'),
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
    )
```

---

## Continuous Deployment

### GitHub Actions

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        run: railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

---

## Troubleshooting

### Common Issues

**1. Static files not loading**
```bash
python manage.py collectstatic --noinput
```

**2. Database connection failed**
- Check DATABASE_URL
- Verify PostgreSQL is running
- Check firewall rules

**3. CORS errors**
- Update CORS_ALLOWED_ORIGINS
- Check frontend API URL

**4. 502 Bad Gateway**
- Check Gunicorn is running
- Verify socket permissions
- Check Nginx configuration

---

## Security Checklist

- [ ] SECRET_KEY is unique and secure
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured
- [ ] HTTPS enabled (SSL certificate)
- [ ] Database password is strong
- [ ] Environment variables not in git
- [ ] CORS configured properly
- [ ] Admin panel secured (/admin/)
- [ ] Rate limiting enabled (optional)
- [ ] Firewall configured
- [ ] Regular backups scheduled

---

## Backup Strategy

### Database Backups

**PostgreSQL:**
```bash
# Manual backup
pg_dump -U appuser personal_dev_app > backup.sql

# Automated (cron)
0 2 * * * pg_dump -U appuser personal_dev_app > /backups/db_$(date +\%Y\%m\%d).sql
```

**Heroku:**
```bash
heroku pg:backups:capture
heroku pg:backups:download
```

### Media Files

```bash
# Sync to S3
aws s3 sync /path/to/media s3://your-bucket/media
```

---

## Scaling Considerations

### For 100+ users
- Use managed database (PostgreSQL)
- Enable caching (Redis)
- CDN for static files
- Gunicorn workers: 2-4

### For 1000+ users
- Load balancer
- Multiple app servers
- Redis caching
- Background task queue (Celery)
- Database read replicas

### For 10000+ users
- Auto-scaling groups
- Database sharding
- CDN for all assets
- Advanced monitoring
- Queue workers for heavy tasks

---

## Monitoring

### Health Check Endpoint

Add to Django:
```python
# views.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

### Uptime Monitoring

Use:
- **UptimeRobot** (free)
- **Pingdom**
- **Better Uptime**

---

## Cost Estimate

### MVP (50-100 users)
- Railway/Heroku: $5-15/month
- Domain: $12/year
- **Total: ~$10-20/month**

### Growth (1000 users)
- Server: $25-50/month
- Database: $15-25/month
- CDN: $5-10/month
- **Total: ~$50-100/month**

---

## Next Steps After Deployment

1. Test all features in production
2. Add monitoring and alerts
3. Setup backup schedule
4. Configure custom domain
5. Add SSL certificate
6. Invite beta testers
7. Collect feedback
8. Monitor performance

---

## Support

For issues:
1. Check logs first
2. Review environment variables
3. Verify database connection
4. Test API endpoints directly
5. Check frontend console errors

---

**Last Updated**: February 2, 2026
