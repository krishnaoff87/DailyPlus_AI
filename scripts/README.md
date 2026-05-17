# Port Management Scripts for Streamlit

This directory contains utilities for managing port conflicts when running the Streamlit application.

## 🚀 Quick Start - **RECOMMENDED**

**Use the new comprehensive startup script for the best experience:**

```bash
python scripts/start_app.py
```

This is the recommended way to launch the application. For detailed documentation, see [START_APP_GUIDE.md](START_APP_GUIDE.md)

---

## Files
### 0. `start_app.py` ⭐ **NEW & RECOMMENDED**
Comprehensive cross-platform startup script with advanced features.

**Features:**
- ✅ Cross-platform support (Windows, Linux, macOS)
- ✅ Automatic port management with conflict resolution
- ✅ Interactive prompts for user decisions
- ✅ Colored terminal output for better readability
- ✅ Comprehensive logging to `logs/` directory
- ✅ Graceful shutdown on Ctrl+C
- ✅ Environment validation (Python, Streamlit, app file)
- ✅ Multiple command-line options
- ✅ Detailed help and documentation

**Quick Usage:**
```bash
# Start with defaults (port 8501)
python scripts/start_app.py

# Custom port with auto-kill
python scripts/start_app.py --port 8502 --auto-kill

# Headless mode with verbose logging
python scripts/start_app.py --no-browser --verbose

# Show help
python scripts/start_app.py --help
```

**📖 Full Documentation**: [START_APP_GUIDE.md](START_APP_GUIDE.md)


### 1. `port_manager.py`
Core utility module for port management on Windows.

**Features:**
- Check if a port is in use
- Identify processes using specific ports
- Kill processes on ports (with force option)
- Find available alternative ports
- Get detailed port information

**Command-line Usage:**
```bash
# Check if port 8501 is in use
python scripts/port_manager.py -p 8501 --check

# Get detailed information about port 8501
python scripts/port_manager.py -p 8501 --info

# Kill process using port 8501
python scripts/port_manager.py -p 8501 --kill

# Find an available port starting from 8501
python scripts/port_manager.py -p 8501 --find
```

**Python API Usage:**
```python
from scripts.port_manager import PortManager

# Create port manager
manager = PortManager(default_port=8501)

# Check if port is in use
in_use = manager.is_port_in_use(8501)

# Get process using port
pid = manager.get_process_using_port(8501)

# Kill process on port
success = manager.kill_process_on_port(8501, force=True)

# Find available port
port = manager.find_available_port(start_port=8501)

# Ensure port is available (auto-kill if needed)
success, port = manager.ensure_port_available(port=8501, auto_kill=True)

# Get detailed port information
info = manager.get_port_info(8501)
```

### 2. `start_streamlit.py`
Python launcher script with automatic port management.

**Features:**
- Validates Streamlit app path
- Automatically handles port conflicts
- Finds alternative ports if needed
- Provides clear user feedback
- Supports custom Streamlit arguments

**Usage:**
```bash
# Basic usage (default: app/main.py on port 8501)
python scripts/start_streamlit.py

# Specify custom app path
python scripts/start_streamlit.py -a path/to/app.py

# Use custom port
python scripts/start_streamlit.py -p 8502

# Auto-kill processes on default port
python scripts/start_streamlit.py --auto-kill

# Run without headless mode (opens browser)
python scripts/start_streamlit.py --no-headless

# Pass additional Streamlit arguments
python scripts/start_streamlit.py --streamlit-args --theme.base dark

# Combine options
python scripts/start_streamlit.py -p 8501 --auto-kill --no-headless
```

**Options:**
- `-a, --app`: Path to Streamlit app file (default: `app/main.py`)
- `-p, --port`: Default port to use (default: `8501`)
- `-k, --auto-kill`: Automatically kill processes on the default port
- `--no-headless`: Run Streamlit in non-headless mode (opens browser)
- `--streamlit-args`: Additional arguments to pass to Streamlit

### 3. `start_streamlit.ps1`
PowerShell launcher script with port management (Windows native).

**Features:**
- Native PowerShell implementation
- Colored console output
- Automatic port conflict resolution
- Process management with retries
- User-friendly error messages

**Usage:**
```powershell
# Basic usage
.\scripts\start_streamlit.ps1

# Use custom port
.\scripts\start_streamlit.ps1 -Port 8502

# Don't kill existing processes (find alternative port)
.\scripts\start_streamlit.ps1 -NoKill

# Run in headless mode
.\scripts\start_streamlit.ps1 -NoBrowser

# Combine options
.\scripts\start_streamlit.ps1 -Port 8501 -NoBrowser

# Show help
.\scripts\start_streamlit.ps1 -Help
```

**Parameters:**
- `-Port`: Port to use (default: `8501`)
- `-AppPath`: Path to Streamlit app (default: `app/main.py`)
- `-NoKill`: Don't kill existing processes on the port
- `-NoBrowser`: Run in headless mode (don't open browser)
- `-Help`: Show help message

## Recommended Usage

### For Development
Use the Python launcher for cross-platform compatibility and integration with Python tooling:
```bash
python scripts/start_streamlit.py --auto-kill
```

### For Windows Users
Use the PowerShell script for native Windows experience with colored output:
```powershell
.\scripts\start_streamlit.ps1
```

### For Production/CI
Use the port manager directly in your deployment scripts:
```python
from scripts.port_manager import PortManager

manager = PortManager(default_port=8501)
success, port = manager.ensure_port_available(auto_kill=True)

if success:
    # Launch Streamlit on the available port
    pass
```

## Troubleshooting

### Port Still in Use After Kill
If a port remains in use after attempting to kill the process:
1. The script will automatically search for an alternative port
2. You can manually specify a different port using `-p` or `-Port`
3. Check for zombie processes: `Get-Process | Where-Object {$_.ProcessName -like "*python*"}`

### Permission Errors
If you get permission errors when killing processes:
1. Run PowerShell as Administrator
2. Or use the `-NoKill` flag to find an alternative port instead

### Script Execution Policy (PowerShell)
If you can't run the PowerShell script:
```powershell
# Check current policy
Get-ExecutionPolicy

# Set policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for single execution
powershell -ExecutionPolicy Bypass -File .\scripts\start_streamlit.ps1
```

## Integration with VS Code

Add these tasks to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Streamlit (Python)",
      "type": "shell",
      "command": "python",
      "args": ["scripts/start_streamlit.py", "--auto-kill"],
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    },
    {
      "label": "Start Streamlit (PowerShell)",
      "type": "shell",
      "command": ".\\scripts\\start_streamlit.ps1",
      "problemMatcher": [],
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

## Error Handling

All scripts include comprehensive error handling:
- **Port conflicts**: Automatically resolved by killing processes or finding alternatives
- **Missing app files**: Validated before launch with clear error messages
- **Process termination failures**: Multiple retry attempts with fallback options
- **Timeout handling**: All operations have timeouts to prevent hanging
- **Logging**: Detailed logs for debugging issues

## Requirements

- Python 3.7+
- Windows 10+ (for PowerShell scripts)
- Streamlit installed (`pip install streamlit`)
- Administrator privileges (only if killing processes)

## Notes

- The default port is `8501` (Streamlit's default)
- Port scanning range: 10 ports (e.g., 8501-8510)
- Process kill timeout: 10 seconds with retries
- All scripts work from the workspace root directory
- Logs are written to console with timestamps