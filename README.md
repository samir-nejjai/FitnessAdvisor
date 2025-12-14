# Fitness Advisor

An AI-powered execution coach that creates realistic weekly fitness plans and adapts them based on what you actually do. No multi-agent complexity—just direct Azure OpenAI calls that generate honest, achievable plans.

**Philosophy:** No motivation speeches. No over-engineering. Just realistic plans that adapt to your reality.

**Key Learning:** Started with 5 AI agents (CrewAI), realized it was over-engineering. Simplified to direct LLM prompts → 23% code reduction, same results, faster execution.

---

## 🚀 Quick Start

```bash
# 1. Setup environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure Azure OpenAI
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# 3. Run
python run.py

# 4. Open browser
http://localhost:8000
```

**Documentation**: See [docs/](docs/) for setup guides and architecture details

---

## 🎯 Core Features

- **Realistic Planning**: Azure OpenAI generates achievable weekly plans (3-4 priorities max)
- **Trade-Off Enforcement**: Explicit decisions about what to exclude and why
- **Reality Check-In**: Daily checkboxes + free-text notes to track actual execution
- **Adaptive Plans**: Auto-adjusts remaining days when completion < 70%
- **Plan Persistence**: Auto-saves to state.json, persists across page refreshes
- **One Action Per Day**: Reduces cognitive load, increases follow-through

---

## 🏗️ Architecture

### Simplified Design

**Tech Stack:**
- Python 3.12 + FastAPI
- Azure OpenAI (GPT-4 Turbo)
- Single `state.json` file
- Vanilla HTML/CSS/JavaScript

**Flow:**
```
User Input → FastAPI → Direct LLM Prompt → Azure OpenAI → JSON Response → state.json
```

### Weekly Cycle

```
1. Generate Plan (3-5s)
   └─ LLM creates realistic plan with priorities & daily actions

2. Execute During Week
   └─ Follow daily actions

3. Reality Check-In
   ├─ Check boxes for completed days
   ├─ Write actual notes (what you really did)
   └─ Submit for analysis

4. Adapt if Needed (< 70% completion)
   └─ LLM adjusts remaining days based on actual execution
```

### State Management

- **Single File**: `data/state.json`
- **Contains**: Profile, all plans, reality checks, history
- **Atomic Writes**: Read → Modify → Write
- **No SQL**: Simple, easy to backup/inspect

---

## � Prerequisites

- Python 3.11+ (tested with 3.12.12)
- Azure OpenAI account with API key
- 5 minutes for setup

### Installation

```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure Azure OpenAI
cp .env.example .env
# Edit .env with:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_DEPLOYMENT_ID
# - AZURE_OPENAI_API_VERSION

# 3. Run
python run.py
```

Server runs at `http://localhost:8000`

---

## 📖 Usage

### Web UI

Access at: `http://localhost:8000` (auto-redirects to UI)

**Workflow:**

1. **Setup Tab**: Create profile
   - Objective (e.g., "Lose 6kg in 16 weeks")
   - Available hours/week
   - Hard constraints (work schedule, etc.)
   - Click "💾 Save Profile"

2. **Plan Tab**: Generate weekly plan
   - Click "🤖 Generate New Plan"
   - Wait 3-5 seconds (Azure OpenAI generating)
   - See priorities, daily actions, trade-offs

3. **Check-In Tab**: Track execution
   - Daily checkboxes (auto-detects current day)
   - Free-text notes: "What did you actually do?"
   - Click "🔄 Analyze & Adapt"
   - Get adjusted plan if < 70% completion

4. **Status Tab**: View current week
   - Active plan with daily cards
   - Click day to see detailed breakdown

5. **History Tab**: Past weeks
   - All plans + completion rates
   - Execution patterns

### API Documentation

Interactive docs: `http://localhost:8000/docs`

**Key Endpoints:**

```bash
# Create/update profile
POST /api/v1/profile
{
  "objective": {
    "description": "Lose 6kg without cardio",
    "duration_weeks": 16
  },
  "hard_constraints": {
    "available_hours_per_week": 6,
    "fixed_commitments": ["Work 9-5 Mon-Fri"]
  }
}

# Generate plan
POST /api/v1/plans/generate

# Get latest plan
GET /api/v1/plans/latest

# Submit reality check
POST /api/v1/reality-checks
{
  "week_id": "2025-W50",
  "sessions_completed": 2,
  "energy_level": "moderate",
  "notes": "Completed Mon & Wed, missed Fri"
}

# Adjust plan
POST /api/v1/plans/adjust
{
  "week_id": "2025-W50",
  "reason": "Low completion rate"
}
```

---

## 🔧 Configuration

### Azure OpenAI Setup

Edit `.env` with your Azure credentials:

```env
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_ID=gpt-4-turbo
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### Prompt Customization

Edit `app/services/workflows.py` to modify:
- `_build_plan_prompt()`: How plans are generated
- `_build_reality_check_prompt()`: How execution is analyzed
- `_build_adjustment_prompt()`: How plans adapt

### Data Storage

- Location: `data/state.json`
- Backup: Copy this file
- Reset: Delete this file

---

## 📁 Project Structure

```
FitnessAdvisor/
├── run.py                     # Entry point
├── requirements.txt           # Dependencies
├── .env.example              # Azure OpenAI template
├── app/
│   ├── main.py               # FastAPI app
│   ├── api/v1/endpoints/     # REST routes
│   │   ├── health.py
│   │   ├── profile.py
│   │   ├── plans.py
│   │   └── reality_checks.py
│   ├── services/
│   │   ├── workflows.py      # Plan generation (502 LOC)
│   │   ├── llm.py           # Azure OpenAI client
│   │   └── state_manager.py  # state.json I/O
│   ├── models/schemas.py     # Pydantic models
│   ├── core/config.py        # Settings
│   └── static/               # Frontend
│       ├── index.html        # Single-page app
│       ├── js/app.js        # Vanilla JS (710 LOC)
│       └── css/styles.css   # All styling
├── data/
│   └── state.json           # Single source of truth
└── docs/                     # Full documentation
    ├── PROJECT_SUMMARY.md
    ├── STRUCTURE.md
    ├── SETUP.md
    └── CHECKLIST.md
```

**Total**: ~3,220 lines of code (23% smaller than original multi-agent version)

---

## 🎓 Design Principles

### What This System Does

- ✅ Enforces realistic planning through AI critique
- ✅ Forces explicit trade-offs between priorities
- ✅ Monitors deviation from plans objectively
- ✅ Adjusts plans based on actual constraints
- ✅ Reduces cognitive load (one action per day)
- ✅ Tracks historical performance patterns

### What This System Does NOT Do

- ❌ Provide emotional motivation or encouragement
- ❌ Optimize routines scientifically
- ❌ Replace personal discipline
- ❌ Make decisions for you
- ❌ Generate endless task lists

### Success Criteria

The system succeeds when:
- Weekly replanning frequency decreases
- Scope decreases but completion rate increases
- User spends less time thinking, more time executing
- Plans become more realistic over time

---

## 🔍 Troubleshooting

### "Cannot connect to Azure OpenAI"

```bash
# Check .env configuration
cat .env | grep AZURE

# Verify:
# 1. API key is valid (Azure Portal)
# 2. Endpoint ends with /
# 3. Deployment ID matches deployment name
```

### Profile Not Loading

- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Check browser console (F12) for errors
- Verify `/api/v1/profile` returns 200

### Plan Generation Slow (>10s)

- Normal: 3-5 seconds
- Check internet connection
- Verify Azure OpenAI quota limits

### Port 8000 In Use

```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>
```

### General Debugging

- Check `/api/v1/health` endpoint
- Review terminal logs
- Inspect `data/state.json` file

---

## 🧪 Development

### Code Quality

- Type hints throughout
- Pydantic validation
- Modular FastAPI endpoints
- Single responsibility principle

### Adding Features

1. **New Prompt**: Edit `app/services/workflows.py`
2. **New Route**: Add to `app/api/v1/endpoints/`
3. **New Field**: Update `app/models/schemas.py`
4. **Frontend**: Edit `app/static/js/app.js`

### Run with Debug

```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

---

## 📊 Example: Weekly Flow

**Sunday**: Generate Plan
```bash
curl -X POST http://localhost:8000/api/v1/plans/generate
# → Returns plan with 3-4 priorities, daily actions
# → Saves to data/state.json
```

**During Week**: Execute
- Mon: Full-body lifting (60 min)
- Tue: Meal prep (30 min)
- Wed: Full-body lifting (60 min)
- Thu: Rest
- Fri: Full-body lifting (60 min)
- Sat: Active recovery walk (20 min)
- Sun: Rest

**End of Week**: Reality Check
```bash
curl -X POST http://localhost:8000/api/v1/reality-checks \
  -d '{
    "week_id": "2025-W50",
    "sessions_completed": 2,
    "notes": "Completed Mon/Wed, missed Fri (work deadline)"
  }'
# → Analyzes deviation (2/3 = 67% < 70%)
# → Triggers plan adjustment for next week
```

---

## 🤝 Contributing

This is a reference implementation. Feel free to:
- Fork and customize for your needs
- Adjust agent personalities
- Add new LLM providers
- Enhance the UI
- Improve JSON parsing robustness

---

## 📄 License

MIT License - Use freely, modify as needed

---

## 🙏 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service) - LLM provider

**Note**: Originally built with CrewAI multi-agent system, but simplified to direct LLM prompts after realizing agents were over-engineering for this use case. Result: 23% code reduction, same functionality, faster execution.

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review API docs at `/docs`
3. Inspect logs for detailed error messages
4. Verify environment configuration

**Philosophy**: Execution enforcement, not motivation. Realistic plans that adapt to reality, not endless task lists.

**Key Insight**: Sometimes the best architecture is the simplest one that works. Multi-agent systems are powerful, but often unnecessary. Direct LLM prompts can be just as effective with less complexity.
