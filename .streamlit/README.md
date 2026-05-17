# Streamlit Configuration Guide

This directory contains environment-specific Streamlit configurations for the DailyPlus_AI application.

## 📁 Configuration Files

### `config.toml` (Base/Development)
The default configuration file used for local development. Optimized for developer convenience with relaxed security settings.

**Key Settings:**
- ✅ CORS disabled (`enableCORS = false`)
- ✅ XSRF protection disabled (`enableXsrfProtection = false`)
- ✅ Auto-reload enabled
- ✅ Verbose logging

**Use Case:** Local development and testing

### `config.development.toml`
Explicit development configuration with detailed comments and developer-friendly settings.

**Key Settings:**
- Same as base config.toml
- Additional development tools enabled
- Comprehensive documentation

**Use Case:** Reference configuration for development environments

### `config.production.toml`
Production-ready configuration with security hardening and performance optimizations.

**Key Settings:**
- ✅ CORS enabled (`enableCORS = true`)
- ✅ XSRF protection enabled (`enableXsrfProtection = true`)
- ✅ Websocket compression enabled
- ✅ Error details hidden from users
- ✅ Resource limits enforced

**Use Case:** Production deployments

---

## 🔒 CORS and XSRF Protection Relationship

### Critical Security Rule

**When `enableCORS = false`, `enableXsrfProtection` MUST also be `false`**

This is a Streamlit requirement to prevent configuration conflicts.

### Why This Matters

#### CORS (Cross-Origin Resource Sharing)
- Controls which domains can access your Streamlit app
- When disabled: Any origin can make requests (convenient for development)
- When enabled: Only specified origins can access the app (secure for production)

#### XSRF Protection (Cross-Site Request Forgery)
- Prevents malicious websites from making unauthorized requests
- Requires CORS to be enabled to work properly
- Uses tokens to verify request authenticity

### Configuration Matrix

| Environment | CORS | XSRF | Security Level | Use Case |
|-------------|------|------|----------------|----------|
| Development | ❌ Disabled | ❌ Disabled | Low | Local testing |
| Production | ✅ Enabled | ✅ Enabled | High | Public deployment |

### Invalid Configurations ⚠️

```toml
# ❌ INVALID - Will cause errors
enableCORS = false
enableXsrfProtection = true  # Cannot enable XSRF without CORS
```

```toml
# ✅ VALID - Development
enableCORS = false
enableXsrfProtection = false
```

```toml
# ✅ VALID - Production
enableCORS = true
enableXsrfProtection = true
```

---

## 🚀 Usage Instructions

### Development Environment

**Option 1: Use default config (Recommended)**
```bash
# Uses config.toml automatically
streamlit run app/main.py
```

**Option 2: Explicit development config**
```bash
# Copy development config to config.toml
cp .streamlit/config.development.toml .streamlit/config.toml
streamlit run app/main.py
```

**Option 3: Using Python settings**
```python
from config.settings import settings

# Check environment
print(f"Environment: {settings.ENVIRONMENT}")
print(f"Config path: {settings.get_streamlit_config_path()}")

# Get environment info
info = settings.get_environment_info()
print(info)
```

### Production Environment

**Option 1: Copy production config**
```bash
# Before deployment, copy production config
cp .streamlit/config.production.toml .streamlit/config.toml

# Deploy with production settings
streamlit run app/main.py
```

**Option 2: Environment variable**
```bash
# Set environment to production
export ENVIRONMENT=production

# Application will use production settings
streamlit run app/main.py
```

**Option 3: Command-line override**
```bash
# Override specific settings
streamlit run app/main.py \
  --server.enableCORS=true \
  --server.enableXsrfProtection=true \
  --server.port=8501
```

**Option 4: Cloud platform deployment**
```bash
# Most cloud platforms (Streamlit Cloud, Heroku, etc.)
# automatically enable CORS and XSRF protection
# Just ensure your config.toml has production settings
```

---

## 🔧 Environment Detection

The application automatically detects the environment using the `ENVIRONMENT` variable in `config/.env`:

```bash
# config/.env
ENVIRONMENT=development  # or 'production'
```

### Programmatic Environment Detection

```python
from config.settings import settings

# Check environment
if settings.is_production():
    print("Running in production mode")
    print(f"CORS enabled: {settings.get_environment_info()['cors_enabled']}")
else:
    print("Running in development mode")
    print(f"CORS enabled: {settings.get_environment_info()['cors_enabled']}")

# Get config path
config_path = settings.get_streamlit_config_path()
print(f"Using config: {config_path}")
```

---

## 🐛 Troubleshooting

### Problem: "XSRF protection requires CORS to be enabled"

**Cause:** Invalid configuration with `enableCORS = false` and `enableXsrfProtection = true`

**Solution:**
```bash
# For development
# Edit .streamlit/config.toml
enableCORS = false
enableXsrfProtection = false  # Must match CORS setting

# For production
enableCORS = true
enableXsrfProtection = true  # Both enabled together
```

### Problem: "Connection refused" or CORS errors in browser

**Cause:** CORS is enabled but allowed origins not configured

**Solution:**
```toml
# Add to config.production.toml
[server]
enableCORS = true
corsAllowedOrigins = ["https://yourdomain.com", "https://www.yourdomain.com"]
```

### Problem: App works locally but fails in production

**Cause:** Using development config in production

**Solution:**
```bash
# Ensure production config is active
cp .streamlit/config.production.toml .streamlit/config.toml

# Or set environment variable
export ENVIRONMENT=production
```

### Problem: Changes to config.toml not taking effect

**Cause:** Streamlit caches configuration

**Solution:**
```bash
# Clear Streamlit cache
streamlit cache clear

# Restart the application
# Kill existing process and restart
```

### Problem: Port already in use

**Cause:** Previous Streamlit instance still running

**Solution:**
```bash
# Windows PowerShell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess -Force

# Linux/Mac
lsof -ti:8501 | xargs kill -9

# Then restart
streamlit run app/main.py
```

---

## 📚 Additional Resources

### Streamlit Documentation
- [Configuration Options](https://docs.streamlit.io/library/advanced-features/configuration)
- [CORS and XSRF Protection](https://docs.streamlit.io/library/advanced-features/configuration#server)
- [Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)

### Security Best Practices
1. **Always enable CORS and XSRF in production**
2. **Use HTTPS in production** (required for secure cookies)
3. **Configure allowed origins** explicitly
4. **Set strong session secrets** via environment variables
5. **Hide error details** from end users
6. **Implement rate limiting** for API endpoints
7. **Regular security audits** of configuration

### Configuration Checklist

#### Before Development
- [ ] Copy `config/.env.example` to `config/.env`
- [ ] Set `ENVIRONMENT=development`
- [ ] Verify `config.toml` has CORS and XSRF disabled
- [ ] Test local access at `http://localhost:8501`

#### Before Production Deployment
- [ ] Copy `config.production.toml` to `config.toml`
- [ ] Set `ENVIRONMENT=production` in environment
- [ ] Configure `corsAllowedOrigins` for your domain
- [ ] Set `cookieSecret` via environment variable
- [ ] Enable HTTPS on your hosting platform
- [ ] Test CORS and XSRF protection
- [ ] Verify error details are hidden
- [ ] Monitor logs for security issues

---

## 🔄 Migration Guide

### Upgrading from Old Configuration

If you have an existing `config.toml` with the invalid CORS/XSRF combination:

```bash
# 1. Backup existing config
cp .streamlit/config.toml .streamlit/config.toml.backup

# 2. For development, use the new config
cp .streamlit/config.development.toml .streamlit/config.toml

# 3. For production, use production config
cp .streamlit/config.production.toml .streamlit/config.toml

# 4. Update your deployment scripts to use appropriate config
```

### Switching Between Environments

```bash
# Switch to development
cp .streamlit/config.development.toml .streamlit/config.toml
export ENVIRONMENT=development

# Switch to production
cp .streamlit/config.production.toml .streamlit/config.toml
export ENVIRONMENT=production
```

---

## 📝 Notes

- Configuration files are loaded in order: `config.toml` → environment variables → command-line arguments
- Command-line arguments override all other settings
- Environment variables override config file settings
- The `config.toml` file is the base configuration
- Always test configuration changes in a development environment first
- Keep production secrets out of version control (use environment variables)

---

**Last Updated:** 2026-05-17  
**Maintained By:** DailyPlus_AI Team