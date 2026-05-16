# DailyPlus_AI Technical Architecture

## Overview

DailyPlus_AI is a proof-of-concept AI-powered daily commander that processes emails, calendar events, and chat messages to generate actionable briefings. Built as a 10-hour PoC to demonstrate 30 minutes/day time savings for busy professionals.

## System Architecture

### High-Level Data Flow

```
┌─────────────────┐
│  Mock Data      │
│  (JSON File)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Loader    │
│  (Pydantic)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  AI Processor   │
│  (Claude 3.5)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Prioritizer    │
│  (Eisenhower)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Streamlit UI   │
│  (3 Tabs)       │
└─────────────────┘
```

### Component Architecture

```
app/
  └── main.py                    # Streamlit UI Layer
       ├── Session State Management
       ├── Tab 1: Morning Briefing
       ├── Tab 2: Action Board
       └── Tab 3: Draft Generator

src/
  ├── ingest/
  │   └── loader.py              # Data Ingestion Layer
  │        ├── MockContextItem (Pydantic)
  │        └── load_mock_data()
  │
  └── ai/
      ├── processor.py           # AI Processing Layer
      │    ├── DailyBriefing (Pydantic)
      │    ├── ActionItem (Pydantic)
      │    └── process_daily_context()
      │
      └── prioritizer.py         # Priority Scoring Layer
           ├── calculate_priority_score()
           └── sort_actions_by_priority()

config/
  └── settings.py                # Configuration Layer
       └── Settings (Pydantic)

data/
  └── mock_daily_context.json    # Mock Data (9 items)
```

## Component Descriptions

### 1. Data Ingestion Layer (`src/ingest/loader.py`)

**Purpose**: Load and validate daily context items from mock data source.

**Key Components**:
- `MockContextItem`: Pydantic model with strict validation
  - Fields: id, source, timestamp, subject, body, sender, participants, urgency_hint, has_action
  - Source types: email, calendar, chat
  - Urgency levels: urgent, high, medium, low

- `load_mock_data()`: Loads JSON file and validates each item
  - Returns: `list[MockContextItem]`
  - Error handling: File not found, invalid JSON, validation failures

**Data Validation**:
```python
class MockContextItem(BaseModel):
    id: str
    source: Literal["email", "calendar", "chat"]
    timestamp: str  # ISO 8601 format
    subject: str
    body: str
    sender: str
    participants: list[str]
    urgency_hint: Literal["urgent", "high", "medium", "low"]
    has_action: bool
```

### 2. AI Processing Layer (`src/ai/processor.py`)

**Purpose**: Process daily context using Claude AI to extract structured briefing.

**Key Components**:
- `ActionItem`: Pydantic model for extracted actions
  - Fields: task, assignee, deadline, priority
  
- `DailyBriefing`: Pydantic model for complete briefing
  - Fields: summary (3 bullets), actions (list), stakeholders (list)

- `process_daily_context()`: Main AI processing function
  - Model: Claude 3.5 Sonnet (claude-3-5-sonnet-20241022)
  - Temperature: 0.2 (deterministic)
  - Retry logic: 2 attempts with error handling

**AI Prompt Design**:
```
Analyze these work items and extract:
1. A 3-bullet summary of the day
2. All actionable items with task, assignee, deadline, priority
3. List of all stakeholders mentioned

Return ONLY valid JSON matching this schema:
{
  "summary": "• Bullet 1\n• Bullet 2\n• Bullet 3",
  "actions": [{"task": "...", "assignee": "...", "deadline": "...", "priority": "urgent|high|medium|low"}],
  "stakeholders": ["name1", "name2"]
}
```

**Why This Design**:
- Strict JSON schema ensures consistent output
- Pydantic validation catches malformed responses
- Low temperature (0.2) for consistent results
- Retry logic handles transient API issues

### 3. Priority Scoring Layer (`src/ai/prioritizer.py`)

**Purpose**: Calculate priority scores using Eisenhower matrix principles.

**Scoring Algorithm**:
```python
Base Score (Priority Level):
- urgent: 4 points
- high: 3 points
- medium: 2 points
- low: 1 point

Deadline Urgency Bonus:
- Contains "today", "EOD", or "ASAP": +2 points
- Other deadlines: +0 points

Total Score Range: 1-6
```

**Functions**:
- `calculate_priority_score(action)`: Returns integer score (1-6)
- `sort_actions_by_priority(actions)`: Returns sorted list (highest first)

**Example Scores**:
- Urgent + today = 6 (highest)
- High + EOD = 5
- Urgent + no deadline = 4
- High + no deadline = 3
- Medium + no deadline = 2
- Low + any deadline = 1 (lowest)

### 4. UI Layer (`app/main.py`)

**Purpose**: Streamlit dashboard with 3 tabs for different workflows.

**Session State Management**:
```python
st.session_state = {
    "briefing": DailyBriefing | None,
    "mock_items": list[MockContextItem] | None,
    "draft_context": str,
    "last_load_time": datetime | None
}
```

**Tab 1: Morning Briefing**
- Display 3-bullet summary
- Show stakeholder badges (max 5 per row)
- Display total action count
- Auto-refresh on data load

**Tab 2: Action Board**
- Sort actions by priority score
- Display with expandable cards
- Show priority emoji (🔴 urgent, 🟠 high, 🟡 medium, 🟢 low)
- Include assignee, deadline, and score
- Non-functional checkboxes (PoC limitation)

**Tab 3: Draft Generator**
- Text input for context
- AI-powered draft generation
- Example contexts for quick testing
- Copy-to-clipboard functionality
- Temperature: 0.7 (more creative)

### 5. Configuration Layer (`config/settings.py`)

**Purpose**: Centralized configuration with environment variable loading.

**Settings Model**:
```python
class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    
    model_config = SettingsConfigDict(
        env_file="config/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
```

**Security**:
- API keys stored in `.env` (git-ignored)
- Pydantic validation ensures required keys exist
- No hardcoded credentials

## Data Flow Diagram (Detailed)

```
User Action: Click "Load Daily Context"
    │
    ▼
┌─────────────────────────────────────────┐
│ 1. Load Mock Data                       │
│    - Read data/mock_daily_context.json  │
│    - Validate with Pydantic             │
│    - Return 9 MockContextItem objects   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 2. Process with Claude AI               │
│    - Format items into prompt           │
│    - Call Claude 3.5 Sonnet API         │
│    - Parse JSON response                │
│    - Validate with Pydantic             │
│    - Retry on failure (max 2 attempts)  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 3. Store in Session State               │
│    - st.session_state.briefing          │
│    - st.session_state.mock_items        │
│    - st.session_state.last_load_time    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│ 4. Display in UI                        │
│    Tab 1: Show summary & stakeholders   │
│    Tab 2: Sort & display actions        │
│    Tab 3: Ready for draft generation    │
└─────────────────────────────────────────┘
```

## AI Prompt Engineering

### Morning Briefing Prompt Strategy

**Goals**:
1. Extract 3-bullet summary (concise, actionable)
2. Identify all action items with metadata
3. List all stakeholders mentioned

**Prompt Structure**:
```
[Task Description]
Analyze these work items and extract:
1. A 3-bullet summary of the day
2. All actionable items with task, assignee, deadline, priority
3. List of all stakeholders mentioned

[Schema Definition]
Return ONLY valid JSON matching this schema:
{...}

[Input Data]
Work Items:
[Formatted items]

[Constraint Reminder]
Remember: Return ONLY the JSON object, no additional text or explanation.
```

**Why This Works**:
- Clear task breakdown (1, 2, 3)
- Explicit schema with examples
- Constraint reminder prevents extra text
- Low temperature (0.2) for consistency

### Draft Generator Prompt Strategy

**Goals**:
1. Generate professional, concise replies
2. Keep under 50 words
3. Maintain professional tone

**Prompt Structure**:
```
Generate a professional, concise reply (under 50 words) for the following context:

[User Context]

Keep it professional, clear, and actionable. Return only the draft text, no explanations.
```

**Why This Works**:
- Word limit prevents verbosity
- Clear tone guidance (professional, clear, actionable)
- Higher temperature (0.7) for variety
- Simple constraint (text only)

## Session State Management

**Purpose**: Maintain state across Streamlit reruns without re-processing.

**State Variables**:
```python
{
    "briefing": DailyBriefing | None,      # Cached AI processing result
    "mock_items": list[MockContextItem],   # Cached loaded data
    "draft_context": str,                  # Current draft input
    "last_load_time": datetime | None      # Timestamp for UI display
}
```

**Benefits**:
- Avoid redundant API calls (expensive)
- Preserve user input across reruns
- Enable conditional rendering
- Track data freshness

**Initialization Pattern**:
```python
if "briefing" not in st.session_state:
    st.session_state.briefing = None
```

## Security Measures

### 1. API Key Protection
- Stored in `.env` file (git-ignored)
- Loaded via Pydantic Settings
- Never logged or displayed
- Validated at startup

### 2. Input Validation
- All data validated with Pydantic
- Type checking with Literal types
- Required fields enforced
- Invalid data rejected early

### 3. Error Handling
- API errors caught and displayed safely
- No sensitive data in error messages
- Retry logic for transient failures
- User-friendly error messages

### 4. Data Isolation
- Mock data only (no real user data)
- No database or persistence
- Session state cleared on browser close
- No data sharing between users

## Performance Considerations

### 1. API Call Optimization
- Cache results in session state
- Only process on explicit user action
- Retry logic prevents unnecessary calls
- Low temperature for faster responses

### 2. UI Responsiveness
- Spinner indicators during processing
- Async-style loading states
- Expandable sections (lazy rendering)
- Minimal re-renders

### 3. Data Loading
- Single file read (9 items)
- Pydantic validation is fast
- No database queries
- In-memory processing only

## Limitations (PoC Scope)

### Current Limitations
1. **Mock Data Only**: No real email/calendar/chat integration
2. **No Persistence**: Data cleared on browser close
3. **Single User**: No multi-user support or authentication
4. **No Database**: All data in memory
5. **Limited Error Recovery**: Basic retry logic only
6. **No Action Tracking**: Checkboxes are non-functional
7. **No Notifications**: No email/push notifications
8. **No Mobile App**: Web-only interface

### Intentional Design Choices
- Focus on core AI processing workflow
- Demonstrate value proposition quickly
- Minimize infrastructure complexity
- Enable rapid iteration and feedback

## Technology Stack

### Core Technologies
- **Python 3.11+**: Modern type hints, performance
- **Streamlit**: Rapid UI development
- **LangChain**: AI framework and abstractions
- **Anthropic Claude 3.5 Sonnet**: State-of-the-art LLM
- **Pydantic**: Data validation and settings

### Development Tools
- **uv**: Fast package management
- **pytest**: Testing framework
- **pre-commit**: Code quality automation
- **ruff**: Fast Python linter

### Why These Choices?
- **Streamlit**: Fastest path to interactive UI
- **Claude 3.5**: Best-in-class reasoning and JSON output
- **Pydantic**: Type safety and validation
- **uv**: 10-100x faster than pip
- **LangChain**: Industry-standard AI framework

## Deployment Considerations (Future)

### Production Requirements
1. **Authentication**: OAuth2 with email/calendar providers
2. **Database**: PostgreSQL for user data and history
3. **Caching**: Redis for API response caching
4. **Queue**: Celery for background processing
5. **Monitoring**: Sentry for error tracking
6. **Logging**: Structured logging with ELK stack
7. **Scaling**: Kubernetes for horizontal scaling

### API Integration (v1 Roadmap)
- Gmail API for email ingestion
- Google Calendar API for events
- Slack API for chat messages
- Microsoft Graph API for Office 365
- Real-time webhooks for instant updates

## Testing Strategy

### Current Test Coverage
- Data loading validation
- Pydantic model validation
- Priority scoring algorithm
- Action sorting logic

### Test Files
- `tests/test_basic.py`: Core functionality tests

### Running Tests
```bash
uv run pytest tests/ -v
```

## Future Enhancements

### Phase 1 (v1.0)
- Real API integrations (Gmail, Calendar, Slack)
- User authentication and profiles
- Database persistence
- Action tracking and completion

### Phase 2 (v1.5)
- Mobile app (React Native)
- Push notifications
- Team collaboration features
- Custom priority rules

### Phase 3 (v2.0)
- Multi-language support
- Advanced analytics dashboard
- AI-powered insights and trends
- Integration marketplace

---

**Made with Bob** 🤖