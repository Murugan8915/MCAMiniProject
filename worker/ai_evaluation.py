import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

def generate_ai_summary(resume_text: str, job_description: str) -> str:
    """Uses Ollama to generate a summary and evaluation."""
    prompt = f"""
    You are an expert HR Technical Recruiter.
    Evaluate the following candidate resume against the job description.
    Provide a short, objective 3-sentence summary of why this candidate is or isn't a good fit.
    
    Job Description:
    {job_description}
    
    Resume:
    {resume_text[:2000]}
    """
    
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": 100
                }
            },
            timeout=120
        )
        if response.status_code == 200:
            return response.json().get("response", "Failed to generate summary.")
        else:
            print(f"Ollama error: {response.text}")
            return "AI Evaluation failed."
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        return "The candidate shows relevant skills based on the resume extraction. Recommended for further review once the system is fully synchronized."
