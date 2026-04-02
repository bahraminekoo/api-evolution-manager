from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime


class ClientInfo(BaseModel):
    name: str
    version: Optional[str] = None
    contact: Optional[str] = None


class EndpointUsage(BaseModel):
    endpoint_key: str
    total_calls: int = 0
    unique_clients: int = 0
    clients: List[str] = Field(default_factory=list)
    avg_calls_per_day: float = 0.0
    last_used: Optional[datetime] = None
    error_rate: float = 0.0


class UsageData(BaseModel):
    api_version: str
    time_period_days: int = 30
    total_requests: int = 0
    endpoint_usage: Dict[str, EndpointUsage] = Field(default_factory=dict)
    clients: List[ClientInfo] = Field(default_factory=list)
    
    def get_usage_for_endpoint(self, endpoint_key: str) -> Optional[EndpointUsage]:
        return self.endpoint_usage.get(endpoint_key)
    
    def get_high_usage_endpoints(self, threshold: int = 1000) -> List[EndpointUsage]:
        return [
            usage for usage in self.endpoint_usage.values()
            if usage.total_calls >= threshold
        ]
