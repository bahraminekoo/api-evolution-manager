from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class ImpactLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NONE = "none"


class ChangeType(str, Enum):
    ENDPOINT_REMOVED = "endpoint_removed"
    ENDPOINT_ADDED = "endpoint_added"
    PARAMETER_REMOVED = "parameter_removed"
    PARAMETER_ADDED = "parameter_added"
    PARAMETER_TYPE_CHANGED = "parameter_type_changed"
    PARAMETER_REQUIRED_CHANGED = "parameter_required_changed"
    RESPONSE_SCHEMA_CHANGED = "response_schema_changed"
    REQUEST_SCHEMA_CHANGED = "request_schema_changed"
    ENDPOINT_DEPRECATED = "endpoint_deprecated"


class BreakingChange(BaseModel):
    change_type: ChangeType
    endpoint_key: str
    description: str
    impact_level: ImpactLevel
    affected_clients: List[str] = Field(default_factory=list)
    usage_count: int = 0
    details: Dict[str, Any] = Field(default_factory=dict)
    migration_complexity: str = "medium"


class MigrationStep(BaseModel):
    step_number: int
    title: str
    description: str
    code_example_before: Optional[str] = None
    code_example_after: Optional[str] = None
    estimated_effort_hours: float = 1.0


class MigrationGuide(BaseModel):
    from_version: str
    to_version: str
    overview: str
    total_breaking_changes: int
    estimated_total_effort_hours: float
    recommended_timeline_days: int
    steps: List[MigrationStep] = Field(default_factory=list)
    client_specific_notes: Dict[str, str] = Field(default_factory=dict)
    rollback_strategy: Optional[str] = None


class AnalysisResult(BaseModel):
    analysis_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    old_version: str
    new_version: str
    breaking_changes: List[BreakingChange] = Field(default_factory=list)
    non_breaking_changes: List[Dict[str, Any]] = Field(default_factory=list)
    migration_guide: Optional[MigrationGuide] = None
    summary: str = ""
    total_affected_clients: int = 0
    risk_score: float = 0.0
    
    def get_critical_changes(self) -> List[BreakingChange]:
        return [
            change for change in self.breaking_changes
            if change.impact_level == ImpactLevel.CRITICAL
        ]
    
    def get_high_impact_changes(self) -> List[BreakingChange]:
        return [
            change for change in self.breaking_changes
            if change.impact_level in [ImpactLevel.CRITICAL, ImpactLevel.HIGH]
        ]
