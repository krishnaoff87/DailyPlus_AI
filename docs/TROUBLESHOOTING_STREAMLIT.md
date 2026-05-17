# 🔧 Streamlit Troubleshooting Guide

> **Practical solutions to common Streamlit issues**  
> Error messages, debugging techniques, and resolution strategies

---

## 📋 Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Common Error Messages](#common-error-messages)
- [Port Conflicts](#port-conflicts)
- [CORS and XSRF Issues](#cors-and-xsrf-issues)
- [Configuration Problems](#configuration-problems)
- [Performance Issues](#performance-issues)
- [Debugging Techniques](#debugging-techniques)
- [Platform-Specific Issues](#platform-specific-issues)
- [FAQ](#faq)
- [Getting Help](#getting-help)

---

## 🚨 Quick Diagnostics

### Is Your App Running?

```bash
# Check if Streamlit is running on port 8501
# Windows PowerShell
Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue

# Linux/Mac
lsof -i :8501

# Cross-platform (Python)
python scripts/port_manager.py -p 8501 --check
```

### Quick Health Check

```bash
# 1. Verify Streamlit installation
streamlit --version

# 2. Check configuration
streamlit config show

# 3. Test basic app
echo "import streamlit as st; st.write('Hello')" > test.py
streamlit run test.py

# 4. Check API key
python -c "from config.settings import settings; print('API key valid')"
```

### Configuration Validation Checklist

- [ ] `.streamlit/config.toml` exists
- [ ] CORS and XSRF settings match (both enabled or both disabled)
- [ ] Port is not in use by another process
- [ ] API key is set in `config/.env`
- [ ] Python version is 3.11+
- [ ] All dependencies are installed (`uv sync`)

---

## ❌ Common Error Messages

### Error 1: "XSRF protection requires CORS to be enabled"

**Error Message**:
```
StreamlitAPIException: XSRF protection requires CORS to be enabled.
Please set server.enableCORS=true in your config.
```

**Cause**: Invalid configuration with `enableCORS = false` and `enableXsrfProtection = true`

**Solution**:
```toml
# Option 1: Development (both disabled)
[server]
enableCORS = false
enableXsrfProtection = false

# Option 2: Production (both enabled)
[server]
enableCORS = true
enableXsrfProtection = true
```

**Quick Fix**:
```bash
# For development
cp .streamlit/config.development.toml .streamlit/config.toml

# For production
cp .streamlit/config.production.toml .streamlit/config.toml
```

---

### Error 2: "Address already in use"

**Error Message**:
```
OSError: [Errno 98] Address already in use
or
OSError: [WinError 10048] Only one usage of each socket address is normally permitted
```

**Cause**: Another process is using port 8501

**Solution 1: Use Port Manager (Recommended)**
```bash
# Python launcher (auto-kills existing process)
python scripts/start_streamlit.py --auto-kill

# PowerShell launcher
.\scripts\start_streamlit.ps1
```

**Solution 2: Manual Port Management**
```bash
# Windows PowerShell
Stop-Process -Id (Get-NetTCPConnection -LocalPort 8501).OwningProcess -Force

# Linux/Mac
lsof -ti:8501 | xargs kill -9

# Then restart
streamlit run app/main.py
```

**Solution 3: Use Different Port**
```bash
# Find available port
python scripts/port_manager.py -p 8501 --find

# Run on different port
streamlit run app/main.py --server.port 8502
```

---

### Error 3: "CORS error" in Browser Console

**Error Message** (Browser Console):
```
Access to XMLHttpRequest at 'http://localhost:8501' from origin 'http://example.com' 
has been blocked by CORS policy
```

**Cause**: CORS is enabled but your domain is not in allowed origins

**Solution**:
```toml
# Add your domain to allowed origins
[server]
enableCORS = true
corsAllowedOrigins = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "http://localhost:3000"  # For local frontend development
]
```

**Development Workaround**:
```toml
# Disable CORS for local development
[server]
enableCORS = false
enableXsrfProtection = false
```

---

### Error 4: "ModuleNotFoundError: No module named 'streamlit'"

**Error Message**:
```
ModuleNotFoundError: No module named 'streamlit'
```

**Cause**: Streamlit not installed or wrong Python environment

**Solution**:
```bash
# Check Python version
python --version  # Should be 3.11+

# Install dependencies
uv sync

# Verify installation
uv run streamlit --version

# Run with uv
uv run streamlit run app/main.py
```

---

### Error 5: "Invalid GEMINI_API_KEY format"

**Error Message**:
```
ValueError: Invalid GEMINI_API_KEY format!
The API key must start with 'AIza'.
```

**Cause**: Missing or invalid API key in `config/.env`

**Solution**:
```bash
# 1. Copy example file
cp config/.env.example config/.env

# 2. Edit config/.env and add your API key
# GEMINI_API_KEY=AIza...your-key-here

# 3. Verify
python -c "from config.settings import settings; print('API key valid')"
```

**Get API Key**: https://aistudio.google.com/app/apikey

---

### Error 6: "Connection refused" or "Cannot connect to server"

**Error Message**:
```
ConnectionError: Cannot connect to Streamlit server
```

**Possible Causes & Solutions**:

**Cause 1: Server not running**
```bash
# Check if server is running
python scripts/port_manager.py -p 8501 --check

# Start server
python scripts/start_streamlit.py
```

**Cause 2: Firewall blocking**
```bash
# Windows: Allow Python through firewall
# Settings > Windows Security > Firewall > Allow an app

# Linux: Check firewall rules
sudo ufw status
sudo ufw allow 8501
```

**Cause 3: Wrong server address**
```toml
# For local access only
[browser]
serverAddress = "localhost"

# For network access
[browser]
serverAddress = "0.0.0.0"
```

---

### Error 7: "Session state error" or "Widget state lost"

**Error Message**:
```
StreamlitAPIException: Session state error
```

**Cause**: Session state not properly serialized

**Solution**:
```toml
# Enable session state enforcement
[runner]
enforceSerializableSessionState = true
```

**Code Fix**:
```python
# Use session state correctly
if 'key' not in st.session_state:
    st.session_state.key = initial_value

# Avoid storing non-serializable objects
# ❌ Bad: st.session_state.db = DatabaseConnection()
# ✅ Good: Use @st.cache_resource for connections
```

---

## 🔌 Port Conflicts

### Identifying Port Conflicts

**Check if port is in use**:
```bash
# Method 1: Port manager
python scripts/port_manager.py -p 8501 --info

# Method 2: Windows PowerShell
Get-NetTCPConnection -LocalPort 8501 | Select-Object OwningProcess, State

# Method 3: Linux/Mac
lsof -i :8501
```

### Resolution Strategies

#### Strategy 1: Kill Existing Process (Recommended)
```bash
# Automated (Python)
python scripts/start_streamlit.py --auto-kill

# Automated (PowerShell)
.\scripts\start_streamlit.ps1

# Manual (Windows)
Stop-Process -Id <PID> -Force

# Manual (Linux/Mac)
kill -9 <PID>
```

#### Strategy 2: Use Alternative Port
```bash
# Find available port
python scripts/port_manager.py -p 8501 --find

# Run on alternative port
streamlit run app/main.py --server.port 8502
```

#### Strategy 3: Configure Default Port
```toml
# .streamlit/config.toml
[server]
port = 8502  # Use different default port
```

### Multiple Streamlit Instances

Running multiple apps simultaneously:
```bash
# Terminal 1: Main app on 8501
streamlit run app/main.py --server.port 8501

# Terminal 2: Test app on 8502
streamlit run test_app.py --server.port 8502

# Terminal 3: Debug app on 8503
streamlit run debug_app.py --server.port 8503
```

---

## 🔒 CORS and XSRF Issues

### Understanding the Relationship

```
CORS Disabled → XSRF MUST be Disabled
CORS Enabled → XSRF SHOULD be Enabled
```

### Common CORS/XSRF Scenarios

#### Scenario 1: Local Development
```toml
# ✅ Correct
[server]
enableCORS = false
enableXsrfProtection = false
```

#### Scenario 2: Production Deployment
```toml
# ✅ Correct
[server]
enableCORS = true
enableXsrfProtection = true
corsAllowedOrigins = ["https://yourdomain.com"]
```

#### Scenario 3: Development with Frontend
```toml
# ✅ Correct - Allow localhost origins
[server]
enableCORS = true
enableXsrfProtection = true
corsAllowedOrigins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000"
]
```

### Debugging CORS Issues

**Enable CORS debugging**:
```toml
[logger]
level = "debug"
```

**Check browser console**:
1. Open Developer Tools (F12)
2. Go to Console tab
3. Look for CORS-related errors
4. Check Network tab for failed requests

**Test CORS configuration**:
```bash
# Test from command line
curl -H "Origin: https://yourdomain.com" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS \
     http://localhost:8501
```

---

## ⚙️ Configuration Problems

### Configuration Not Loading

**Problem**: Changes to `config.toml` not taking effect

**Solutions**:
```bash
# 1. Clear Streamlit cache
streamlit cache clear

# 2. Restart the application
# Kill process and restart

# 3. Verify configuration is loaded
streamlit config show

# 4. Check for syntax errors in TOML
python -c "import toml; toml.load('.streamlit/config.toml')"
```

### Wrong Configuration File Loaded

**Problem**: App using wrong environment config

**Diagnosis**:
```python
# Check which config is active
from config.settings import settings
print(settings.get_environment_info())
```

**Solution**:
```bash
# Ensure correct config is copied
cp .streamlit/config.production.toml .streamlit/config.toml

# Or set environment variable
export ENVIRONMENT=production
```

### Configuration Validation

**Validate configuration syntax**:
```python
import toml

try:
    config = toml.load('.streamlit/config.toml')
    print("✅ Configuration is valid")
    print(config)
except Exception as e:
    print(f"❌ Configuration error: {e}")
```

**Common TOML syntax errors**:
```toml
# ❌ Wrong: Missing quotes
corsAllowedOrigins = [https://example.com]

# ✅ Correct: With quotes
corsAllowedOrigins = ["https://example.com"]

# ❌ Wrong: Wrong boolean
enableCORS = True  # Python syntax

# ✅ Correct: TOML boolean
enableCORS = true  # TOML syntax
```

---

## 🐌 Performance Issues

### Slow App Loading

**Diagnosis**:
```python
import time
import streamlit as st

start = time.time()
# Your code here
st.write(f"Load time: {time.time() - start:.2f}s")
```

**Solutions**:

**1. Enable Caching**
```python
@st.cache_data
def load_data():
    # Expensive data loading
    return data

@st.cache_resource
def get_model():
    # Load ML model once
    return model
```

**2. Enable Websocket Compression**
```toml
[server]
enableWebsocketCompression = true
```

**3. Optimize Reruns**
```toml
[runner]
fastReruns = true
```

**4. Reduce Upload Size**
```toml
[server]
maxUploadSize = 50  # MB
```

### High Memory Usage

**Diagnosis**:
```python
import psutil
import streamlit as st

process = psutil.Process()
memory_mb = process.memory_info().rss / 1024 / 1024
st.write(f"Memory usage: {memory_mb:.2f} MB")
```

**Solutions**:

**1. Clear Cache Periodically**
```python
if st.button("Clear Cache"):
    st.cache_data.clear()
    st.cache_resource.clear()
```

**2. Use Generators for Large Data**
```python
def process_large_file():
    for chunk in read_chunks():
        yield process(chunk)
```

**3. Limit Session State Size**
```python
# Store only necessary data
if 'large_data' in st.session_state:
    del st.session_state.large_data
```

### Slow Reruns

**Problem**: App reruns slowly on every interaction

**Solutions**:

**1. Use st.form for Multiple Inputs**
```python
with st.form("my_form"):
    name = st.text_input("Name")
    age = st.number_input("Age")
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        # Process only on submit
        process_data(name, age)
```

**2. Use Callbacks**
```python
def on_change():
    # Handle change
    pass

st.text_input("Name", on_change=on_change)
```

**3. Optimize Expensive Operations**
```python
# ❌ Bad: Runs on every rerun
data = expensive_operation()

# ✅ Good: Cached
@st.cache_data
def get_data():
    return expensive_operation()

data = get_data()
```

---

## 🔍 Debugging Techniques

### Enable Debug Logging

```toml
# .streamlit/config.toml
[logger]
level = "debug"
messageFormat = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
```

### Use Streamlit's Built-in Debugging

```python
import streamlit as st

# Show session state
st.write("Session State:", st.session_state)

# Show configuration
st.write("Config:", st.config.get_option("server.port"))

# Show exception details
try:
    risky_operation()
except Exception as e:
    st.exception(e)
```

### Add Logging to Your App

```python
import logging
import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Use in your app
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Use st.echo for Code Display

```python
import streamlit as st

with st.echo():
    # This code will be displayed and executed
    x = 10
    y = 20
    result = x + y
    st.write(f"Result: {result}")
```

### Profile Performance

```python
import cProfile
import pstats
import streamlit as st

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    expensive_operation()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)

if st.button("Profile"):
    profile_function()
```

---

## 💻 Platform-Specific Issues

### Windows Issues

#### PowerShell Execution Policy
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single execution
powershell -ExecutionPolicy Bypass -File .\scripts\start_streamlit.ps1
```

#### Path Issues
```powershell
# Use forward slashes or escaped backslashes
streamlit run app/main.py  # ✅ Good
streamlit run app\main.py  # ✅ Also works
```

#### Port Management
```powershell
# Find process using port
Get-NetTCPConnection -LocalPort 8501 | Select-Object OwningProcess

# Kill process
Stop-Process -Id <PID> -Force

# Or use our script
.\scripts\start_streamlit.ps1
```

### Linux/Mac Issues

#### Permission Denied
```bash
# Make scripts executable
chmod +x scripts/start_streamlit.py

# Or run with python
python scripts/start_streamlit.py
```

#### Port Binding Issues
```bash
# Ports below 1024 require sudo
sudo streamlit run app/main.py --server.port 80

# Use port 8501 instead (no sudo needed)
streamlit run app/main.py --server.port 8501
```

#### Python Version Issues
```bash
# Check Python version
python --version
python3 --version

# Use specific version
python3.11 -m streamlit run app/main.py
```

### Docker Issues

#### Container Not Accessible
```dockerfile
# Expose port in Dockerfile
EXPOSE 8501

# Run with correct host
CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
```

#### Volume Mounting
```bash
# Mount config directory
docker run -v $(pwd)/.streamlit:/app/.streamlit myapp
```

---

## ❓ FAQ

### Q: How do I check if Streamlit is running?

**A**: Use the port manager:
```bash
python scripts/port_manager.py -p 8501 --check
```

### Q: Can I run multiple Streamlit apps simultaneously?

**A**: Yes, use different ports:
```bash
streamlit run app1.py --server.port 8501
streamlit run app2.py --server.port 8502
```

### Q: How do I clear the cache?

**A**: Use the command:
```bash
streamlit cache clear
```

Or in code:
```python
st.cache_data.clear()
st.cache_resource.clear()
```

### Q: Why does my app reload constantly?

**A**: Check `runOnSave` setting:
```toml
[server]
runOnSave = false  # Disable auto-reload
```

### Q: How do I hide the "Made with Streamlit" footer?

**A**: Use custom CSS:
```python
hide_footer = """
<style>
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_footer, unsafe_allow_html=True)
```

### Q: Can I use environment variables for configuration?

**A**: Yes:
```bash
export STREAMLIT_SERVER_PORT=8502
export STREAMLIT_SERVER_ENABLE_CORS=true
streamlit run app/main.py
```

### Q: How do I deploy to production?

**A**: See [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)

### Q: My app works locally but not in production. Why?

**A**: Common causes:
1. Wrong configuration (use `config.production.toml`)
2. CORS not configured for your domain
3. Missing environment variables
4. Different Python version

### Q: How do I debug CORS issues?

**A**: 
1. Check browser console for CORS errors
2. Enable debug logging
3. Verify `corsAllowedOrigins` includes your domain
4. Ensure HTTPS is used in production

### Q: Can I customize the theme?

**A**: Yes, in `config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

---

## 🆘 Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide**
2. **Review error messages carefully**
3. **Check Streamlit logs**
4. **Verify configuration**
5. **Test with minimal example**

### Information to Provide

When asking for help, include:
- **Error message** (full traceback)
- **Streamlit version** (`streamlit --version`)
- **Python version** (`python --version`)
- **Operating system**
- **Configuration file** (`.streamlit/config.toml`)
- **Minimal reproducible example**

### Resources

- **Project Documentation**:
  - [Configuration Guide](STREAMLIT_CONFIGURATION_GUIDE.md)
  - [Deployment Checklist](DEPLOYMENT_CHECKLIST.md)
  - [Port Management](../scripts/README.md)

- **Official Resources**:
  - [Streamlit Documentation](https://docs.streamlit.io)
  - [Streamlit Forum](https://discuss.streamlit.io)
  - [Streamlit GitHub](https://github.com/streamlit/streamlit)

- **Community**:
  - [Stack Overflow](https://stackoverflow.com/questions/tagged/streamlit)
  - [Reddit r/streamlit](https://reddit.com/r/streamlit)

### Quick Support Commands

```bash
# Get system info
streamlit --version
python --version
uv --version

# Check configuration
streamlit config show

# Verify installation
python -c "import streamlit; print(streamlit.__version__)"

# Test basic functionality
echo "import streamlit as st; st.write('Test')" | streamlit run -
```

---

**Last Updated**: 2026-05-17  
**Maintained By**: DailyPlus_AI Team  
**Version**: 1.0.0

---

**Made with Bob** 🤖