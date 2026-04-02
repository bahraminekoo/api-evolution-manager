# Quick Start Guide

Get the API Evolution Manager running in 5 minutes!

## Step 1: Set Up Environment (2 minutes)

```bash
# Navigate to project
cd /home/hossein/CascadeProjects/APIEvolutionManager

# Create .env file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

Add your OpenAI API key:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

## Step 2: Install Dependencies (2 minutes)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 3: Run the Demo (1 minute)

### Option A: Command Line Test
```bash
python test_analysis.py
```

### Option B: Web Dashboard

**Terminal 1 - Start Backend:**
```bash
./start_backend.sh
```

**Terminal 2 - Start Frontend:**
```bash
./start_frontend.sh
```

Then open http://localhost:5173 and click "Run Demo Analysis"

## What You'll See

- **12 Breaking Changes** detected
- **Risk Score: 7.5/10**
- **4 Affected Clients** identified
- **40+ hours** migration effort estimated
- **90 days** recommended timeline
- **Step-by-step migration guide** with code examples

## Next Steps

- Read the full [Getting Started Guide](docs/GETTING_STARTED.md)
- Review the [Architecture Documentation](docs/ARCHITECTURE.md)
- Check out the [Demo Guide](docs/DEMO_GUIDE.md) for presentation tips

## Troubleshooting

**Backend won't start?**
- Make sure you added your OpenAI API key to `.env`
- Activate the virtual environment: `source backend/venv/bin/activate`

**Frontend can't connect?**
- Make sure backend is running on port 8000
- Check http://localhost:8000/api/health

**Need help?**
- Check the detailed docs in the `docs/` folder
- Review the API documentation at http://localhost:8000/docs
