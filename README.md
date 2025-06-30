# 🚀AI-powered-recruitment-agent


AI-powered recruitment agent that automatically sources LinkedIn candidates, scores them using advanced LLMs, and generates personalized outreach messages.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)


### Streamlit Deploy Project Link
https://ai-powered-recruitment-agent-i7uqzbmutnf5zmhcjzgmsf.streamlit.app/

## 🌟 Features

- **🔍 LinkedIn Profile Discovery**: Automated candidate search using SerpAPI Google Search
- **🧠 AI-Powered Scoring**: Intelligent candidate evaluation using Groq LLM (Llama 3.1 70B)
- **💌 Personalized Outreach**: Custom message generation for each candidate
- **📊 Professional JSON Export**: Structured results with scores and analytics
- **🌐 REST API**: FastAPI web interface for integration
- **⚡ Batch Processing**: Efficient handling of multiple candidates
- **🎯 Smart Matching**: Advanced regex patterns for company and role extraction

## 🏗️ Architecture

```
ai-sourcing-agent/
├── app/
│   ├── agent.py          # Main pipeline orchestrator
│   ├── scraper.py        # LinkedIn profile extraction
│   ├── scorer.py         # AI candidate scoring
│   ├── messenger.py      # Outreach message generation
│   └── __init__.py       # Package initialization
├── api/
│   └── main.py           # FastAPI REST endpoints
├── test_pipeline.py      # Demo script
├── requirements.txt      # Dependencies
├── .env                  # Environment variables (not tracked)
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- [Groq API Key](https://console.groq.com/) (Free tier available)
- [SerpAPI Key](https://serpapi.com/) (Free tier: 100 searches/month)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-sourcing-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   SERPAPI_API_KEY=your_serpapi_key_here
   ```

### 🎯 Run Demo

```bash
python test_pipeline.py
```

**Sample Output:**
```
🚀 AI SOURCING AGENT
============================================================
 STEP 1: LinkedIn Profile Discovery
🔍 Searching LinkedIn for 5 candidates...
  [1/5] Searching: Andrej Karpathy
Found: Andrej Karpathy at OpenAI (Former Tesla AI Director)

 STEP 2: AI-Powered Candidate Scoring
  [1/5] Scoring: Andrej Karpathy
 SCORE: 78.0/100 (Strong Fit)

 STEP 3: Personalized Outreach Generation
  [1/5] Generating message for: Andrej Karpathy
Message generated (430 characters)

🏆 Top candidate: Andrej Karpathy (78.0/100)
Results exported to: recruitment_results_software-engineer-abc123.json
```

## 🌐 API Usage

### Start the API Server

```bash
uvicorn api.main:app --reload
```

The API will be available at: `http://localhost:8000`

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information and available endpoints |
| GET | `/health` | Service health check |
| GET | `/docs` | Interactive API documentation (Swagger UI) |
| GET | `/sample-request` | Sample request format for testing |
| POST | `/source-candidates` | Main endpoint for candidate sourcing |

### Sample API Request

**POST** `/source-candidates`

```json
{
  "job_description": "Software Engineer, ML Research at Windsurf. Looking for candidates with experience in LLMs, Python, and production ML systems. Must have 2+ years experience and strong background from top CS programs.",
  "candidate_names": [
    "Andrej Karpathy",
    "Shreya Shankar",
    "Sebastian Ruder"
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "job_id": "software-engineer,-ml-research-a1b2c3",
  "candidates_found": 3,
  "execution_time": 25.8,
  "top_candidates": [
    {
      "name": "Andrej Karpathy",
      "score": 78.0,
      "fit_level": "Strong Fit",
      "company": "OpenAI (Former Tesla AI Director)",
      "location": "San Francisco, California, United States",
      "linkedin_url": "https://www.linkedin.com/in/andrej-karpathy-9a650716",
      "outreach_message": "Hi Andrej,\n\nI came across your profile and was impressed by your experience in the ML space, particularly your work at Tesla and OpenAI..."
    }
  ]
}
```

### Test with curl

```bash
curl -X POST "http://localhost:8000/source-candidates" \
     -H "Content-Type: application/json" \
     -d '{
       "job_description": "Software Engineer at Google",
       "candidate_names": ["Andrej Karpathy", "Shreya Shankar"]
     }'
```

## 📊 Scoring System

The AI scoring system evaluates candidates across multiple dimensions:

- **Technical Skills Match** (30%): Relevance to job requirements
- **Experience Level** (25%): Years and quality of experience  
- **Education Background** (20%): University ranking and degree relevance
- **Company Prestige** (15%): Previous employers and career progression
- **Location Fit** (10%): Geographic alignment with job location

### Score Interpretation

| Score Range | Fit Level | Recommendation |
|-------------|-----------|----------------|
| 80-100 | Excellent Fit | High priority contact |
| 70-79 | Strong Fit | Definitely reach out |
| 60-69 | Good Fit | Worth contacting |
| 40-59 | Fair Fit | Consider if other candidates unavailable |
| 0-39 | Poor Fit | Not recommended |

## 🛠️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for LLM access | Yes |
| `SERPAPI_API_KEY` | SerpAPI key for Google search | Yes |

### Model Configuration

The system uses these AI models:
- **Scoring**: `llama-3.1-70b-versatile` (High accuracy for candidate evaluation)
- **Messaging**: `gemma2-9b-it` (Fast and creative for outreach generation)

## 📁 Output Format

Results are exported as JSON files with the following structure:

```json
{
  "job_id": "unique-job-identifier",
  "status": "success",
  "timestamp": "2025-06-29T10:30:00Z",
  "job_description": "Full job posting text...",
  "candidates_found": 5,
  "execution_time": 25.8,
  "pipeline_summary": {
    "excellent_fits": 0,
    "strong_fits": 2,
    "good_fits": 2,
    "fair_fits": 1,
    "poor_fits": 0
  },
  "top_candidates": [
    {
      "name": "Candidate Name",
      "score": 78.0,
      "fit_level": "Strong Fit",
      "company": "Company Name",
      "location": "City, State, Country",
      "linkedin_url": "https://linkedin.com/in/profile",
      "education": "PhD Computer Science",
      "current_role": "Senior ML Engineer",
      "outreach_message": "Personalized message...",
      "scoring_explanation": {
        "technical_skills": 85,
        "experience_level": 75,
        "education_background": 90,
        "company_prestige": 80,
        "location_fit": 60,
        "reasoning": "Strong technical background..."
      }
    }
  ]
}
```

## 🚦 Error Handling

The system includes comprehensive error handling:

- **API Rate Limits**: Automatic retry with backoff
- **Invalid Profiles**: Graceful skipping of inaccessible LinkedIn profiles
- **LLM Failures**: Fallback scoring mechanisms
- **Network Issues**: Timeout handling and error reporting

## 🧪 Testing

### Run Individual Component Tests

```bash
# Test LinkedIn scraping
python -c "from app.scraper import search_linkedin_profile; print(search_linkedin_profile('Andrej Karpathy'))"

# Test AI scoring
python -c "from app.scorer import score_candidate; print(score_candidate({}, 'Job description'))"

# Test message generation
python -c "from app.messenger import generate_outreach_message; print(generate_outreach_message({}, 'Job description'))"
```

### Interactive API Testing

Visit `http://localhost:8000/docs` for Swagger UI testing interface.

## 🔧 Troubleshooting

### Common Issues

1. **"Module not found" errors**
   ```bash
   # Ensure you're in the right directory and venv is activated
   pip install -r requirements.txt
   ```

2. **API key errors**
   ```bash
   # Check your .env file exists and has correct keys
   cat .env
   ```

3. **LinkedIn search returning no results**
   - Verify SerpAPI key is valid
   - Check if candidate names are spelled correctly
   - Try alternative name formats

4. **Slow API responses**
   - Normal for first run (cold start)
   - Subsequent runs are faster due to caching

## 📈 Performance

- **Average execution time**: 20-30 seconds for 5 candidates
- **LinkedIn search**: ~2-3 seconds per candidate
- **AI scoring**: ~3-4 seconds per candidate  
- **Message generation**: ~2-3 seconds per candidate
- **Concurrent processing**: Batch optimization for multiple candidates

## 🔐 Security & Privacy

- **No data storage**: All processing is ephemeral
- **API keys**: Stored securely in environment variables
- **Public data only**: Uses publicly available LinkedIn information
- **No authentication**: Implement auth for production use


### Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup

```bash
# Production environment variables
GROQ_API_KEY=prod_groq_key
SERPAPI_API_KEY=prod_serpapi_key
ENV=production
LOG_LEVEL=info
```

---

**Built with ❤️ for modern recruitment automation**
