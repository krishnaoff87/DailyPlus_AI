"""
Streamlit Startup Script with Port Management
Automatically handles port conflicts and launches Streamlit with the correct configuration.
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Add the scripts directory to the path to import port_manager
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from port_manager import PortManager, logger


class StreamlitLauncher:
    """Handles launching Streamlit with port management."""

    def __init__(self, app_path: str = "app/main.py", default_port: int = 8501):
        """
        Initialize the StreamlitLauncher.

        Args:
            app_path: Path to the Streamlit app file
            default_port: Default port to use
        """
        self.app_path = app_path
        self.default_port = default_port
        self.port_manager = PortManager(default_port=default_port)
        self.workspace_dir = Path(__file__).parent.parent

    def validate_app_path(self) -> bool:
        """
        Validate that the Streamlit app file exists.

        Returns:
            True if app file exists, False otherwise
        """
        app_file = self.workspace_dir / self.app_path
        if not app_file.exists():
            logger.error(f"Streamlit app file not found: {app_file}")
            return False
        return True

    def launch_streamlit(
        self, port: int, headless: bool = True, additional_args: list = None
    ) -> subprocess.Popen:
        """
        Launch Streamlit with the specified configuration.

        Args:
            port: Port to use
            headless: Whether to run in headless mode
            additional_args: Additional Streamlit arguments

        Returns:
            Subprocess object
        """
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            self.app_path,
            "--server.port",
            str(port),
        ]

        if headless:
            cmd.extend(["--server.headless", "true"])

        if additional_args:
            cmd.extend(additional_args)

        logger.info(f"Launching Streamlit on port {port}")
        logger.info(f"Command: {' '.join(cmd)}")

        try:
            process = subprocess.Popen(
                cmd,
                cwd=str(self.workspace_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            return process
        except Exception as e:
            logger.error(f"Failed to launch Streamlit: {e}")
            raise

    def start(
        self,
        auto_kill: bool = False,
        headless: bool = True,
        additional_args: list = None,
    ) -> int:
        """
        Start the Streamlit application with port management.

        Args:
            auto_kill: Whether to automatically kill processes on the default port
            headless: Whether to run in headless mode
            additional_args: Additional Streamlit arguments

        Returns:
            Exit code (0 for success, 1 for failure)
        """
        # Validate app path
        if not self.validate_app_path():
            return 1

        # Ensure port is available
        logger.info(f"Checking port availability for port {self.default_port}")
        success, port = self.port_manager.ensure_port_available(
            port=self.default_port, auto_kill=auto_kill
        )

        if not success or port is None:
            logger.error("Failed to find an available port")
            return 1

        if port != self.default_port:
            logger.warning(f"Default port {self.default_port} was not available")
            logger.info(f"Using alternative port: {port}")

        # Display port information
        print("\n" + "=" * 60)
        print("  🚀 Starting Streamlit Application")
        print("=" * 60)
        print(f"  Port: {port}")
        print(f"  URL: http://localhost:{port}")
        print(f"  App: {self.app_path}")
        print("=" * 60 + "\n")

        # Launch Streamlit
        try:
            process = self.launch_streamlit(
                port=port, headless=headless, additional_args=additional_args
            )

            # Wait for the process to complete
            logger.info("Streamlit is running. Press Ctrl+C to stop.")

            try:
                # Stream output
                for line in process.stdout:
                    print(line, end="")

                process.wait()
                return process.returncode

            except KeyboardInterrupt:
                logger.info("\nReceived interrupt signal. Stopping Streamlit...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Process did not terminate gracefully, forcing...")
                    process.kill()
                return 0

        except Exception as e:
            logger.error(f"Error running Streamlit: {e}")
            return 1


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Launch Streamlit with automatic port management"
    )
    parser.add_argument(
        "-a",
        "--app",
        default="app/main.py",
        help="Path to Streamlit app file (default: app/main.py)",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8501,
        help="Default port to use (default: 8501)",
    )
    parser.add_argument(
        "-k",
        "--auto-kill",
        action="store_true",
        help="Automatically kill processes on the default port",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run Streamlit in non-headless mode (opens browser)",
    )
    parser.add_argument(
        "--streamlit-args", nargs="*", help="Additional arguments to pass to Streamlit"
    )

    args = parser.parse_args()

    launcher = StreamlitLauncher(app_path=args.app, default_port=args.port)

    exit_code = launcher.start(
        auto_kill=args.auto_kill,
        headless=not args.no_headless,
        additional_args=args.streamlit_args,
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()

# Made with Bob
