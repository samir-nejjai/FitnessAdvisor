"""
Example script demonstrating the Agentic Execution Coach workflow programmatically.
This shows how to use the system without the web UI.
"""
from datetime import date, timedelta
from models import (
    HardConstraint,
    NonNegotiable,
    Objective,
    RealityCheck,
    UserProfile,
    EnergyLevel,
)
from state_manager import StateManager
from workflows import WorkflowOrchestrator


def run_example():
    """Run a complete example workflow."""
    print("🎯 Agentic Execution Coach - Example Workflow\n")
    
    # Initialize components
    state_manager = StateManager()
    orchestrator = WorkflowOrchestrator(state_manager=state_manager)
    
    # Step 1: Create user profile
    print("Step 1: Creating user profile...")
    profile = UserProfile(
        objective=Objective(
            id="obj_001",
            description="Improve strength and conditioning over 12 weeks while learning Python",
            duration_weeks=12,
            version=1
        ),
        hard_constraints=HardConstraint(
            available_hours_per_week=10.0,
            fixed_commitments=[
                "Work meetings Mon/Wed 9-5",
                "Family time weekends"
            ],
            physical_constraints=[
                "Lower back issue - limit heavy deadlifts"
            ]
        ),
        non_negotiables=NonNegotiable(
            minimum_training_frequency=3,
            rest_days=["Sunday"],
            other_rules=["No training after 9 PM"]
        )
    )
    
    state_manager.save_profile(profile)
    print("✅ Profile created\n")
    
    # Step 2: Generate weekly plan
    print("Step 2: Generating weekly plan...")
    print("⏳ This will take 30-60 seconds as agents work...\n")
    
    # Use next Monday
    today = date.today()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    next_monday = today + timedelta(days=days_until_monday)
    
    try:
        plan = orchestrator.generate_weekly_plan(week_start_date=next_monday)
        
        print(f"✅ Plan generated for {plan.week_id}\n")
        print("📋 Priorities:")
        for i, priority in enumerate(plan.priorities, 1):
            print(f"  {i}. {priority}")
        
        print("\n❌ Excluded:")
        for excluded in plan.excluded:
            print(f"  - {excluded}")
        
        print(f"\n⚖️  Trade-off Rationale:")
        print(f"  {plan.trade_off_rationale}")
        
        print("\n📅 Daily Actions:")
        for action in plan.daily_actions:
            print(f"  {action.day}: {action.action} ({action.time_estimate_minutes} min)")
        
        print("\n" + "="*60 + "\n")
        
        # Step 3: Simulate reality check (optional - comment out if you want)
        print("Step 3: Simulating reality check...")
        reality_check = RealityCheck(
            week_id=plan.week_id,
            sessions_completed=3,
            sessions_planned=4,
            energy_level=EnergyLevel.MODERATE,
            unexpected_events=[
                "Client meeting ran late on Tuesday",
                "Had to work late on Thursday"
            ]
        )
        
        print("⏳ Analyzing deviation...\n")
        deviation_report = orchestrator.process_reality_check(reality_check)
        
        print(f"✅ Deviation analysis complete\n")
        print(f"📊 Completion Rate: {deviation_report.completion_rate * 100:.0f}%")
        print(f"⚠️  Deviation Detected: {deviation_report.deviation_detected}")
        print(f"📝 Summary: {deviation_report.deviation_summary}")
        print(f"💡 Recommended Action: {deviation_report.recommended_action}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your .env file is configured with valid LLM credentials.")
        return
    
    print("\n" + "="*60)
    print("✅ Example workflow complete!")
    print("\nNext steps:")
    print("  - Run 'python api.py' to start the web server")
    print("  - Open http://localhost:8000/ui in your browser")
    print("  - Or use the API at http://localhost:8000/docs")


if __name__ == "__main__":
    run_example()
