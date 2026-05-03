import docx
import re

def clean_doc(path):
    doc = docx.Document(path)
    count = 0
    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue
        
        # Split by '. ' or just '.' to find sentences
        sentences = [s.strip() for s in re.split(r'\.\s*', text) if s.strip()]
        
        if len(sentences) < 2:
            continue
            
        unique_sentences = []
        seen = set()
        
        for s in sentences:
            norm = s.lower().replace(' ', '')
            if norm not in seen:
                seen.add(norm)
                unique_sentences.append(s)
                
        if len(unique_sentences) < len(sentences):
            new_text = '. '.join(unique_sentences)
            if text.endswith('.') and not new_text.endswith('.'):
                new_text += '.'
            elif not text.endswith('.') and new_text.endswith('.'):
                 new_text = new_text[:-1]
            
            # Reassigning p.text
            p.text = new_text
            count += 1
            
    doc.save(path)
    print(f"Deduplication complete. Modified {count} paragraphs.")

if __name__ == '__main__':
    clean_doc('documentation/Detailed_Project_Report.docx')
