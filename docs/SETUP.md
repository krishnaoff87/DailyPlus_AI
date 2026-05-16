# DailyPlus_AI Setup Guide

## Prerequisites

- **Python 3.11+** - Required for modern type hints and performance
- **uv package manager** - Fast Python package installer and resolver
  - Install: `pip install uv` or visit [uv documentation](https://github.com/astral-sh/uv)

## Installation

Follow these steps to set up the DailyPlus_AI PoC on your local machine:

### 1. Clone Repository

```bash
git clone <repository-url>
cd DailyPlus_AI
```

### 2. Install Dependencies

Use `uv` to install all project dependencies:

```bash
uv sync
```

This will:
- Create a virtual environment
- Install all dependencies from `pyproject.toml`
- Lock versions in `uv.lock`

### 3. Configure Environment Variables

Copy the example environment file and add your API key:

```bash
# Windows (PowerShell)
Copy-Item config\.env.example config\.env

# Linux/Mac
cp config/.env.example config/.env
```

Edit `config/.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
```

**Getting an API Key:**
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy and paste into `.env` file

### 4. Install Pre-commit Hooks

Set up code quality checks:

```bash
uv run pre-commit install
```

This enables automatic code formatting and linting on every commit.

## Running the Application

Start the Streamlit dashboard:

```bash
uv run streamlit run app/main.py
```

The application will open in your default browser at `http://localhost:8501`

**Alternative Port:**
```bash
uv run streamlit run app/main.py --server.port 8502
```

## Testing

Run the test suite:

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_basic.py -v
```

## Code Quality Checks

Run pre-commit checks manually:

```bash
# Run all checks
uv run pre-commit run --all-files

# Run specific hook
uv run pre-commit run ruff --all-files
```

## Troubleshooting

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:**
1. Verify `.env` file exists in `config/` directory
2. Check that `ANTHROPIC_API_KEY` is set correctly
3. Restart the Streamlit application

### Issue: "Module not found" errors

**Solution:**
```bash
# Reinstall dependencies
uv sync --reinstall
```

### Issue: Pre-commit hooks failing

**Solution:**
```bash
# Update pre-commit hooks
uv run pre-commit autoupdate

# Clear cache and reinstall
uv run pre-commit clean
uv run pre-commit install
```

### Issue: Port already in use

**Solution:**
```bash
# Use a different port
uv run streamlit run app/main.py --server.port 8502
```

## Project Structure

```
DailyPlus_AI/
├── app/
│   └── main.py              # Streamlit dashboard
├── config/
│   ├── .env.example         # Environment template
│   ├── .env                 # Your API keys (git-ignored)
│   └── settings.py          # Configuration loader
├── data/
│   └── mock_daily_context.json  # Mock data (9 items)
├── docs/
│   ├── SETUP.md            # This file
│   ├── ARCHITECTURE.md     # Technical architecture
│   └── PITCH.md            # Business pitch deck
├── src/
│   ├── ingest/
│   │   └── loader.py       # Data loading with Pydantic
│   └── ai/
│       ├── processor.py    # Claude AI processing
│       └── prioritizer.py  # Priority scoring
├── tests/
│   └── test_basic.py       # Pytest test suite
├── .gitignore
├── .pre-commit-config.yaml
├── pyproject.toml          # Project dependencies
├── uv.lock                 # Locked dependencies
└── README.md               # Project overview
```

## Next Steps

1. **Explore the Dashboard**: Load daily context and explore the 3 tabs
2. **Review the Code**: Check `src/` directory for implementation details
3. **Run Tests**: Verify everything works with `uv run pytest tests/ -v`
4. **Read Architecture**: See `docs/ARCHITECTURE.md` for technical details

## Development Workflow

1. Make code changes
2. Run tests: `uv run pytest tests/`
3. Check code quality: `uv run pre-commit run --all-files`
4. Commit changes (pre-commit hooks run automatically)
5. Test in Streamlit: `uv run streamlit run app/main.py`

## Support

For issues or questions:
- Check `docs/ARCHITECTURE.md` for technical details
- Review error messages in the Streamlit UI
- Verify API key is valid and has credits

---

**Made with Bob** 🤖