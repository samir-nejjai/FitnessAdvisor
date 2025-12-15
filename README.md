# Fitness Advisor

An AI-powered execution coach that creates realistic weekly fitness plans and adapts based on what you actually do. Uses direct Azure OpenAI calls without multi-agent complexity.

**Philosophy:** No motivation speeches. Just realistic plans that adapt to reality.

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

See [docs/](docs/) for detailed guides.

---

## 🎯 Features

- **Realistic Planning**: Achievable weekly plans (3-4 priorities max)
- **Trade-Off Enforcement**: Explicit decisions about what to exclude
- **Reality Check-In**: Daily tracking with checkboxes and notes
- **Adaptive Plans**: Auto-adjusts when completion < 70%
- **One Action Per Day**: Reduces cognitive load

---

## 🏗️ Architecture

**Tech Stack:**
- Python 3.12 + FastAPI
- Azure OpenAI (GPT-4 Turbo)
- Single `state.json` file
- Vanilla HTML/CSS/JavaScript

**Weekly Cycle:**
1. Generate Plan (3-5s)
2. Execute daily actions
3. Reality Check-In (track completion + notes)
4. Auto-adjust if < 70% completion

**State:** Single `data/state.json` file contains all data

---

## Installation

**Requirements:** Python 3.11+, Azure OpenAI account

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with Azure OpenAI credentials

# Run
python run.py
```

Access at `http://localhost:8000`

---

## 📖 Usage

**Web UI Workflow:**

1. **Setup**: Create profile with objective, available hours, and constraints
2. **Plan**: Generate weekly plan (3-5s)
3. **Check-In**: Track daily completion with notes
4. **Status**: View current week and history

**API Documentation:** `http://localhost:8000/docs`

**Key Endpoints:**
```bash
POST /api/v1/profile          # Create/update profile
POST /api/v1/plans/generate   # Generate plan
GET  /api/v1/plans/latest     # Get latest plan
POST /api/v1/reality-checks   # Submit check-in
POST /api/v1/plans/adjust     # Adjust plan
```

---

## 🔧 Configuration

**Prompts:** Edit `app/services/workflows.py` to customize plan generation, analysis, and adjustment logic

**Data:** All state stored in `data/state.json`

---

## 📁 Project Structure

```
FitnessAdvisor/
├── run.py                  # Entry point
├── app/
│   ├── main.py            # FastAPI app
│   ├── api/v1/endpoints/  # REST routes
│   ├── services/          # Plan generation, LLM client, state I/O
│   ├── models/schemas.py  # Pydantic models
│   └── static/            # HTML/CSS/JavaScript frontend
├── data/state.json        # State storage
└── docs/                  # Documentation
```

---

## 🎓 Design Principles

**Does:**
- ✅ Enforce realistic planning through AI critique
- ✅ Force explicit trade-offs
- ✅ Monitor and adapt based on actual execution
- ✅ Reduce cognitive load

**Does Not:**
- ❌ Provide motivation or encouragement
- ❌ Optimize routines scientifically
- ❌ Replace personal discipline
- ❌ Generate endless task lists

**Success:** When scope decreases but completion increases over time.

---

## 🔍 Troubleshooting

**Azure OpenAI Connection:**
- Verify `.env` credentials
- Check API key validity
- Ensure endpoint ends with `/`

**General Issues:**
- Check `/api/v1/health` endpoint
- Review terminal logs
- Inspect `data/state.json`
- Hard refresh browser (Cmd+Shift+R)

**Port 8000 in use:**
```bash
lsof -i :8000
kill -9 <PID>
```

---

## 🧪 Development

**Adding Features:**
1. New prompts: Edit `app/services/workflows.py`
2. New routes: Add to `app/api/v1/endpoints/`
3. New fields: Update `app/models/schemas.py`
4. Frontend: Edit `app/static/js/app.js`

**Debug mode:**
```bash
LOG_LEVEL=DEBUG uvicorn app.main:app --reload
```

---

## 📄 License

MIT License

---

**Built with:** [FastAPI](https://fastapi.tiangolo.com/), [Pydantic](https://docs.pydantic.dev/), [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-services/openai-service)