# 🔧 Streamlit Configuration Guide

> **Comprehensive guide to configuring Streamlit for DailyPlus_AI**  
> Best practices, security considerations, and optimization techniques

---

## 📋 Table of Contents

- [Overview](#overview)
- [Configuration File Hierarchy](#configuration-file-hierarchy)
- [Environment-Specific Configuration](#environment-specific-configuration)
- [Security Best Practices](#security-best-practices)
- [Performance Optimization](#performance-optimization)
- [Common Configuration Patterns](#common-configuration-patterns)
- [Advanced Customization](#advanced-customization)
- [Configuration Reference](#configuration-reference)
- [Quick Reference Card](#quick-reference-card)

---

## 🎯 Overview

Streamlit uses TOML configuration files to customize application behavior. DailyPlus_AI implements a multi-environment configuration strategy with separate settings for development and production.

### Why Configuration Matters

- **Security**: Proper CORS/XSRF settings protect against attacks
- **Performance**: Optimized settings improve user experience
- **Reliability**: Correct configuration prevents runtime errors
- **Maintainability**: Environment-specific configs simplify deployment

### Configuration Philosophy

```
Development: Convenience > Security (local testing)
Production: Security > Convenience (public deployment)
```

---

## 📁 Configuration File Hierarchy

### File Structure

```
.streamlit/
├── config.toml                    # Base configuration (development)
├── config.development.toml        # Explicit development settings
├── config.production.toml         # Production-ready settings
└── README.md                      # Configuration documentation
```

### Loading Precedence

Streamlit loads configuration in this order (later overrides earlier):

1. **Default Streamlit settings** (built-in)
2. **`.streamlit/config.toml`** (project-level)
3. **Environment variables** (e.g., `STREAMLIT_SERVER_PORT`)
4. **Command-line arguments** (e.g., `--server.port 8501`)

### Example Override Chain

```bash
# Base config sets port to 8501
# Environment variable overrides to 8502
export STREAMLIT_SERVER_PORT=8502

# Command-line argument overrides to 8503 (highest priority)
streamlit run app/main.py --server.port 8503
```

---

## 🌍 Environment-Specific Configuration

### Development Configuration

**File**: `.streamlit/config.toml` or `.streamlit/config.development.toml`

**Purpose**: Local development and testing

**Key Features**:
- ✅ CORS disabled for easy local access
- ✅ XSRF protection disabled (required when CORS is off)
- ✅ Auto-reload on file changes
- ✅ Verbose logging for debugging
- ✅ Generous upload limits
- ✅ Error details shown to developers

**Example**:
```toml
[server]
enableCORS = false
enableXsrfProtection = false  # MUST match CORS setting
runOnSave = true
maxUploadSize = 200  # MB

[logger]
level = "debug"

[client]
showErrorDetails = true
toolbarMode = "developer"
```

**When to Use**:
- Local development on `localhost`
- Testing new features
- Debugging issues
- Rapid prototyping

### Production Configuration

**File**: `.streamlit/config.production.toml`

**Purpose**: Public deployment with security hardening

**Key Features**:
- ✅ CORS enabled with allowed origins
- ✅ XSRF protection enabled
- ✅ Websocket compression for performance
- ✅ Error details hidden from users
- ✅ Resource limits enforced
- ✅ Auto-reload disabled

**Example**:
```toml
[server]
enableCORS = true
enableXsrfProtection = true  # MUST be true with CORS
enableWebsocketCompression = true
maxUploadSize = 50  # MB
runOnSave = false

[logger]
level = "info"

[client]
showErrorDetails = false
toolbarMode = "minimal"
```

**When to Use**:
- Production deployments
- Public-facing applications
- Cloud hosting (Streamlit Cloud, Heroku, AWS)
- Any environment accessible from the internet

### Switching Between Environments

**Method 1: Copy Configuration File**
```bash
# Switch to development
cp .streamlit/config.development.toml .streamlit/config.toml

# Switch to production
cp .streamlit/config.production.toml .streamlit/config.toml
```

**Method 2: Environment Variable**
```bash
# Set environment in config/.env
ENVIRONMENT=production

# Application detects and uses appropriate config
python -c "from config.settings import settings; print(settings.get_environment_info())"
```

**Method 3: Command-Line Override**
```bash
# Override specific settings without changing files
streamlit run app/main.py \
  --server.enableCORS=true \
  --server.enableXsrfProtection=true \
  --server.port=8501
```

---

## 🔒 Security Best Practices

### Critical Security Rule: CORS and XSRF Relationship

**⚠️ IMPORTANT**: When `enableCORS = false`, `enableXsrfProtection` MUST also be `false`

This is a Streamlit requirement to prevent configuration conflicts.

### Understanding CORS (Cross-Origin Resource Sharing)

**What it does**:
- Controls which domains can access your Streamlit app
- Prevents unauthorized cross-origin requests
- Essential for public deployments

**Configuration**:
```toml
[server]
enableCORS = true
corsAllowedOrigins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://app.yourdomain.com"
]
```

**When to enable**:
- ✅ Production deployments
- ✅ Public-facing applications
- ✅ Multi-domain setups
- ❌ Local development (localhost only)

### Understanding XSRF Protection (Cross-Site Request Forgery)

**What it does**:
- Prevents malicious websites from making unauthorized requests
- Uses tokens to verify request authenticity
- Requires CORS to be enabled

**Configuration**:
```toml
[server]
enableXsrfProtection = true  # Only when CORS is enabled
```

**When to enable**:
- ✅ Always in production (with CORS)
- ✅ When handling sensitive data
- ✅ When users can perform actions
- ❌ Local development (convenience)

### Valid Configuration Matrix

| Environment | CORS | XSRF | Security Level | Use Case |
|-------------|------|------|----------------|----------|
| Development | ❌ | ❌ | Low | Local testing |
| Staging | ✅ | ✅ | High | Pre-production |
| Production | ✅ | ✅ | High | Public deployment |

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

### Additional Security Measures

#### 1. Cookie Security
```toml
[server]
cookieSecret = "your-secret-key-here"  # Set via environment variable
```

**Best practices**:
- Use strong, random secrets (32+ characters)
- Store in environment variables, not config files
- Rotate secrets periodically
- Never commit secrets to version control

#### 2. HTTPS Enforcement
```toml
[server]
# Ensure your hosting platform provides HTTPS
# Most cloud platforms handle this automatically
```

**Requirements**:
- SSL/TLS certificate
- HTTPS redirect at load balancer/proxy level
- Secure cookie flags enabled

#### 3. Session Management
```toml
[server]
sessionStateMaxAge = 3600  # 1 hour timeout
```

**Recommendations**:
- Set appropriate session timeouts
- Clear sensitive data on logout
- Implement session invalidation

#### 4. Rate Limiting

While Streamlit doesn't have built-in rate limiting, implement at the infrastructure level:
- Use reverse proxy (nginx, Caddy)
- Cloud platform rate limiting (Cloudflare, AWS WAF)
- Application-level throttling

---

## ⚡ Performance Optimization

### Caching Configuration

```toml
[client]
caching = true
```

**Best practices**:
- Use `@st.cache_data` for data transformations
- Use `@st.cache_resource` for ML models, database connections
- Set appropriate TTL (time-to-live) values
- Clear cache when data changes

### Websocket Compression

```toml
[server]
enableWebsocketCompression = true
```

**Benefits**:
- Reduces bandwidth usage by 60-80%
- Faster page loads
- Better performance on slow connections
- Essential for production

**When to enable**:
- ✅ Production deployments
- ✅ Large data transfers
- ✅ Slow network connections
- ❌ Local development (minimal benefit)

### Upload Size Limits

```toml
[server]
maxUploadSize = 50  # MB
```

**Recommendations**:
- Development: 200 MB (generous for testing)
- Production: 50 MB (reasonable limit)
- Adjust based on your use case
- Consider cloud storage for large files

### Fast Reruns

```toml
[runner]
fastReruns = true
```

**Benefits**:
- Faster UI updates
- Better user experience
- Reduced server load

### Static File Serving

```toml
[server]
enableStaticServing = false  # Disable if using CDN
```

**Recommendations**:
- Development: `true` (serve locally)
- Production with CDN: `false` (use CDN)
- Production without CDN: `true` (serve from app)

---

## 🎨 Common Configuration Patterns

### Pattern 1: Local Development

```toml
# .streamlit/config.toml
[theme]
primaryColor = "#333333"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f4f4f4"
textColor = "#333333"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = false
enableXsrfProtection = false
runOnSave = true
maxUploadSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"

[logger]
level = "debug"

[client]
showErrorDetails = true
toolbarMode = "developer"
```

### Pattern 2: Production Deployment

```toml
# .streamlit/config.production.toml
[theme]
primaryColor = "#333333"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f4f4f4"
textColor = "#333333"
font = "sans serif"

[server]
headless = true
port = 8501
enableCORS = true
enableXsrfProtection = true
enableWebsocketCompression = true
maxUploadSize = 50
runOnSave = false
corsAllowedOrigins = ["https://yourdomain.com"]

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"

[logger]
level = "info"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[runner]
fastReruns = true
enforceSerializableSessionState = true
```

### Pattern 3: Staging Environment

```toml
# .streamlit/config.staging.toml
# Hybrid: Production security with development debugging

[server]
enableCORS = true
enableXsrfProtection = true
corsAllowedOrigins = ["https://staging.yourdomain.com"]

[logger]
level = "debug"  # More verbose than production

[client]
showErrorDetails = true  # Show errors to testers
toolbarMode = "developer"
```

### Pattern 4: Multi-Port Development

```toml
# For running multiple instances
[server]
port = 8501  # Main instance

# Run additional instances:
# streamlit run app/main.py --server.port 8502
# streamlit run app/main.py --server.port 8503
```

---

## 🚀 Advanced Customization

### Custom Themes

```toml
[theme]
# Primary color (buttons, links)
primaryColor = "#FF4B4B"

# Background color
backgroundColor = "#0E1117"

# Secondary background (sidebar, inputs)
secondaryBackgroundColor = "#262730"

# Text color
textColor = "#FAFAFA"

# Font family
font = "sans serif"  # Options: "sans serif", "serif", "monospace"
```

**Theme presets**:
- Light mode: `backgroundColor = "#ffffff"`, `textColor = "#333333"`
- Dark mode: `backgroundColor = "#0E1117"`, `textColor = "#FAFAFA"`
- High contrast: Increase color differences for accessibility

### Custom Server Settings

```toml
[server]
# Base URL path (for reverse proxy)
baseUrlPath = "/app"

# File watcher type
fileWatcherType = "auto"  # Options: "auto", "poll", "none"

# Max message size (MB)
maxMessageSize = 200

# Enable CORS for all origins (development only!)
# corsAllowedOrigins = ["*"]  # ⚠️ NEVER use in production
```

### Browser Behavior

```toml
[browser]
# Prevent automatic browser launch
gatherUsageStats = false

# Server address for browser
serverAddress = "localhost"  # or "0.0.0.0" for all interfaces

# Server port for browser
serverPort = 8501
```

### Logger Configuration

```toml
[logger]
# Log level: "debug", "info", "warning", "error", "critical"
level = "info"

# Message format
messageFormat = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

### Runner Settings

```toml
[runner]
# Enable magic commands
magicEnabled = true

# Install tracer (development only)
installTracer = false

# Fix matplotlib backend
fixMatplotlib = true

# Fast reruns
fastReruns = true

# Enforce serializable session state
enforceSerializableSessionState = true

# Post-script GC (garbage collection)
postScriptGC = true
```

### Deprecation Warnings

```toml
[deprecation]
# Show pyplot global use warning
showPyplotGlobalUse = false

# Show file uploader encoding warning
showfileUploaderEncoding = false
```

---

## 📖 Configuration Reference

### Complete Configuration Options

#### [theme]
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `primaryColor` | string | "#FF4B4B" | Primary accent color |
| `backgroundColor` | string | "#FFFFFF" | Main background color |
| `secondaryBackgroundColor` | string | "#F0F2F6" | Sidebar/input background |
| `textColor` | string | "#262730" | Text color |
| `font` | string | "sans serif" | Font family |

#### [server]
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `headless` | boolean | false | Run without browser |
| `port` | integer | 8501 | Server port |
| `enableCORS` | boolean | true | Enable CORS |
| `enableXsrfProtection` | boolean | true | Enable XSRF protection |
| `corsAllowedOrigins` | array | [] | Allowed origins |
| `maxUploadSize` | integer | 200 | Max upload size (MB) |
| `enableWebsocketCompression` | boolean | true | Enable compression |
| `runOnSave` | boolean | false | Auto-reload on save |

#### [browser]
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `gatherUsageStats` | boolean | true | Collect usage stats |
| `serverAddress` | string | "localhost" | Server address |
| `serverPort` | integer | 8501 | Server port |

#### [logger]
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `level` | string | "info" | Log level |
| `messageFormat` | string | "%(message)s" | Log format |

#### [client]
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `showErrorDetails` | boolean | true | Show error details |
| `toolbarMode` | string | "auto" | Toolbar mode |

#### [runner]
| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `magicEnabled` | boolean | true | Enable magic commands |
| `fastReruns` | boolean | true | Fast reruns |
| `enforceSerializableSessionState` | boolean | false | Enforce serialization |

---

## 🎯 Quick Reference Card

### Development Quick Start
```bash
# Use default development config
streamlit run app/main.py

# Or use Python launcher with port management
python scripts/start_streamlit.py --auto-kill
```

### Production Deployment
```bash
# Copy production config
cp .streamlit/config.production.toml .streamlit/config.toml

# Set environment
export ENVIRONMENT=production

# Deploy
streamlit run app/main.py
```

### Common Commands
```bash
# Check configuration
streamlit config show

# Clear cache
streamlit cache clear

# Run with custom port
streamlit run app/main.py --server.port 8502

# Run with custom config
streamlit run app/main.py --server.enableCORS=true
```

### Configuration Checklist

#### Development ✅
- [ ] CORS disabled
- [ ] XSRF disabled
- [ ] Auto-reload enabled
- [ ] Debug logging enabled
- [ ] Error details shown

#### Production ✅
- [ ] CORS enabled
- [ ] XSRF enabled
- [ ] Allowed origins configured
- [ ] HTTPS enabled
- [ ] Error details hidden
- [ ] Websocket compression enabled
- [ ] Appropriate upload limits
- [ ] Session timeout configured

---

## 📚 Additional Resources

### Official Documentation
- [Streamlit Configuration](https://docs.streamlit.io/library/advanced-features/configuration)
- [Streamlit Security](https://docs.streamlit.io/library/advanced-features/configuration#server)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)

### Project Documentation
- [Troubleshooting Guide](TROUBLESHOOTING_STREAMLIT.md)
- [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
- [Port Management](../scripts/README.md)
- [Configuration README](../.streamlit/README.md)

### Related Topics
- [Environment Configuration](../config/settings.py)
- [Application Architecture](ARCHITECTURE.md)
- [Setup Guide](SETUP.md)

---

**Last Updated**: 2026-05-17  
**Maintained By**: DailyPlus_AI Team  
**Version**: 1.0.0

---

**Made with Bob** 🤖