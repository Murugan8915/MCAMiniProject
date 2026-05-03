import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
import re
import os
from xml.sax.saxutils import escape

source_pdf = 'DC2332306010017_SECURE_DATA_SHARING_USING_RSA.pdf'

def clean_text(text):
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    seen = set()
    unique_sentences = []
    for s in sentences:
        norm = s.lower().replace(' ', '')
        if norm not in seen:
            seen.add(norm)
            unique_sentences.append(s)
    return ' '.join(unique_sentences)

def build_pdf_with_params(cleaned_paragraphs, font_size, leading, space_after, margin, filename):
    doc = SimpleDocTemplate(
        filename, 
        pagesize=letter,
        rightMargin=margin, leftMargin=margin,
        topMargin=margin, bottomMargin=margin
    )
    styles = getSampleStyleSheet()
    normal_style = ParagraphStyle(
        'Normal', parent=styles['Normal'], 
        alignment=TA_JUSTIFY, 
        spaceAfter=space_after, 
        fontSize=font_size, 
        leading=leading
    )
    topic_style = ParagraphStyle(
        'Topic', parent=styles['Heading2'], 
        alignment=TA_CENTER, 
        spaceAfter=space_after + 10, 
        fontSize=font_size + 6,
        leading=leading + 6
    )
    
    story = []
    for p_type, content in cleaned_paragraphs:
        if p_type == 'topic':
            story.append(Paragraph(escape(content), topic_style))
        else:
            if content:
                story.append(Paragraph(escape(content), normal_style))
    
    doc.build(story)
    
    reader = PyPDF2.PdfReader(filename)
    return len(reader.pages)

def extract_and_format():
    if not os.path.exists(source_pdf):
        print(f"{source_pdf} not found.")
        return

    reader = PyPDF2.PdfReader(source_pdf)
    num_pages = len(reader.pages)
    
    cleaned_paragraphs = []
    for i in range(5, min(81, num_pages)):
        page_text = reader.pages[i].extract_text()
        if not page_text: continue
        
        lines = page_text.split('\n')
        current_para = []
        
        for line in lines:
            line_strip = line.strip()
            if not line_strip: continue
            
            if len(line_strip) < 60 and line_strip.isupper() and not line_strip.isdigit():
                if current_para:
                    cleaned = clean_text(' '.join(current_para))
                    if cleaned: cleaned_paragraphs.append(('text', cleaned))
                    current_para = []
                cleaned_paragraphs.append(('topic', line_strip))
            else:
                current_para.append(line_strip)
                
        if current_para:
            cleaned = clean_text(' '.join(current_para))
            if cleaned: cleaned_paragraphs.append(('text', cleaned))
            
        cleaned_paragraphs.append(('pagebreak', '')) # We'll just ignore pagebreaks to let reportlab flow it naturally, or maybe we want them?
        # Actually, let's not force page breaks so it flows evenly, except maybe we just let it flow.
        
    # Remove the pagebreaks from cleaned_paragraphs, let reportlab do it
    cleaned_paragraphs = [p for p in cleaned_paragraphs if p[0] != 'pagebreak']

    target_pages = 76  # 81 total - 5 preserved
    temp_pdf = "temp_formatted_content.pdf"
    
    # Base parameters
    font_size = 14.0
    leading = 20.0
    space_after = 15.0
    margin = 72.0 # 1 inch

    # Binary search approach
    min_mult = 1.0
    max_mult = 3.0
    best_mult = 1.0
    best_diff = 100
    
    print("Finding optimal formatting parameters...")
    for iteration in range(15):
        mult = (min_mult + max_mult) / 2
        fs = font_size * mult
        ld = leading * mult
        sa = space_after * mult
        mg = margin + (mult - 1) * 20
        
        pages = build_pdf_with_params(cleaned_paragraphs, fs, ld, sa, mg, temp_pdf)
        print(f"Iteration {iteration}: mult={mult:.3f} -> pages={pages}")
        
        if pages == target_pages:
            print("Target reached!")
            best_mult = mult
            break
        elif pages < target_pages:
            min_mult = mult
            if target_pages - pages < best_diff:
                best_diff = target_pages - pages
                best_mult = mult
        else:
            max_mult = mult
            
    # Final build with best_mult if target wasn't exactly hit
    fs = font_size * best_mult
    ld = leading * best_mult
    sa = space_after * best_mult
    mg = margin + (best_mult - 1) * 20
    pages = build_pdf_with_params(cleaned_paragraphs, fs, ld, sa, mg, temp_pdf)
    print(f"Final build -> pages={pages}")
    
    # If still not exactly 76, we can add page breaks at the end to pad it
    if pages < target_pages:
        print(f"Padding with {target_pages - pages} blank pages")
        
        # We need to modify build_pdf_with_params to support 'pagebreak'
        # Let's redefine a local build function for padding:
        def build_padded(extra_pages):
            doc = SimpleDocTemplate(
                temp_pdf, 
                pagesize=letter,
                rightMargin=mg, leftMargin=mg,
                topMargin=mg, bottomMargin=mg
            )
            styles = getSampleStyleSheet()
            normal_style = ParagraphStyle('Normal', parent=styles['Normal'], alignment=TA_JUSTIFY, spaceAfter=sa, fontSize=fs, leading=ld)
            topic_style = ParagraphStyle('Topic', parent=styles['Heading2'], alignment=TA_CENTER, spaceAfter=sa + 10, fontSize=fs + 6, leading=ld + 6)
            
            story = []
            for p_type, content in cleaned_paragraphs:
                if p_type == 'topic':
                    story.append(Paragraph(escape(content), topic_style))
                else:
                    if content:
                        story.append(Paragraph(escape(content), normal_style))
            
            for _ in range(extra_pages):
                story.append(PageBreak())
                story.append(Paragraph(" ", normal_style))
            
            doc.build(story)
            return len(PyPDF2.PdfReader(temp_pdf).pages)
            
        pages = build_padded(target_pages - pages)
        print(f"Padded build -> pages={pages}")
    # Now merge with first 5 pages
    writer = PyPDF2.PdfWriter()
    for i in range(min(5, num_pages)):
        writer.add_page(reader.pages[i])
        
    if os.path.exists(temp_pdf):
        temp_reader = PyPDF2.PdfReader(temp_pdf)
        for page in temp_reader.pages:
            writer.add_page(page)
            
    # Save final output
    output_pdf = 'Detailed_Project_Reports.pdf'
    with open(output_pdf, 'wb') as f:
        writer.write(f)
        
    print(f"Successfully processed and saved to {output_pdf}")

if __name__ == '__main__':
    extract_and_format()
