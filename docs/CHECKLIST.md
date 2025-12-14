# ✅ Setup & Launch Checklist

Quick validation to ensure Fitness Advisor is ready to use.

## Pre-Launch (5 min)

### System Check
- [ ] Python 3.11+ installed: `python3 --version`
- [ ] Azure OpenAI API key obtained
- [ ] Project directory: `cd ~/Projects/FitnessAdvisor`

### Environment Setup
- [ ] Copy template: `cp .env.example .env`
- [ ] Edit `.env` with Azure credentials:
  - [ ] `AZURE_OPENAI_API_KEY=...`
  - [ ] `AZURE_OPENAI_ENDPOINT=https://...`
  - [ ] `AZURE_OPENAI_DEPLOYMENT_ID=...`
  - [ ] `AZURE_OPENAI_API_VERSION=...`

### Dependencies (2 min)
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
- [ ] No errors during install
- [ ] Virtual environment activated

### Launch Server (1 min)
```bash
python run.py
```
- [ ] Server started
- [ ] "Application startup complete" in logs
- [ ] Running on http://localhost:8000

### Health Check (1 min)
Visit http://localhost:8000/api/v1/health in browser:
- [ ] Response shows `"status": "healthy"`
- [ ] Shows `"llm_configured": true`
- [ ] All timestamps present

## First Use (15 min)

### 1. Open UI
- [ ] Navigate to http://localhost:8000
- [ ] Page auto-redirects to static UI
- [ ] All 5 tabs visible (Setup, Plan, Check-In, Status, History)

### 2. Create Profile (Setup Tab)
Fill in your information:
- [ ] **Objective**: What's your goal? (e.g., "Lose 6kg in 16 weeks")
- [ ] **Duration**: How many weeks? (e.g., 16)
- [ ] **Available Hours/Week**: Be realistic (e.g., 6)
- [ ] **Hard Constraints**: Fixed commitments (work schedule, etc.)
- [ ] Click "💾 Save Profile"
- [ ] See success message: "✅ Profile saved successfully!"

### 3. Generate First Plan (Plan Tab)
- [ ] Click "🤖 Generate New Plan"
- [ ] **Wait 3-5 seconds** (Azure OpenAI generating)
- [ ] Plan appears with:
  - [ ] Week ID (e.g., "2025-W51")
  - [ ] Priorities (3-4 max)
  - [ ] Daily actions with time estimates
  - [ ] What was excluded and why
  - [ ] Trade-off rationale

### 4. Review Daily Actions
- [ ] Check each day's action is realistic
- [ ] Time estimate is reasonable
- [ ] Understanding trade-offs made

### 5. Execute During Week
- [ ] Follow the daily actions
- [ ] Document what you actually do (don't just estimate!)

### 6. Submit Check-In (Check-In Tab)
At end of week:
- [ ] Check boxes for completed days
- [ ] For each day, write actual notes in textarea:
  - What did you actually do?
  - How did you feel?
  - Any obstacles?
- [ ] Click "🔄 Analyze & Adapt Remaining Days"
- [ ] See deviation analysis
- [ ] If < 70% completion, get adapted plan

### 7. Check Execution History (Status Tab)
- [ ] View all weeks completed
- [ ] See completion rates
- [ ] Notice patterns

## Troubleshooting

### "Cannot connect to Azure OpenAI"
```bash
# Check credentials
cat .env | grep AZURE

# Verify endpoint format (should end with /)
# Verify key works: https://portal.azure.com
```
- [ ] API key is valid
- [ ] Endpoint has trailing slash
- [ ] Deployment ID matches deployment name

### "Profile not loading in Setup tab"
```bash
# Try hard refresh
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

# Check browser console (F12)
# Look for errors in Network tab
```
- [ ] Browser cache cleared
- [ ] Console shows no errors
- [ ] Network shows successful GET /api/v1/profile

### "Plan generation taking >10 seconds"
- [ ] Check internet connection
- [ ] Check Azure portal for quota limits
- [ ] Normal: 3-5 seconds average

### "Port 8000 already in use"
```bash
# Find process
lsof -i :8000

# Kill it
kill -9 <PID>
```
- [ ] Port freed up
- [ ] Server restarted

### "JavaScript errors in browser"
```bash
# Full page refresh
Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```
- [ ] Try incognito/private window
- [ ] Check all static files loaded (F12 → Network)

## Success Checklist

You're ready when all ✅:
- [ ] ✅ Server running without errors
- [ ] ✅ Health endpoint returns healthy status
- [ ] ✅ Web UI loads (all tabs visible)
- [ ] ✅ Profile created and saved
- [ ] ✅ First plan generated (< 10 seconds)
- [ ] ✅ Daily actions visible
- [ ] ✅ Can submit check-in

## Next Steps

1. **Week 1**: Execute the plan as written
2. **End of Week 1**: Submit reality check with actual notes
3. **Week 2**: Generate new plan (system adapts based on Week 1)
4. **Ongoing**: Repeat weekly - plans become more realistic
5. **Review**: After 4 weeks, check if patterns improve

## Tips for Best Results

- **Be Honest**: Don't overestimate available time
- **Document Reality**: Detailed check-in notes help adaptation
- **One Action/Day**: Resist adding more
- **Review Trade-offs**: Understand what was cut and why
- **Iterate**: 3-4 weeks to see patterns emerge

## Resources

| Resource | URL |
|----------|-----|
| Setup Guide | [SETUP.md](SETUP.md) |
| API Docs | http://localhost:8000/docs |
| Project Summary | [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) |
| Architecture | [STRUCTURE.md](STRUCTURE.md) |
| Health Check | http://localhost:8000/api/v1/health |

---

**Philosophy**: This is an execution enforcer, not a motivator. Success comes from realistic planning, explicit trade-offs, and honest execution tracking.

---

Last updated: December 2025
Version: 1.0 (Simplified - No Agents)
