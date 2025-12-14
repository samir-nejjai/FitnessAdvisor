"""Simplified prompt-based workflow orchestration."""
import json
from datetime import date, timedelta
from typing import Dict, List, Optional

from app.services.llm_factory import LLMFactory
from app.models.schemas import (
    AdjustmentRequest,
    DailyAction,
    DeviationReport,
    ExecutionHistory,
    RealityCheck,
    UserProfile,
    WeeklyPlan,
)
from app.services.state_manager import StateManager


class WorkflowOrchestrator:
    """Orchestrates LLM-based workflows for the execution coach."""
    
    def __init__(self, state_manager: Optional[StateManager] = None, llm=None):
        """Initialize workflow orchestrator.
        
        Args:
            state_manager: State manager instance
            llm: LLM instance for generating plans
        """
        self.state_manager = state_manager or StateManager()
        self.llm = llm or LLMFactory.create_llm()
    
    def generate_weekly_plan(self, week_start_date: Optional[date] = None) -> WeeklyPlan:
        """Generate a new weekly plan using a single LLM call.
        
        Args:
            week_start_date: Start date of the week. Defaults to next Monday.
            
        Returns:
            Generated WeeklyPlan
            
        Raises:
            ValueError: If user profile doesn't exist
        """
        profile = self.state_manager.load_profile()
        if not profile:
            raise ValueError("User profile must be created before generating plans")
        
        # Calculate week_id and dates
        if week_start_date is None:
            today = date.today()
            days_until_monday = (7 - today.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            week_start_date = today + timedelta(days=days_until_monday)
        
        week_id = f"{week_start_date.year}-W{week_start_date.isocalendar()[1]:02d}"
        
        # Get execution history for context
        history = self.state_manager.get_execution_history(limit=4)
        
        # Build comprehensive planning prompt
        prompt = self._build_planning_prompt(profile, history, week_id, week_start_date)
        
        # Generate plan with LLM
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            plan_data = self._extract_json(content)
            
            if not plan_data:
                # Log the actual response for debugging
                print(f"Failed to parse LLM response. Raw content:\n{content[:500]}")
                raise ValueError("Failed to parse plan from LLM response")
            
            # Build the WeeklyPlan
            weekly_plan = WeeklyPlan(
                week_id=week_id,
                start_date=week_start_date,
                priorities=plan_data.get("priorities", [])[:5],  # Max 5
                excluded=plan_data.get("excluded", []),
                daily_actions=[
                    DailyAction(**action) for action in plan_data.get("daily_actions", [])
                ],
                trade_off_rationale=plan_data.get("trade_off_rationale", ""),
                assumptions=plan_data.get("assumptions", [])
            )
            
            # Save the plan
            self.state_manager.save_plan(weekly_plan)
            
            # Create history entry
            history_entry = ExecutionHistory(
                week_id=week_id,
                plan=weekly_plan
            )
            self.state_manager.save_history_entry(history_entry)
            
            return weekly_plan
            
        except Exception as e:
            raise ValueError(f"Failed to generate plan: {str(e)}")
    
    def process_reality_check(self, reality_check: RealityCheck) -> DeviationReport:
        """Process a reality check and generate deviation report using LLM.
        
        Args:
            reality_check: Reality check data
            
        Returns:
            Generated DeviationReport
        """
        # Save reality check
        self.state_manager.save_reality_check(reality_check)
        
        # Get the active plan
        plan = self.state_manager.get_active_plan(reality_check.week_id)
        if not plan:
            raise ValueError(f"No active plan found for week {reality_check.week_id}")
        
        # Build analysis prompt
        prompt = self._build_reality_check_prompt(plan, reality_check)
        
        # Analyze with LLM
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            report_data = self._extract_json(content)
            
            if not report_data:
                # Fallback calculation
                completion_rate = (
                    reality_check.sessions_completed / reality_check.sessions_planned
                    if reality_check.sessions_planned > 0 else 0.0
                )
                report_data = {
                    "deviation_detected": completion_rate < 0.7,
                    "completion_rate": completion_rate,
                    "deviation_summary": f"Completed {reality_check.sessions_completed}/{reality_check.sessions_planned} sessions",
                    "confidence_score": 0.5,
                    "recommended_action": "adjust" if completion_rate < 0.7 else "recommit"
                }
            
            # Create deviation report
            deviation_report = DeviationReport(
                week_id=reality_check.week_id,
                deviation_detected=report_data.get("deviation_detected", False),
                completion_rate=report_data.get("completion_rate", 0.0),
                deviation_summary=report_data.get("deviation_summary", ""),
                confidence_score=report_data.get("confidence_score", 0.5),
                recommended_action=report_data.get("recommended_action", "recommit")
            )
            
            # Save deviation report
            self.state_manager.save_deviation_report(deviation_report)
            
            # Update history entry
            history = self.state_manager.get_history_entry(reality_check.week_id)
            if history:
                history.reality_check = reality_check
                history.deviation_report = deviation_report
                history.final_completion_rate = deviation_report.completion_rate
                self.state_manager.save_history_entry(history)
            
            return deviation_report
            
        except Exception as e:
            raise ValueError(f"Failed to process reality check: {str(e)}")
    
    def adjust_plan(self, adjustment_request: AdjustmentRequest) -> WeeklyPlan:
        """Adjust current plan based on mid-week reality."""
        # Get current plan
        plan = self.state_manager.get_active_plan(adjustment_request.week_id)
        if not plan:
            raise ValueError(f"No active plan found for week {adjustment_request.week_id}")
        
        # Get profile
        profile = self.state_manager.get_profile()
        if not profile:
            raise ValueError("Profile not found")
        
        # Get deviation report if exists
        deviation_report = self.state_manager.get_deviation_report(adjustment_request.week_id)
        
        # Build adjustment prompt with current day context
        prompt = self._build_adjustment_prompt(plan, adjustment_request, deviation_report, profile)
        
        # Get adjusted plan from LLM
        try:
            response = self.llm.invoke(prompt)
            content = response.content if hasattr(response, 'content') else str(response)
            plan_data = self._extract_json(content)
            
            if not plan_data:
                raise ValueError("Failed to extract plan data from LLM response")
            
            # Update the existing plan with adjusted data
            plan.priorities = plan_data.get("priorities", plan.priorities)
            plan.excluded = plan_data.get("excluded", plan.excluded)
            plan.trade_off_rationale = plan_data.get("trade_off_rationale", plan.trade_off_rationale)
            plan.assumptions = plan_data.get("assumptions", plan.assumptions)
            
            # Update daily actions for remaining days only
            if "daily_actions" in plan_data:
                adjusted_actions = [DailyAction(**action) for action in plan_data["daily_actions"]]
                # Keep completed past days, update remaining days
                days_map = {action.day: action for action in adjusted_actions}
                for i, action in enumerate(plan.daily_actions):
                    if action.day in days_map and not action.completed:
                        plan.daily_actions[i] = days_map[action.day]
            
            # Save adjusted plan
            self.state_manager.save_plan(plan)
            
            return plan
            
        except Exception as e:
            raise ValueError(f"Failed to adjust plan: {str(e)}")
    
    def _build_planning_prompt(
        self, 
        profile: UserProfile, 
        history: List[ExecutionHistory],
        week_id: str,
        week_start_date: date
    ) -> str:
        """Build comprehensive planning prompt."""
        
        history_context = ""
        if history:
            history_context = "\n\nPast Performance (learn from this):"
            for entry in history[:3]:
                if entry.final_completion_rate is not None:
                    history_context += f"\n- {entry.week_id}: {entry.final_completion_rate*100:.0f}% completion"
                    if entry.deviation_report:
                        history_context += f" - {entry.deviation_report.deviation_summary}"
        
        return f"""You are a brutally honest execution coach creating a realistic weekly plan for week {week_id} starting {week_start_date.strftime('%Y-%m-%d')}.

USER PROFILE:
Primary Objective: {profile.objective.description}
Duration: {profile.objective.duration_weeks} weeks
Available Time: {profile.hard_constraints.available_hours_per_week} hours/week
Fixed Commitments: {', '.join(profile.hard_constraints.fixed_commitments)}
Physical Constraints: {', '.join(profile.hard_constraints.physical_constraints) if profile.hard_constraints.physical_constraints else 'None'}
Minimum Training Frequency: {profile.non_negotiables.minimum_training_frequency} sessions/week
Rest Days: {', '.join(profile.non_negotiables.rest_days)}
{history_context}

YOUR PHILOSOPHY:
You are a REALIST, not an optimist. Your job is to create plans people actually complete, not plans that look impressive on paper.

CRITICAL RULES:
1. BUFFER EVERYTHING - Assume tasks take 50% longer than estimated
2. PLAN FOR DISRUPTIONS - Every week has unexpected events (meetings, fatigue, life)
3. ENERGY IS FINITE - People overestimate their weekly energy by 30-40%
4. LESS IS MORE - 3 well-executed priorities beat 5 half-done ones
5. LEARN FROM FAILURE - If past completion was <80%, the plan was TOO AMBITIOUS

YOUR TASK:
Create a weekly plan that:
1. Respects ALL hard constraints and non-negotiables
2. Includes 3-4 priorities MAXIMUM (not 5 - be ruthless)
3. Accounts for 20% buffer time for unexpected events
4. Explicitly states what is EXCLUDED and why
5. Provides honest trade-off rationale
6. Lists realistic assumptions (expect them to break)
7. Generates ONE concrete daily action per day (7 days total)
8. Builds in rest/recovery - humans are not machines

CRITICAL THINKING:
- If past completion rate was <80%, CUT MORE from this plan
- What's the MINIMUM viable plan that still drives progress?
- Where is this person lying to themselves about available time/energy?
- Which priority looks good but won't actually get done?
- What will they drop when Tuesday gets busy? Plan around that.

DAILY ACTIONS MUST BE:
- Specific enough to start immediately
- Time-boxed (30-90 min max per action)
- Sequenced to avoid burnout
- Include at least 2 rest/recovery days
- Each action should have a detailed_plan with step-by-step breakdown

OUTPUT FORMAT - RESPOND WITH ONLY THE JSON, NO OTHER TEXT:
{{
  "priorities": ["priority 1", "priority 2", "priority 3"],
  "excluded": ["excluded item 1", "excluded item 2", "excluded item 3"],
  "trade_off_rationale": "Honest explanation of what was cut and WHY (mention buffer time, energy constraints, past performance)",
  "assumptions": ["assumption 1 that could break", "assumption 2 that could break"],
  "daily_actions": [
    {{"day": "Mon", "action": "Specific actionable task", "time_estimate_minutes": 60, "detailed_plan": "Step-by-step breakdown:\n1. Warm-up (10 min)\n2. Main work (40 min)\n3. Cool-down (10 min)"}},
    {{"day": "Tue", "action": "Specific actionable task", "time_estimate_minutes": 45, "detailed_plan": "Detailed session plan with sets, reps, or specific activities"}},
    {{"day": "Wed", "action": "Rest/recovery or light activity", "time_estimate_minutes": 0, "detailed_plan": "Light stretching or complete rest - listen to your body"}},
    {{"day": "Thu", "action": "Specific actionable task", "time_estimate_minutes": 60, "detailed_plan": "Step-by-step breakdown for this session"}},
    {{"day": "Fri", "action": "Specific actionable task", "time_estimate_minutes": 45, "detailed_plan": "Detailed plan with specific exercises or activities"}},
    {{"day": "Sat", "action": "Specific actionable task", "time_estimate_minutes": 75, "detailed_plan": "Longer session breakdown with specific activities"}},
    {{"day": "Sun", "action": "Rest/recovery", "time_estimate_minutes": 0, "detailed_plan": "Complete rest day - no training"}}
  ]
}}

IMPORTANT: Return ONLY the JSON object above. Do not include any explanatory text before or after.

Remember: Your success is measured by completion rate, not by how ambitious the plan looks."""
    
    def _build_reality_check_prompt(
        self, 
        plan: WeeklyPlan, 
        reality_check: RealityCheck
    ) -> str:
        """Build reality check analysis prompt."""
        
        # Build planned vs actual comparison
        planned_actions = "\n".join([f"{a.day}: {a.action} ({a.time_estimate_minutes} min)" for a in plan.daily_actions])
        
        return f"""You are an execution auditor analyzing actual vs planned performance for week {reality_check.week_id}.

PLANNED ACTIONS:
{planned_actions}

ACTUAL EXECUTION:
Sessions Completed: {reality_check.sessions_completed} / {reality_check.sessions_planned}
Energy Level: {reality_check.energy_level}
Unexpected Events: {', '.join(reality_check.unexpected_events) if reality_check.unexpected_events else 'None'}

DETAILED NOTES ON WHAT WAS ACTUALLY DONE:
{reality_check.notes or 'No detailed notes provided'}

YOUR ANALYSIS:
Calculate completion rate and determine if significant deviation occurred.
A deviation is "significant" if:
- Completion rate < 70%
- Multiple unexpected events disrupted the plan
- Significant mismatch between planned and actual execution (check the detailed notes)
- Energy levels were consistently low

Use the detailed notes to understand:
- What was actually done vs what was planned
- Quality and duration of execution
- Patterns of deviation (skipped types, modified workouts, etc.)

Provide:
1. Completion rate (0.0 to 1.0)
2. Whether deviation is significant
3. Clear summary incorporating insights from the actual execution notes
4. Confidence score on whether the plan was realistic (0.0 = unrealistic, 1.0 = perfectly realistic)
5. Recommended action: "adjust" (need to revise plan) or "recommit" (plan was fine, just execute better)

Provide:
1. Completion rate (0.0 to 1.0)
2. Whether deviation is significant
3. Clear summary of what happened
4. Confidence score on whether the plan was realistic (0.0 = unrealistic, 1.0 = perfectly realistic)
5. Recommended action: "adjust" (need to revise plan) or "recommit" (plan was fine, just execute better)

OUTPUT FORMAT - RESPOND WITH ONLY THE JSON, NO OTHER TEXT:
{{
  "deviation_detected": true,
  "completion_rate": 0.65,
  "deviation_summary": "Clear explanation of what happened",
  "confidence_score": 0.7,
  "recommended_action": "adjust"
}}

IMPORTANT: Return ONLY the JSON object above. Do not include any explanatory text."""
    
    def _build_adjustment_prompt(
        self,
        current_plan: WeeklyPlan,
        adjustment_request: AdjustmentRequest,
        deviation_report: Optional[DeviationReport],
        profile: UserProfile
    ) -> str:
        """Build plan adjustment prompt."""
        
        # Build actual execution context from daily actions
        actual_execution = "\n".join([
            f"{a.day}: {'✅ Done' if a.completed else '❌ Not Done'} - {a.actual_notes if a.actual_notes else 'No notes'}"
            for a in current_plan.daily_actions
        ])
        
        deviation_context = ""
        if deviation_report:
            deviation_context = f"""
DEVIATION ANALYSIS:
Completion Rate: {deviation_report.completion_rate*100:.0f}%
Summary: {deviation_report.deviation_summary}
Recommended Action: {deviation_report.recommended_action}
"""
        
        return f"""You are an execution coach adjusting a weekly plan mid-week based on actual execution data.

ORIGINAL PLAN (Week {adjustment_request.week_id}):
Priorities: {', '.join(current_plan.priorities)}
Excluded: {', '.join(current_plan.excluded)}

ACTUAL EXECUTION SO FAR:
{actual_execution}

REASON FOR ADJUSTMENT:
{adjustment_request.reason}
{deviation_context}

USER CONSTRAINTS (from profile):
Available Time: {profile.hard_constraints.available_hours_per_week} hours/week
Minimum Training: {profile.non_negotiables.minimum_training_frequency} sessions/week

YOUR TASK:
Create an adjusted plan for the REMAINING days of this week that:
1. Ruthlessly cuts scope based on reality
2. Keeps 2-3 priorities maximum (force trade-offs)
3. Focuses on what's achievable in remaining time
4. Maintains momentum without overwhelming the user
5. Provides honest rationale for what was cut

CRITICAL: This is a RESCUE operation, not a fresh start. Be conservative.

OUTPUT FORMAT (valid JSON only):
{{
  "priorities": ["adjusted priority 1", "adjusted priority 2"],
  "excluded": ["now excluded 1", "now excluded 2"],
  "trade_off_rationale": "Honest explanation of cuts and why",
  "assumptions": ["assumption 1"],
  "daily_actions": [
    {{"day": "Thu", "action": "Specific actionable task", "time_estimate_minutes": 45}},
    {{"day": "Fri", "action": "Specific actionable task", "time_estimate_minutes": 45}},
    {{"day": "Sat", "action": "Rest/recovery", "time_estimate_minutes": 0}},
    {{"day": "Sun", "action": "Light activity", "time_estimate_minutes": 30}}
  ]
}}

Focus on salvaging the week, not heroics."""
    
    def _extract_json(self, content: str) -> Dict:
        """Extract JSON from LLM response with better error handling.
        
        Tries multiple strategies to find and parse JSON, handling various
        cases where LLM adds extra text or formatting.
        """
        if not content:
            return {}
        
        # Clean common issues
        content = content.strip()
        
        # Strategy 1: Direct JSON parse
        try:
            return json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        
        # Strategy 2: Find JSON object (first valid one)
        try:
            start = content.find('{')
            if start != -1:
                # Try to find matching closing brace
                brace_count = 0
                for i in range(start, len(content)):
                    if content[i] == '{':
                        brace_count += 1
                    elif content[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_str = content[start:i+1]
                            # Remove any non-ASCII characters that might cause issues
                            json_str = json_str.encode('ascii', 'ignore').decode('ascii')
                            return json.loads(json_str)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        
        # Strategy 3: Look for JSON in code blocks
        try:
            # Check for markdown code blocks
            if '```json' in content:
                start = content.find('```json') + 7
                end = content.find('```', start)
                if end > start:
                    json_str = content[start:end].strip()
                    return json.loads(json_str)
            elif '```' in content:
                start = content.find('```') + 3
                end = content.find('```', start)
                if end > start:
                    json_str = content[start:end].strip()
                    # Try to parse what's in the code block
                    if json_str.startswith('{'):
                        return json.loads(json_str)
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        
        # Strategy 4: Find JSON array (for daily_actions)
        try:
            start = content.find('[')
            if start != -1:
                bracket_count = 0
                for i in range(start, len(content)):
                    if content[i] == '[':
                        bracket_count += 1
                    elif content[i] == ']':
                        bracket_count -= 1
                        if bracket_count == 0:
                            json_str = content[start:i+1]
                            parsed = json.loads(json_str)
                            if isinstance(parsed, list):
                                return {"daily_actions": parsed}
                            return parsed
        except (json.JSONDecodeError, UnicodeDecodeError):
            pass
        
        return {}
