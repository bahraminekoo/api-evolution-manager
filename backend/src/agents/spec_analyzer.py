from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from ..models.api_spec import APISpec
from ..utils.config import settings


class SpecAnalysis(BaseModel):
    """Output model for spec analysis"""
    total_endpoints: int
    endpoints_by_method: Dict[str, int]
    deprecated_endpoints: List[str] = Field(default_factory=list)
    key_observations: List[str] = Field(default_factory=list)
    complexity_score: float = Field(ge=0, le=10)


class SpecAnalyzerAgent:
    """Agent responsible for analyzing API specifications"""
    
    def __init__(self):
        llm_params = {
            "model": settings.openai_model,
            "temperature": 0.1,
            "api_key": settings.openai_api_key
        }
        if settings.openai_base_url:
            llm_params["base_url"] = settings.openai_base_url
        self.llm = ChatOpenAI(**llm_params)
        self.parser = PydanticOutputParser(pydantic_object=SpecAnalysis)
    
    def analyze_spec(self, spec: APISpec) -> SpecAnalysis:
        """Analyze a single API specification"""
        
        # Create a summary of the spec
        spec_summary = self._create_spec_summary(spec)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert API analyst. Analyze the provided API specification and provide insights.
            
{format_instructions}

Focus on:
- Total number of endpoints
- Distribution by HTTP method
- Deprecated endpoints
- Key observations about the API design
- Complexity score (0-10, where 10 is most complex)"""),
            ("user", "API Specification:\n{spec_summary}")
        ])
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "spec_summary": spec_summary,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            # Fallback to basic analysis
            return self._basic_analysis(spec)
    
    def _create_spec_summary(self, spec: APISpec) -> str:
        """Create a text summary of the API spec"""
        lines = [
            f"API: {spec.title} (v{spec.version})",
            f"Description: {spec.description or 'N/A'}",
            f"Base URL: {spec.base_url or 'N/A'}",
            f"\nEndpoints ({len(spec.endpoints)}):"
        ]
        
        for endpoint in spec.endpoints:
            deprecated = " [DEPRECATED]" if endpoint.deprecated else ""
            params = f" ({len(endpoint.parameters)} params)" if endpoint.parameters else ""
            lines.append(f"  {endpoint.method.value} {endpoint.path}{params}{deprecated}")
            if endpoint.summary:
                lines.append(f"    Summary: {endpoint.summary}")
        
        return "\n".join(lines)
    
    def _basic_analysis(self, spec: APISpec) -> SpecAnalysis:
        """Fallback basic analysis without LLM"""
        endpoints_by_method = {}
        deprecated = []
        
        for endpoint in spec.endpoints:
            method = endpoint.method.value
            endpoints_by_method[method] = endpoints_by_method.get(method, 0) + 1
            
            if endpoint.deprecated:
                deprecated.append(f"{method} {endpoint.path}")
        
        # Calculate complexity based on number of endpoints and parameters
        total_params = sum(len(ep.parameters) for ep in spec.endpoints)
        complexity = min(10, (len(spec.endpoints) / 10) + (total_params / 50))
        
        observations = [
            f"API has {len(spec.endpoints)} total endpoints",
            f"Most common method: {max(endpoints_by_method, key=endpoints_by_method.get) if endpoints_by_method else 'N/A'}",
        ]
        
        if deprecated:
            observations.append(f"{len(deprecated)} deprecated endpoints found")
        
        return SpecAnalysis(
            total_endpoints=len(spec.endpoints),
            endpoints_by_method=endpoints_by_method,
            deprecated_endpoints=deprecated,
            key_observations=observations,
            complexity_score=round(complexity, 2)
        )
    
    def compare_specs(self, old_spec: APISpec, new_spec: APISpec) -> str:
        """Generate a high-level comparison between two specs"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert API analyst. Compare two versions of an API specification and provide a high-level summary of changes.
            
Focus on:
- Major structural changes
- New capabilities added
- Removed functionality
- Overall evolution direction"""),
            ("user", """Old API Spec:
{old_spec}

New API Spec:
{new_spec}

Provide a concise comparison summary.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "old_spec": self._create_spec_summary(old_spec),
                "new_spec": self._create_spec_summary(new_spec)
            })
            return result.content
        except Exception as e:
            return f"Error comparing specs: {str(e)}"
