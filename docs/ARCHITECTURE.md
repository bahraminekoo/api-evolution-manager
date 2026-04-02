# API Evolution Manager - Architecture

## System Overview

The API Evolution Manager is a multi-agent AI system that analyzes API evolution using LangChain and LangGraph. It follows a pipeline architecture where specialized agents work together to provide comprehensive API migration analysis.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                           │
│              (React Dashboard / API Client)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                  (REST API Endpoints)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Orchestrator Agent                          │
│            (Coordinates workflow execution)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph Workflow                          │
│              (State Machine Orchestration)                   │
└─────┬──────┬──────┬──────┬──────┬──────┬──────┬────────────┘
      │      │      │      │      │      │      │
      ▼      ▼      ▼      ▼      ▼      ▼      ▼
   ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐
   │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │ │ 6  │ │ 7  │
   └────┘ └────┘ └────┘ └────┘ └────┘ └────┘ └────┘
   Spec   Spec   Spec   Usage  Impact Migration Final
   Old    New    Comp   Track  Assess Generate  Result
```

## Agent Responsibilities

### 1. Spec Analyzer Agent
**Purpose**: Analyze OpenAPI specifications

**Capabilities**:
- Parse OpenAPI 3.0 JSON specs
- Extract endpoints, parameters, schemas
- Identify deprecated endpoints
- Calculate API complexity scores
- Compare two API versions

**LLM Usage**: Uses GPT-4 to provide insights on API design patterns and complexity

### 2. Usage Tracker Agent
**Purpose**: Analyze API usage patterns

**Capabilities**:
- Parse usage data (mock or real logs)
- Identify high-traffic endpoints
- Map client dependencies
- Calculate usage statistics
- Estimate migration impact per endpoint

**LLM Usage**: Generates insights about usage patterns and recommendations

### 3. Impact Assessor Agent
**Purpose**: Detect and assess breaking changes

**Capabilities**:
- Compare old vs new API specs
- Detect breaking changes (removed endpoints, changed parameters, etc.)
- Calculate impact levels (Critical, High, Medium, Low)
- Generate impact summaries
- Calculate risk scores

**LLM Usage**: Assesses migration complexity and generates comprehensive impact reports

### 4. Migration Generator Agent
**Purpose**: Create migration guides

**Capabilities**:
- Generate step-by-step migration instructions
- Create before/after code examples
- Estimate effort and timeline
- Provide client-specific recommendations
- Suggest rollback strategies

**LLM Usage**: Generates migration overviews, code examples, and strategic recommendations

### 5. Orchestrator Agent
**Purpose**: Coordinate the entire workflow

**Capabilities**:
- Load and validate input data
- Execute LangGraph workflow
- Handle errors and retries
- Return final analysis results

## LangGraph Workflow

The workflow is implemented as a state machine with the following nodes:

```python
1. analyze_old_spec     → Analyze v1 API
2. analyze_new_spec     → Analyze v2 API
3. compare_specs        → High-level comparison
4. analyze_usage        → Usage pattern analysis
5. assess_impact        → Breaking change detection
6. generate_migration   → Migration guide creation
7. finalize_result      → Package final result
```

### State Management

The workflow maintains a shared state (`WorkflowState`) that includes:
- API specifications (old and new)
- Usage data
- Analysis results from each agent
- Breaking changes list
- Migration guide
- Final analysis result

## Data Models

### Core Models

1. **APISpec**: Represents an OpenAPI specification
   - Endpoints, parameters, schemas
   - Version, title, description

2. **UsageData**: Represents API usage patterns
   - Endpoint usage statistics
   - Client information
   - Call volumes, error rates

3. **BreakingChange**: Represents a detected breaking change
   - Change type, description
   - Impact level, affected clients
   - Usage count, migration complexity

4. **MigrationGuide**: Complete migration guide
   - Overview, steps, timeline
   - Code examples, rollback strategy
   - Client-specific notes

5. **AnalysisResult**: Final output
   - All breaking changes
   - Migration guide
   - Summary, risk score

## Technology Stack

### Backend
- **Python 3.10+**: Core language
- **LangChain**: LLM framework and agent tools
- **LangGraph**: State machine orchestration
- **FastAPI**: REST API framework
- **Pydantic**: Data validation
- **OpenAI GPT-4**: Language model

### Frontend (Planned)
- **React + TypeScript**: UI framework
- **TailwindCSS**: Styling
- **shadcn/ui**: Component library
- **Recharts**: Data visualization

## Scalability Considerations

### Current Implementation
- Synchronous workflow execution
- In-memory state management
- Mock usage data

### Future Enhancements
- Async workflow execution
- Database for storing analysis results
- Real log file parsing
- Caching for repeated analyses
- Batch processing for multiple APIs
- WebSocket for real-time updates

## Security Considerations

1. **API Key Management**: OpenAI keys stored in environment variables
2. **Input Validation**: All inputs validated with Pydantic
3. **CORS**: Configured for specific origins
4. **File Upload**: Validates OpenAPI spec format
5. **Error Handling**: Sanitized error messages

## Performance

### Typical Analysis Time
- Small API (< 20 endpoints): 30-60 seconds
- Medium API (20-50 endpoints): 1-2 minutes
- Large API (> 50 endpoints): 2-5 minutes

### Bottlenecks
- LLM API calls (can be parallelized)
- Code example generation (most time-consuming)

### Optimization Strategies
- Cache LLM responses for similar changes
- Parallel agent execution where possible
- Batch LLM requests
- Use faster models for simple tasks

## Error Handling

Each agent includes fallback mechanisms:
- If LLM fails, use rule-based analysis
- Graceful degradation of features
- Detailed error logging
- User-friendly error messages

## Testing Strategy

1. **Unit Tests**: Individual agent functions
2. **Integration Tests**: Workflow execution
3. **End-to-End Tests**: API endpoints
4. **Mock Data Tests**: Validate with known scenarios

## Deployment

### Development
```bash
uvicorn src.api.main:app --reload
```

### Production (Future)
- Docker containerization
- Environment-based configuration
- Load balancing for multiple instances
- Monitoring and logging
