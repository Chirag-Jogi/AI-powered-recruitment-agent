import os
from dotenv import load_dotenv
import httpx

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

def generate_outreach_message(candidate, job_description):
    prompt = f"""
    You are a professional technical recruiter.

    Write a personalized LinkedIn message to {candidate['name']}, who is a {candidate['title']}, and these are its snippets: {candidate['snippet']} based on this job:

    {job_description}

    Make the message reference their background. Keep it short, friendly, and professional. Do not exaggerate or use emojis.
    """

    payload = {
        "model":"gemma2-9b-it",  # Use the appropriate model for your needs
        "messages": [
            {"role": "system", "content": "You are a helpful and professional recruiter."},
            {"role": "user", "content": prompt}
        ]
    }

    response = httpx.post(GROQ_URL, headers=HEADERS, json=payload)
    content = response.json()["choices"][0]["message"]["content"]
    
    return content
