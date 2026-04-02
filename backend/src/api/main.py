from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import tempfile
import os

from ..agents.orchestrator import OrchestratorAgent
from ..models.api_spec import APISpec
from ..models.usage_data import UsageData
from ..models.analysis_result import AnalysisResult
from ..tools.spec_parser import SpecParser

app = FastAPI(
    title="API Evolution Manager",
    description="Intelligent API evolution analysis and migration planning",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = OrchestratorAgent()
spec_parser = SpecParser()


class AnalysisRequest(BaseModel):
    old_spec_path: str
    new_spec_path: str
    usage_data_path: str


class AnalysisResponse(BaseModel):
    analysis_id: str
    old_version: str
    new_version: str
    total_breaking_changes: int
    critical_changes: int
    high_impact_changes: int
    risk_score: float
    total_affected_clients: int
    estimated_effort_hours: float
    recommended_timeline_days: int


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "API Evolution Manager",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "agents": {
            "orchestrator": "ready",
            "spec_analyzer": "ready",
            "usage_tracker": "ready",
            "impact_assessor": "ready",
            "migration_generator": "ready"
        }
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_api_evolution(request: AnalysisRequest):
    """
    Analyze API evolution between two versions
    
    Expects paths to:
    - old_spec_path: OpenAPI 3.0 spec for old version
    - new_spec_path: OpenAPI 3.0 spec for new version
    - usage_data_path: Usage data JSON file
    """
    try:
        # Run analysis
        result = orchestrator.analyze_api_evolution(
            request.old_spec_path,
            request.new_spec_path,
            request.usage_data_path
        )
        
        # Count critical and high impact changes
        critical_count = len(result.get_critical_changes())
        high_impact_count = len(result.get_high_impact_changes())
        
        return AnalysisResponse(
            analysis_id=result.analysis_id,
            old_version=result.old_version,
            new_version=result.new_version,
            total_breaking_changes=len(result.breaking_changes),
            critical_changes=critical_count,
            high_impact_changes=high_impact_count,
            risk_score=result.risk_score,
            total_affected_clients=result.total_affected_clients,
            estimated_effort_hours=result.migration_guide.estimated_total_effort_hours if result.migration_guide else 0,
            recommended_timeline_days=result.migration_guide.recommended_timeline_days if result.migration_guide else 0
        )
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"File not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@app.get("/api/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str):
    """Get full analysis result by ID (placeholder - would need database)"""
    raise HTTPException(status_code=501, detail="Not implemented - requires database")


@app.post("/api/analyze/demo")
async def analyze_demo():
    """
    Run analysis on demo data
    
    Uses the pre-configured mock data for demonstration
    """
    try:
        # Use mock data paths
        base_path = os.path.join(os.path.dirname(__file__), "../../../mock_data")
        
        old_spec_path = os.path.join(base_path, "v1_api_spec.json")
        new_spec_path = os.path.join(base_path, "v2_api_spec.json")
        usage_data_path = os.path.join(base_path, "usage_logs.json")
        
        # Run analysis
        result = orchestrator.analyze_api_evolution(
            old_spec_path,
            new_spec_path,
            usage_data_path
        )
        
        # Return full result for demo
        return {
            "analysis_id": result.analysis_id,
            "timestamp": result.timestamp.isoformat(),
            "old_version": result.old_version,
            "new_version": result.new_version,
            "summary": result.summary,
            "risk_score": result.risk_score,
            "total_affected_clients": result.total_affected_clients,
            "breaking_changes": [
                {
                    "change_type": change.change_type.value,
                    "endpoint_key": change.endpoint_key,
                    "description": change.description,
                    "impact_level": change.impact_level.value,
                    "affected_clients": change.affected_clients,
                    "usage_count": change.usage_count,
                    "migration_complexity": change.migration_complexity
                }
                for change in result.breaking_changes
            ],
            "migration_guide": {
                "from_version": result.migration_guide.from_version,
                "to_version": result.migration_guide.to_version,
                "overview": result.migration_guide.overview,
                "total_breaking_changes": result.migration_guide.total_breaking_changes,
                "estimated_total_effort_hours": result.migration_guide.estimated_total_effort_hours,
                "recommended_timeline_days": result.migration_guide.recommended_timeline_days,
                "steps": [
                    {
                        "step_number": step.step_number,
                        "title": step.title,
                        "description": step.description,
                        "code_example_before": step.code_example_before,
                        "code_example_after": step.code_example_after,
                        "estimated_effort_hours": step.estimated_effort_hours
                    }
                    for step in result.migration_guide.steps
                ],
                "client_specific_notes": result.migration_guide.client_specific_notes,
                "rollback_strategy": result.migration_guide.rollback_strategy
            } if result.migration_guide else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo analysis failed: {str(e)}")


@app.post("/api/upload/spec")
async def upload_spec(file: UploadFile = File(...)):
    """Upload an OpenAPI spec file"""
    try:
        content = await file.read()
        spec_data = json.loads(content)
        
        # Validate it's a valid OpenAPI spec
        spec = spec_parser.parse_openapi_spec(spec_data)
        
        return {
            "status": "success",
            "filename": file.filename,
            "version": spec.version,
            "title": spec.title,
            "endpoints": len(spec.endpoints)
        }
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid OpenAPI spec: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
