
"""
IRIDOLOGY REPORT PDF GENERATOR
Generates professional PDF reports from Claude AI iris analysis
Uses ReportLab for clean, formatted output
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.lib import colors
from datetime import datetime
import asyncpg
import re
import io
import json

async def generate_iridology_pdf(analysis_id: int) -> bytes:
    """
    Generate iridology analysis PDF report
    Returns: PDF as bytes buffer
    """
    
    # Connect to database
    conn = await asyncpg.connect(
        host="localhost", port=5432, user="celloxen_user",
        password="CelloxenSecure2025", database="celloxen_portal"
    )
    
    try:
        # Get analysis data with patient info
        analysis = await conn.fetchrow("""
            SELECT 
                ia.*,
                p.first_name, p.last_name, p.patient_number, p.date_of_birth,
                c.name
            FROM iridology_analyses ia
            JOIN patients p ON ia.patient_id = p.id
            JOIN clinics c ON ia.clinic_id = c.id
            WHERE ia.id = $1
        """, analysis_id)
        
        if not analysis:
            raise Exception(f"Analysis {analysis_id} not found")
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceBefore=12,
            spaceAfter=6
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#3b82f6'),
            spaceBefore=10,
            spaceAfter=4
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['BodyText'],
            fontSize=11,
            leading=14,
            spaceBefore=4,
            spaceAfter=4
        )
        
        meta_style = ParagraphStyle(
            'Meta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        # Build PDF content
        story = []
        
        # Header
        story.append(Paragraph("CELLOXEN WELLNESS IRIDOLOGY REPORT", title_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Patient & Analysis Info
        info_text = f"""
        <b>Patient:</b> {analysis['first_name']} {analysis['last_name']} ({analysis['patient_number']})<br/>
        <b>Analysis Number:</b> {analysis['analysis_number']}<br/>
        <b>Analysis Date:</b> {analysis['created_at'].strftime('%d %B %Y')}<br/>
        <b>Clinic:</b> {analysis['name']}<br/>
        <b>Constitutional Type:</b> {analysis['constitutional_type'] or 'Not determined'}<br/>
        <b>Constitutional Strength:</b> {analysis['constitutional_strength'] or 'Not determined'}
        """
        story.append(Paragraph(info_text, body_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Get the report text
        combined_analysis = json.loads(analysis['combined_analysis'])
        if combined_analysis and 'raw_text' in combined_analysis:
            report_text = combined_analysis['raw_text']
            
            # Convert markdown to ReportLab elements
            lines = report_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                if not line:
                    story.append(Spacer(1, 0.1*inch))
                    continue
                
                # Main headings (# )
                if line.startswith('# '):
                    text = line[2:].strip()
                    if text and text != '---':
                        story.append(PageBreak())
                        story.append(Paragraph(text, heading_style))
                
                # Subheadings (## )
                elif line.startswith('## '):
                    text = line[3:].strip()
                    if text and text != '---':
                        story.append(Spacer(1, 0.15*inch))
                        story.append(Paragraph(text, subheading_style))
                
                # Sub-subheadings (### )
                elif line.startswith('### '):
                    text = line[4:].strip()
                    story.append(Paragraph(f"<b>{text}</b>", body_style))
                
                # Bullet points
                elif line.startswith('- ') or line.startswith('* '):
                    text = line[2:].strip()
                    # Convert markdown bold to HTML
                    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                    story.append(Paragraph(f"• {text}", body_style))
                
                # Numbered lists
                elif re.match(r'^\d+\.', line):
                    text = re.sub(r'^\d+\.\s*', '', line)
                    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
                    story.append(Paragraph(text, body_style))
                
                # Horizontal rules
                elif line == '---':
                    story.append(Spacer(1, 0.2*inch))
                
                # Regular paragraphs
                elif not line.startswith('**'):
                    # Convert markdown bold to HTML
                    line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
                    # Convert markdown italic to HTML  
                    line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)
                    story.append(Paragraph(line, body_style))
        
        # Footer
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("---", meta_style))
        footer_text = f"""
        Report generated: {datetime.now().strftime('%d %B %Y at %H:%M')}<br/>
        Celloxen Health Portal - Professional Iridology Analysis<br/>
        <i>This report is for wellness support purposes only and does not constitute medical diagnosis or treatment.</i>
        """
        story.append(Paragraph(footer_text, meta_style))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF bytes
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
        
    finally:
        await conn.close()
