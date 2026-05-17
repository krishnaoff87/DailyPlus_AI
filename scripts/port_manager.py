"""
Port Manager Utility for Streamlit Application
Handles port conflicts and provides port management functionality for Windows and Unix-based systems.
Enhanced with psutil for robust cross-platform process management.
"""

import subprocess
import sys
import time
import logging
import platform
from typing import Optional, Tuple

# Try to import psutil for robust process management
try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PortManager:
    """Manages port availability and process handling on Windows and Unix-based systems."""

    def __init__(self, default_port: int = 8501):
        """
        Initialize the PortManager.

        Args:
            default_port: The default port to check (default: 8501)
        """
        self.default_port = default_port
        self.max_port_attempts = 10
        self.is_windows = platform.system() == "Windows"

    def is_port_in_use(self, port: int) -> bool:
        """
        Check if a port is currently in use.

        Args:
            port: Port number to check

        Returns:
            True if port is in use, False otherwise
        """
        try:
            if PSUTIL_AVAILABLE:
                # Use psutil for robust cross-platform port checking
                for conn in psutil.net_connections(kind="inet"):
                    if conn.laddr.port == port:
                        return True
                return False
            else:
                # Fallback to platform-specific commands
                if self.is_windows:
                    # Use PowerShell to check if port is in use
                    cmd = f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue"
                    result = subprocess.run(
                        ["powershell", "-Command", cmd],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    return bool(result.stdout.strip())
                else:
                    # Use lsof or netstat on Unix-based systems
                    try:
                        # Try lsof first (more reliable)
                        result = subprocess.run(
                            ["lsof", "-i", f":{port}", "-t"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        return bool(result.stdout.strip())
                    except FileNotFoundError:
                        # Fall back to netstat if lsof is not available
                        result = subprocess.run(
                            ["netstat", "-an"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        return f":{port}" in result.stdout
        except subprocess.TimeoutExpired:
            logger.warning(f"Timeout while checking port {port}")
            return False
        except Exception as e:
            logger.error(f"Error checking port {port}: {e}")
            return False

    def get_process_using_port(self, port: int) -> Optional[int]:
        """
        Get the process ID using a specific port.

        Args:
            port: Port number to check

        Returns:
            Process ID if found, None otherwise
        """
        try:
            if PSUTIL_AVAILABLE:
                # Use psutil for robust cross-platform process detection
                for conn in psutil.net_connections(kind="inet"):
                    if (
                        hasattr(conn, "laddr")
                        and conn.laddr
                        and conn.laddr.port == port
                    ):
                        if conn.pid:
                            logger.info(
                                f"Port {port} is being used by process ID: {conn.pid}"
                            )
                            return conn.pid
                return None
            else:
                # Fallback to platform-specific commands
                if self.is_windows:
                    cmd = f"(Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -First 1).OwningProcess"
                    result = subprocess.run(
                        ["powershell", "-Command", cmd],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.stdout.strip():
                        # Handle potential multiple PIDs by taking the first one
                        pid_str = result.stdout.strip().split("\n")[0].strip()
                        if pid_str:
                            pid = int(pid_str)
                            logger.info(
                                f"Port {port} is being used by process ID: {pid}"
                            )
                            return pid
                else:
                    # Use lsof on Unix-based systems
                    try:
                        result = subprocess.run(
                            ["lsof", "-i", f":{port}", "-t"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if result.stdout.strip():
                            pid = int(result.stdout.strip().split("\n")[0])
                            logger.info(
                                f"Port {port} is being used by process ID: {pid}"
                            )
                            return pid
                    except FileNotFoundError:
                        logger.warning("lsof command not found, cannot get process ID")
                return None
        except (ValueError, subprocess.TimeoutExpired) as e:
            logger.error(f"Error getting process for port {port}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def get_process_name(self, pid: int) -> Optional[str]:
        """
        Get the name of a process by its PID.

        Args:
            pid: Process ID

        Returns:
            Process name if found, None otherwise
        """
        try:
            if self.is_windows:
                cmd = (
                    f"(Get-Process -Id {pid} -ErrorAction SilentlyContinue).ProcessName"
                )
                result = subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.stdout.strip():
                    return result.stdout.strip()
            else:
                # Use ps on Unix-based systems
                result = subprocess.run(
                    ["ps", "-p", str(pid), "-o", "comm="],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.stdout.strip():
                    return result.stdout.strip()
            return None
        except Exception as e:
            logger.error(f"Error getting process name for PID {pid}: {e}")
            return None

    def kill_process_on_port(self, port: int, force: bool = True) -> bool:
        """
        Kill the process using a specific port.

        Args:
            port: Port number
            force: Whether to force kill the process

        Returns:
            True if process was killed successfully, False otherwise
        """
        pid = self.get_process_using_port(port)

        if pid is None:
            logger.info(f"No process found using port {port}")
            return True

        process_name = self.get_process_name(pid)
        logger.info(
            f"Attempting to kill process {process_name or 'Unknown'} (PID: {pid}) on port {port}"
        )

        try:
            if self.is_windows:
                force_flag = "-Force" if force else ""
                cmd = (
                    f"Stop-Process -Id {pid} {force_flag} -ErrorAction SilentlyContinue"
                )
                result = subprocess.run(
                    ["powershell", "-Command", cmd],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
            else:
                # Use kill on Unix-based systems
                signal = "-9" if force else "-15"
                result = subprocess.run(
                    ["kill", signal, str(pid)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

            # Wait a moment for the process to terminate
            time.sleep(2)

            # Verify the port is now free
            if not self.is_port_in_use(port):
                logger.info(f"Successfully killed process on port {port}")
                return True
            else:
                logger.warning(f"Port {port} is still in use after kill attempt")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout while trying to kill process on port {port}")
            return False
        except Exception as e:
            logger.error(f"Error killing process on port {port}: {e}")
            return False

    def find_available_port(self, start_port: Optional[int] = None) -> Optional[int]:
        """
        Find an available port starting from a given port.

        Args:
            start_port: Port to start searching from (default: self.default_port)

        Returns:
            Available port number if found, None otherwise
        """
        if start_port is None:
            start_port = self.default_port

        for port in range(start_port, start_port + self.max_port_attempts):
            if not self.is_port_in_use(port):
                logger.info(f"Found available port: {port}")
                return port

        logger.error(
            f"No available ports found in range {start_port}-{start_port + self.max_port_attempts}"
        )
        return None

    def ensure_port_available(
        self, port: Optional[int] = None, auto_kill: bool = False
    ) -> Tuple[bool, Optional[int]]:
        """
        Ensure a port is available, optionally killing the process using it.

        Args:
            port: Port to check (default: self.default_port)
            auto_kill: Whether to automatically kill the process using the port

        Returns:
            Tuple of (success, port_number)
        """
        if port is None:
            port = self.default_port

        if not self.is_port_in_use(port):
            logger.info(f"Port {port} is available")
            return True, port

        logger.warning(f"Port {port} is in use")

        if auto_kill:
            logger.info(f"Attempting to free port {port}")
            if self.kill_process_on_port(port):
                return True, port
            else:
                logger.warning(f"Failed to free port {port}, searching for alternative")
                alt_port = self.find_available_port(port + 1)
                if alt_port:
                    return True, alt_port
                return False, None
        else:
            # Find alternative port
            alt_port = self.find_available_port(port + 1)
            if alt_port:
                logger.info(f"Using alternative port: {alt_port}")
                return True, alt_port
            return False, None

    def get_port_info(self, port: int) -> dict:
        """
        Get detailed information about a port.

        Args:
            port: Port number to check

        Returns:
            Dictionary with port information
        """
        in_use = self.is_port_in_use(port)
        info = {"port": port, "in_use": in_use, "pid": None, "process_name": None}

        if in_use:
            pid = self.get_process_using_port(port)
            if pid:
                info["pid"] = pid
                info["process_name"] = self.get_process_name(pid)

        return info


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Port Manager for Streamlit Application"
    )
    parser.add_argument(
        "-p", "--port", type=int, default=8501, help="Port to manage (default: 8501)"
    )
    parser.add_argument(
        "-c", "--check", action="store_true", help="Check if port is in use"
    )
    parser.add_argument(
        "-k", "--kill", action="store_true", help="Kill process using the port"
    )
    parser.add_argument(
        "-f", "--find", action="store_true", help="Find an available port"
    )
    parser.add_argument(
        "-i", "--info", action="store_true", help="Get detailed port information"
    )

    args = parser.parse_args()

    manager = PortManager(default_port=args.port)

    if args.check:
        in_use = manager.is_port_in_use(args.port)
        print(f"Port {args.port} is {'IN USE' if in_use else 'AVAILABLE'}")
        sys.exit(0 if not in_use else 1)

    elif args.kill:
        success = manager.kill_process_on_port(args.port)
        if success:
            print(f"Successfully freed port {args.port}")
            sys.exit(0)
        else:
            print(f"Failed to free port {args.port}")
            sys.exit(1)

    elif args.find:
        port = manager.find_available_port(args.port)
        if port:
            print(f"Available port found: {port}")
            sys.exit(0)
        else:
            print("No available ports found")
            sys.exit(1)

    elif args.info:
        info = manager.get_port_info(args.port)
        print("\nPort Information:")
        print(f"  Port: {info['port']}")
        print(f"  Status: {'IN USE' if info['in_use'] else 'AVAILABLE'}")
        if info["in_use"]:
            print(f"  Process ID: {info['pid']}")
            print(f"  Process Name: {info['process_name']}")
        sys.exit(0)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
