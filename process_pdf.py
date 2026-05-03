import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import re
import os

source_pdf = 'DC2332306010017_SECURE_DATA_SHARING_USING_RSA.pdf'

def clean_text(text):
    # Remove unwanted space
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove repeated content (sentences)
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    seen = set()
    unique_sentences = []
    for s in sentences:
        norm = s.lower().replace(' ', '')
        if norm not in seen:
            seen.add(norm)
            unique_sentences.append(s)
    return ' '.join(unique_sentences)

def extract_and_format():
    if not os.path.exists(source_pdf):
        print(f"{source_pdf} not found.")
        return

    reader = PyPDF2.PdfReader(source_pdf)
    num_pages = len(reader.pages)
    print(f"Total pages in source: {num_pages}")
    
    writer = PyPDF2.PdfWriter()
    
    # Keep first 5 pages unchanged
    for i in range(min(5, num_pages)):
        writer.add_page(reader.pages[i])
        
    extracted_topics = []
    
    # Process remaining pages
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle('Normal', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceAfter=10, fontSize=12, leading=14)
    topic_style = ParagraphStyle('Topic', parent=styles['Heading2'], alignment=TA_CENTER, spaceAfter=15, fontSize=16)
    
    story = []
    
    for i in range(5, min(81, num_pages)):
        page_text = reader.pages[i].extract_text()
        if not page_text: continue
        
        # simple heuristic for topics: lines that are short and uppercase
        lines = page_text.split('\n')
        cleaned_paragraphs = []
        current_para = []
        
        for line in lines:
            line_strip = line.strip()
            if not line_strip: continue
            
            if len(line_strip) < 60 and line_strip.isupper() and not line_strip.isdigit():
                # Treat as topic
                if current_para:
                    cleaned_paragraphs.append(('text', ' '.join(current_para)))
                    current_para = []
                cleaned_paragraphs.append(('topic', line_strip))
                extracted_topics.append(line_strip)
            else:
                current_para.append(line_strip)
                
        if current_para:
            cleaned_paragraphs.append(('text', ' '.join(current_para)))
            
        for p_type, content in cleaned_paragraphs:
            from xml.sax.saxutils import escape
            if p_type == 'topic':
                story.append(Paragraph(escape(content), topic_style))
            else:
                cleaned = clean_text(content)
                if cleaned:
                    story.append(Paragraph(escape(cleaned), normal_style))
                    
        story.append(PageBreak())
        
    # Generate temporary PDF with the new content
    temp_pdf = "temp_formatted_content.pdf"
    doc = SimpleDocTemplate(temp_pdf, pagesize=letter)
    doc.build(story)
    
    # Merge temp_pdf into writer
    if os.path.exists(temp_pdf):
        temp_reader = PyPDF2.PdfReader(temp_pdf)
        for page in temp_reader.pages:
            writer.add_page(page)
            
    # Save final output
    output_pdf = 'Detailed_Project_Reports.pdf'
    with open(output_pdf, 'wb') as f:
        writer.write(f)
        
    print(f"Successfully processed and saved to {output_pdf}")
    
    # Save extracted topics
    with open("extracted_topics.txt", "w", encoding="utf-8") as f:
        for t in extracted_topics:
            f.write(t + "\n")
    print("Extracted topics saved to extracted_topics.txt")

if __name__ == '__main__':
    extract_and_format()
