from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Preformatted, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
import os

class ProjectSpecific80PagePDF:
    def __init__(self, md_file, output_filename):
        self.md_file = md_file
        self.output_filename = output_filename
        self.font_size = 14 # Large font for volume
        self.leading = 22
        self.margin = 100 # Large margins for volume

    def build_pdf(self, current_leading):
        doc = SimpleDocTemplate(self.output_filename, pagesize=letter,
                                rightMargin=self.margin, leftMargin=self.margin,
                                topMargin=self.margin, bottomMargin=self.margin)
        styles = getSampleStyleSheet()
        
        # Styles
        title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=28, alignment=TA_CENTER, spaceBefore=180, spaceAfter=50, leading=32)
        h2_style = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=22, spaceBefore=40, spaceAfter=20, color=colors.black)
        h3_style = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=18, spaceBefore=25, spaceAfter=15)
        normal_style = ParagraphStyle('Normal', parent=styles['Normal'], fontSize=self.font_size, leading=current_leading, alignment=TA_JUSTIFY, spaceAfter=18)
        prelim_style = ParagraphStyle('Prelim', parent=styles['Normal'], fontSize=16, alignment=TA_CENTER, spaceAfter=35, leading=35)
        
        toc_style_left = ParagraphStyle('TOCLeft', parent=styles['Normal'], fontSize=13, leading=20, alignment=TA_LEFT)
        toc_style_right = ParagraphStyle('TOCRight', parent=styles['Normal'], fontSize=13, leading=20, alignment=TA_RIGHT)

        story = []
        with open(self.md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        in_prelim = True
        
        for line in lines:
            line_strip = line.strip()
            
            if line_strip == "---":
                story.append(PageBreak())
                continue
                
            if not line_strip:
                story.append(Spacer(1, 18))
                continue

            if line_strip.startswith('# '):
                story.append(Paragraph(line_strip[2:], title_style))
                in_prelim = False
            elif line_strip.startswith('## '):
                story.append(PageBreak())
                story.append(Paragraph(line_strip[3:], h2_style))
            elif line_strip.startswith('### '):
                story.append(Paragraph(line_strip[4:], h3_style))
            elif '....' in line_strip:
                parts = line_strip.split('....')
                section = parts[0].strip()
                page = parts[-1].replace('.', '').strip()
                t = Table([[Paragraph(section, toc_style_left), Paragraph(page, toc_style_right)]], colWidths=[330, 50])
                t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'BOTTOM')]))
                story.append(t)
            elif line_strip.startswith('!['):
                # Handle images: ![caption](path)
                try:
                    import re
                    match = re.match(r'!\[(.*?)\]\((.*?)\)', line_strip)
                    if match:
                        caption = match.group(1)
                        img_path = match.group(2)
                        # Normalize path
                        img_path = img_path.strip().replace('file:///', '').replace('/', os.sep)
                        if os.path.exists(img_path):
                            img = Image(img_path, width=400, height=300)
                            story.append(img)
                            if caption:
                                story.append(Paragraph(f"Figure: {caption}", ParagraphStyle('Caption', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER, spaceAfter=10)))
                            story.append(Spacer(1, 12))
                except Exception as e:
                    print(f"Error loading image: {e}")
            else:
                style = prelim_style if in_prelim else normal_style
                story.append(Paragraph(line_strip.replace('**', '').replace('*', ''), style))

        doc.build(story)
        return doc.page

    def generate(self):
        current_leading = 22
        pages = self.build_pdf(current_leading)
        print(f"Initial page count: {pages}")
        
        if pages < 80:
            while pages < 80 and current_leading < 60:
                prev_leading = current_leading
                current_leading += 0.2
                pages = self.build_pdf(current_leading)
                if pages > 80:
                    current_leading = prev_leading
                    self.build_pdf(current_leading)
                    break
                print(f"Adjustment: Leading {current_leading} -> Pages {pages}")
        elif pages > 80:
            while pages > 80 and current_leading > 18:
                current_leading -= 0.2
                pages = self.build_pdf(current_leading)
                print(f"Adjustment: Leading {current_leading} -> Pages {pages}")
        
        print(f"Final Count: {self.build_pdf(current_leading)} pages with leading {current_leading}")

if __name__ == "__main__":
    gen = ProjectSpecific80PagePDF('documentation/Detailed_Project_Report.md', 'documentation/Detailed_Project_Report.pdf')
    gen.generate()
