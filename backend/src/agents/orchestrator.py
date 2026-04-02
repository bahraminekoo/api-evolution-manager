from typing import Optional
from ..models.api_spec import APISpec
from ..models.usage_data import UsageData
from ..models.analysis_result import AnalysisResult
from ..workflows.evolution_workflow import EvolutionWorkflow
from ..tools.spec_parser import SpecParser
import json
from pathlib import Path


class OrchestratorAgent:
    """Main orchestrator that coordinates the entire analysis workflow"""
    
    def __init__(self):
        self.workflow = EvolutionWorkflow()
        self.spec_parser = SpecParser()
    
    def analyze_api_evolution(
        self,
        old_spec_path: str,
        new_spec_path: str,
        usage_data_path: str
    ) -> AnalysisResult:
        """
        Main entry point for API evolution analysis
        
        Args:
            old_spec_path: Path to old OpenAPI spec JSON file
            new_spec_path: Path to new OpenAPI spec JSON file
            usage_data_path: Path to usage data JSON file
            
        Returns:
            Complete analysis result with migration guide
        """
        
        # Load and parse specifications
        old_spec = self.spec_parser.load_from_file(old_spec_path)
        new_spec = self.spec_parser.load_from_file(new_spec_path)
        
        # Load usage data
        usage_data = self._load_usage_data(usage_data_path)
        
        # Run the workflow
        result = self.workflow.run_analysis(old_spec, new_spec, usage_data)
        
        return result
    
    def analyze_from_specs(
        self,
        old_spec: APISpec,
        new_spec: APISpec,
        usage_data: UsageData
    ) -> AnalysisResult:
        """
        Analyze API evolution from already parsed specs
        
        Args:
            old_spec: Parsed old API specification
            new_spec: Parsed new API specification
            usage_data: Usage data
            
        Returns:
            Complete analysis result with migration guide
        """
        return self.workflow.run_analysis(old_spec, new_spec, usage_data)
    
    def _load_usage_data(self, usage_data_path: str) -> UsageData:
        """Load usage data from JSON file"""
        path = Path(usage_data_path)
        with open(path, 'r') as f:
            data = json.load(f)
        return UsageData(**data)
