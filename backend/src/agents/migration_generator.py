from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from typing import List, Dict
from datetime import datetime, timedelta
from ..models.api_spec import APISpec
from ..models.usage_data import UsageData
from ..models.analysis_result import (
    BreakingChange, MigrationGuide, MigrationStep, ImpactLevel
)
from ..utils.config import settings


class MigrationGeneratorAgent:
    """Agent responsible for generating migration guides"""
    
    def __init__(self):
        llm_params = {
            "model": settings.openai_model,
            "temperature": 0.3,
            "api_key": settings.openai_api_key
        }
        if settings.openai_base_url:
            llm_params["base_url"] = settings.openai_base_url
        self.llm = ChatOpenAI(**llm_params)
    
    def generate_migration_guide(
        self,
        old_spec: APISpec,
        new_spec: APISpec,
        breaking_changes: List[BreakingChange],
        usage_data: UsageData
    ) -> MigrationGuide:
        """Generate a comprehensive migration guide"""
        
        # Generate overview
        overview = self._generate_overview(old_spec, new_spec, breaking_changes)
        
        # Generate migration steps
        steps = self._generate_migration_steps(breaking_changes, old_spec, new_spec)
        
        # Calculate effort and timeline
        total_effort = sum(step.estimated_effort_hours for step in steps)
        timeline_days = self._calculate_timeline(breaking_changes, total_effort)
        
        # Generate client-specific notes
        client_notes = self._generate_client_notes(breaking_changes, usage_data)
        
        # Generate rollback strategy
        rollback = self._generate_rollback_strategy(old_spec, new_spec)
        
        return MigrationGuide(
            from_version=old_spec.version,
            to_version=new_spec.version,
            overview=overview,
            total_breaking_changes=len(breaking_changes),
            estimated_total_effort_hours=total_effort,
            recommended_timeline_days=timeline_days,
            steps=steps,
            client_specific_notes=client_notes,
            rollback_strategy=rollback
        )
    
    def _generate_overview(
        self,
        old_spec: APISpec,
        new_spec: APISpec,
        breaking_changes: List[BreakingChange]
    ) -> str:
        """Generate migration overview using LLM"""
        
        changes_summary = "\n".join([
            f"- {change.description} (Impact: {change.impact_level.value})"
            for change in breaking_changes[:10]
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technical writer creating API migration guides.
            
Generate a clear, concise overview for migrating from one API version to another.

Include:
- What's changing and why
- Who is affected
- High-level migration approach
- Key risks to be aware of

Keep it under 200 words."""),
            ("user", """API Migration: {old_version} → {new_version}

Breaking Changes:
{changes_summary}

Generate the migration overview.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "old_version": old_spec.version,
                "new_version": new_spec.version,
                "changes_summary": changes_summary
            })
            return result.content
        except Exception:
            return self._basic_overview(old_spec, new_spec, breaking_changes)
    
    def _basic_overview(
        self,
        old_spec: APISpec,
        new_spec: APISpec,
        breaking_changes: List[BreakingChange]
    ) -> str:
        """Generate basic overview without LLM"""
        critical = sum(1 for c in breaking_changes if c.impact_level == ImpactLevel.CRITICAL)
        high = sum(1 for c in breaking_changes if c.impact_level == ImpactLevel.HIGH)
        
        return f"""Migration Guide: {old_spec.title} v{old_spec.version} → v{new_spec.version}

This guide covers the migration from API version {old_spec.version} to {new_spec.version}. 
There are {len(breaking_changes)} breaking changes that require attention, including {critical} critical 
and {high} high-impact changes.

All API consumers must update their implementations to maintain compatibility. 
This migration requires careful planning and testing before deployment."""
    
    def _generate_migration_steps(
        self,
        breaking_changes: List[BreakingChange],
        old_spec: APISpec,
        new_spec: APISpec
    ) -> List[MigrationStep]:
        """Generate detailed migration steps"""
        
        steps = []
        step_number = 1
        
        # Sort by impact level
        sorted_changes = sorted(
            breaking_changes,
            key=lambda x: (
                0 if x.impact_level == ImpactLevel.CRITICAL else
                1 if x.impact_level == ImpactLevel.HIGH else
                2 if x.impact_level == ImpactLevel.MEDIUM else 3
            )
        )
        
        for change in sorted_changes:
            if change.impact_level == ImpactLevel.NONE:
                continue
            
            step = self._create_migration_step(change, step_number, old_spec, new_spec)
            if step:
                steps.append(step)
                step_number += 1
        
        return steps
    
    def _create_migration_step(
        self,
        change: BreakingChange,
        step_number: int,
        old_spec: APISpec,
        new_spec: APISpec
    ) -> MigrationStep:
        """Create a single migration step with code examples"""
        
        # Generate code examples using LLM
        code_before, code_after = self._generate_code_examples(change, old_spec, new_spec)
        
        # Estimate effort
        effort = self._estimate_effort(change)
        
        return MigrationStep(
            step_number=step_number,
            title=f"Migrate {change.endpoint_key}",
            description=change.description,
            code_example_before=code_before,
            code_example_after=code_after,
            estimated_effort_hours=effort
        )
    
    def _generate_code_examples(
        self,
        change: BreakingChange,
        old_spec: APISpec,
        new_spec: APISpec
    ) -> tuple[str, str]:
        """Generate before/after code examples using LLM"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert developer creating migration examples.

Generate realistic "before" and "after" code examples in JavaScript/TypeScript for this API change.

Format:
BEFORE:
```javascript
// code here
```

AFTER:
```javascript
// code here
```

Keep examples concise (5-10 lines each) and practical."""),
            ("user", """Change Type: {change_type}
Endpoint: {endpoint_key}
Description: {description}
Details: {details}

Generate code examples.""")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "change_type": change.change_type.value,
                "endpoint_key": change.endpoint_key,
                "description": change.description,
                "details": str(change.details)
            })
            
            content = result.content
            
            # Parse before/after from response
            if "BEFORE:" in content and "AFTER:" in content:
                before_part = content.split("BEFORE:")[1].split("AFTER:")[0].strip()
                after_part = content.split("AFTER:")[1].strip()
                
                # Extract code from markdown blocks
                before = self._extract_code(before_part)
                after = self._extract_code(after_part)
                
                return before, after
        except Exception:
            pass
        
        # Fallback to basic examples
        return self._basic_code_examples(change)
    
    def _extract_code(self, text: str) -> str:
        """Extract code from markdown code blocks"""
        if "```" in text:
            parts = text.split("```")
            if len(parts) >= 2:
                code = parts[1]
                # Remove language identifier
                if "\n" in code:
                    code = "\n".join(code.split("\n")[1:])
                return code.strip()
        return text.strip()
    
    def _basic_code_examples(self, change: BreakingChange) -> tuple[str, str]:
        """Generate basic code examples without LLM"""
        endpoint = change.endpoint_key
        
        if "PARAMETER_REMOVED" in change.change_type.value:
            param = change.details.get("parameter", "param")
            before = f"// Old API call\nfetch('/api{endpoint.split(' ')[1]}?{param}=value')"
            after = f"// New API call (parameter removed)\nfetch('/api{endpoint.split(' ')[1]}')"
        elif "ENDPOINT_REMOVED" in change.change_type.value:
            before = f"// Old API call\nfetch('/api{endpoint.split(' ')[1]}')"
            after = f"// Endpoint removed - use alternative endpoint\n// Contact API team for migration path"
        else:
            before = f"// Old API implementation\n// {change.description}"
            after = f"// New API implementation\n// Update required based on changes"
        
        return before, after
    
    def _estimate_effort(self, change: BreakingChange) -> float:
        """Estimate effort in hours for this change"""
        base_effort = 2.0
        
        if change.impact_level == ImpactLevel.CRITICAL:
            base_effort *= 3
        elif change.impact_level == ImpactLevel.HIGH:
            base_effort *= 2
        elif change.impact_level == ImpactLevel.MEDIUM:
            base_effort *= 1.5
        
        # Add effort based on number of affected clients
        base_effort += len(change.affected_clients) * 0.5
        
        return round(base_effort, 1)
    
    def _calculate_timeline(
        self,
        breaking_changes: List[BreakingChange],
        total_effort_hours: float
    ) -> int:
        """Calculate recommended timeline in days"""
        # Base timeline on effort and impact
        critical_count = sum(1 for c in breaking_changes if c.impact_level == ImpactLevel.CRITICAL)
        
        # Minimum 30 days for any breaking changes
        min_days = 30
        
        # Add days based on effort (assuming 4 hours/day of migration work)
        effort_days = int(total_effort_hours / 4)
        
        # Add buffer for critical changes
        critical_buffer = critical_count * 14
        
        return max(min_days, effort_days + critical_buffer)
    
    def _generate_client_notes(
        self,
        breaking_changes: List[BreakingChange],
        usage_data: UsageData
    ) -> Dict[str, str]:
        """Generate client-specific migration notes"""
        client_notes = {}
        
        for client in usage_data.clients:
            affected_changes = [
                c for c in breaking_changes
                if client.name in c.affected_clients
            ]
            
            if affected_changes:
                note = f"Client '{client.name}' is affected by {len(affected_changes)} breaking changes:\n"
                for change in affected_changes[:5]:
                    note += f"- {change.endpoint_key}: {change.description}\n"
                
                if len(affected_changes) > 5:
                    note += f"... and {len(affected_changes) - 5} more changes\n"
                
                note += f"\nContact: {client.contact or 'N/A'}"
                client_notes[client.name] = note
        
        return client_notes
    
    def _generate_rollback_strategy(
        self,
        old_spec: APISpec,
        new_spec: APISpec
    ) -> str:
        """Generate rollback strategy"""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in API deployment strategies.

Generate a concise rollback strategy for this API migration.

Include:
- How to rollback if issues occur
- What to monitor
- Rollback triggers
- Data considerations

Keep it under 150 words."""),
            ("user", "API Migration: {old_version} → {new_version}\n\nGenerate rollback strategy.")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({
                "old_version": old_spec.version,
                "new_version": new_spec.version
            })
            return result.content
        except Exception:
            return """Rollback Strategy:
1. Keep v1 API running in parallel during migration period
2. Monitor error rates, latency, and client feedback
3. Rollback triggers: >5% error rate increase, critical client failures
4. Rollback process: Route traffic back to v1 endpoints
5. Ensure database schema is backward compatible
6. Maintain v1 for at least 90 days post-migration"""
