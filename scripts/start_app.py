#!/usr/bin/env python3
"""
Comprehensive Cross-Platform Startup Script for Streamlit Application
Handles port management, error handling, logging, graceful shutdown, and cache cleanup.

Usage:
    python scripts/start_app.py                    # Start with defaults
    python scripts/start_app.py --port 8502        # Custom port
    python scripts/start_app.py --auto-kill        # Auto-kill conflicting processes
    python scripts/start_app.py --no-browser       # Headless mode
    python scripts/start_app.py --force            # Skip all confirmations
    python scripts/start_app.py --cleanup-only     # Just cleanup and exit
    python scripts/start_app.py --help             # Show help
"""

import sys
import os
import subprocess
import argparse
import signal
import time
import platform
import shutil
import atexit
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import logging

# Try to import psutil for robust process management
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Install with: pip install psutil")

# Add the scripts directory to the path to import port_manager
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from port_manager import PortManager

# ============================================
# Color Output Support
# ============================================


class Colors:
    """ANSI color codes for terminal output"""

    # Check if colors are supported
    SUPPORTS_COLOR = (
        hasattr(sys.stdout, "isatty")
        and sys.stdout.isatty()
        and (
            platform.system() != "Windows"
            or "ANSICON" in os.environ
            or "WT_SESSION" in os.environ
            or "TERM_PROGRAM" in os.environ
        )
    )

    if SUPPORTS_COLOR:
        RESET = "\033[0m"
        BOLD = "\033[1m"
        DIM = "\033[2m"

        # Foreground colors
        BLACK = "\033[30m"
        RED = "\033[31m"
        GREEN = "\033[32m"
        YELLOW = "\033[33m"
        BLUE = "\033[34m"
        MAGENTA = "\033[35m"
        CYAN = "\033[36m"
        WHITE = "\033[37m"

        # Bright foreground colors
        BRIGHT_BLACK = "\033[90m"
        BRIGHT_RED = "\033[91m"
        BRIGHT_GREEN = "\033[92m"
        BRIGHT_YELLOW = "\033[93m"
        BRIGHT_BLUE = "\033[94m"
        BRIGHT_MAGENTA = "\033[95m"
        BRIGHT_CYAN = "\033[96m"
        BRIGHT_WHITE = "\033[97m"
    else:
        # No color support
        RESET = BOLD = DIM = ""
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = ""
        BRIGHT_BLACK = BRIGHT_RED = BRIGHT_GREEN = BRIGHT_YELLOW = ""
        BRIGHT_BLUE = BRIGHT_MAGENTA = BRIGHT_CYAN = BRIGHT_WHITE = ""


def print_success(message: str):
    """Print success message in green"""
    try:
        print(f"{Colors.BRIGHT_GREEN}✓ {message}{Colors.RESET}")
    except UnicodeEncodeError:
        print(f"{Colors.BRIGHT_GREEN}[OK] {message}{Colors.RESET}")


def print_info(message: str):
    """Print info message in cyan"""
    try:
        print(f"{Colors.BRIGHT_CYAN}ℹ {message}{Colors.RESET}")
    except UnicodeEncodeError:
        print(f"{Colors.BRIGHT_CYAN}[INFO] {message}{Colors.RESET}")


def print_warning(message: str):
    """Print warning message in yellow"""
    try:
        print(f"{Colors.BRIGHT_YELLOW}⚠ {message}{Colors.RESET}")
    except UnicodeEncodeError:
        print(f"{Colors.BRIGHT_YELLOW}[WARNING] {message}{Colors.RESET}")


def print_error(message: str):
    """Print error message in red"""
    try:
        print(f"{Colors.BRIGHT_RED}✗ {message}{Colors.RESET}")
    except UnicodeEncodeError:
        print(f"{Colors.BRIGHT_RED}[ERROR] {message}{Colors.RESET}")


def print_banner(port: int, app_path: str):
    """Print startup banner"""
    print()
    print(f"{Colors.BRIGHT_CYAN}{'='*70}{Colors.RESET}")
    print(
        f"{Colors.BRIGHT_CYAN}{Colors.BOLD}  🚀 DailyPlus AI - Streamlit Application{Colors.RESET}"
    )
    print(f"{Colors.BRIGHT_CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.CYAN}  Port:        {Colors.BRIGHT_WHITE}{port}{Colors.RESET}")
    print(
        f"{Colors.CYAN}  URL:         {Colors.BRIGHT_WHITE}http://localhost:{port}{Colors.RESET}"
    )
    print(f"{Colors.CYAN}  App:         {Colors.BRIGHT_WHITE}{app_path}{Colors.RESET}")
    print(
        f"{Colors.CYAN}  Platform:    {Colors.BRIGHT_WHITE}{platform.system()} {platform.release()}{Colors.RESET}"
    )
    print(f"{Colors.BRIGHT_CYAN}{'='*70}{Colors.RESET}")
    print()


def print_separator():
    """Print a separator line"""
    try:
        print(f"{Colors.DIM}{'─'*70}{Colors.RESET}")
    except UnicodeEncodeError:
        print(f"{Colors.DIM}{'-'*70}{Colors.RESET}")


# ============================================
# Cache and Cleanup Management
# ============================================


class CacheManager:
    """Manages cache directories and cleanup operations"""

    def __init__(self, workspace_dir: Path, logger: logging.Logger):
        """
        Initialize the CacheManager.

        Args:
            workspace_dir: Project workspace directory
            logger: Logger instance
        """
        self.workspace_dir = workspace_dir
        self.logger = logger
        self.is_windows = platform.system() == "Windows"

    def get_cache_directories(self) -> List[Path]:
        """
        Get all cache directories to clear.

        Returns:
            List of cache directory paths
        """
        cache_dirs = []

        # Project-specific caches
        project_caches = [
            self.workspace_dir / ".streamlit" / "cache",
            self.workspace_dir / "__pycache__",
        ]

        for cache_dir in project_caches:
            if cache_dir.exists():
                cache_dirs.append(cache_dir)

        # Find all __pycache__ directories recursively
        try:
            for pycache in self.workspace_dir.rglob("__pycache__"):
                if pycache.is_dir():
                    cache_dirs.append(pycache)
        except Exception as e:
            self.logger.warning(f"Error finding __pycache__ directories: {e}")

        # Platform-specific Streamlit cache directories
        home = Path.home()

        if self.is_windows:
            # Windows: %LOCALAPPDATA%\streamlit\cache
            local_app_data = os.environ.get("LOCALAPPDATA")
            if local_app_data:
                streamlit_cache = Path(local_app_data) / "streamlit" / "cache"
                if streamlit_cache.exists():
                    cache_dirs.append(streamlit_cache)
        elif platform.system() == "Darwin":
            # macOS: ~/Library/Caches/streamlit
            streamlit_cache = home / "Library" / "Caches" / "streamlit"
            if streamlit_cache.exists():
                cache_dirs.append(streamlit_cache)
        else:
            # Linux: ~/.streamlit/cache
            streamlit_cache = home / ".streamlit" / "cache"
            if streamlit_cache.exists():
                cache_dirs.append(streamlit_cache)

        return cache_dirs

    def get_directory_size(self, path: Path) -> int:
        """
        Calculate total size of a directory.

        Args:
            path: Directory path

        Returns:
            Size in bytes
        """
        total_size = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    try:
                        total_size += item.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except Exception as e:
            self.logger.warning(f"Error calculating size for {path}: {e}")
        return total_size

    def format_size(self, size_bytes: int) -> str:
        """
        Format size in bytes to human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def clear_cache_directory(self, cache_dir: Path) -> Tuple[bool, str]:
        """
        Clear a cache directory.

        Args:
            cache_dir: Directory to clear

        Returns:
            Tuple of (success, message)
        """
        try:
            size_before = self.get_directory_size(cache_dir)
            shutil.rmtree(cache_dir)
            self.logger.info(
                f"Cleared cache: {cache_dir} ({self.format_size(size_before)})"
            )
            return True, f"Cleared {self.format_size(size_before)}"
        except PermissionError:
            msg = f"Permission denied: {cache_dir}"
            self.logger.error(msg)
            return False, msg
        except Exception as e:
            msg = f"Error clearing {cache_dir}: {e}"
            self.logger.error(msg)
            return False, str(e)

    def clear_all_caches(self, force: bool = False) -> Dict[str, any]:
        """
        Clear all cache directories.

        Args:
            force: Skip confirmation prompts

        Returns:
            Dictionary with cleanup results
        """
        cache_dirs = self.get_cache_directories()

        if not cache_dirs:
            print_info("No cache directories found")
            return {"cleared": 0, "failed": 0, "total_size": 0}

        # Show what will be cleared
        print_info(
            f"Found {len(cache_dirs)} cache director{'y' if len(cache_dirs) == 1 else 'ies'}:"
        )
        total_size = 0
        for cache_dir in cache_dirs:
            size = self.get_directory_size(cache_dir)
            total_size += size
            print(
                f"  {Colors.DIM}• {cache_dir} ({self.format_size(size)}){Colors.RESET}"
            )

        print_info(f"Total cache size: {self.format_size(total_size)}")

        # Confirm if not forced
        if not force:
            if not ask_yes_no("Clear all cache directories?", default=True):
                print_warning("Cache cleanup cancelled")
                return {"cleared": 0, "failed": 0, "total_size": 0, "cancelled": True}

        # Clear caches
        print_info("Clearing caches...")
        cleared = 0
        failed = 0

        for cache_dir in cache_dirs:
            success, msg = self.clear_cache_directory(cache_dir)
            if success:
                print_success(f"Cleared: {cache_dir}")
                cleared += 1
            else:
                print_error(f"Failed: {cache_dir} - {msg}")
                failed += 1

        return {
            "cleared": cleared,
            "failed": failed,
            "total_size": total_size,
            "total": len(cache_dirs),
        }


class ProcessTracker:
    """Tracks spawned processes and manages cleanup"""

    def __init__(self, logger: logging.Logger):
        """
        Initialize the ProcessTracker.

        Args:
            logger: Logger instance
        """
        self.logger = logger
        self.tracked_processes: List[Dict] = []
        self.tracked_ports: List[int] = []

    def track_process(self, process: subprocess.Popen, port: int):
        """
        Track a spawned process.

        Args:
            process: Process object
            port: Port number
        """
        process_info = {
            "process": process,
            "pid": process.pid,
            "port": port,
            "start_time": time.time(),
        }
        self.tracked_processes.append(process_info)
        if port not in self.tracked_ports:
            self.tracked_ports.append(port)

        self.logger.info(f"Tracking process PID {process.pid} on port {port}")

    def find_streamlit_processes(self) -> List[Dict]:
        """
        Find all Streamlit processes on tracked ports.

        Returns:
            List of process information dictionaries
        """
        processes = []

        if PSUTIL_AVAILABLE:
            # Use psutil for robust process detection
            for proc in psutil.process_iter(["pid", "name", "cmdline"]):
                try:
                    # Check if it's a Python/Streamlit process
                    cmdline = proc.info.get("cmdline", [])
                    if cmdline and any(
                        "streamlit" in str(arg).lower() for arg in cmdline
                    ):
                        # Check if it's using one of our tracked ports
                        try:
                            connections = proc.connections()
                            for conn in connections:
                                if (
                                    hasattr(conn, "laddr")
                                    and hasattr(conn.laddr, "port")
                                    and conn.laddr.port in self.tracked_ports
                                ):
                                    processes.append(
                                        {
                                            "pid": proc.info["pid"],
                                            "name": proc.info["name"],
                                            "port": conn.laddr.port,
                                            "process": proc,
                                        }
                                    )
                                    break
                        except (psutil.AccessDenied, AttributeError):
                            # Can't access connections, skip this process
                            pass
                except (
                    psutil.NoSuchProcess,
                    psutil.AccessDenied,
                    psutil.ZombieProcess,
                ):
                    pass
        else:
            # Fallback: use tracked processes
            for proc_info in self.tracked_processes:
                if proc_info["process"].poll() is None:  # Still running
                    processes.append(proc_info)

        return processes

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """
        Kill a process by PID.

        Args:
            pid: Process ID
            force: Use force kill

        Returns:
            True if successful
        """
        try:
            if PSUTIL_AVAILABLE:
                proc = psutil.Process(pid)
                if force:
                    proc.kill()
                else:
                    proc.terminate()
                    try:
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        proc.kill()
                return True
            else:
                # Fallback to system commands
                if platform.system() == "Windows":
                    cmd = f"taskkill /F /PID {pid}" if force else f"taskkill /PID {pid}"
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
                else:
                    signal_num = signal.SIGKILL if force else signal.SIGTERM
                    os.kill(pid, signal_num)
                return True
        except Exception as e:
            self.logger.error(f"Error killing process {pid}: {e}")
            return False

    def kill_all_processes(self, force: bool = False) -> Dict[str, int]:
        """
        Kill all tracked Streamlit processes.

        Args:
            force: Skip confirmation and use force kill

        Returns:
            Dictionary with kill results
        """
        processes = self.find_streamlit_processes()

        if not processes:
            print_info("No Streamlit processes found")
            return {"killed": 0, "failed": 0, "total": 0}

        # Show what will be killed
        print_info(
            f"Found {len(processes)} Streamlit process{'es' if len(processes) != 1 else ''}:"
        )
        for proc in processes:
            port = proc.get("port", "unknown")
            name = proc.get("name", "unknown")
            print(
                f"  {Colors.DIM}• PID {proc['pid']} ({name}) on port {port}{Colors.RESET}"
            )

        # Confirm if not forced
        if not force:
            if not ask_yes_no("Kill all Streamlit processes?", default=True):
                print_warning("Process cleanup cancelled")
                return {
                    "killed": 0,
                    "failed": 0,
                    "total": len(processes),
                    "cancelled": True,
                }

        # Kill processes
        print_info("Stopping processes...")
        killed = 0
        failed = 0

        for proc in processes:
            pid = proc["pid"]
            port = proc.get("port", "unknown")

            # Try graceful termination first
            if self.kill_process(pid, force=False):
                time.sleep(1)
                # Check if still running
                try:
                    if PSUTIL_AVAILABLE:
                        if not psutil.pid_exists(pid):
                            print_success(f"Stopped process {pid} on port {port}")
                            killed += 1
                            continue
                    else:
                        # Assume success if no exception
                        print_success(f"Stopped process {pid} on port {port}")
                        killed += 1
                        continue
                except:
                    pass

                # Force kill if still running
                if self.kill_process(pid, force=True):
                    print_success(f"Force stopped process {pid} on port {port}")
                    killed += 1
                else:
                    print_error(f"Failed to stop process {pid} on port {port}")
                    failed += 1
            else:
                print_error(f"Failed to stop process {pid} on port {port}")
                failed += 1

        return {"killed": killed, "failed": failed, "total": len(processes)}


# ============================================
# Logging Configuration
# ============================================


def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    log_level = logging.DEBUG if verbose else logging.INFO

    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)

    # Configure logging
    log_file = log_dir / f'streamlit_startup_{time.strftime("%Y%m%d_%H%M%S")}.log'

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout) if verbose else logging.NullHandler(),
        ],
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized. Log file: {log_file}")

    return logger


# ============================================
# Interactive Prompts
# ============================================


def ask_yes_no(question: str, default: bool = True) -> bool:
    """
    Ask a yes/no question and return the answer.

    Args:
        question: The question to ask
        default: Default answer if user just presses Enter

    Returns:
        True for yes, False for no
    """
    default_str = "Y/n" if default else "y/N"
    prompt = f"{Colors.BRIGHT_YELLOW}? {question} [{default_str}]: {Colors.RESET}"

    while True:
        try:
            answer = input(prompt).strip().lower()

            if not answer:
                return default

            if answer in ["y", "yes"]:
                return True
            elif answer in ["n", "no"]:
                return False
            else:
                print_warning("Please answer 'y' or 'n'")
        except (KeyboardInterrupt, EOFError):
            print()
            return default


# ============================================
# Streamlit Application Launcher
# ============================================


class StreamlitApp:
    """Manages the Streamlit application lifecycle"""

    def __init__(
        self,
        app_path: str = "app/main.py",
        default_port: int = 8501,
        auto_kill: bool = False,
        no_browser: bool = False,
        verbose: bool = False,
        force: bool = False,
        no_cache_clear: bool = False,
        keep_processes: bool = False,
    ):
        """
        Initialize the StreamlitApp.

        Args:
            app_path: Path to the Streamlit app file
            default_port: Default port to use
            auto_kill: Whether to automatically kill processes on the default port
            no_browser: Whether to run in headless mode
            verbose: Enable verbose logging
            force: Skip all confirmations
            no_cache_clear: Don't clear cache on shutdown
            keep_processes: Don't kill processes on shutdown
        """
        self.app_path = app_path
        self.default_port = default_port
        self.auto_kill = auto_kill
        self.no_browser = no_browser
        self.verbose = verbose
        self.force = force
        self.no_cache_clear = no_cache_clear
        self.keep_processes = keep_processes

        self.port_manager = PortManager(default_port=default_port)
        self.workspace_dir = Path(__file__).parent.parent
        self.process: Optional[subprocess.Popen] = None
        self.logger = setup_logging(verbose)

        # Initialize cleanup managers
        self.cache_manager = CacheManager(self.workspace_dir, self.logger)
        self.process_tracker = ProcessTracker(self.logger)

        # Register signal handlers for graceful shutdown
        self.register_signal_handlers()

        # Register atexit cleanup as fallback
        atexit.register(self._atexit_cleanup)

    def register_signal_handlers(self):
        """Register signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Windows-specific: handle Ctrl+Break
        if platform.system() == "Windows":
            try:
                signal.signal(signal.SIGBREAK, self._signal_handler)
            except AttributeError:
                pass

    def _signal_handler(self, signum, frame):
        """Handle interrupt signals for graceful shutdown"""
        print()
        print_warning("Received interrupt signal. Shutting down gracefully...")
        self.cleanup_all(force=self.force)
        sys.exit(0)

    def _atexit_cleanup(self):
        """Cleanup function called on exit"""
        if self.process and self.process.poll() is None:
            self.logger.info("atexit cleanup triggered")
            self.cleanup_all(force=True, silent=True)

    def validate_environment(self) -> bool:
        """
        Validate the environment before starting.

        Returns:
            True if environment is valid, False otherwise
        """
        # Check if app file exists
        app_file = self.workspace_dir / self.app_path
        if not app_file.exists():
            print_error(f"Streamlit app file not found: {app_file}")
            print_info("Please ensure the app file exists at the specified path.")
            self.logger.error(f"App file not found: {app_file}")
            return False

        print_success(f"Found app file: {self.app_path}")
        self.logger.info(f"App file validated: {app_file}")

        # Check if Python is available
        try:
            result = subprocess.run(
                [sys.executable, "--version"], capture_output=True, text=True, timeout=5
            )
            python_version = result.stdout.strip()
            print_success(f"Python: {python_version}")
            self.logger.info(f"Python version: {python_version}")
        except Exception as e:
            print_error(f"Failed to check Python version: {e}")
            self.logger.error(f"Python check failed: {e}")
            return False

        # Check if Streamlit is installed
        try:
            result = subprocess.run(
                [sys.executable, "-m", "streamlit", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                streamlit_version = result.stdout.strip()
                print_success(f"Streamlit: {streamlit_version}")
                self.logger.info(f"Streamlit version: {streamlit_version}")
            else:
                print_error("Streamlit is not installed or not accessible")
                print_info("Install with: pip install streamlit")
                self.logger.error("Streamlit not found")
                return False
        except Exception as e:
            print_error(f"Failed to check Streamlit: {e}")
            print_info("Install with: pip install streamlit")
            self.logger.error(f"Streamlit check failed: {e}")
            return False

        return True

    def handle_port_conflict(self, port: int) -> Optional[int]:
        """
        Handle port conflicts by killing process or finding alternative.

        Args:
            port: The port to check

        Returns:
            Available port number or None if failed
        """
        if not self.port_manager.is_port_in_use(port):
            print_success(f"Port {port} is available")
            self.logger.info(f"Port {port} is available")
            return port

        # Port is in use
        print_warning(f"Port {port} is currently in use")
        self.logger.warning(f"Port {port} is in use")

        # Get process information
        pid = self.port_manager.get_process_using_port(port)
        if pid:
            process_name = self.port_manager.get_process_name(pid)
            print_info(f"Process: {process_name or 'Unknown'} (PID: {pid})")
            self.logger.info(f"Port {port} used by {process_name} (PID: {pid})")

        # Decide whether to kill the process
        should_kill = self.auto_kill

        if not self.auto_kill:
            should_kill = ask_yes_no(
                f"Kill the process using port {port}?", default=False
            )

        if should_kill:
            print_info(f"Attempting to free port {port}...")
            self.logger.info(f"Attempting to kill process on port {port}")

            if self.port_manager.kill_process_on_port(port):
                print_success(f"Successfully freed port {port}")
                self.logger.info(f"Port {port} freed successfully")
                return port
            else:
                print_warning(f"Failed to free port {port}")
                self.logger.warning(f"Failed to free port {port}")

        # Find alternative port
        print_info("Searching for alternative port...")
        self.logger.info("Searching for alternative port")

        alt_port = self.port_manager.find_available_port(port + 1)

        if alt_port:
            print_success(f"Found alternative port: {alt_port}")
            self.logger.info(f"Using alternative port: {alt_port}")
            return alt_port
        else:
            print_error("No available ports found")
            self.logger.error("No available ports found")
            return None

    def launch_streamlit(self, port: int) -> bool:
        """
        Launch the Streamlit application.

        Args:
            port: Port to use

        Returns:
            True if launched successfully, False otherwise
        """
        # Build command
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            self.app_path,
            "--server.port",
            str(port),
            "--server.headless",
            "true" if self.no_browser else "false",
            "--browser.gatherUsageStats",
            "false",
        ]

        self.logger.info(f"Launching Streamlit: {' '.join(cmd)}")

        try:
            # Launch process
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.workspace_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )

            # Wait a moment to check if process started successfully
            time.sleep(2)

            if self.process.poll() is not None:
                # Process terminated immediately
                print_error("Streamlit failed to start")
                self.logger.error("Streamlit process terminated immediately")
                return False

            # Track the process
            self.process_tracker.track_process(self.process, port)

            print_success("Streamlit started successfully")
            self.logger.info("Streamlit process started")

            return True

        except Exception as e:
            print_error(f"Failed to launch Streamlit: {e}")
            self.logger.error(f"Launch failed: {e}")
            return False

    def stream_output(self):
        """Stream Streamlit output to console"""
        if not self.process or not self.process.stdout:
            return

        print_separator()
        print_info("Streamlit output (Press Ctrl+C to stop):")
        print_separator()
        print()

        try:
            for line in self.process.stdout:
                print(line, end="")
                self.logger.debug(f"Streamlit: {line.rstrip()}")
        except KeyboardInterrupt:
            pass

    def cleanup(self, timeout: int = 5):
        """
        Cleanup and stop the Streamlit process.

        Args:
            timeout: Timeout in seconds for graceful shutdown
        """
        if not self.process:
            return

        print()
        print_info("Stopping Streamlit...")
        self.logger.info("Initiating shutdown")

        try:
            # Try graceful termination first
            self.process.terminate()

            # Wait for process to terminate
            try:
                self.process.wait(timeout=timeout)
                print_success("Streamlit stopped gracefully")
                self.logger.info("Streamlit stopped gracefully")
            except subprocess.TimeoutExpired:
                # Force kill if graceful shutdown fails
                print_warning("Graceful shutdown timed out, forcing...")
                self.logger.warning("Graceful shutdown timed out")

                self.process.kill()
                self.process.wait(timeout=2)

                print_success("Streamlit stopped (forced)")
                self.logger.info("Streamlit stopped (forced)")

        except Exception as e:
            print_error(f"Error during cleanup: {e}")
            self.logger.error(f"Cleanup error: {e}")

    def cleanup_all(self, force: bool = False, silent: bool = False, timeout: int = 10):
        """
        Comprehensive cleanup: stop processes and clear caches.

        Args:
            force: Skip all confirmations
            silent: Suppress output messages
            timeout: Maximum time for cleanup operations
        """
        if not silent:
            print()
            print_separator()
            print_info("Starting comprehensive cleanup...")
            print_separator()

        self.logger.info("Starting comprehensive cleanup")
        start_time = time.time()

        try:
            # Step 1: Stop the main process
            if self.process and self.process.poll() is None:
                if not silent:
                    print_info("Stopping main Streamlit process...")
                self.cleanup(timeout=5)

            # Step 2: Kill all Streamlit processes on tracked ports
            if not self.keep_processes:
                if not silent:
                    print()
                    print_info("Checking for other Streamlit processes...")

                results = self.process_tracker.kill_all_processes(
                    force=force or self.force
                )

                if not silent and results.get("total", 0) > 0:
                    print_success(f"Stopped {results['killed']} process(es)")
                    if results.get("failed", 0) > 0:
                        print_warning(f"Failed to stop {results['failed']} process(es)")
            else:
                if not silent:
                    print_info("Skipping process cleanup (--keep-processes flag)")

            # Step 3: Clear caches
            if not self.no_cache_clear:
                if not silent:
                    print()
                    print_info("Clearing cache directories...")

                cache_results = self.cache_manager.clear_all_caches(
                    force=force or self.force
                )

                if not silent and not cache_results.get("cancelled", False):
                    if cache_results["cleared"] > 0:
                        size_str = self.cache_manager.format_size(
                            cache_results["total_size"]
                        )
                        print_success(
                            f"Cleared {cache_results['cleared']} cache director{'y' if cache_results['cleared'] == 1 else 'ies'} ({size_str})"
                        )
                    if cache_results.get("failed", 0) > 0:
                        print_warning(
                            f"Failed to clear {cache_results['failed']} cache director{'y' if cache_results['failed'] == 1 else 'ies'}"
                        )
            else:
                if not silent:
                    print_info("Skipping cache cleanup (--no-cache-clear flag)")

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                if not silent:
                    print_warning(f"Cleanup timed out after {elapsed:.1f}s")
                self.logger.warning(f"Cleanup timed out after {elapsed:.1f}s")
            else:
                if not silent:
                    print()
                    print_success(f"Cleanup completed in {elapsed:.1f}s")
                self.logger.info(f"Cleanup completed in {elapsed:.1f}s")

        except Exception as e:
            if not silent:
                print_error(f"Error during cleanup: {e}")
            self.logger.error(f"Cleanup error: {e}")

        if not silent:
            print_separator()

    def start(self) -> int:
        """
        Start the Streamlit application.

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print()
        print_info("Starting DailyPlus AI Streamlit Application...")
        print()

        # Validate environment
        print_info("Validating environment...")
        if not self.validate_environment():
            return 1

        print()

        # Handle port conflicts
        print_info(f"Checking port {self.default_port}...")
        port = self.handle_port_conflict(self.default_port)

        if port is None:
            print_error("Failed to find an available port")
            print_info("Troubleshooting tips:")
            print_info("  1. Close other applications using ports 8501-8510")
            print_info("  2. Use --auto-kill flag to automatically free the port")
            print_info("  3. Specify a different port with --port <number>")
            return 1

        print()

        # Display startup banner
        print_banner(port, self.app_path)

        # Launch Streamlit
        if not self.launch_streamlit(port):
            return 1

        # Stream output
        try:
            self.stream_output()

            # Wait for process to complete
            if self.process:
                return_code = self.process.wait()

                if return_code == 0:
                    print_success("Streamlit exited successfully")
                else:
                    print_warning(f"Streamlit exited with code: {return_code}")

                return return_code

            return 1

        except KeyboardInterrupt:
            print()
            print_warning("Received interrupt signal")
            self.cleanup_all(force=self.force)
            return 0

        except Exception as e:
            print_error(f"Unexpected error: {e}")
            self.logger.error(f"Unexpected error: {e}")
            self.cleanup_all(force=True)
            return 1

    def cleanup_only(self) -> int:
        """
        Run cleanup operations only (don't start the app).

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        print()
        print_info("Running cleanup operations...")
        print()

        try:
            self.cleanup_all(force=self.force)
            return 0
        except Exception as e:
            print_error(f"Cleanup failed: {e}")
            self.logger.error(f"Cleanup failed: {e}")
            return 1


# ============================================
# Command-Line Interface
# ============================================


def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(
        description="Comprehensive Cross-Platform Startup Script for Streamlit Application with Cleanup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Start with defaults (port 8501)
  %(prog)s --port 8502              Start on custom port
  %(prog)s --auto-kill              Auto-kill conflicting processes
  %(prog)s --no-browser             Run in headless mode
  %(prog)s --force                  Skip all confirmations
  %(prog)s --cleanup-only           Just run cleanup and exit
  %(prog)s --no-cache-clear         Don't clear cache on shutdown
  %(prog)s --keep-processes         Don't kill processes on shutdown
  %(prog)s --verbose                Enable verbose logging

For more information, visit: https://github.com/yourusername/DailyPlus_AI
        """,
    )

    parser.add_argument(
        "-a",
        "--app",
        default="app/main.py",
        help="Path to Streamlit app file (default: app/main.py)",
    )

    parser.add_argument(
        "-p", "--port", type=int, default=8501, help="Port to use (default: 8501)"
    )

    parser.add_argument(
        "-k",
        "--auto-kill",
        action="store_true",
        help="Automatically kill processes on the specified port",
    )

    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Run in headless mode (don't open browser)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose logging"
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Skip all confirmations during cleanup",
    )

    parser.add_argument(
        "--no-cache-clear",
        action="store_true",
        help="Don't clear cache directories on shutdown",
    )

    parser.add_argument(
        "--keep-processes",
        action="store_true",
        help="Don't kill Streamlit processes on shutdown",
    )

    parser.add_argument(
        "--cleanup-only",
        action="store_true",
        help="Just run cleanup operations and exit (don't start app)",
    )

    parser.add_argument("--version", action="version", version="%(prog)s 2.0.0")

    args = parser.parse_args()

    # Create the application
    app = StreamlitApp(
        app_path=args.app,
        default_port=args.port,
        auto_kill=args.auto_kill,
        no_browser=args.no_browser,
        verbose=args.verbose,
        force=args.force,
        no_cache_clear=args.no_cache_clear,
        keep_processes=args.keep_processes,
    )

    # Run cleanup only if requested
    if args.cleanup_only:
        exit_code = app.cleanup_only()
    else:
        exit_code = app.start()

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

# Made with Bob
