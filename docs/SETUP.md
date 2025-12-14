# 🚀 Quick Setup Guide

Follow these steps to get the Fitness Advisor running on your machine.

## Prerequisites

- **Python**: 3.11+ (tested with 3.12.12)
- **Azure OpenAI Account**: API key + endpoint
  - Get key: https://portal.azure.com → OpenAI → API Keys
  - Get endpoint: Azure portal → OpenAI resource → Endpoints

## Installation

### 1. Clone & Navigate
```bash
cd /path/to/FitnessAdvisor
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Azure OpenAI
```bash
# Copy template
cp .env.example .env

# Edit with your credentials
# Required:
# - AZURE_OPENAI_API_KEY
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_DEPLOYMENT_ID
# - AZURE_OPENAI_API_VERSION
```

### 5. Start Server
```bash
python run.py
```

✅ Server running at http://localhost:8000

## First Time Use

### Step 1: Open UI
```
http://localhost:8000
```
Auto-redirects to `/static/index.html`

### Step 2: Setup Tab
Create your profile:
- **Objective**: What do you want to achieve? (e.g., "Lose 6kg in 16 weeks")
- **Available Time**: Hours per week you can dedicate
- **Hard Constraints**: Fixed commitments (work schedule, family time)
- **Non-Negotiables**: Things that can't be cut (e.g., sleep, specific activities)

Click "💾 Save Profile" → Will see success message

### Step 3: Plan Tab
Generate your first weekly plan:
1. Click "🤖 Generate New Plan"
2. **Wait 3-5 seconds** (Azure OpenAI generating plan)
3. See priorities, daily actions, trade-offs

Example output:
```
WEEK 1: Build Foundation
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PRIORITIES:
1. Full-body lifting 3x/week (3 hours)
2. Nutrition tracking + meal prep (2 hours)

EXCLUDED (why):
- Cardio: Conflicts with strength focus
- Mobility work: Can add later once consistent

DAILY ACTIONS:
Mon: Full-body lifting (60 min) - Step-by-step breakdown...
Tue: Meal prep Sunday dinner (30 min) - Detailed guide...
Wed: Full-body lifting (60 min)...
```

### Step 4: Execute & Check-In Tab
During the week:
1. Check the "Weekly Plan" or "Plan" tab to see today's action
2. Do the action (or don't - that's why we check-in!)
3. At end of week, go to "Check-In" tab
4. For each day:
   - ✅ Check the box if you completed it
   - 📝 Describe what you **actually** did (textarea)
5. Click "🔄 Analyze & Adapt Remaining Days"

System will:
- Calculate completion rate
- Show you deviations
- Adapt remaining days if < 70% completion
- Save adapted plan

### Step 5: View Execution History
"Status" tab shows all weeks and completion rates.

## Troubleshooting

### "Cannot connect to Azure OpenAI"
**Check**:
```bash
# 1. .env file exists with correct keys
cat .env

# 2. API key is valid (go to Azure Portal)

# 3. Endpoint format: https://XXX.openai.azure.com/ (with trailing slash)

# 4. Deployment ID matches your model deployment name
```

### "ModuleNotFoundError: No module named 'fastapi'"
```bash
# Activate venv and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

### "Profile not loading"
1. Refresh page (Ctrl+Shift+R or Cmd+Shift+R)
2. Check browser console (F12 → Console) for errors
3. Verify profile was saved (Setup tab → you should see your values)

### "Port 8000 already in use"
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python -c "
import uvicorn
uvicorn.run('app.main:app', host='0.0.0.0', port=8001)
"
```

### "Plan takes >10 seconds to generate"
- **Normal**: 3-5s average (Azure latency varies)
- **Check**: Azure OpenAI quota/rate limits
- **Check**: Internet connection
- **Watch**: Browser console (F12 → Network tab) to see request status

## Configuration Reference

### .env Template
```env
# Required - Get from Azure Portal
AZURE_OPENAI_API_KEY=your-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_ID=gpt-4-turbo  # or whatever you deployed
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Optional
PORT=8000
CORS_ORIGINS=http://localhost:8000
LOG_LEVEL=INFO
```

### Data Storage
- **Location**: `data/state.json`
- **Contains**: Profiles, plans, reality checks, history
- **Backup**: Copy this file to backup everything
- **Reset**: Delete this file to start fresh

## Development

### Auto-reload during coding
```bash
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug
```

### Check for Python errors
```bash
python -m py_compile app/**/*.py
```

### View API docs
- Swagger: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Quick Reference

| URL | Purpose |
|-----|---------|
| http://localhost:8000/ | Main UI |
| http://localhost:8000/api/v1/health | Server status |
| http://localhost:8000/docs | API documentation |
| http://localhost:8000/redoc | Alternate API docs |

---

**Pro tip**: This is an execution coach, not a motivator. Realistic plans + honest check-ins = sustainable progress. Start small, build the habit.
