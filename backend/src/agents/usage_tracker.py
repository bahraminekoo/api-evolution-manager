from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, List
from ..models.usage_data import UsageData, EndpointUsage
from ..utils.config import settings


class UsageTrackerAgent:
    """Agent responsible for analyzing API usage patterns"""
    
    def __init__(self):
        llm_params = {
            "model": settings.openai_model,
            "temperature": 0.1,
            "api_key": settings.openai_api_key
        }
        if settings.openai_base_url:
            llm_params["base_url"] = settings.openai_base_url
        self.llm = ChatOpenAI(**llm_params)
    
    def analyze_usage_patterns(self, usage_data: UsageData) -> str:
        """Analyze usage patterns and generate insights"""
        
        usage_summary = self._create_usage_summary(usage_data)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in API usage analysis. Analyze the usage patterns and provide actionable insights.

Focus on:
- Most heavily used endpoints
- Endpoints with low usage that might be candidates for deprecation
- Client distribution and dependencies
- Error rates and potential issues
- Usage trends and patterns"""),
            ("user", "Usage Data:\n{usage_summary}\n\nProvide key insights and recommendations.")
        ])
        
        chain = prompt | self.llm
        
        try:
            result = chain.invoke({"usage_summary": usage_summary})
            return result.content
        except Exception as e:
            return f"Error analyzing usage: {str(e)}"
    
    def identify_critical_endpoints(self, usage_data: UsageData, threshold: int = 1000) -> List[str]:
        """Identify endpoints that are critical based on usage"""
        critical = []
        
        for endpoint_key, usage in usage_data.endpoint_usage.items():
            if usage.total_calls >= threshold or usage.unique_clients >= 2:
                critical.append(endpoint_key)
        
        return critical
    
    def get_client_dependencies(self, usage_data: UsageData) -> Dict[str, List[str]]:
        """Map which clients depend on which endpoints"""
        client_deps = {}
        
        for client in usage_data.clients:
            client_deps[client.name] = []
        
        for endpoint_key, usage in usage_data.endpoint_usage.items():
            for client_name in usage.clients:
                if client_name in client_deps:
                    client_deps[client_name].append(endpoint_key)
        
        return client_deps
    
    def _create_usage_summary(self, usage_data: UsageData) -> str:
        """Create a text summary of usage data"""
        lines = [
            f"API Version: {usage_data.api_version}",
            f"Analysis Period: {usage_data.time_period_days} days",
            f"Total Requests: {usage_data.total_requests:,}",
            f"Total Clients: {len(usage_data.clients)}",
            f"\nClients:"
        ]
        
        for client in usage_data.clients:
            lines.append(f"  - {client.name} (v{client.version})")
        
        lines.append(f"\nEndpoint Usage (Top 10 by calls):")
        
        sorted_usage = sorted(
            usage_data.endpoint_usage.items(),
            key=lambda x: x[1].total_calls,
            reverse=True
        )[:10]
        
        for endpoint_key, usage in sorted_usage:
            lines.append(
                f"  {endpoint_key}: {usage.total_calls:,} calls, "
                f"{usage.unique_clients} clients, "
                f"{usage.error_rate:.1%} error rate"
            )
            lines.append(f"    Clients: {', '.join(usage.clients)}")
        
        return "\n".join(lines)
    
    def estimate_migration_impact(
        self,
        endpoint_key: str,
        usage_data: UsageData
    ) -> Dict[str, any]:
        """Estimate the impact of changing/removing an endpoint"""
        usage = usage_data.get_usage_for_endpoint(endpoint_key)
        
        if not usage:
            return {
                "impact": "low",
                "affected_clients": [],
                "daily_calls": 0,
                "recommendation": "Safe to modify - no usage detected"
            }
        
        impact_level = "low"
        if usage.total_calls >= 5000 or usage.unique_clients >= 3:
            impact_level = "critical"
        elif usage.total_calls >= 1000 or usage.unique_clients >= 2:
            impact_level = "high"
        elif usage.total_calls >= 100:
            impact_level = "medium"
        
        return {
            "impact": impact_level,
            "affected_clients": usage.clients,
            "daily_calls": usage.avg_calls_per_day,
            "total_calls": usage.total_calls,
            "unique_clients": usage.unique_clients,
            "recommendation": self._get_recommendation(impact_level, usage)
        }
    
    def _get_recommendation(self, impact_level: str, usage: EndpointUsage) -> str:
        """Get recommendation based on impact level"""
        if impact_level == "critical":
            return (
                f"HIGH PRIORITY: This endpoint is heavily used by {usage.unique_clients} clients. "
                f"Requires careful migration planning and extended deprecation period."
            )
        elif impact_level == "high":
            return (
                f"MODERATE PRIORITY: Significant usage detected. "
                f"Coordinate with affected teams before making changes."
            )
        elif impact_level == "medium":
            return "LOW-MEDIUM PRIORITY: Some usage detected. Provide migration guide."
        else:
            return "LOW PRIORITY: Minimal usage. Standard deprecation process is sufficient."
