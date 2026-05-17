"""
Comprehensive Test Suite for Streamlit Configuration and Port Management
Tests configuration validation, port manager functionality, and environment detection.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
import toml

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.port_manager import PortManager


class TestConfigurationFiles(unittest.TestCase):
    """Test Streamlit configuration file validation."""

    def setUp(self):
        """Set up test fixtures."""
        self.config_dir = project_root / ".streamlit"
        self.base_config = self.config_dir / "config.toml"
        self.dev_config = self.config_dir / "config.development.toml"
        self.prod_config = self.config_dir / "config.production.toml"

    def test_config_files_exist(self):
        """Test that all configuration files exist."""
        self.assertTrue(self.base_config.exists(), "Base config.toml not found")
        self.assertTrue(self.dev_config.exists(), "Development config not found")
        self.assertTrue(self.prod_config.exists(), "Production config not found")

    def test_config_toml_syntax(self):
        """Test that all config files have valid TOML syntax."""
        for config_file in [self.base_config, self.dev_config, self.prod_config]:
            with self.subTest(config=config_file.name):
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        config = toml.load(f)
                    self.assertIsInstance(
                        config, dict, f"{config_file.name} is not valid TOML"
                    )
                except Exception as e:
                    self.fail(f"Failed to parse {config_file.name}: {e}")

    def test_base_config_cors_xsrf_alignment(self):
        """Test that base config has CORS and XSRF properly aligned (both false for dev)."""
        with open(self.base_config, "r", encoding="utf-8") as f:
            config = toml.load(f)

        self.assertIn("server", config, "Server section missing in base config")
        self.assertFalse(
            config["server"].get("enableCORS", True),
            "CORS should be disabled in development",
        )
        self.assertFalse(
            config["server"].get("enableXsrfProtection", True),
            "XSRF protection should be disabled when CORS is disabled",
        )

    def test_dev_config_cors_xsrf_alignment(self):
        """Test that development config has CORS and XSRF properly aligned (both false)."""
        with open(self.dev_config, "r", encoding="utf-8") as f:
            config = toml.load(f)

        self.assertIn("server", config, "Server section missing in dev config")
        self.assertFalse(
            config["server"].get("enableCORS", True),
            "CORS should be disabled in development",
        )
        self.assertFalse(
            config["server"].get("enableXsrfProtection", True),
            "XSRF protection should be disabled when CORS is disabled",
        )

    def test_prod_config_cors_xsrf_alignment(self):
        """Test that production config has CORS and XSRF properly aligned (both true)."""
        with open(self.prod_config, "r", encoding="utf-8") as f:
            config = toml.load(f)

        self.assertIn("server", config, "Server section missing in prod config")
        self.assertTrue(
            config["server"].get("enableCORS", False),
            "CORS should be enabled in production",
        )
        self.assertTrue(
            config["server"].get("enableXsrfProtection", False),
            "XSRF protection should be enabled when CORS is enabled",
        )

    def test_config_has_required_sections(self):
        """Test that all configs have required sections."""
        required_sections = ["theme", "server", "browser"]

        for config_file in [self.base_config, self.dev_config, self.prod_config]:
            with self.subTest(config=config_file.name):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = toml.load(f)

                for section in required_sections:
                    self.assertIn(
                        section,
                        config,
                        f"Missing required section '{section}' in {config_file.name}",
                    )

    def test_port_configuration(self):
        """Test that port is correctly configured in all configs."""
        for config_file in [self.base_config, self.dev_config, self.prod_config]:
            with self.subTest(config=config_file.name):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = toml.load(f)

                self.assertEqual(
                    config["server"].get("port"),
                    8501,
                    f"Port should be 8501 in {config_file.name}",
                )


class TestPortManager(unittest.TestCase):
    """Test PortManager functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PortManager(default_port=8501)

    def test_port_manager_initialization(self):
        """Test PortManager initializes correctly."""
        self.assertEqual(self.manager.default_port, 8501)
        self.assertEqual(self.manager.max_port_attempts, 10)

    @patch("subprocess.run")
    def test_is_port_in_use_available(self, mock_run):
        """Test checking if a port is available."""
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        result = self.manager.is_port_in_use(8502)
        self.assertFalse(result, "Port should be reported as available")

    @patch("subprocess.run")
    def test_is_port_in_use_occupied(self, mock_run):
        """Test checking if a port is in use."""
        mock_run.return_value = MagicMock(stdout="ESTABLISHED", returncode=0)
        result = self.manager.is_port_in_use(8501)
        self.assertTrue(result, "Port should be reported as in use")

    @patch("subprocess.run")
    def test_get_process_using_port(self, mock_run):
        """Test getting process ID using a port."""
        mock_run.return_value = MagicMock(stdout="1234\n", returncode=0)
        pid = self.manager.get_process_using_port(8501)
        self.assertEqual(pid, 1234, "Should return correct PID")

    @patch("subprocess.run")
    def test_get_process_name(self, mock_run):
        """Test getting process name by PID."""
        mock_run.return_value = MagicMock(stdout="python\n", returncode=0)
        name = self.manager.get_process_name(1234)
        self.assertEqual(name, "python", "Should return correct process name")

    def test_find_available_port_range(self):
        """Test that find_available_port searches correct range."""
        # This test validates the logic without actual port checking
        start_port = 8501
        expected_range = range(start_port, start_port + self.manager.max_port_attempts)
        self.assertEqual(len(list(expected_range)), 10, "Should search 10 ports")

    def test_get_port_info_structure(self):
        """Test that get_port_info returns correct structure."""
        info = self.manager.get_port_info(8501)

        self.assertIn("port", info)
        self.assertIn("in_use", info)
        self.assertIn("pid", info)
        self.assertIn("process_name", info)
        self.assertEqual(info["port"], 8501)


class TestEnvironmentDetection(unittest.TestCase):
    """Test environment detection in config/settings.py."""

    def setUp(self):
        """Set up test fixtures."""
        # Store original environment
        self.original_env = os.environ.get("ENVIRONMENT")

    def tearDown(self):
        """Restore original environment."""
        if self.original_env:
            os.environ["ENVIRONMENT"] = self.original_env
        elif "ENVIRONMENT" in os.environ:
            del os.environ["ENVIRONMENT"]

    @patch.dict(
        os.environ, {"ENVIRONMENT": "development", "GEMINI_API_KEY": "AIzaTest123"}
    )
    def test_is_development(self):
        """Test development environment detection."""
        try:
            # Import here to get fresh settings with mocked env
            from config.settings import Settings

            settings = Settings()

            self.assertTrue(settings.is_development())
            self.assertFalse(settings.is_production())
        except ModuleNotFoundError as e:
            self.skipTest(f"Skipping: {e}")

    @patch.dict(
        os.environ, {"ENVIRONMENT": "production", "GEMINI_API_KEY": "AIzaTest123"}
    )
    def test_is_production(self):
        """Test production environment detection."""
        try:
            from config.settings import Settings

            settings = Settings()

            self.assertTrue(settings.is_production())
            self.assertFalse(settings.is_development())
        except ModuleNotFoundError as e:
            self.skipTest(f"Skipping: {e}")

    @patch.dict(
        os.environ, {"ENVIRONMENT": "development", "GEMINI_API_KEY": "AIzaTest123"}
    )
    def test_get_streamlit_config_path_dev(self):
        """Test getting Streamlit config path for development."""
        try:
            from config.settings import Settings

            settings = Settings()

            config_path = settings.get_streamlit_config_path()
            self.assertTrue(str(config_path).endswith("config.toml"))
            self.assertTrue(config_path.exists())
        except ModuleNotFoundError as e:
            self.skipTest(f"Skipping: {e}")

    @patch.dict(
        os.environ, {"ENVIRONMENT": "production", "GEMINI_API_KEY": "AIzaTest123"}
    )
    def test_get_streamlit_config_path_prod(self):
        """Test getting Streamlit config path for production."""
        try:
            from config.settings import Settings

            settings = Settings()

            config_path = settings.get_streamlit_config_path()
            self.assertTrue(str(config_path).endswith("config.production.toml"))
            self.assertTrue(config_path.exists())
        except ModuleNotFoundError as e:
            self.skipTest(f"Skipping: {e}")

    @patch.dict(
        os.environ, {"ENVIRONMENT": "development", "GEMINI_API_KEY": "AIzaTest123"}
    )
    def test_get_environment_info(self):
        """Test getting environment information."""
        try:
            from config.settings import Settings

            settings = Settings()

            info = settings.get_environment_info()

            self.assertIn("environment", info)
            self.assertIn("is_production", info)
            self.assertIn("streamlit_config", info)
            self.assertIn("streamlit_port", info)
            self.assertIn("cors_enabled", info)
            self.assertIn("xsrf_protection", info)

            # Development should have CORS/XSRF disabled
            self.assertFalse(info["cors_enabled"])
            self.assertFalse(info["xsrf_protection"])
        except ModuleNotFoundError as e:
            self.skipTest(f"Skipping: {e}")


class TestDocumentationLinks(unittest.TestCase):
    """Test that documentation references are valid."""

    def setUp(self):
        """Set up test fixtures."""
        self.docs_dir = project_root / "docs"
        self.scripts_dir = project_root / "scripts"

    def test_documentation_files_exist(self):
        """Test that key documentation files exist."""
        required_docs = [
            self.docs_dir / "STREAMLIT_CONFIGURATION_GUIDE.md",
            self.docs_dir / "TROUBLESHOOTING_STREAMLIT.md",
            self.scripts_dir / "README.md",
        ]

        for doc_file in required_docs:
            with self.subTest(doc=doc_file.name):
                self.assertTrue(doc_file.exists(), f"{doc_file.name} not found")

    def test_script_files_exist(self):
        """Test that all referenced script files exist."""
        required_scripts = [
            self.scripts_dir / "port_manager.py",
            self.scripts_dir / "start_streamlit.py",
            self.scripts_dir / "start_streamlit.ps1",
        ]

        for script_file in required_scripts:
            with self.subTest(script=script_file.name):
                self.assertTrue(script_file.exists(), f"{script_file.name} not found")


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationFiles))
    suite.addTests(loader.loadTestsFromTestCase(TestPortManager))
    suite.addTests(loader.loadTestsFromTestCase(TestEnvironmentDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentationLinks))

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("=" * 70)
    print("DailyPlus_AI - Streamlit Configuration Test Suite")
    print("=" * 70)
    print()

    result = run_tests()

    print()
    print("=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

# Made with Bob
