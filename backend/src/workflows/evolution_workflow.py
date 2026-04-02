from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime
import uuid

from ..models.api_spec import APISpec
from ..models.usage_data import UsageData
from ..models.analysis_result import AnalysisResult, BreakingChange, MigrationGuide
from ..agents.spec_analyzer import SpecAnalyzerAgent
from ..agents.usage_tracker import UsageTrackerAgent
from ..agents.impact_assessor import ImpactAssessorAgent
from ..agents.migration_generator import MigrationGeneratorAgent


class WorkflowState(TypedDict):
    """State for the evolution analysis workflow"""
    old_spec: APISpec
    new_spec: APISpec
    usage_data: UsageData
    spec_analysis_old: str
    spec_analysis_new: str
    spec_comparison: str
    usage_insights: str
    breaking_changes: list[BreakingChange]
    impact_summary: str
    risk_score: float
    migration_guide: MigrationGuide
    analysis_result: AnalysisResult
    messages: Annotated[Sequence[BaseMessage], operator.add]
    current_step: str
    error: str


class EvolutionWorkflow:
    """LangGraph workflow for API evolution analysis"""
    
    def __init__(self):
        self.spec_analyzer = SpecAnalyzerAgent()
        self.usage_tracker = UsageTrackerAgent()
        self.impact_assessor = ImpactAssessorAgent()
        self.migration_generator = MigrationGeneratorAgent()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("analyze_old_spec", self._analyze_old_spec)
        workflow.add_node("analyze_new_spec", self._analyze_new_spec)
        workflow.add_node("compare_specs", self._compare_specs)
        workflow.add_node("analyze_usage", self._analyze_usage)
        workflow.add_node("assess_impact", self._assess_impact)
        workflow.add_node("generate_migration", self._generate_migration)
        workflow.add_node("finalize_result", self._finalize_result)
        
        # Define the workflow edges
        workflow.set_entry_point("analyze_old_spec")
        workflow.add_edge("analyze_old_spec", "analyze_new_spec")
        workflow.add_edge("analyze_new_spec", "compare_specs")
        workflow.add_edge("compare_specs", "analyze_usage")
        workflow.add_edge("analyze_usage", "assess_impact")
        workflow.add_edge("assess_impact", "generate_migration")
        workflow.add_edge("generate_migration", "finalize_result")
        workflow.add_edge("finalize_result", END)
        
        return workflow.compile()
    
    def _analyze_old_spec(self, state: WorkflowState) -> dict:
        """Analyze the old API specification"""
        print("📊 Analyzing old API specification...")
        
        try:
            analysis = self.spec_analyzer.analyze_spec(state["old_spec"])
            return {
                "spec_analysis_old": f"Old API Analysis: {analysis.total_endpoints} endpoints, complexity: {analysis.complexity_score}/10",
                "current_step": "analyze_old_spec"
            }
        except Exception as e:
            return {
                "spec_analysis_old": f"Error analyzing old spec: {str(e)}",
                "current_step": "analyze_old_spec",
                "error": str(e)
            }
    
    def _analyze_new_spec(self, state: WorkflowState) -> dict:
        """Analyze the new API specification"""
        print("📊 Analyzing new API specification...")
        
        try:
            analysis = self.spec_analyzer.analyze_spec(state["new_spec"])
            return {
                "spec_analysis_new": f"New API Analysis: {analysis.total_endpoints} endpoints, complexity: {analysis.complexity_score}/10",
                "current_step": "analyze_new_spec"
            }
        except Exception as e:
            return {
                "spec_analysis_new": f"Error analyzing new spec: {str(e)}",
                "current_step": "analyze_new_spec",
                "error": str(e)
            }
    
    def _compare_specs(self, state: WorkflowState) -> dict:
        """Compare old and new specifications"""
        print("🔍 Comparing API specifications...")
        
        try:
            comparison = self.spec_analyzer.compare_specs(
                state["old_spec"],
                state["new_spec"]
            )
            return {
                "spec_comparison": comparison,
                "current_step": "compare_specs"
            }
        except Exception as e:
            return {
                "spec_comparison": f"Error comparing specs: {str(e)}",
                "current_step": "compare_specs",
                "error": str(e)
            }
    
    def _analyze_usage(self, state: WorkflowState) -> dict:
        """Analyze usage patterns"""
        print("📈 Analyzing usage patterns...")
        
        try:
            insights = self.usage_tracker.analyze_usage_patterns(state["usage_data"])
            return {
                "usage_insights": insights,
                "current_step": "analyze_usage"
            }
        except Exception as e:
            return {
                "usage_insights": f"Error analyzing usage: {str(e)}",
                "current_step": "analyze_usage",
                "error": str(e)
            }
    
    def _assess_impact(self, state: WorkflowState) -> dict:
        """Assess impact of changes"""
        print("⚠️  Assessing impact of changes...")
        
        try:
            breaking_changes = self.impact_assessor.assess_impact(
                state["old_spec"],
                state["new_spec"],
                state["usage_data"]
            )
            
            impact_summary = self.impact_assessor.generate_impact_summary(
                breaking_changes,
                state["old_spec"].version,
                state["new_spec"].version
            )
            
            risk_score = self.impact_assessor.calculate_risk_score(breaking_changes)
            
            return {
                "breaking_changes": breaking_changes,
                "impact_summary": impact_summary,
                "risk_score": risk_score,
                "current_step": "assess_impact"
            }
        except Exception as e:
            return {
                "breaking_changes": [],
                "impact_summary": f"Error assessing impact: {str(e)}",
                "risk_score": 0.0,
                "current_step": "assess_impact",
                "error": str(e)
            }
    
    def _generate_migration(self, state: WorkflowState) -> dict:
        """Generate migration guide"""
        print("📝 Generating migration guide...")
        
        try:
            migration_guide = self.migration_generator.generate_migration_guide(
                state["old_spec"],
                state["new_spec"],
                state["breaking_changes"],
                state["usage_data"]
            )
            
            return {
                "migration_guide": migration_guide,
                "current_step": "generate_migration"
            }
        except Exception as e:
            return {
                "migration_guide": None,
                "current_step": "generate_migration",
                "error": str(e)
            }
    
    def _finalize_result(self, state: WorkflowState) -> dict:
        """Finalize the analysis result"""
        print("✅ Finalizing analysis result...")
        
        # Count affected clients
        all_affected_clients = set()
        for change in state["breaking_changes"]:
            all_affected_clients.update(change.affected_clients)
        
        # Create the final analysis result
        analysis_result = AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            old_version=state["old_spec"].version,
            new_version=state["new_spec"].version,
            breaking_changes=state["breaking_changes"],
            migration_guide=state["migration_guide"],
            summary=state["impact_summary"],
            total_affected_clients=len(all_affected_clients),
            risk_score=state["risk_score"]
        )
        
        return {
            "analysis_result": analysis_result,
            "current_step": "finalized"
        }
    
    def run_analysis(
        self,
        old_spec: APISpec,
        new_spec: APISpec,
        usage_data: UsageData
    ) -> AnalysisResult:
        """Run the complete analysis workflow"""
        
        print(f"\n🚀 Starting API Evolution Analysis")
        print(f"   Old Version: {old_spec.version}")
        print(f"   New Version: {new_spec.version}")
        print(f"   Usage Period: {usage_data.time_period_days} days\n")
        
        initial_state = {
            "old_spec": old_spec,
            "new_spec": new_spec,
            "usage_data": usage_data,
            "spec_analysis_old": "",
            "spec_analysis_new": "",
            "spec_comparison": "",
            "usage_insights": "",
            "breaking_changes": [],
            "impact_summary": "",
            "risk_score": 0.0,
            "migration_guide": None,
            "analysis_result": None,
            "messages": [],
            "current_step": "start",
            "error": ""
        }
        
        # Run the workflow
        final_state = self.workflow.invoke(initial_state)
        
        print(f"\n✨ Analysis complete!")
        print(f"   Breaking Changes: {len(final_state['breaking_changes'])}")
        print(f"   Risk Score: {final_state['risk_score']:.1f}/10")
        print(f"   Affected Clients: {final_state['analysis_result'].total_affected_clients}\n")
        
        return final_state["analysis_result"]
