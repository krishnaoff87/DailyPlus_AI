# 🚀 Streamlit Deployment Checklist

> **Production deployment guide for DailyPlus_AI**  
> Pre-deployment verification, security hardening, and post-deployment validation

---

## 📋 Table of Contents

- [Overview](#overview)
- [Pre-Deployment Checklist](#pre-deployment-checklist)
- [Configuration Migration](#configuration-migration)
- [Security Hardening](#security-hardening)
- [Deployment Procedures](#deployment-procedures)
- [Post-Deployment Validation](#post-deployment-validation)
- [Rollback Procedures](#rollback-procedures)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Platform-Specific Guides](#platform-specific-guides)

---

## 🎯 Overview

This checklist ensures a smooth, secure deployment of your Streamlit application to production. Follow each section carefully to avoid common pitfalls.

### Deployment Phases

```
Pre-Deployment → Configuration → Security → Deploy → Validate → Monitor
```

### Estimated Time

- **First deployment**: 2-4 hours
- **Subsequent deployments**: 30-60 minutes

---

## ✅ Pre-Deployment Checklist

### 1. Code Readiness

- [ ] All tests passing (`uv run pytest tests/ -v`)
- [ ] Code linting clean (`uv run pre-commit run --all-files`)
- [ ] No debug code or print statements in production code
- [ ] All TODO comments addressed or documented
- [ ] Version number updated in relevant files
- [ ] CHANGELOG.md updated with release notes

**Verification**:
```bash
# Run all checks
uv run pytest tests/ -v
uv run pre-commit run --all-files
grep -r "TODO" src/ app/  # Review remaining TODOs
```

### 2. Dependencies

- [ ] All dependencies listed in `pyproject.toml`
- [ ] Lock file updated (`uv lock`)
- [ ] No development-only dependencies in production
- [ ] Dependency versions pinned (no wildcards)
- [ ] Security vulnerabilities checked

**Verification**:
```bash
# Update lock file
uv lock

# Check for security issues (if using pip-audit)
uv run pip-audit

# Verify dependencies
uv run pip list
```

### 3. Environment Configuration

- [ ] `config/.env.example` is up to date
- [ ] Production environment variables documented
- [ ] API keys obtained for production
- [ ] Database credentials secured
- [ ] Third-party service credentials ready

**Verification**:
```bash
# Check environment variables
python -c "from config.settings import settings; print(settings.get_environment_info())"
```

### 4. Data and Assets

- [ ] Mock data removed or disabled in production
- [ ] Production data sources configured
- [ ] Static assets optimized (images, CSS)
- [ ] Large files moved to CDN or cloud storage
- [ ] Database migrations prepared (if applicable)

### 5. Documentation

- [ ] README.md updated with deployment instructions
- [ ] API documentation current
- [ ] Configuration guide reviewed
- [ ] Troubleshooting guide accessible
- [ ] Runbook created for operations team

---

## 🔄 Configuration Migration

### Step 1: Backup Current Configuration

```bash
# Backup existing config
cp .streamlit/config.toml .streamlit/config.toml.backup.$(date +%Y%m%d)

# Backup environment file
cp config/.env config/.env.backup.$(date +%Y%m%d)
```

### Step 2: Copy Production Configuration

```bash
# Copy production config
cp .streamlit/config.production.toml .streamlit/config.toml

# Verify configuration
cat .streamlit/config.toml
```

### Step 3: Update Environment Variables

**Create production `.env` file**:
```bash
# config/.env (production)
ENVIRONMENT=production
GEMINI_API_KEY=AIza...your-production-key
STREAMLIT_SERVER_PORT=8501

# Add production-specific variables
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
```

### Step 4: Validate Configuration

```bash
# Validate TOML syntax
python -c "import toml; toml.load('.streamlit/config.toml')"

# Check environment detection
python -c "from config.settings import settings; print(settings.get_environment_info())"

# Verify CORS/XSRF settings
python -c "
import toml
config = toml.load('.streamlit/config.toml')
cors = config['server']['enableCORS']
xsrf = config['server']['enableXsrfProtection']
assert cors == xsrf, 'CORS and XSRF must match'
print('✅ Configuration valid')
"
```

### Configuration Comparison

| Setting | Development | Production |
|---------|-------------|------------|
| `enableCORS` | `false` | `true` |
| `enableXsrfProtection` | `false` | `true` |
| `runOnSave` | `true` | `false` |
| `showErrorDetails` | `true` | `false` |
| `logger.level` | `"debug"` | `"info"` |
| `maxUploadSize` | `200` | `50` |
| `enableWebsocketCompression` | `false` | `true` |

---

## 🔒 Security Hardening

### 1. CORS Configuration

**Critical**: Configure allowed origins

```toml
# .streamlit/config.toml
[server]
enableCORS = true
corsAllowedOrigins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://app.yourdomain.com"
]
```

**Checklist**:
- [ ] CORS enabled (`enableCORS = true`)
- [ ] Allowed origins explicitly listed (no wildcards)
- [ ] All production domains included
- [ ] HTTPS used for all origins
- [ ] Subdomains properly configured

**Verification**:
```bash
# Test CORS from allowed origin
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://your-app-url.com
```

### 2. XSRF Protection

```toml
[server]
enableXsrfProtection = true
```

**Checklist**:
- [ ] XSRF protection enabled
- [ ] CORS also enabled (required)
- [ ] Cookie secret configured
- [ ] HTTPS enabled (required for secure cookies)

### 3. Session Security

```toml
[server]
cookieSecret = "your-secret-key-here"  # Set via environment variable
sessionStateMaxAge = 3600  # 1 hour
```

**Checklist**:
- [ ] Strong cookie secret (32+ characters)
- [ ] Secret stored in environment variable
- [ ] Appropriate session timeout
- [ ] Session invalidation on logout

**Generate secure secret**:
```bash
# Generate random secret
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Error Handling

```toml
[client]
showErrorDetails = false
toolbarMode = "minimal"
```

**Checklist**:
- [ ] Error details hidden from users
- [ ] Custom error pages configured
- [ ] Sensitive information not logged
- [ ] Error monitoring configured

### 5. API Key Protection

**Checklist**:
- [ ] API keys in environment variables only
- [ ] No keys in code or config files
- [ ] Keys not logged or displayed
- [ ] Separate keys for dev/staging/production
- [ ] Key rotation schedule established

**Verification**:
```bash
# Check for exposed keys in code
grep -r "AIza" src/ app/ --exclude-dir=.git

# Should only find references in config/settings.py
```

### 6. HTTPS Enforcement

**Checklist**:
- [ ] SSL/TLS certificate installed
- [ ] HTTP redirects to HTTPS
- [ ] HSTS header configured
- [ ] Secure cookie flags enabled
- [ ] Mixed content warnings resolved

### 7. Rate Limiting

**Implement at infrastructure level**:
- [ ] Reverse proxy rate limiting (nginx, Caddy)
- [ ] Cloud platform rate limiting (Cloudflare, AWS WAF)
- [ ] Application-level throttling
- [ ] DDoS protection enabled

### 8. Access Control

**Checklist**:
- [ ] Authentication implemented (if required)
- [ ] Authorization rules configured
- [ ] Admin access restricted
- [ ] Audit logging enabled
- [ ] IP whitelisting (if applicable)

---

## 🚀 Deployment Procedures

### Option 1: Streamlit Cloud

**Steps**:
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Configure secrets in Streamlit Cloud dashboard
4. Deploy

**Configuration**:
```toml
# Streamlit Cloud automatically sets:
# - enableCORS = true
# - enableXsrfProtection = true
# - HTTPS enabled

# Add secrets in dashboard:
# GEMINI_API_KEY = AIza...
# ENVIRONMENT = production
```

**Checklist**:
- [ ] Repository connected
- [ ] Secrets configured
- [ ] Custom domain configured (optional)
- [ ] App deployed and accessible

### Option 2: Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy application
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
```

**Build and run**:
```bash
# Build image
docker build -t dailyplus-ai .

# Run container
docker run -d \
  -p 8501:8501 \
  -e ENVIRONMENT=production \
  -e GEMINI_API_KEY=AIza... \
  --name dailyplus-ai \
  dailyplus-ai

# Check logs
docker logs dailyplus-ai
```

**Checklist**:
- [ ] Dockerfile created
- [ ] Image built successfully
- [ ] Container runs without errors
- [ ] Environment variables passed
- [ ] Health check working
- [ ] Logs accessible

### Option 3: Cloud Platform (AWS, GCP, Azure)

**General steps**:
1. Provision compute instance
2. Install dependencies
3. Configure environment
4. Set up reverse proxy (nginx)
5. Configure SSL/TLS
6. Start application

**Example (AWS EC2)**:
```bash
# SSH into instance
ssh -i key.pem ubuntu@instance-ip

# Install dependencies
sudo apt update
sudo apt install python3.11 python3-pip nginx

# Clone repository
git clone https://github.com/yourusername/DailyPlus_AI.git
cd DailyPlus_AI

# Install uv and dependencies
pip install uv
uv sync

# Configure environment
cp config/.env.example config/.env
nano config/.env  # Add production values

# Copy production config
cp .streamlit/config.production.toml .streamlit/config.toml

# Start with systemd
sudo nano /etc/systemd/system/dailyplus-ai.service
sudo systemctl enable dailyplus-ai
sudo systemctl start dailyplus-ai
```

**Systemd service file**:
```ini
[Unit]
Description=DailyPlus AI Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/DailyPlus_AI
Environment="PATH=/home/ubuntu/.local/bin:/usr/bin"
ExecStart=/home/ubuntu/.local/bin/uv run streamlit run app/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

**Checklist**:
- [ ] Instance provisioned
- [ ] Dependencies installed
- [ ] Application deployed
- [ ] Reverse proxy configured
- [ ] SSL certificate installed
- [ ] Firewall rules configured
- [ ] Service auto-starts on boot

### Option 4: Heroku

**Steps**:
```bash
# Install Heroku CLI
# Login
heroku login

# Create app
heroku create dailyplus-ai

# Set environment variables
heroku config:set ENVIRONMENT=production
heroku config:set GEMINI_API_KEY=AIza...

# Deploy
git push heroku main

# Open app
heroku open
```

**Procfile**:
```
web: streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0
```

**Checklist**:
- [ ] Heroku app created
- [ ] Environment variables set
- [ ] Procfile configured
- [ ] App deployed
- [ ] Custom domain configured (optional)

---

## ✅ Post-Deployment Validation

### 1. Functional Testing

**Basic functionality**:
- [ ] Application loads without errors
- [ ] All pages/tabs accessible
- [ ] Forms submit correctly
- [ ] Data displays properly
- [ ] API calls succeed

**Test script**:
```bash
# Test homepage
curl -I https://your-app-url.com

# Test health endpoint (if available)
curl https://your-app-url.com/_stcore/health

# Test with browser
# Open https://your-app-url.com
# Navigate through all features
```

### 2. Security Validation

**CORS testing**:
```bash
# Test from allowed origin (should succeed)
curl -H "Origin: https://yourdomain.com" \
     https://your-app-url.com

# Test from disallowed origin (should fail)
curl -H "Origin: https://malicious.com" \
     https://your-app-url.com
```

**HTTPS validation**:
- [ ] HTTPS loads without warnings
- [ ] HTTP redirects to HTTPS
- [ ] SSL certificate valid
- [ ] No mixed content warnings

**Security headers**:
```bash
# Check security headers
curl -I https://your-app-url.com | grep -i "strict-transport-security\|x-frame-options\|x-content-type-options"
```

### 3. Performance Testing

**Load time**:
- [ ] Initial load < 3 seconds
- [ ] Subsequent loads < 1 second
- [ ] API responses < 500ms

**Load testing**:
```bash
# Simple load test with Apache Bench
ab -n 100 -c 10 https://your-app-url.com/

# Or use more sophisticated tools
# - Locust
# - JMeter
# - k6
```

### 4. Monitoring Setup

**Checklist**:
- [ ] Application logs accessible
- [ ] Error tracking configured (Sentry, etc.)
- [ ] Uptime monitoring enabled (UptimeRobot, etc.)
- [ ] Performance monitoring configured
- [ ] Alerts configured for critical issues

### 5. Backup Verification

**Checklist**:
- [ ] Configuration backed up
- [ ] Database backed up (if applicable)
- [ ] Backup restoration tested
- [ ] Backup schedule configured

---

## 🔙 Rollback Procedures

### When to Rollback

- Critical bugs in production
- Security vulnerabilities discovered
- Performance degradation
- Data corruption
- User-facing errors

### Quick Rollback Steps

**1. Identify issue**:
```bash
# Check logs
tail -f /var/log/dailyplus-ai.log

# Check application status
systemctl status dailyplus-ai
```

**2. Restore previous configuration**:
```bash
# Restore config
cp .streamlit/config.toml.backup.YYYYMMDD .streamlit/config.toml

# Restore environment
cp config/.env.backup.YYYYMMDD config/.env
```

**3. Restart application**:
```bash
# Systemd
sudo systemctl restart dailyplus-ai

# Docker
docker restart dailyplus-ai

# Manual
pkill -f streamlit
uv run streamlit run app/main.py
```

**4. Verify rollback**:
```bash
# Test application
curl -I https://your-app-url.com

# Check logs
tail -f /var/log/dailyplus-ai.log
```

### Git-Based Rollback

```bash
# Find previous working commit
git log --oneline

# Rollback to specific commit
git revert <commit-hash>

# Or reset (destructive)
git reset --hard <commit-hash>

# Redeploy
git push origin main --force  # If needed
```

### Platform-Specific Rollback

**Streamlit Cloud**:
- Use dashboard to redeploy previous version
- Or push previous commit to GitHub

**Docker**:
```bash
# Use previous image
docker stop dailyplus-ai
docker run -d --name dailyplus-ai dailyplus-ai:previous-tag
```

**Heroku**:
```bash
# Rollback to previous release
heroku rollback
```

---

## 📊 Monitoring and Maintenance

### Daily Monitoring

**Checklist**:
- [ ] Check application uptime
- [ ] Review error logs
- [ ] Monitor response times
- [ ] Check resource usage (CPU, memory)
- [ ] Verify backup completion

**Monitoring script**:
```bash
#!/bin/bash
# daily-check.sh

echo "=== Daily Health Check ==="
echo "Date: $(date)"

# Check if app is running
if curl -s -o /dev/null -w "%{http_code}" https://your-app-url.com | grep -q "200"; then
    echo "✅ Application is up"
else
    echo "❌ Application is down"
    # Send alert
fi

# Check disk space
df -h | grep -E "/$|/var"

# Check memory
free -h

# Check recent errors
tail -n 50 /var/log/dailyplus-ai.log | grep -i error
```

### Weekly Maintenance

**Checklist**:
- [ ] Review performance metrics
- [ ] Check for security updates
- [ ] Update dependencies (if needed)
- [ ] Review and rotate logs
- [ ] Test backup restoration
- [ ] Review user feedback

### Monthly Maintenance

**Checklist**:
- [ ] Security audit
- [ ] Performance optimization review
- [ ] Dependency updates
- [ ] SSL certificate renewal check
- [ ] Capacity planning review
- [ ] Documentation updates

### Quarterly Maintenance

**Checklist**:
- [ ] Major version updates
- [ ] Infrastructure review
- [ ] Disaster recovery drill
- [ ] Security penetration testing
- [ ] Cost optimization review

---

## 🌐 Platform-Specific Guides

### Streamlit Cloud

**Advantages**:
- Zero infrastructure management
- Automatic HTTPS
- Built-in secrets management
- Easy GitHub integration

**Configuration**:
```toml
# No special config needed
# Streamlit Cloud handles CORS/XSRF automatically
```

**Secrets management**:
1. Go to app settings
2. Click "Secrets"
3. Add in TOML format:
```toml
GEMINI_API_KEY = "AIza..."
ENVIRONMENT = "production"
```

### AWS (EC2 + nginx)

**nginx configuration**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Google Cloud Platform (Cloud Run)

**Dockerfile** (optimized for Cloud Run):
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv && uv sync

EXPOSE 8080

CMD ["uv", "run", "streamlit", "run", "app/main.py", "--server.port=8080", "--server.address=0.0.0.0"]
```

**Deploy**:
```bash
gcloud run deploy dailyplus-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure (App Service)

**Configuration**:
```bash
# Create app service
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name dailyplus-ai \
  --runtime "PYTHON:3.11"

# Configure environment
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name dailyplus-ai \
  --settings ENVIRONMENT=production GEMINI_API_KEY=AIza...

# Deploy
az webapp up --name dailyplus-ai
```

---

## 📝 Deployment Log Template

Keep a log of each deployment:

```markdown
# Deployment Log

## Deployment #X - YYYY-MM-DD

### Pre-Deployment
- [ ] Tests passed
- [ ] Configuration validated
- [ ] Backup created

### Deployment
- **Time**: HH:MM UTC
- **Version**: vX.Y.Z
- **Deployed by**: Name
- **Platform**: Streamlit Cloud / AWS / etc.

### Changes
- Feature 1
- Bug fix 2
- Configuration update 3

### Post-Deployment
- [ ] Functional tests passed
- [ ] Security validated
- [ ] Performance acceptable
- [ ] Monitoring configured

### Issues
- None / List any issues

### Rollback Plan
- Restore from backup YYYYMMDD
- Revert to commit abc123

### Notes
- Any additional notes
```

---

**Last Updated**: 2026-05-17  
**Maintained By**: DailyPlus_AI Team  
**Version**: 1.0.0

---

**Made with Bob** 🤖