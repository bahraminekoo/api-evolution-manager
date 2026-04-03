# API Evolution Manager

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![LangChain](https://img.shields.io/badge/LangChain-🦜-green.svg)](https://python.langchain.com/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)

An intelligent multi-agent AI system built with LangChain and LangGraph that helps developers manage REST API evolution by analyzing usage patterns, detecting breaking changes, and generating comprehensive migration guides.

## � Live Demo

![API Evolution Manager Demo](assets/API%20Evolution%20Demo.gif)

*Watch the multi-agent system analyze API changes, detect breaking changes, and generate migration guides in real-time*

## �🎯 Overview

API Evolution Manager solves a critical problem that current AI assistants don't handle well: managing API changes across multiple codebases. It uses a sophisticated multi-agent architecture to:

- **Analyze API specifications** using OpenAPI 3.0 specs
- **Track usage patterns** to understand real-world impact
- **Detect breaking changes** automatically
- **Assess impact** based on actual usage data
- **Generate migration guides** with code examples
- **Provide client-specific recommendations**

## 🤖 Multi-Agent Architecture

The system uses **5 specialized LangChain agents** orchestrated via **LangGraph**:

1. **Spec Analyzer Agent** - Parses and analyzes OpenAPI specifications
2. **Usage Tracker Agent** - Analyzes API usage patterns and identifies critical endpoints
3. **Impact Assessor Agent** - Detects breaking changes and calculates impact scores
4. **Migration Generator Agent** - Creates step-by-step migration guides with code examples
5. **Orchestrator Agent** - Coordinates the workflow using LangGraph state machines

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key
- Node.js 18+ (for frontend)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../.env.example ../.env
# Edit .env and add your OPENAI_API_KEY
```

### Run Demo Analysis

```bash
# Test the backend with mock data
python test_analysis.py
```

### Start API Server

```bash
# Start FastAPI server
uvicorn src.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 📊 Demo Scenario

The included mock data demonstrates an e-commerce API upgrading from v1.0.0 to v2.0.0 with several breaking changes:

### Breaking Changes Detected:
- ❌ `DELETE /users/{id}` endpoint removed
- ⚠️ Pagination parameters changed (`limit/offset` → `page/page_size`)
- ⚠️ Request body fields renamed (`user_id` → `customer_id`)
- ⚠️ New required fields added

### Impact Analysis:
- **3-4 critical changes** affecting multiple clients
- **15,000+ API calls/day** impacted
- **4 client applications** need updates
- **40+ hours** estimated migration effort
- **90 days** recommended timeline

## 🔧 API Endpoints

### `POST /api/analyze/demo`
Run analysis on demo data (no parameters needed)

```bash
curl -X POST http://localhost:8000/api/analyze/demo
```

### `POST /api/analyze`
Analyze custom API specs

```json
{
  "old_spec_path": "/path/to/v1_spec.json",
  "new_spec_path": "/path/to/v2_spec.json",
  "usage_data_path": "/path/to/usage.json"
}
```

### `GET /api/health`
Health check endpoint

## 📁 Project Structure

```
APIEvolutionManager/
├── backend/
│   ├── src/
│   │   ├── agents/              # LangChain agents
│   │   │   ├── orchestrator.py
│   │   │   ├── spec_analyzer.py
│   │   │   ├── usage_tracker.py
│   │   │   ├── impact_assessor.py
│   │   │   └── migration_generator.py
│   │   ├── models/              # Pydantic data models
│   │   ├── tools/               # Utility tools
│   │   ├── workflows/           # LangGraph workflows
│   │   ├── api/                 # FastAPI endpoints
│   │   └── utils/               # Configuration
│   ├── mock_data/               # Demo data
│   ├── test_analysis.py         # Test script
│   └── requirements.txt
├── frontend/                    # Web dashboard
├── docs/                        # Documentation
└── README.md
```

## 🎨 Key Features

### 1. Intelligent Breaking Change Detection
- Not just structural diff - understands semantic impact
- Considers actual usage patterns
- Prioritizes by business impact

### 2. Multi-Agent Collaboration
- Clear separation of concerns
- LangGraph state management
- Coordinated agent workflows

### 3. Comprehensive Migration Guides
- Step-by-step instructions
- Before/after code examples
- Effort estimation
- Client-specific recommendations
- Rollback strategies

### 4. Usage-Based Impact Assessment
- Analyzes real usage data
- Identifies critical endpoints
- Maps client dependencies
- Calculates risk scores

## �️ Technology Stack

- **AI/ML**: LangChain, LangGraph, OpenAI GPT-4
- **Backend**: Python 3.10+, FastAPI, Pydantic
- **Data Validation**: OpenAPI 3.0 spec validation
- **Testing**: pytest, pytest-asyncio
- **Architecture**: Multi-agent system with state management

## 🔮 Future Enhancements

- [ ] React dashboard with interactive visualizations
- [ ] Real log file parsing (nginx, application logs)
- [ ] GitHub integration for automatic PR analysis
- [ ] Export migration guides as Markdown/PDF
- [ ] Email notifications for breaking changes
- [ ] GraphQL API support
- [ ] Multi-language SDK generation

## 📝 Example Output

```
🚀 Starting API Evolution Analysis
   Old Version: 1.0.0
   New Version: 2.0.0
   Usage Period: 30 days

📊 Analyzing old API specification...
📊 Analyzing new API specification...
🔍 Comparing API specifications...
📈 Analyzing usage patterns...
⚠️  Assessing impact of changes...
📝 Generating migration guide...
✅ Finalizing analysis result...

✨ Analysis complete!
   Breaking Changes: 12
   Risk Score: 7.5/10
   Affected Clients: 4
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

MIT License - See LICENSE file for details.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://python.langchain.com/) - LLM framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) - Agent orchestration
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [OpenAI](https://openai.com/) - GPT-4 language model
