# 🚀 DailyPlus_AI

> **AI-Powered Daily Commander** - Save 30 minutes every day with intelligent email, calendar, and chat processing.

A proof-of-concept application built in 10 hours to demonstrate how AI can transform daily information overload into actionable insights. DailyPlus_AI processes your daily context (emails, calendar events, chat messages) and generates prioritized briefings, action boards, and professional drafts.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Security](#security)
- [Limitations](#limitations)
- [Next Steps](#next-steps)
- [Documentation](#documentation)
- [License](#license)

---

## 🎯 Overview

**The Problem**: Busy professionals waste 30+ minutes daily switching between email, calendar, and chat to understand their day and prioritize tasks.

**The Solution**: DailyPlus_AI uses Claude 3.5 Sonnet to automatically:
- Generate 3-bullet morning briefings
- Extract and prioritize action items using Eisenhower matrix
- Identify key stakeholders
- Generate professional draft responses

**Time Savings**: 30 minutes/day = **2.5 hours/week** = **130 hours/year** per user

**PoC Scope**: 10-hour proof-of-concept with mock data to validate the core AI processing workflow and demonstrate business value.

---

## ✨ Features

### 📅 Morning Briefing Tab
- **11-Category Daily Summary**: Comprehensive briefing with AI-powered insights
  - 📊 Executive Overview with metrics
  - 🎯 Project Progress & Milestones
  - 📈 Productivity Metrics
  - 🚨 Critical Actions & Deadlines
  - ⚠️ Risks, Blockers & Challenges
  - 👥 Team & Stakeholder Activity
  - 🏢 Departmental Breakdown
  - 🎉 Notable Events & Decisions
  - **NEW** 📊 Trends Analysis - Pattern recognition and velocity tracking
  - **NEW** 🔮 Forecasts & Predictions - Data-driven timeline projections
  - **NEW** 🤖 AI Recommendations - Actionable optimization suggestions
- **Stakeholder Badges**: Visual display of key people involved
- **Action Count**: Quick metric of total tasks
- **Auto-Refresh**: Updates when new data is loaded

### ✅ Action Board Tab
- **Smart Prioritization**: Eisenhower matrix scoring (1-6 scale)
- **Priority Indicators**: Color-coded emoji (🔴 urgent, 🟠 high, 🟡 medium, 🟢 low)
- **Expandable Cards**: Detailed view with assignee, deadline, and score
- **Sorted Display**: Highest priority actions first
- **Score Transparency**: Shows calculation for each action

### 📝 Draft Generator Tab
- **AI-Powered Drafts**: Professional responses in under 50 words
- **Context Input**: Flexible text area for any scenario
- **Example Templates**: Quick-start with common contexts
- **Copy-to-Clipboard**: Easy integration into your workflow
- **Professional Tone**: Consistent, clear, and actionable language

---

## 🛠️ Tech Stack

### Core Technologies
- **Python 3.11+** - Modern type hints and performance
- **Streamlit** - Rapid interactive UI development
- **LangChain** - AI framework and abstractions
- **Anthropic Claude 3.5 Sonnet** - State-of-the-art language model
- **Pydantic** - Data validation and settings management

### Development Tools
- **uv** - Fast Python package manager (10-100x faster than pip)
- **pytest** - Testing framework
- **pre-commit** - Automated code quality checks
- **ruff** - Fast Python linter and formatter

### Why These Choices?
- **Streamlit**: Fastest path from code to interactive dashboard
- **Claude 3.5**: Best-in-class reasoning and structured output
- **Pydantic**: Type safety and runtime validation
- **uv**: Blazing fast dependency management
- **LangChain**: Industry-standard AI framework

---

## 🚀 Quick Start

Get up and running in 3 commands:

```bash
# 1. Install dependencies
uv sync

# 2. Configure API key
cp config/.env.example config/.env
# Edit config/.env and add your GEMINI_API_KEY

# 3. Run the app
uv run streamlit run app/main.py
```

The dashboard will open at `http://localhost:8501`

**First Time Setup?** See [docs/SETUP.md](docs/SETUP.md) for detailed instructions.

---

## 🎮 Running the Application

### Quick Start (Recommended)

**Option 1: Python Launcher with Port Management**
```bash
# Automatically handles port conflicts
python scripts/start_streamlit.py --auto-kill
```

**Option 2: PowerShell Launcher (Windows)**
```powershell
# Native Windows experience with colored output
.\scripts\start_streamlit.ps1
```

**Option 3: Direct Streamlit Command**
```bash
# Standard Streamlit launch
uv run streamlit run app/main.py
```

### Advanced Options

**Custom Port**:
```bash
# Python launcher
python scripts/start_streamlit.py -p 8502

# PowerShell
.\scripts\start_streamlit.ps1 -Port 8502

# Direct command
uv run streamlit run app/main.py --server.port 8502
```

**Development Mode** (auto-reload on file changes):
```bash
# Already enabled in .streamlit/config.toml
uv run streamlit run app/main.py
```

**Production Mode**:
```bash
# Copy production config first
cp .streamlit/config.production.toml .streamlit/config.toml

# Set environment
export ENVIRONMENT=production  # Linux/Mac
$env:ENVIRONMENT="production"  # PowerShell

# Run application
uv run streamlit run app/main.py
```

### Port Management Utilities

Our port management scripts automatically handle common issues:

- ✅ **Auto-detect** port conflicts
- ✅ **Auto-kill** existing processes (with confirmation)
- ✅ **Find alternative** ports if needed
- ✅ **Validate** app path before launch
- ✅ **Provide clear** error messages

**Check if port is in use**:
```bash
python scripts/port_manager.py -p 8501 --check
```

**Get detailed port information**:
```bash
python scripts/port_manager.py -p 8501 --info
```

**Find available port**:
```bash
python scripts/port_manager.py -p 8501 --find
```

See [scripts/README.md](scripts/README.md) for complete port management documentation.

### Troubleshooting Quick Links

**Common Issues**:
- 🔴 **Port already in use**: Use `python scripts/start_streamlit.py --auto-kill`
- 🔴 **CORS/XSRF errors**: See [Troubleshooting Guide](docs/TROUBLESHOOTING_STREAMLIT.md#cors-and-xsrf-issues)
- 🔴 **Configuration not loading**: See [Configuration Guide](docs/STREAMLIT_CONFIGURATION_GUIDE.md)
- 🔴 **API key errors**: Check `config/.env` has valid `GEMINI_API_KEY`

**Full troubleshooting guide**: [docs/TROUBLESHOOTING_STREAMLIT.md](docs/TROUBLESHOOTING_STREAMLIT.md)

---

## 🏗️ Architecture

### High-Level Data Flow

```
Mock Data (JSON) → Data Loader (Pydantic) → AI Processor (Claude) 
    → Prioritizer (Eisenhower) → Streamlit UI (3 Tabs)
```

### Component Overview

```
DailyPlus_AI/
├── app/
│   └── main.py              # Streamlit dashboard (3 tabs)
├── src/
│   ├── ingest/
│   │   └── loader.py        # Data loading with Pydantic validation
│   └── ai/
│       ├── processor.py     # Claude AI processing (briefing extraction)
│       └── prioritizer.py   # Eisenhower matrix scoring
├── config/
│   ├── settings.py          # Configuration management
│   └── .env                 # API keys (git-ignored)
├── data/
│   └── mock_daily_context.json  # 9 sample items (email, calendar, chat)
├── tests/
│   └── test_basic.py        # Pytest test suite
└── docs/
    ├── SETUP.md             # Installation guide
    ├── ARCHITECTURE.md      # Technical deep-dive
    └── PITCH.md             # Business pitch deck
```

### Key Design Decisions

1. **Pydantic Everywhere**: Type-safe data validation at every layer
2. **Session State**: Cache AI results to avoid redundant API calls
3. **Retry Logic**: 2-attempt retry for transient API failures
4. **Low Temperature**: 0.2 for consistent briefing generation
5. **Strict JSON Schema**: Ensures reliable AI output parsing

**Deep Dive**: See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for complete technical documentation.

---

## 🔒 Security

### API Key Protection
- ✅ Stored in `.env` file (git-ignored)
- ✅ Loaded via Pydantic Settings
- ✅ Never logged or displayed in UI
- ✅ Validated at application startup

### Data Validation
- ✅ All inputs validated with Pydantic models
- ✅ Type checking with Python Literal types
- ✅ Required fields enforced
- ✅ Invalid data rejected early

### Error Handling
- ✅ API errors caught and displayed safely
- ✅ No sensitive data in error messages
- ✅ User-friendly troubleshooting tips
- ✅ Retry logic for transient failures

### Data Isolation
- ✅ Mock data only (no real user data in PoC)
- ✅ No database or persistence layer
- ✅ Session state cleared on browser close
- ✅ No data sharing between users

---

## ⚠️ Limitations

This is a **proof-of-concept** with intentional scope limitations:

### Current Limitations
- **Mock Data Only**: Uses 9 hardcoded items, no real API integrations
- **No Persistence**: Data cleared when browser closes
- **Single User**: No authentication or multi-user support
- **No Database**: All processing in-memory
- **Limited Error Recovery**: Basic retry logic only
- **No Action Tracking**: Checkboxes are non-functional (UI only)
- **No Notifications**: No email/push alerts
- **Web Only**: No mobile app

### Why These Limitations?
- Focus on **core AI processing workflow**
- Demonstrate **value proposition quickly** (10-hour PoC)
- Minimize **infrastructure complexity**
- Enable **rapid iteration** and feedback

---

## 🎯 Next Steps

### Phase 1: Production MVP (v1.0)
- [ ] Real API integrations (Gmail, Google Calendar, Slack)
- [ ] User authentication (OAuth2)
- [ ] PostgreSQL database for persistence
- [ ] Action tracking and completion
- [ ] Email notifications for urgent items
- [ ] Multi-user support with data isolation

### Phase 2: Enhanced Features (v1.5)
- [ ] Mobile app (React Native)
- [ ] Push notifications
- [ ] Team collaboration features
- [ ] Custom priority rules per user
- [ ] Historical analytics dashboard
- [ ] Integration with Microsoft 365

### Phase 3: Enterprise (v2.0)
- [ ] Multi-language support
- [ ] Advanced AI insights and trends
- [ ] Integration marketplace
- [ ] SSO and enterprise security
- [ ] Custom AI model fine-tuning
- [ ] White-label deployment options

**Business Case**: See [docs/PITCH.md](docs/PITCH.md) for ROI analysis and pitch deck.

---

## 📚 Documentation

### Getting Started
- **[SETUP.md](docs/SETUP.md)** - Installation and configuration guide
- **[PITCH.md](docs/PITCH.md)** - Business pitch deck and ROI analysis

### Architecture & Design
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technical architecture and design decisions
- **[NEW_FEATURES_DAILY_SUMMARY.md](docs/NEW_FEATURES_DAILY_SUMMARY.md)** - ⭐ AI-powered Trends, Forecasts & Recommendations

### Streamlit Configuration & Deployment
- **[STREAMLIT_CONFIGURATION_GUIDE.md](docs/STREAMLIT_CONFIGURATION_GUIDE.md)** - ⭐ NEW: Comprehensive configuration best practices
- **[TROUBLESHOOTING_STREAMLIT.md](docs/TROUBLESHOOTING_STREAMLIT.md)** - ⭐ NEW: Common issues and solutions
- **[DEPLOYMENT_CHECKLIST.md](docs/DEPLOYMENT_CHECKLIST.md)** - ⭐ NEW: Production deployment guide
- **[.streamlit/README.md](.streamlit/README.md)** - CORS/XSRF configuration details
- **[scripts/README.md](scripts/README.md)** - Port management utilities

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html
```

### Code Quality

```bash
# Run all pre-commit checks
uv run pre-commit run --all-files

# Run specific checks
uv run pre-commit run ruff --all-files
```

---

## 🤝 Contributing

This is a proof-of-concept project. For production deployment:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run tests and linting (`uv run pytest && uv run pre-commit run --all-files`)
4. Commit changes (`git commit -m 'Add amazing feature'`)
5. Push to branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** - see below for details:

```
MIT License

Copyright (c) 2026 DailyPlus_AI Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- **Anthropic** - Claude 3.5 Sonnet API
- **Streamlit** - Rapid UI framework
- **LangChain** - AI development framework
- **Astral** - uv package manager and ruff linter

---

## 📞 Support

For questions or issues:
- 📖 Check [docs/SETUP.md](docs/SETUP.md) for setup help
- 🏗️ Review [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for technical details
- 🐛 Open an issue on GitHub
- 💬 Contact the development team

---

**Made with Bob** 🤖 | Built in 10 hours | Saves 30 minutes/day

---

## 📊 Project Stats

- **Lines of Code**: ~1,500
- **Development Time**: 10 hours
- **Test Coverage**: Core functionality
- **Dependencies**: 8 core packages
- **Mock Data Items**: 9 (email, calendar, chat)
- **Priority Levels**: 4 (urgent, high, medium, low)
- **Score Range**: 1-6 (Eisenhower matrix)

---

*This is a proof-of-concept demonstrating AI-powered daily workflow optimization. Not intended for production use without proper API integrations, authentication, and security hardening.*