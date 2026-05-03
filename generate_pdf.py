from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 12)
        self.cell(0, 10, 'AI Recruitment Platform - Project Documentation', 0, new_x="LMARGIN", new_y="NEXT", align='C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(md_file, pdf_file):
    pdf = PDF()
    pdf.set_left_margin(20)
    pdf.set_right_margin(20)
    pdf.add_page()
    pdf.set_font("helvetica", size=11)
    
    if not os.path.exists(md_file):
        print(f"File {md_file} not found.")
        return

    with open(md_file, 'r', encoding='utf-8') as f:
        text = f.read()

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        if line.startswith('# '):
            pdf.ln(5)
            pdf.set_font("helvetica", 'B', 16)
            pdf.multi_cell(0, 10, line[2:])
            pdf.set_font("helvetica", size=11)
        elif line.startswith('## '):
            pdf.ln(5)
            pdf.set_font("helvetica", 'B', 14)
            pdf.multi_cell(0, 10, line[3:])
            pdf.set_font("helvetica", size=11)
        elif line.startswith('### '):
            pdf.ln(3)
            pdf.set_font("helvetica", 'B', 12)
            pdf.multi_cell(0, 8, line[4:])
            pdf.set_font("helvetica", size=11)
        elif line.startswith('**'):
            pdf.set_font("helvetica", 'B', 11)
            pdf.multi_cell(0, 7, line.replace('**', ''))
            pdf.set_font("helvetica", size=11)
        elif line.startswith('- '):
            pdf.multi_cell(0, 7, "  " + line)
        else:
            pdf.multi_cell(0, 7, line)
            
    pdf.output(pdf_file)
    print(f"PDF created: {pdf_file}")

if __name__ == "__main__":
    create_pdf('documentation/Project_Report.md', 'documentation/Project_Report.pdf')
