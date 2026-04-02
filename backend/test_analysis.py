#!/usr/bin/env python3
"""
Test script to verify the API Evolution Manager backend works correctly
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.orchestrator import OrchestratorAgent


def main():
    print("=" * 80)
    print("API Evolution Manager - Test Script")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent()
    
    # Define paths to mock data
    base_path = os.path.join(os.path.dirname(__file__), "mock_data")
    old_spec_path = os.path.join(base_path, "v1_api_spec.json")
    new_spec_path = os.path.join(base_path, "v2_api_spec.json")
    usage_data_path = os.path.join(base_path, "usage_logs.json")
    
    # Verify files exist
    for path, name in [(old_spec_path, "v1 spec"), (new_spec_path, "v2 spec"), (usage_data_path, "usage data")]:
        if not os.path.exists(path):
            print(f"❌ Error: {name} not found at {path}")
            return 1
        print(f"✅ Found {name}")
    
    print("\n" + "=" * 80)
    
    # Run analysis
    try:
        result = orchestrator.analyze_api_evolution(
            old_spec_path,
            new_spec_path,
            usage_data_path
        )
        
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        
        print(f"\n📊 Analysis ID: {result.analysis_id}")
        print(f"📅 Timestamp: {result.timestamp}")
        print(f"🔄 Version Change: {result.old_version} → {result.new_version}")
        print(f"⚠️  Breaking Changes: {len(result.breaking_changes)}")
        print(f"🎯 Risk Score: {result.risk_score:.1f}/10")
        print(f"👥 Affected Clients: {result.total_affected_clients}")
        
        if result.breaking_changes:
            print(f"\n🔴 Breaking Changes:")
            for i, change in enumerate(result.breaking_changes[:5], 1):
                print(f"\n  {i}. {change.endpoint_key}")
                print(f"     Type: {change.change_type.value}")
                print(f"     Impact: {change.impact_level.value.upper()}")
                print(f"     Description: {change.description}")
                print(f"     Affected Clients: {', '.join(change.affected_clients) if change.affected_clients else 'None'}")
                print(f"     Usage: {change.usage_count:,} calls")
            
            if len(result.breaking_changes) > 5:
                print(f"\n  ... and {len(result.breaking_changes) - 5} more changes")
        
        if result.migration_guide:
            print(f"\n📝 Migration Guide:")
            print(f"   Estimated Effort: {result.migration_guide.estimated_total_effort_hours:.1f} hours")
            print(f"   Recommended Timeline: {result.migration_guide.recommended_timeline_days} days")
            print(f"   Migration Steps: {len(result.migration_guide.steps)}")
            
            if result.migration_guide.steps:
                print(f"\n   First 3 Steps:")
                for step in result.migration_guide.steps[:3]:
                    print(f"\n   Step {step.step_number}: {step.title}")
                    print(f"   Effort: {step.estimated_effort_hours} hours")
        
        print(f"\n📋 Summary:")
        print(f"{result.summary}")
        
        print("\n" + "=" * 80)
        print("✅ Test completed successfully!")
        print("=" * 80)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
