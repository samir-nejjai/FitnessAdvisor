# Project Structure

This project follows best practices for FastAPI applications with a clean, modular architecture.

## Directory Structure

```
FitnessAdvisor/
├── app/                        # Main application
│   ├── __init__.py
│   ├── main.py                 # FastAPI app & static files
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # Settings & environment
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py     # Router registration
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── health.py   # GET /health
│   │           ├── profile.py  # POST/GET /profile
│   │           ├── plans.py    # Plans CRUD + generation
│   │           └── reality_checks.py  # Check-ins & history
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic data models
│   ├── services/               # Business logic
│   │   ├── __init__.py
│   │   ├── llm.py              # LLM provider (Azure OpenAI)
│   │   ├── state_manager.py    # State.json I/O
│   │   └── workflows.py        # Plan generation & adaptation
│   └── static/                 # Frontend
│       ├── index.html          # Single-page app
│       ├── css/
│       │   └── styles.css      # All styling
│       └── js/
│           └── app.js          # Vanilla JS (710 lines)
├── data/                       # Runtime storage
│   └── state.json              # Single source of truth
├── docs/                       # Documentation
│   ├── PROJECT_SUMMARY.md      # Overview
│   ├── STRUCTURE.md            # This file
│   ├── SETUP.md                # Installation guide
│   └── CHECKLIST.md            # Feature checklist
├── run.py                      # Entry point
├── requirements.txt            # pip dependencies
├── .env.example                # Environment template
└── .gitignore
```

## Architecture

### Simplified Design (23% code reduction)
```
User Input (HTML)
    ↓
[app.js - Vanilla JS]
    ↓
[FastAPI Routes]
    ↓
[Workflows Service] → [Azure OpenAI] → Structured JSON output
    ↓
[State Manager] → [data/state.json]
    ↓
Response back to UI
```

### Key Components

| Component | Purpose | LOC |
|-----------|---------|-----|
| **app.js** | Frontend state & API calls | 710 |
| **workflows.py** | Plan generation, adaptation, prompts | 502 |
| **state_manager.py** | JSON file I/O, atomic writes | 89 |
| **endpoints/** | HTTP request handlers | 122 |
| **schemas.py** | Pydantic validation | 186 |
| **llm.py** | Azure OpenAI initialization | 45 |
| **styles.css** | All UI styling | 808 |
| **index.html** | HTML structure | 306 |
| **main.py** | FastAPI setup, static files | 52 |
| **TOTAL** | | ~3,220 |

### No CrewAI
- ✅ Removed 5-agent orchestration system
- ✅ Removed multi-provider LLM abstraction
- ✅ Removed dependency injection frameworks
- ✅ Direct LLM calls from `workflows.py`
- ✅ Single Azure OpenAI provider only

### Single State File
- ✅ All data in `data/state.json`
- ✅ Atomic file writes (read-modify-write)
- ✅ No SQL, no migrations, no schema versioning
- ✅ Easy to backup, inspect, reset

## Running the Application

### Start Server
```bash
python run.py
# or
uvicorn app.main:app --reload --port 8000
```

### Access Points
- **Web UI**: http://localhost:8000/static/index.html (auto-redirects from /)
- **API Swagger**: http://localhost:8000/docs
- **Health**: http://localhost:8000/api/v1/health

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/profile` | Create/update profile |
| GET | `/api/v1/profile` | Get current profile |
| POST | `/api/v1/plans/generate` | Generate weekly plan |
| GET | `/api/v1/plans/latest` | Get current week plan |
| GET | `/api/v1/plans/{week_id}` | Get specific week |
| GET | `/api/v1/plans` | Get all plans |
| POST | `/api/v1/plans/adjust` | Adapt remaining days |
| POST | `/api/v1/reality-checks` | Submit check-in |
| GET | `/api/v1/reality-checks/{week_id}` | Get analysis |
| GET | `/api/v1/reality-checks/history` | All weeks |

## Key Files Explained

### [app/main.py](app/main.py)
- FastAPI app initialization
- Static file routing (index.html, CSS, JS)
- CORS configuration
- Health check endpoint

### [app/services/workflows.py](app/services/workflows.py)
- `generate_weekly_plan()`: Calls Azure OpenAI to create 3-4 priority weekly plan
- `process_reality_check()`: Analyzes actual vs planned execution
- `adjust_plan()`: Adapts remaining days based on what was actually completed
- Prompts are detailed and explicit (not agent-based)

### [app/services/state_manager.py](app/services/state_manager.py)
- `load_state()`: Read from state.json
- `save_state()`: Atomic write (read→modify→write)
- Single file = single source of truth
- All profile, plans, history in one place

### [app/services/llm.py](app/services/llm.py)
- Initializes Azure OpenAI client
- Single provider only (no switching)
- Uses environment variables for auth

### [app/static/js/app.js](app/static/js/app.js)
- `loadProfile()`: Fetch profile, populate form
- `handleFormSubmit()`: POST profile update
- `handlePlanGenerate()`: POST generate plan (shows loading...)
- `loadWeekProgressForCheckin()`: Auto-detect current day
- `handleCheckinSubmit()`: POST reality check with actual_notes
- `displayAdaptedPlan()`: Show adapted plan if completion < 70%

### [app/models/schemas.py](app/models/schemas.py)
All data models with validation:
- `UserProfile`: objective, hard_constraints, non_negotiables
- `WeeklyPlan`: priorities, excluded, daily_actions
- `DailyAction`: day, action, time_minutes, detailed_plan, actual_notes
- `RealityCheck`: week_id, sessions_completed, actual_notes per day
