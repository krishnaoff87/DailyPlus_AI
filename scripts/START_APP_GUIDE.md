# DailyPlus AI - Startup Script Guide

## Overview

`start_app.py` is a comprehensive cross-platform startup script for the DailyPlus AI Streamlit application. It provides robust port management, error handling, logging, graceful shutdown capabilities, and **automatic cleanup with cache management**.

## Features

### ✨ Core Features

- **Cross-Platform Support**: Works seamlessly on Windows, Linux, and macOS
- **Automatic Port Management**: Detects and resolves port conflicts automatically
- **Interactive Prompts**: User-friendly prompts for decision-making
- **Colored Output**: Beautiful, colored terminal output for better readability
- **Comprehensive Logging**: Detailed logs saved to `logs/` directory
- **Graceful Shutdown**: Proper cleanup on Ctrl+C or termination signals
- **Environment Validation**: Checks Python, Streamlit, and app file before starting
- **🆕 Automatic Cache Cleanup**: Clears Streamlit and Python caches on shutdown
- **🆕 Process Tracking**: Tracks and manages all spawned Streamlit processes
- **🆕 Enhanced Signal Handling**: Handles SIGINT, SIGTERM, and SIGBREAK (Windows)

### 🔧 Port Management

- **Automatic Port Detection**: Checks if the default port (8501) is available
- **Conflict Resolution**:
  - Option to kill conflicting processes
  - Automatic fallback to alternative ports (8502, 8503, etc.)
- **Process Information**: Shows which process is using a port
- **Custom Port Support**: Specify any port via command-line argument
- **🆕 Enhanced with psutil**: Uses psutil library for robust cross-platform process detection

### 🧹 Cleanup & Cache Management

- **Automatic Cleanup on Shutdown**: Triggered by Ctrl+C, SIGTERM, or script exit
- **Process Tracking**: Tracks all spawned Streamlit processes and ports
- **Comprehensive Process Cleanup**:
  - Finds and kills all Streamlit processes on tracked ports
  - Graceful termination with force kill fallback
  - Works even if main process crashes
- **Cache Directory Clearing**:
  - Project-specific caches (`.streamlit/cache/`, `__pycache__/`)
  - Recursive `__pycache__` cleanup throughout project
  - Platform-specific Streamlit caches:
    - Windows: `%LOCALAPPDATA%\streamlit\cache`
    - Linux: `~/.streamlit/cache`
    - macOS: `~/Library/Caches/streamlit`
- **Interactive Confirmations**: Shows what will be cleaned before proceeding
- **Force Mode**: Skip all confirmations with `--force` flag
- **Selective Cleanup**: Control what gets cleaned with flags
- **Cleanup-Only Mode**: Run cleanup without starting the app

### 📊 Error Handling & Logging

- **Comprehensive Error Messages**: Clear, actionable error messages
- **Troubleshooting Tips**: Helpful suggestions when errors occur
- **Detailed Logging**: All operations logged to timestamped log files
- **Verbose Mode**: Optional detailed console output for debugging

## Installation

### Required Dependencies

The script works with Python standard library, but for enhanced functionality, install:

```bash
pip install psutil
```

**psutil** provides:
- Robust cross-platform process management
- Better port detection
- More reliable process termination
- Detailed process information

The script will work without psutil but will fall back to platform-specific commands (PowerShell on Windows, lsof/netstat on Unix).

### Verify Installation

```bash
python scripts/start_app.py --version
```

## Usage

### Basic Usage

Start the application with default settings (port 8501):

```bash
python scripts/start_app.py
```

### Command-Line Options

```bash
python scripts/start_app.py [OPTIONS]
```

#### Available Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--app` | `-a` | Path to Streamlit app file | `app/main.py` |
| `--port` | `-p` | Port to use | `8501` |
| `--auto-kill` | `-k` | Automatically kill processes on the port | `False` |
| `--no-browser` | | Run in headless mode (don't open browser) | `False` |
| `--verbose` | `-v` | Enable verbose logging | `False` |
| `--force` | `-f` | 🆕 Skip all confirmations during cleanup | `False` |
| `--no-cache-clear` | | 🆕 Don't clear cache directories on shutdown | `False` |
| `--keep-processes` | | 🆕 Don't kill Streamlit processes on shutdown | `False` |
| `--cleanup-only` | | 🆕 Just run cleanup and exit (don't start app) | `False` |
| `--help` | `-h` | Show help message | |
| `--version` | | Show version number | |

### Examples

#### 1. Start with Default Settings
```bash
python scripts/start_app.py
```

#### 2. Use Custom Port
```bash
python scripts/start_app.py --port 8502
```

#### 3. Auto-Kill Conflicting Processes
```bash
python scripts/start_app.py --auto-kill
```

#### 4. Headless Mode (No Browser)
```bash
python scripts/start_app.py --no-browser
```

#### 5. Custom Port with Auto-Kill
```bash
python scripts/start_app.py --port 8502 --auto-kill
```

#### 6. Verbose Logging for Debugging
```bash
python scripts/start_app.py --verbose
```

#### 7. Custom App Path
```bash
python scripts/start_app.py --app custom/path/to/app.py
```

#### 8. 🆕 Force Cleanup Without Prompts
```bash
python scripts/start_app.py --force
```

#### 9. 🆕 Cleanup Only (Don't Start App)
```bash
python scripts/start_app.py --cleanup-only
```

#### 10. 🆕 Start Without Cache Cleanup
```bash
python scripts/start_app.py --no-cache-clear
```

#### 11. 🆕 Start Without Process Cleanup
```bash
python scripts/start_app.py --keep-processes
```

#### 12. 🆕 Development Mode (Auto-kill + Force Cleanup)
```bash
python scripts/start_app.py --auto-kill --force
```

## Interactive Prompts

When a port conflict is detected and `--auto-kill` is not specified, the script will prompt:

```
⚠ Port 8501 is currently in use
ℹ Process: python (PID: 12345)
? Kill the process using port 8501? [y/N]:
```

- Press `y` or `yes` to kill the process
- Press `n` or `no` to search for an alternative port
- Press `Enter` to use the default (No)

## Output Examples

### Successful Startup

```
ℹ Starting DailyPlus AI Streamlit Application...

ℹ Validating environment...
✓ Found app file: app/main.py
✓ Python: Python 3.11.0
✓ Streamlit: Streamlit, version 1.28.0

ℹ Checking port 8501...
✓ Port 8501 is available

======================================================================
  🚀 DailyPlus AI - Streamlit Application
======================================================================
  Port:        8501
  URL:         http://localhost:8501
  App:         app/main.py
  Platform:    Windows 10
======================================================================

✓ Streamlit started successfully
──────────────────────────────────────────────────────────────────────
ℹ Streamlit output (Press Ctrl+C to stop):
──────────────────────────────────────────────────────────────────────


## 🆕 Cleanup Operations

### Automatic Cleanup on Shutdown

When you press Ctrl+C or the script receives a termination signal, it automatically:

1. **Stops the main Streamlit process** (gracefully, then force if needed)
2. **Finds and kills all Streamlit processes** on tracked ports
3. **Clears cache directories**:
   - `.streamlit/cache/` in project
   - All `__pycache__/` directories recursively
   - Platform-specific Streamlit system caches

### Cleanup Output Example

```
──────────────────────────────────────────────────────────────────────
ℹ Starting comprehensive cleanup...
──────────────────────────────────────────────────────────────────────
ℹ Stopping main Streamlit process...
✓ Streamlit stopped gracefully

ℹ Checking for other Streamlit processes...
ℹ Found 2 Streamlit processes:
  • PID 12345 (python) on port 8501
  • PID 12346 (python) on port 8502
? Kill all Streamlit processes? [Y/n]: y
ℹ Stopping processes...
✓ Stopped process 12345 on port 8501
✓ Stopped process 12346 on port 8502
✓ Stopped 2 process(es)

ℹ Clearing cache directories...
ℹ Found 5 cache directories:
  • c:\Users\User\Desktop\Project\.streamlit\cache (2.34 MB)
  • c:\Users\User\Desktop\Project\__pycache__ (156.78 KB)
  • c:\Users\User\Desktop\Project\app\__pycache__ (89.12 KB)
  • c:\Users\User\Desktop\Project\src\__pycache__ (234.56 KB)
  • C:\Users\User\AppData\Local\streamlit\cache (15.67 MB)
ℹ Total cache size: 18.48 MB
? Clear all cache directories? [Y/n]: y
ℹ Clearing caches...
✓ Cleared: c:\Users\User\Desktop\Project\.streamlit\cache
✓ Cleared: c:\Users\User\Desktop\Project\__pycache__
✓ Cleared: c:\Users\User\Desktop\Project\app\__pycache__
✓ Cleared: c:\Users\User\Desktop\Project\src\__pycache__
✓ Cleared: C:\Users\User\AppData\Local\streamlit\cache
✓ Cleared 5 cache directories (18.48 MB)

✓ Cleanup completed in 3.2s
──────────────────────────────────────────────────────────────────────
```

### Force Mode (Skip Confirmations)

Use `--force` to skip all confirmation prompts:

```bash
python scripts/start_app.py --force
```

When you press Ctrl+C, cleanup runs automatically without asking for confirmation.

### Cleanup-Only Mode

Run cleanup operations without starting the app:

```bash
python scripts/start_app.py --cleanup-only
```

This is useful for:
- Cleaning up after a crash
- Freeing ports before starting
- Clearing caches to troubleshoot issues
- Scheduled maintenance

### Selective Cleanup

Control what gets cleaned:

```bash
# Don't clear caches (only kill processes)
python scripts/start_app.py --no-cache-clear

# Don't kill processes (only clear caches)
python scripts/start_app.py --keep-processes

# No cleanup at all
python scripts/start_app.py --no-cache-clear --keep-processes
```

### Signal Handling

The script handles multiple signals for graceful shutdown:

- **SIGINT** (Ctrl+C): User interrupt
- **SIGTERM**: Termination signal from system
- **SIGBREAK** (Windows only): Ctrl+Break
- **atexit**: Fallback cleanup on script exit

### Cleanup Timeout

Cleanup operations have a 10-second timeout:
- If cleanup takes longer, a warning is logged
- The script continues to exit gracefully
- Force kill is used if graceful shutdown fails

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.100:8501
```

### Port Conflict Resolution

```
ℹ Checking port 8501...
⚠ Port 8501 is currently in use
ℹ Process: python (PID: 12345)
? Kill the process using port 8501? [y/N]: n
ℹ Searching for alternative port...
✓ Found alternative port: 8502
```

### Graceful Shutdown

```
^C
⚠ Received interrupt signal
ℹ Stopping Streamlit...
✓ Streamlit stopped gracefully
```

## Logging

Logs are automatically saved to the `logs/` directory with timestamps:

```
logs/streamlit_startup_20260517_162930.log
```

Log files contain:
- Timestamp for each operation
- Environment validation results
- Port management operations
- Process information
- Streamlit output (in verbose mode)
- Error details and stack traces

### Viewing Logs

```bash
# View the latest log
cat logs/streamlit_startup_*.log | tail -n 50

# Follow log in real-time (Unix/Linux/macOS)
tail -f logs/streamlit_startup_*.log
```

## Troubleshooting

### Common Issues

#### 1. Port Already in Use

**Problem**: Port 8501 is occupied by another process

**Solutions**:

#### 6. 🆕 Cleanup Fails or Times Out

**Problem**: Cleanup operations fail or take too long

**Solutions**:
- Use `--force` flag to skip confirmations and speed up cleanup
- Check if you have permission to kill processes (may need admin/sudo)
- Use `--cleanup-only` to run cleanup separately
- Check logs for specific error messages
- Install psutil for more reliable cleanup: `pip install psutil`

#### 7. 🆕 Cache Directories Not Found

**Problem**: Script reports no cache directories found

**Solutions**:
- Caches may not exist yet (normal for first run)
- Check if Streamlit has been run before
- Verify project structure matches expected layout
- Use `--verbose` to see detailed cache detection logs

#### 8. 🆕 Permission Denied During Cache Cleanup

**Problem**: Cannot delete cache directories due to permissions

**Solutions**:
- Close any applications that might be using cache files
- On Windows: Run as Administrator
- On Unix/Linux: Use `sudo` if needed
- Check file permissions on cache directories
- Some system caches may require elevated privileges

#### 9. 🆕 Processes Not Being Killed

**Problem**: Streamlit processes remain after cleanup

**Solutions**:
- Install psutil for better process detection: `pip install psutil`
- Use `--force` flag for force kill
- Check if processes are owned by different user
- Manually kill with Task Manager (Windows) or `kill` command (Unix)
- Verify processes are actually Streamlit (check with `ps` or Task Manager)

#### 10. 🆕 Cleanup Runs But App Doesn't Start

**Problem**: Using `--cleanup-only` but expecting app to start

**Solution**:
- `--cleanup-only` is designed to only run cleanup
- Remove the flag to start the app normally
- Use separate commands: cleanup first, then start

- Use `--auto-kill` flag to automatically free the port
- Specify a different port with `--port 8502`
- Manually kill the process using the port

#### 2. Streamlit Not Found

**Problem**: `Streamlit is not installed or not accessible`

**Solution**:
```bash
pip install streamlit
```

#### 3. App File Not Found

**Problem**: `Streamlit app file not found: app/main.py`

**Solutions**:
- Ensure you're running from the project root directory
- Verify the app file exists at the specified path
- Use `--app` flag to specify the correct path

#### 4. Permission Denied (Unix/Linux/macOS)

**Problem**: Cannot kill process due to permissions

**Solutions**:
- Run with sudo: `sudo python scripts/start_app.py --auto-kill`
- Kill the process manually: `kill -9 <PID>`

#### 5. Colors Not Displaying (Windows)

**Problem**: ANSI colors not showing in Windows Command Prompt

**Solutions**:
- Use Windows Terminal instead of Command Prompt
- Use PowerShell
- Colors are automatically disabled if not supported

### Debug Mode

Enable verbose logging to see detailed information:

```bash
python scripts/start_app.py --verbose
```

This will:
- Show all log messages in the console
- Display detailed Streamlit output
- Help identify issues during startup

## Platform-Specific Notes

### Windows

- Uses PowerShell commands for port management
- Supports Windows Terminal for colored output
- May require administrator privileges to kill certain processes

### Linux/macOS

- Uses `lsof` or `netstat` for port checking
- Uses `kill` command for process termination
- May require `sudo` for killing system processes

## Integration with Existing Scripts

The new `start_app.py` script consolidates and improves upon:

- `scripts/start_streamlit.py` - Python-based launcher
- `scripts/start_streamlit.ps1` - PowerShell-based launcher

You can continue using the old scripts, but `start_app.py` is recommended for:
- Better cross-platform support
- Enhanced error handling
- Improved user experience
- Comprehensive logging

## Advanced Usage

### Environment Variables

You can set environment variables before running:

```bash
# Unix/Linux/macOS
export STREAMLIT_SERVER_PORT=8502
python scripts/start_app.py

# Windows PowerShell
$env:STREAMLIT_SERVER_PORT=8502
python scripts/start_app.py
```

### Automation

For automated deployments or CI/CD:

```bash
# Non-interactive mode with auto-kill
python scripts/start_app.py --auto-kill --no-browser --verbose
```

### Custom Configuration

Create a wrapper script for your specific needs:

```bash
#!/bin/bash
# my_start.sh

# Set custom environment
export PYTHONPATH=/path/to/project
export STREAMLIT_SERVER_PORT=8502

# Start with custom settings
python scripts/start_app.py \
    --port 8502 \
    --auto-kill \
    --no-browser \
    --verbose
```

## Best Practices

1. **Use `--auto-kill` in Development**: Automatically free ports during development
2. **Use `--no-browser` in Production**: Prevent browser from opening on servers
3. **Enable `--verbose` for Debugging**: Get detailed logs when troubleshooting
4. **Check Logs Regularly**: Review log files for errors and warnings
5. **Use Custom Ports in Multi-App Environments**: Avoid conflicts with other applications
6. **🆕 Install psutil**: For best performance and reliability: `pip install psutil`
7. **🆕 Use `--force` in CI/CD**: Skip confirmations in automated environments
8. **🆕 Run `--cleanup-only` After Crashes**: Clean up orphaned processes and caches
9. **🆕 Regular Cache Cleanup**: Periodically run cleanup to free disk space
10. **🆕 Monitor Cleanup Logs**: Check logs to ensure cleanup completes successfully

## Security Considerations

- **Process Killing**: Be cautious when using `--auto-kill` as it will terminate processes
- **Port Access**: Ensure the application has permission to bind to the specified port
- **Log Files**: Log files may contain sensitive information; secure the `logs/` directory
- **Network Exposure**: Use `--no-browser` and configure firewall rules for production
- **🆕 Cache Cleanup**: Cache directories may contain sensitive data; review before cleanup
- **🆕 Force Mode**: `--force` skips confirmations; use carefully in production
- **🆕 Process Permissions**: Killing processes may require elevated privileges

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review log files in the `logs/` directory
3. Run with `--verbose` flag for detailed output
4. Check the main project documentation in `docs/`

## Version History

### v2.0.0 (2026-05-17) - 🆕 Cleanup & Cache Management Release

**New Features:**
- Comprehensive cleanup system with process tracking
- Automatic cache clearing on shutdown
- Enhanced signal handling (SIGINT, SIGTERM, SIGBREAK)
- Process tracking for all spawned Streamlit instances
- Platform-specific cache detection and cleanup
- Interactive cleanup confirmations
- Force mode for automated environments
- Cleanup-only mode for maintenance
- Selective cleanup options (--no-cache-clear, --keep-processes)
- psutil integration for robust cross-platform support
- atexit fallback cleanup
- Cleanup timeout handling (10 seconds)

**Enhancements:**
- Better error handling during cleanup
- Detailed cleanup logging and reporting
- Cache size calculation before deletion
- Graceful and force kill options
- Improved process detection with psutil

**Command-Line Options Added:**
- `--force` / `-f`: Skip all confirmations
- `--no-cache-clear`: Don't clear caches on shutdown
- `--keep-processes`: Don't kill processes on shutdown
- `--cleanup-only`: Run cleanup without starting app

### v1.0.0 (2026-05-17)
- Initial release
- Cross-platform support (Windows, Linux, macOS)
- Automatic port management
- Interactive prompts
- Colored output
- Comprehensive logging
- Graceful shutdown
- Environment validation

---

**Made with ❤️ by Bob**