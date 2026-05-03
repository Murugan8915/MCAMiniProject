import re
from pdfminer.high_level import extract_text
import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except Exception as e:
    print(f"Warning: Failed to load spaCy model. Error: {e}")
    nlp = None

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text from a PDF file."""
    try:
        text = extract_text(pdf_path)
        return text
    except Exception as e:
        print(f"Error parsing PDF {pdf_path}: {e}")
        return ""

def extract_email(text: str) -> str:
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, text)
    return emails[0] if emails else ""

def extract_mobile(text: str) -> str:
    # Basic phone pattern for various formats
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phones = re.findall(phone_pattern, text)
    return phones[0] if phones else ""

def extract_name(text: str) -> str:
    if not nlp:
        return ""
    doc = nlp(text[:1000]) # Scan first 1000 chars for name
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text
    return ""

def extract_entities(text: str) -> dict:
    """Extract named entities, contact info, and infer skills."""
    res = {
        "candidate_name": extract_name(text),
        "candidate_email": extract_email(text),
        "candidate_mobile": extract_mobile(text),
        "potential_skills": []
    }
    
    if nlp:
        doc = nlp(text)
        potential_skills = [chunk.text.lower() for chunk in doc.noun_chunks]
        res["potential_skills"] = list(set(potential_skills))
    
    return res

def calculate_score(extracted_skills: list, required_skills: list) -> float:
    """Calculate a rule-based match score."""
    if not required_skills:
        return 0.0
        
    extracted_lower = [s.lower() for s in extracted_skills]
    required_lower = [s.lower() for s in required_skills]
    
    match_count = 0
    for req in required_lower:
        if any(req in ext for ext in extracted_lower):
            match_count += 1
            
    score = (match_count / len(required_skills)) * 100.0
    return round(score, 2)
