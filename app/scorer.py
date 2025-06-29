

import os
import requests
from dotenv import load_dotenv 
import json
import re

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def score_candidate(candidate: dict, job_description: str) -> dict:
    """
    Uses LLM to score candidate based on rubric.
    Returns dict with final score and explanation for each criterion.
    """

   
    prompt = f"""
You are a technical recruiter expert at scoring candidates objectively. Analyze THIS SPECIFIC candidate against the job requirements.

=== JOB REQUIREMENTS ===
{job_description}

=== CANDIDATE DATA TO ANALYZE ===
Name: {candidate.get("name", "N/A")}
Headline: {candidate.get("headline", "N/A")} 
Current Role: {candidate.get("current_role", "N/A")}
Company: {candidate.get("company", "N/A")}
Location: {candidate.get("location", "N/A")}
Education: {candidate.get("education", "N/A")}
Profile Snippet: {candidate.get("snippet", "N/A")}

=== ANALYSIS INSTRUCTIONS ===
1. Extract education from snippet if not in education field
2. Determine actual experience level from headline/snippet
3. Compare candidate's location with job location from description
4. Assess company relevance to job requirements
5. Calculate weighted score based on actual data

=== SCORING WEIGHTS ===
Education (20%): 1-10 points
- Elite schools (IIT/MIT/Stanford/NIT/IIIT): 9-10
- Good universities: 7-8  
- Standard colleges: 5-6
- Not specified: 3-4

Experience Match (25%): 1-10 points
- Perfect skill match: 9-10
- Strong overlap (70%+): 7-8
- Some relevant skills (40-60%): 5-6
- Basic relevant skills: 3-4

Company Relevance (15%): 1-10 points
- FAANG/Top tech: 9-10
- Relevant industry: 7-8
- Any tech company: 5-6
- Non-tech/intern: 3-4

Career Trajectory (20%): 1-10 points
- Senior level: 8-10
- Mid-level: 6-8
- Junior/intern: 4-6
- Student only: 3-4

Location Match (10%): 1-10 points
- Same city: 10
- Same country: 6
- Different country: 3

Tenure (10%): 1-10 points
- 2+ years per role: 8-10
- 1-2 years: 6-8
- Internship level: 4-6
- No experience: 3

=== CALCULATION ===
Final = (Education×0.2) + (Experience×0.25) + (Company×0.15) + (Level×0.2) + (Location×0.1) + (Tenure×0.1) × 10

=== OUTPUT FORMAT ===
Return ONLY this JSON structure with CONSISTENT explanations:

{{"final_score": [calculated_score], "explanation": {{"education": "[education_analysis with exact points]", "experience": "[experience_match with exact points]", "company": "[company_relevance with exact points]", "trajectory": "[career_level with exact points]", "location": "[location_match with exact points]", "tenure": "[tenure_analysis with exact points]"}}}}

IMPORTANT: Make explanations match the points given. If you score company as 3 points, explanation must reflect that (e.g., "Startup/intern level - 3 points").
"""


    body = {
        "model": "gemma2-9b-it", 
        "messages": [
             {"role": "system", "content": "You are a technical recruiter expert at scoring candidates objectively."},
            {"role": "user", "content": prompt}
            ],
        "temperature": 0.2
    }



    # ✅ Added debug print
    # print(f"[DEBUG] Scoring candidate: {candidate.get('name', 'Unknown')}")

    response = requests.post(GROQ_URL, headers=HEADERS, json=body)

        # ✅ Added response status check
    if response.status_code != 200:
        # print(f"[ERROR] API Error: Status {response.status_code}")
        # print(f"[ERROR] Response: {response.text}")
        return {"final_score": 0, "explanation": {"error": f"API Error: {response.status_code}"}}
    

    try:
        response_data = response.json()
        # print(f"[DEBUG] API Response: {response_data}")  # Debug print
        
        output = response_data["choices"][0]["message"]["content"]
        # print(f"[DEBUG] Raw LLM output: {output}")  # Debug print

          # ✅ Extract JSON from markdown code blocks
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', output, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
            result = json.loads(json_str)  # Use json.loads instead of eval
            # print(f"[DEBUG] Extracted from markdown: {json_str[:50]}...")
        else:
            # Try to find JSON without markdown
            json_match = re.search(r'(\{.*?\})', output, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                result = json.loads(json_str)
                # print(f"[DEBUG] Found JSON: {json_str[:50]}...")
            else:
                result = eval(output)  # Last resort
                # print(f"[DEBUG] Used eval fallback")
        
        # print(f"[DEBUG] Parsed score: {result.get('final_score', 'No score')}")
        return result 
    except Exception as e:
        # print(f"[ERROR] Scoring failed: {e}")
        # print(f"[ERROR] Raw response: {response.text}")
        return {"final_score": 0, "explanation": {"error": f"Scoring failed: {str(e)}"}}
