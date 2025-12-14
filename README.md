# Agentic Execution Coach

An AI-powered execution enforcement system that converts vague objectives into realistic weekly execution plans, continuously reconciles intent with reality, and enforces trade-offs when constraints are violated.

**Philosophy:** This is not a productivity dashboard or motivation tool. It's an execution enforcement system that reduces cognitive load by outputting only what matters next.

---

## 🚀 Quick Start

```bash
# 1. Clone and navigate to project
cd FitnessAdvisor

# 2. Create virtual environment with Python 3.11 or 3.12
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 5. Run the application
python run.py

# 6. Access the UI
# Open http://localhost:8000/static/index.html
```

**Project Structure**: See [docs/STRUCTURE.md](docs/STRUCTURE.md) for detailed architecture

---

## 🎯 Core Features

- **Realistic Planning**: AI agents convert long-term objectives into achievable weekly plans (3-5 priorities max)
- **Trade-Off Enforcement**: Explicit decisions about what to exclude and why
- **Reality Reconciliation**: Weekly check-ins compare planned vs actual execution
- **Deviation Monitoring**: Automatic detection when plans diverge from reality
- **Plan Adjustment**: Dynamic plan modification based on real-world constraints
- **Multi-LLM Support**: Switch between Azure OpenAI, OpenAI, and Google Gemini

---

## 🏗️ Architecture

### Multi-Agent System (CrewAI)

The system uses 5 specialized AI agents:

1. **Planner Agent**: Translates objectives into realistic weekly plans
2. **Execution Agent**: Converts weekly priorities into daily actions (one per day)
3. **Reviewer Agent**: Compares planned vs actual execution, calculates deviation
4. **Critic Agent**: Challenges assumptions and forces explicit trade-offs
5. **Coordinator Agent**: Orchestrates agent workflows and manages state

### Weekly Cycle

```
Sunday: Generate Plan
├─ Planner creates draft
├─ Critic challenges assumptions
├─ Planner revises
└─ Execution Agent generates daily actions

During Week: Monitor Execution
├─ User submits reality check
├─ Reviewer analyzes deviation
└─ If needed: Critic + Planner adjust plan

End of Week: Record History
└─ Store completion rate and learnings
```

### State Management

- **Persistence**: JSON files in `./data/` directory
- **State Components**:
  - User profile (objectives, constraints, non-negotiables)
  - Weekly plans (versioned with adjustments)
  - Reality checks (execution data)
  - Deviation reports (analysis)
  - Execution history (performance tracking)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- API key for one of:
  - Azure OpenAI
  - OpenAI
  - Google Gemini

### Installation

1. **Clone and setup**
```bash
cd /Users/Samir_Nejjai/Projects/FitnessAdvisor
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API credentials
```

Example `.env` configuration:
```env
# Choose provider: azure_openai, openai, or gemini
LLM_PROVIDER=azure_openai

# Azure OpenAI (if using)
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Data directory
DATA_DIR=./data
```

3. **Start the server**
```bash
python run.py
# Or use the start script
./scripts/start.sh
```

The API will be available at `http://localhost:8000`

---

## 📖 Usage

### Web UI

Access the web interface at: `http://localhost:8000/static/index.html`

**Workflow:**

1. **Setup Tab**: Create your profile
   - Define primary objective
   - Set hard constraints (available time, commitments)
   - Specify non-negotiables (rest days, minimum frequency)

2. **Weekly Plan Tab**: Generate plans
   - Click "Generate New Plan"
   - AI agents create a realistic plan with priorities, exclusions, and daily actions
   - Takes 30-60 seconds (agents are working!)

3. **Check-In Tab**: Submit reality checks
   - Report sessions completed vs planned
   - Rate energy levels
   - Document unexpected events
   - Get deviation analysis

4. **Status Tab**: View current week
   - See active plan
   - Check completion status
   - Review statistics

5. **History Tab**: Track performance
   - View past weeks
   - Analyze completion rates
   - Learn from patterns

### API Documentation

Interactive API docs available at: `http://localhost:8000/docs`

**Key Endpoints:**

```bash
# Create profile
POST /api/v1/profile
{
  "objective_description": "Improve strength over 12 weeks",
  "duration_weeks": 12,
  "available_hours_per_week": 10,
  "minimum_training_frequency": 3,
  "rest_days": ["Sunday"]
}

# Generate weekly plan
POST /api/v1/plans/generate
{
  "week_start_date": "2025-12-16"  # Optional
}

# Submit reality check
POST /api/v1/reality-checks
{
  "week_id": "2025-W50",
  "sessions_completed": 3,
  "sessions_planned": 4,
  "energy_level": "moderate",
  "unexpected_events": ["Client emergency Tuesday"]
}

# Get current status
GET /api/v1/status

# View history
GET /api/v1/history?limit=10
```

---

## 🔧 Configuration

### LLM Provider Switching

Edit `.env` to change providers:

```env
# Use Azure OpenAI
LLM_PROVIDER=azure_openai

# Use OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL_NAME=gpt-4-turbo-preview

# Use Google Gemini
LLM_PROVIDER=gemini
GOOGLE_API_KEY=...
GEMINI_MODEL_NAME=gemini-pro
```

### Agent Customization

Edit `app/services/workflows.py` to modify agent behaviors:
- Change roles, goals, and backstories
- Adjust temperature settings
- Modify verbosity levels

### Workflow Customization

Edit `app/services/workflows.py` to:
- Modify task descriptions and prompts
- Change agent collaboration patterns
- Adjust JSON parsing logic

---

## 📁 Project Structure

```
FitnessAdvisor/
├── run.py                      # Application entry point
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── app/                       # Main application package
│   ├── main.py                # FastAPI app
│   ├── api/                   # API endpoints
│   │   └── v1/
│   │       └── endpoints/     # Route handlers
│   ├── services/              # Business logic
│   │   ├── workflows.py       # AI agent workflows
│   │   ├── llm_factory.py     # Multi-LLM support
│   │   └── state_manager.py   # JSON persistence
│   ├── models/                # Pydantic schemas
│   │   └── schemas.py
│   ├── core/                  # Configuration
│   │   └── config.py
│   └── static/                # Web UI
│       ├── index.html
│       └── css/ & js/
├── data/                      # State files (auto-created)
│   └── state.json
├── scripts/                   # Utility scripts
│   └── start.sh
├── tests/                     # Test suite
└── docs/                      # Documentation
```

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

### Agent Execution Takes Too Long

- Normal: 30-60 seconds for plan generation
- Agents are doing real LLM calls and reasoning
- Check network connection to LLM provider

### JSON Parsing Errors

- Agents sometimes produce non-JSON output
- Check `workflows.py` `_parse_crew_result()` method
- May need to adjust agent prompts for stricter JSON

### Profile Not Found

- Create profile in Setup tab first
- Check `data/profile.json` exists
- Verify file permissions

### LLM API Errors

- Verify API keys in `.env`
- Check endpoint URLs (Azure requires full endpoint)
- Test with `/health` endpoint
- Review logs for specific error messages

---

## 🧪 Development

### Running Tests

```bash
pytest
```

### Code Style

The codebase follows:
- PEP 8 style guidelines
- Type hints for clarity
- Pydantic for data validation
- Clear separation of concerns

### Adding New Features

1. **New Workflow**: Edit `app/services/workflows.py`
2. **New Endpoint**: Add route to `app/api/v1/endpoints/`
3. **New Model**: Add to `app/models/schemas.py` with Pydantic validation
4. **New Service**: Add to `app/services/`

---

## 📊 Example Workflow

```python
# 1. Create profile (one-time)
profile = {
    "objective": "Run a marathon in 16 weeks",
    "duration_weeks": 16,
    "available_hours_per_week": 8,
    "minimum_training_frequency": 4,
    "rest_days": ["Sunday"]
}

# 2. Generate weekly plan (every Sunday)
plan = orchestrator.generate_weekly_plan()
# Returns: 3-5 priorities, exclusions, daily actions

# 3. Execute during week
# ... follow daily actions ...

# 4. Reality check (end of week)
reality = {
    "week_id": "2025-W50",
    "sessions_completed": 3,
    "sessions_planned": 4,
    "energy_level": "low",
    "unexpected_events": ["Work deadline on Wednesday"]
}

# 5. Get deviation analysis
report = orchestrator.process_reality_check(reality)
# Returns: completion rate, deviation summary, recommended action

# 6. Adjust if needed
if report.deviation_detected:
    adjusted_plan = orchestrator.adjust_plan(adjustment_request)
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
- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent framework
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Pydantic](https://docs.pydantic.dev/) - Data validation
- [LangChain](https://python.langchain.com/) - LLM integrations

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review API docs at `/docs`
3. Inspect logs for detailed error messages
4. Verify environment configuration

**Remember**: This system enforces execution, not inspiration. Use it to reduce planning overhead and increase follow-through.
