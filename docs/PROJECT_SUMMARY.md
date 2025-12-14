# 📦 Project Summary: Agentic Execution Coach

## Overview

An AI-powered execution coaching system built with FastAPI and Azure OpenAI. The system creates realistic weekly fitness plans and enforces consistency through adaptive reality check-ins that adjust plans based on actual execution.

**Philosophy**: No motivation speeches. Just realistic plans that adapt to your reality.

## 🎯 Core Features

### 1. **Smart Plan Generation**
- Analyzes user constraints (work schedule, energy levels, time availability)
- Creates brutally honest 3-4 priority plans (not 5-10 unrealistic ones)
- Builds in 50% buffer time for disruptions
- Generates detailed daily breakdowns with step-by-step guidance
- Learns from past completion rates

### 2. **Reality Check-In System**
- Auto-detects current day of the week
- Shows daily checkboxes for past/current/future days
- Free-text fields for users to describe what they actually did
- Collects energy levels and unexpected events
- Analyzes actual vs planned execution

### 3. **Adaptive Plan Adjustment**
- Detects significant deviations (< 70% completion or major disruptions)
- Generates adapted plans for remaining days
- Preserves completed past actions
- Adjusts remaining days based on actual performance
- Provides honest rationale for changes

### 4. **Plan Persistence**
- Auto-saves plans to single state.json file
- Persists across page refreshes
- Shows "Generate New Plan" option when plan exists
- Retrieves latest plan on app load

## 🏗️ Architecture

### Technology Stack

- **Backend**: Python 3.12 with FastAPI
- **AI/LLM**: Azure OpenAI (GPT-3.5-turbo)
- **Persistence**: Single JSON file state management
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Data Validation**: Pydantic v2

### Component Overview

```
┌─────────────────────────────────────────────────────────┐
│                      Web UI (Browser)                    │
│            Vanilla HTML/CSS/JavaScript                   │
│     • Profile Setup  • Weekly Plan  • Reality Check-In   │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP REST (relative URLs)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Backend                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│  │ Profile  │  │  Weekly  │  │   Reality    │          │
│  │   API    │  │ Plan API │  │  Check API   │          │
│  └──────────┘  └──────────┘  └──────────────┘          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Workflow Orchestrator                       │
│         (Single LLM prompt-based workflows)              │
│  • generate_weekly_plan()                               │
│  • process_reality_check()                              │
│  • adjust_plan()                                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  Azure OpenAI (GPT-3.5)                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              State Manager (JSON File)                   │
│    data/state.json (single source of truth)             │
│  • profile, plans[], history[], deviation_reports[]     │
└─────────────────────────────────────────────────────────┘
```

## 📁 File Structure

```
FitnessAdvisor/
├── run.py                      # Application entry point
├── requirements.txt            # Production dependencies
├── .env.example               # Environment variable template
├── .gitignore                 # Git ignore rules
├── data/
│   └── state.json             # Single state file (auto-created)
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI application
│   ├── api/                   # API layer
│   │   ├── __init__.py
│   │   ├── deps.py            # Dependency injection
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── profile.py      # Create/get profile
│   │           ├── plans.py        # Generate/adjust/get plans
│   │           ├── reality_checks.py   # Reality check-ins
│   │           ├── status.py       # Status dashboard
│   │           └── health.py       # Health check
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py          # Settings management
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py         # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_factory.py     # Azure OpenAI setup
│   │   ├── state_manager.py   # JSON persistence
│   │   └── workflows.py       # LLM prompt workflows
│   └── static/
│       ├── index.html         # Main UI
│       ├── css/styles.css     # Styling
│       └── js/app.js          # Frontend logic
├── docs/
│   ├── STRUCTURE.md           # Project structure
│   ├── SETUP.md              # Setup guide
│   ├── PROJECT_SUMMARY.md    # This file
│   └── CHECKLIST.md          # Feature checklist
└── README.md                  # Quick start
```

## 🔄 Application Flow

### 1. User Creates Profile
1. User enters objective (e.g., "Move from 78kg to 72kg without cardio")
2. Provides constraints (work schedule, energy levels, fixed commitments)
3. System saves to `data/state.json`

### 2. Generate Weekly Plan
1. System analyzes profile + past execution history
2. Azure OpenAI generates "brutally honest" plan
3. Includes 3-4 priorities max, detailed daily actions, trade-off rationale
4. Plan persists in `data/state.json`
5. Frontend auto-loads plan on page refresh

### 3. Execute & Check-In
1. User navigates to "Reality Check-In" tab
2. System auto-detects current day of week
3. Shows checkboxes for past/current/future days
4. User marks completed actions and describes what actually happened
5. Provides energy level and unexpected events

### 4. Analyze & Adapt
1. System calculates completion rate
2. LLM analyzes deviation using actual execution notes
3. If completion < 70% or major deviation detected:
   - Generates adapted plan for remaining days
   - Shows why changes were made
   - Preserves completed past actions
4. Plan is updated and persists

## 📊 Data Models

### UserProfile
```python
{
  "objective": {
    "description": "Move from 78kg to 72kg without cardio",
    "duration_weeks": 16
  },
  "hard_constraints": {
    "available_hours_per_week": 6.0,
    "fixed_commitments": ["Work meetings", "Limited evening availability"],
    "physical_constraints": ["None"]
  },
  "non_negotiables": {
    "minimum_training_frequency": 3,
    "rest_days": ["No mandatory rest day"]
  }
}
```

### WeeklyPlan
```python
{
  "week_id": "2025-W51",
  "start_date": "2025-12-15",
  "priorities": ["3-4 max"],
  "excluded": ["What was cut and why"],
  "daily_actions": [
    {
      "day": "Mon",
      "action": "Full-body weight lifting",
      "time_estimate_minutes": 60,
      "detailed_plan": "Step-by-step breakdown",
      "completed": false,
      "actual_notes": "What user actually did"
    }
  ],
  "trade_off_rationale": "Why we cut scope"
}
```

### RealityCheck
```python
{
  "week_id": "2025-W51",
  "sessions_completed": 2,
  "sessions_planned": 3,
  "energy_level": "moderate",
  "unexpected_events": ["Work deadline", "Sick Wednesday"],
  "notes": "Detailed execution notes from user"
}
```

## 🎯 Design Principles

### Philosophy
- **Enforcement over Motivation**: Forces realistic planning
- **Explicit Trade-offs**: Nothing gets ignored
- **One Action Per Day**: Reduces cognitive load
- **Continuous Reconciliation**: Reality vs intent

### Code Quality
- ✅ Type hints throughout
- ✅ Pydantic validation
- ✅ Separation of concerns
- ✅ Clean architecture patterns
- ✅ Error handling
- ✅ Logging support

### Best Practices Applied
- Single Responsibility Principle (agents, managers)
- Dependency Injection (LLM, state manager)
- Factory Pattern (agents, LLM)
- Repository Pattern (state manager)
- Immutable plans (versioning for changes)
- Structured outputs (JSON schemas)

## 🚀 Usage Patterns

### Web UI Flow
1. **Setup** → Configure profile (objective, constraints)
2. **Plan** → Generate weekly plan with daily actions
3. **Check-In** → Track execution with daily checkboxes
4. **Notes** → Document what you actually did vs plan
5. **Adapt** → Get adjusted plan if completion < 70%

### REST API
```bash
# Create/update profile
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{
    "objective": {"description": "Lose 6kg in 16 weeks"},
    "hard_constraints": {"available_hours_per_week": 6}
  }'

# Generate weekly plan
curl -X POST http://localhost:8000/api/v1/plans/generate

# Get latest plan
curl -X GET http://localhost:8000/api/v1/plans/latest

# Submit reality check
curl -X POST http://localhost:8000/api/v1/reality-checks \
  -d '{
    "week_id": "2025-W50",
    "sessions_completed": 2,
    "notes": "Completed Mon and Wed, missed Fri due to work"
  }'

# Get deviation analysis
curl -X GET http://localhost:8000/api/v1/reality-checks/2025-W50
```

## ⚙️ Configuration

### Environment Variables
```env
# Azure OpenAI (Required)
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_ID=gpt-4-turbo
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Server
PORT=8000
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Data
DATA_DIR=./data
LOG_LEVEL=INFO
```

### Runtime Settings
Update in [app/config.py](app/config.py):
- `DATA_DIR`: Where to store state.json
- `CORS_ORIGINS`: Allowed origins
- `LOG_LEVEL`: DEBUG|INFO|WARNING|ERROR

## 🚀 Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Create profile | <1s | Validates input |
| Generate plan | 3-5s | Azure OpenAI latency |
| Reality check | <1s | Local processing |
| Adjust plan | 3-5s | If deviation > 30% |
| Page load | <100ms | From state.json |

### Resource Usage
- **Memory**: ~40MB (Python process)
- **Storage**: ~2KB per week (state.json)
- **Network**: Only to Azure OpenAI

## 🧪 Testing

Quick validation:
```bash
# Check Azure OpenAI connection
python -c "from app.services.llm import create_llm; create_llm()"

# Test API endpoint
curl -X GET http://localhost:8000/api/v1/health

# Run with debug logging
LOG_LEVEL=DEBUG uvicorn app.main:app
```

## 🔐 Security

- ✅ API keys in `.env` (git-ignored)
- ⚠️ No authentication (add before deploying)
- ✅ Input validation via Pydantic
- ✅ CORS configured for local dev
- ℹ️ Single-user only (file-based state)

## 📝 Future Enhancements

### Phase 2
- User authentication
- Multi-user support with SQLite
- Email notifications on plan updates
- CSV export of execution history

### Phase 3
- Mobile app (React Native)
- Calendar integration
- Slack/Discord notifications
- Advanced analytics dashboard

### Phase 4
- PostgreSQL for scale
- Redis caching
- Docker containerization
- Multi-region deployment

## 🤝 Contributing

### Development Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Code Quality
```bash
# Format
python -m black .

# Type check
python -m mypy app/

# Lint
python -m pylint app/
```

---

**Built with ❤️ for consistent execution, not motivation.**
