# Getting Started with API Evolution Manager

This guide will help you set up and run the API Evolution Manager on your local machine.

## Prerequisites

- **Python 3.10 or higher**
- **OpenAI API Key** (get one at https://platform.openai.com/api-keys)
- **Git** (for cloning the repository)

## Installation Steps

### 1. Clone or Navigate to the Project

```bash
cd /home/hossein/CascadeProjects/APIEvolutionManager
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4-turbo-preview
BACKEND_PORT=8000
FRONTEND_PORT=5173
LOG_LEVEL=INFO
```

### 3. Install Backend Dependencies

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Application

### Option 1: Using Startup Scripts (Recommended)

**Terminal 1 - Start Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
./start_frontend.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python -m uvicorn src.api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
python3 -m http.server 5173
```

## Accessing the Application

1. **Frontend Dashboard**: http://localhost:5173
2. **API Documentation**: http://localhost:8000/docs
3. **API Health Check**: http://localhost:8000/api/health

## Running the Demo

### Via Web Dashboard

1. Open http://localhost:5173 in your browser
2. Click the "Run Demo Analysis" button
3. Wait 30-60 seconds for the analysis to complete
4. Explore the results:
   - Summary metrics
   - Breaking changes
   - Migration guide with code examples

### Via Command Line

```bash
cd backend
source venv/bin/activate
python test_analysis.py
```

This will run the analysis and display results in the terminal.

### Via API (cURL)

```bash
curl -X POST http://localhost:8000/api/analyze/demo
```

## Understanding the Demo Data

The demo analyzes an e-commerce API upgrade from v1.0.0 to v2.0.0:

### Key Changes:
- ❌ `DELETE /users/{id}` endpoint removed
- ⚠️ Pagination changed from `limit/offset` to `page/page_size`
- ⚠️ Request body fields renamed (`user_id` → `customer_id`)
- ⚠️ New required fields added

### Mock Usage Data:
- 45,780 total API calls over 30 days
- 4 client applications affected
- 15,000+ calls/day on changed endpoints

## Testing with Your Own Data

### 1. Prepare Your API Specs

Create two OpenAPI 3.0 JSON files:
- `my_v1_spec.json` - Old API version
- `my_v2_spec.json` - New API version

### 2. Create Usage Data

Create a JSON file with this structure:

```json
{
  "api_version": "1.0.0",
  "time_period_days": 30,
  "total_requests": 10000,
  "clients": [
    {
      "name": "web-app",
      "version": "1.0.0",
      "contact": "team@example.com"
    }
  ],
  "endpoint_usage": {
    "GET /users": {
      "endpoint_key": "GET /users",
      "total_calls": 5000,
      "unique_clients": 1,
      "clients": ["web-app"],
      "avg_calls_per_day": 167,
      "last_used": "2026-04-01T12:00:00Z",
      "error_rate": 0.01
    }
  }
}
```

### 3. Run Analysis

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "old_spec_path": "/path/to/my_v1_spec.json",
    "new_spec_path": "/path/to/my_v2_spec.json",
    "usage_data_path": "/path/to/usage_data.json"
  }'
```

## Troubleshooting

### Backend won't start

**Error: "ModuleNotFoundError: No module named 'langchain'"**
- Solution: Make sure you activated the virtual environment and installed dependencies
  ```bash
  source backend/venv/bin/activate
  pip install -r backend/requirements.txt
  ```

**Error: "OpenAI API key not found"**
- Solution: Check that your `.env` file exists and contains a valid `OPENAI_API_KEY`

### Frontend can't connect to backend

**Error: "Failed to fetch" or CORS errors**
- Solution: Make sure the backend is running on port 8000
- Check that CORS is properly configured in `backend/src/api/main.py`

### Analysis takes too long

- The first run may take 1-2 minutes as it makes multiple LLM calls
- Subsequent runs with similar data may be faster
- For large APIs (50+ endpoints), expect 2-5 minutes

### OpenAI Rate Limits

If you hit rate limits:
- Wait a few minutes and try again
- Consider upgrading your OpenAI plan
- Reduce the number of endpoints in your test specs

## Next Steps

1. **Explore the Code**: Check out the multi-agent architecture in `backend/src/agents/`
2. **Read the Docs**: See `docs/ARCHITECTURE.md` for system design details
3. **Customize**: Modify agents to add custom analysis logic
4. **Extend**: Add support for GraphQL, gRPC, or other API types

## Getting Help

- Check the API documentation at http://localhost:8000/docs
- Review the architecture documentation in `docs/ARCHITECTURE.md`
- Look at the example mock data in `backend/mock_data/`

## Performance Tips

1. **Cache Results**: Store analysis results to avoid re-running
2. **Batch Requests**: Analyze multiple API pairs in sequence
3. **Use Faster Models**: Switch to `gpt-3.5-turbo` for quicker (but less detailed) results
4. **Parallel Processing**: Run multiple analyses in parallel (requires code changes)

## Security Notes

- Never commit your `.env` file with real API keys
- Use environment variables for all sensitive data
- Validate all uploaded API specs before processing
- Consider rate limiting for production use

## What's Next?

Now that you have the system running, try:
1. Running the demo analysis
2. Exploring the generated migration guide
3. Testing with your own API specs
4. Customizing the agents for your specific needs

Happy analyzing! 🚀
