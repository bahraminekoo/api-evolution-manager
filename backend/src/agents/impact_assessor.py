from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Dict
from ..models.api_spec import APISpec
from ..models.usage_data import UsageData
from ..models.analysis_result import BreakingChange, ImpactLevel
from ..tools.diff_analyzer import DiffAnalyzer
from ..utils.config import settings


class ImpactAssessorAgent:
    """Agent responsible for assessing the impact of API changes"""
    
    def __init__(self):
        llm_params = {
            "model": settings.openai_model,
            "temperature": 0.2,
            "api_key": settings.openai_api_key
        }
        if settings.openai_base_url:
            llm_params["base_url"] = settings.openai_base_url
        self.llm = ChatOpenAI(**llm_params)
        self.diff_analyzer = DiffAnalyzer()
    
    def assess_impact(
        self,
        old_spec: APISpec,
        new_spec: APISpec,
        usage_data: UsageData
    ) -> List[BreakingChange]:
        """Assess the impact of changes between two API versions"""
        
        # First, use the diff analyzer to detect changes
        breaking_changes = self.diff_analyzer.analyze_changes(
            old_spec, new_spec, usage_data
        )
        
        # Enhance with LLM analysis for complex changes
        for change in breaking_changes:
            if change.impact_level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]:
                change.migration_complexity = self._assess_migration_complexity(change)
        
        return breaking_changes
    
    def _assess_migration_complexity(self, change: BreakingChange) -> str:
        """Use LLM to assess migration complexity"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in API migrations. Assess the complexity of migrating from the old API to the new API given this breaking change.

Respond with one of: "simple", "moderate", "complex", "very_complex"

Consider:
- Type of change
- Number of affected clients
- Usage frequency
- Availability of alternatives"""),
            ("user", """Breaking Change:
Type: {change_type}
Description: {description}
Affected Clients: {num_clients}
Usage Count: {usage_count}
Details: {details}

What is the migration complexity?""")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "change_type": change.change_type.value,
                "description": change.description,
                "num_clients": len(change.affected_clients),
                "usage_count": change.usage_count,
                "details": str(change.details)
            })
            
            complexity = result.content.strip().lower()
            if complexity in ["simple", "moderate", "complex", "very_complex"]:
                return complexity
            return "moderate"
        except Exception:
            return "moderate"
    
    def generate_impact_summary(
        self,
        breaking_changes: List[BreakingChange],
        old_version: str,
        new_version: str
    ) -> str:
        """Generate a comprehensive impact summary using LLM"""
        
        changes_summary = self._format_changes_for_summary(breaking_changes)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert API architect. Generate a comprehensive impact summary for API changes.

Include:
1. Executive summary
2. Risk assessment
3. Key concerns
4. Recommended actions
5. Timeline suggestions

Be concise but thorough."""),
            ("user", """API Version Change: {old_version} → {new_version}

Breaking Changes Detected:
{changes_summary}

Generate an impact summary.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "old_version": old_version,
                "new_version": new_version,
                "changes_summary": changes_summary
            })
            return result.content
        except Exception as e:
            return self._generate_basic_summary(breaking_changes, old_version, new_version)
    
    def _format_changes_for_summary(self, changes: List[BreakingChange]) -> str:
        """Format breaking changes for LLM consumption"""
        lines = []
        
        by_impact = {
            ImpactLevel.CRITICAL: [],
            ImpactLevel.HIGH: [],
            ImpactLevel.MEDIUM: [],
            ImpactLevel.LOW: []
        }
        
        for change in changes:
            if change.impact_level != ImpactLevel.NONE:
                by_impact[change.impact_level].append(change)
        
        for impact_level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH, ImpactLevel.MEDIUM, ImpactLevel.LOW]:
            if by_impact[impact_level]:
                lines.append(f"\n{impact_level.value.upper()} IMPACT ({len(by_impact[impact_level])} changes):")
                for change in by_impact[impact_level]:
                    lines.append(f"  - {change.description}")
                    lines.append(f"    Affected clients: {', '.join(change.affected_clients) if change.affected_clients else 'Unknown'}")
                    lines.append(f"    Usage: {change.usage_count:,} calls")
        
        return "\n".join(lines) if lines else "No breaking changes detected"
    
    def _generate_basic_summary(
        self,
        breaking_changes: List[BreakingChange],
        old_version: str,
        new_version: str
    ) -> str:
        """Generate a basic summary without LLM"""
        critical = sum(1 for c in breaking_changes if c.impact_level == ImpactLevel.CRITICAL)
        high = sum(1 for c in breaking_changes if c.impact_level == ImpactLevel.HIGH)
        medium = sum(1 for c in breaking_changes if c.impact_level == ImpactLevel.MEDIUM)
        
        total_affected_calls = sum(c.usage_count for c in breaking_changes)
        all_affected_clients = set()
        for c in breaking_changes:
            all_affected_clients.update(c.affected_clients)
        
        summary = f"""API Evolution Impact Summary
Version: {old_version} → {new_version}

Breaking Changes: {len(breaking_changes)} total
  - Critical: {critical}
  - High: {high}
  - Medium: {medium}

Affected Clients: {len(all_affected_clients)}
Total Impacted API Calls: {total_affected_calls:,}

Risk Level: {"CRITICAL" if critical > 0 else "HIGH" if high > 0 else "MEDIUM" if medium > 0 else "LOW"}

Recommendation: {"Requires immediate attention and careful migration planning" if critical > 0 else "Plan migration carefully with affected teams" if high > 0 else "Standard migration process recommended"}
"""
        return summary
    
    def calculate_risk_score(self, breaking_changes: List[BreakingChange]) -> float:
        """Calculate overall risk score (0-10)"""
        if not breaking_changes:
            return 0.0
        
        score = 0.0
        
        for change in breaking_changes:
            if change.impact_level == ImpactLevel.CRITICAL:
                score += 3.0
            elif change.impact_level == ImpactLevel.HIGH:
                score += 2.0
            elif change.impact_level == ImpactLevel.MEDIUM:
                score += 1.0
            elif change.impact_level == ImpactLevel.LOW:
                score += 0.5
        
        # Normalize to 0-10 scale
        return min(10.0, score)
