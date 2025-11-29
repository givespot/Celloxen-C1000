"""
IRIDOLOGY REPORT PDF GENERATOR
Professional Navy Blue Design - Matching Wellness Report Style
VERSION 2.0 - UK Compliant (No Supplements)
Updated: 26 November 2025
"""

from weasyprint import HTML
from datetime import datetime
import asyncpg
import json
import io


def format_british_date(date_obj=None):
    """Format date in British style: 26 November 2025"""
    if date_obj is None:
        date_obj = datetime.now()
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except:
            return date_obj
    return date_obj.strftime('%d %B %Y')


def format_british_datetime(date_obj=None):
    """Format datetime in British style: 26 November 2025 at 14:30"""
    if date_obj is None:
        date_obj = datetime.now()
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except:
            return date_obj
    return date_obj.strftime('%d %B %Y at %H:%M')


def convert_markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML for PDF rendering"""
    import re
    
    lines = text.split('\n')
    html_lines = []
    in_list = False
    
    for line in lines:
        line = line.strip()
        
        if not line:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<div class="spacer"></div>')
            continue
        
        # Main headings
        if line.startswith('# '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            text = line[2:].strip()
            html_lines.append(f'<h1 class="main-heading">{text}</h1>')
        
        # Section headings
        elif line.startswith('## '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            text = line[3:].strip()
            html_lines.append(f'<h2 class="section-heading">{text}</h2>')
        
        # Sub-headings
        elif line.startswith('### '):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            text = line[4:].strip()
            html_lines.append(f'<h3 class="sub-heading">{text}</h3>')
        
        # Bullet points
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list:
                html_lines.append('<ul class="bullet-list">')
                in_list = True
            text = line[2:].strip()
            # Convert markdown bold/italic
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            html_lines.append(f'<li>{text}</li>')
        
        # Numbered items
        elif re.match(r'^\d+\.', line):
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            text = re.sub(r'^\d+\.\s*', '', line)
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
            html_lines.append(f'<p class="numbered-item">{text}</p>')
        
        # Horizontal rule
        elif line == '---':
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            html_lines.append('<hr class="divider">')
        
        # Regular paragraphs
        else:
            if in_list:
                html_lines.append('</ul>')
                in_list = False
            # Convert markdown formatting
            text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', line)
            text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
            html_lines.append(f'<p>{text}</p>')
    
    if in_list:
        html_lines.append('</ul>')
    
    return '\n'.join(html_lines)


async def generate_iridology_pdf(analysis_id: int) -> bytes:
    """Generate professional iridology PDF report with Navy Blue branding"""
    
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
                c.name as clinic_name
            FROM iridology_analyses ia
            JOIN patients p ON ia.patient_id = p.id
            JOIN clinics c ON ia.clinic_id = c.id
            WHERE ia.id = $1
        """, analysis_id)
        
        if not analysis:
            raise Exception(f"Analysis {analysis_id} not found")
        
        # Extract data
        patient_name = f"{analysis['first_name']} {analysis['last_name']}"
        patient_number = analysis['patient_number']
        clinic_name = analysis['clinic_name']
        analysis_number = analysis['analysis_number']
        analysis_date = format_british_date(analysis['created_at'])
        
        # Get constitutional type - with fallback
        constitutional_type = analysis['constitutional_type'] or 'Mixed'
        constitutional_strength = analysis['constitutional_strength'] or 'Moderate'
        
        # If still showing defaults, try to extract from combined_analysis
        if constitutional_type in ['Unknown', 'Not determined', None]:
            try:
                combined = json.loads(analysis['combined_analysis']) if analysis['combined_analysis'] else {}
                constitutional_type = combined.get('constitutional_type', 'Mixed')
                constitutional_strength = combined.get('constitutional_strength', 'Moderate')
            except:
                constitutional_type = 'Mixed'
                constitutional_strength = 'Moderate'
        
        # Get report content
        report_html = ""
        try:
            combined_analysis = json.loads(analysis['combined_analysis']) if analysis['combined_analysis'] else {}
            if 'raw_text' in combined_analysis:
                report_html = convert_markdown_to_html(combined_analysis['raw_text'])
            else:
                report_html = "<p>Analysis report content not available.</p>"
        except:
            report_html = "<p>Unable to parse analysis report.</p>"
        
        report_datetime = format_british_datetime()
        
        # Build HTML with Navy Blue professional styling
        html_content = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
    <meta charset="utf-8">
    <title>Iridology Report - {patient_name}</title>
    <style>
        @page {{
            size: A4;
            margin: 20mm 15mm 25mm 15mm;
            @top-center {{
                content: "CELLOXEN HEALTH - Iridology Wellness Analysis";
                font-family: Helvetica, Arial, sans-serif;
                font-size: 8pt;
                color: #6b7280;
                border-bottom: 1px solid #e5e7eb;
                padding-bottom: 5mm;
            }}
            @bottom-left {{
                content: "{patient_name} | {patient_number}";
                font-family: Helvetica, Arial, sans-serif;
                font-size: 7pt;
                color: #6b7280;
            }}
            @bottom-center {{
                content: "Page " counter(page) " of " counter(pages);
                font-family: Helvetica, Arial, sans-serif;
                font-size: 7pt;
                color: #6b7280;
            }}
            @bottom-right {{
                content: "www.celloxen.co.uk";
                font-family: Helvetica, Arial, sans-serif;
                font-size: 7pt;
                color: #1e3a8a;
            }}
        }}
        
        @page :first {{
            @top-center {{ content: ""; border-bottom: none; }}
        }}
        
        * {{ box-sizing: border-box; }}
        
        body {{
            font-family: Helvetica, Arial, sans-serif;
            color: #1f2937;
            line-height: 1.6;
            font-size: 10pt;
            margin: 0;
            padding: 0;
        }}
        
        /* Header */
        .report-header {{
            text-align: center;
            border-bottom: 3px solid #1e3a8a;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        
        .report-header h1 {{
            color: #1e3a8a;
            font-size: 24pt;
            margin: 0 0 5px 0;
            letter-spacing: 1px;
            font-weight: 700;
        }}
        
        .report-header .subtitle {{
            color: #3b82f6;
            font-size: 12pt;
            margin: 0;
            font-weight: 400;
        }}
        
        /* Info Section */
        .info-section {{
            display: table;
            width: 100%;
            margin-bottom: 20px;
        }}
        
        .patient-info {{
            display: table-cell;
            width: 60%;
            vertical-align: top;
            padding-right: 20px;
        }}
        
        .constitutional-box {{
            display: table-cell;
            width: 40%;
            vertical-align: top;
        }}
        
        .info-table {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 15px;
            width: 100%;
        }}
        
        .info-table table {{
            width: 100%;
            border-collapse: collapse;
        }}
        
        .info-table td {{
            padding: 6px 10px;
            border-bottom: 1px solid #e5e7eb;
            font-size: 9.5pt;
        }}
        
        .info-table td:first-child {{
            font-weight: 600;
            color: #475569;
            width: 45%;
        }}
        
        .info-table tr:last-child td {{
            border-bottom: none;
        }}
        
        .constitution-card {{
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .constitution-card .label {{
            font-size: 9pt;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        
        .constitution-card .type {{
            font-size: 18pt;
            font-weight: 700;
            margin: 5px 0;
        }}
        
        .constitution-card .strength {{
            font-size: 11pt;
            opacity: 0.95;
        }}
        
        /* Content Sections */
        .main-heading {{
            color: #1e3a8a;
            font-size: 16pt;
            margin: 25px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #3b82f6;
            page-break-after: avoid;
        }}
        
        .section-heading {{
            color: #1e3a8a;
            font-size: 13pt;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid #93c5fd;
            page-break-after: avoid;
        }}
        
        .sub-heading {{
            color: #3b82f6;
            font-size: 11pt;
            margin: 15px 0 8px 0;
            font-weight: 600;
            page-break-after: avoid;
        }}
        
        p {{
            margin: 8px 0;
            text-align: justify;
        }}
        
        .bullet-list {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        
        .bullet-list li {{
            margin: 6px 0;
            line-height: 1.5;
        }}
        
        .numbered-item {{
            margin: 8px 0;
            padding-left: 15px;
        }}
        
        .spacer {{
            height: 10px;
        }}
        
        .divider {{
            border: none;
            border-top: 1px solid #e5e7eb;
            margin: 15px 0;
        }}
        
        strong {{
            color: #1e3a8a;
        }}
        
        /* Disclaimer */
        .disclaimer {{
            background: #fef3c7;
            border: 2px solid #f59e0b;
            border-radius: 8px;
            padding: 15px 18px;
            margin-top: 25px;
            page-break-inside: avoid;
        }}
        
        .disclaimer h3 {{
            color: #92400e;
            margin: 0 0 10px 0;
            font-size: 11pt;
        }}
        
        .disclaimer p {{
            margin: 6px 0;
            font-size: 9pt;
            text-align: left;
        }}
        
        /* Footer */
        .report-footer {{
            text-align: center;
            color: #6b7280;
            font-size: 8pt;
            margin-top: 25px;
            padding-top: 15px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .report-footer .brand {{
            color: #1e3a8a;
            font-weight: 600;
        }}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>CELLOXEN HEALTH</h1>
        <p class="subtitle">Iridology Wellness Analysis Report</p>
    </div>
    
    <div class="info-section">
        <div class="patient-info">
            <div class="info-table">
                <table>
                    <tr><td>Patient Name:</td><td>{patient_name}</td></tr>
                    <tr><td>Patient Number:</td><td>{patient_number}</td></tr>
                    <tr><td>Analysis Number:</td><td>{analysis_number}</td></tr>
                    <tr><td>Analysis Date:</td><td>{analysis_date}</td></tr>
                    <tr><td>Clinic:</td><td>{clinic_name}</td></tr>
                </table>
            </div>
        </div>
        <div class="constitutional-box">
            <div class="constitution-card">
                <div class="label">Constitutional Type</div>
                <div class="type">{constitutional_type}</div>
                <div class="strength">{constitutional_strength} Constitution</div>
            </div>
        </div>
    </div>
    
    <div class="report-content">
        {report_html}
    </div>
    
    <div class="disclaimer">
        <h3>Important Information</h3>
        <p><strong>This iridology analysis provides holistic wellness insights and does not constitute medical diagnosis or treatment.</strong></p>
        <p>Iridology is a complementary wellness assessment tool. The findings and recommendations in this report are for wellness support purposes only.</p>
        <p>• Please consult your GP for any medical concerns or before making significant health changes</p>
        <p>• This analysis does not replace professional medical advice, diagnosis, or treatment</p>
        <p>• If you experience any acute symptoms, please seek immediate medical attention</p>
    </div>
    
    <div class="report-footer">
        <p>Report Generated: {report_datetime} | Analysis Reference: {analysis_number}</p>
        <p class="brand">Celloxen Health | Professional Iridology Wellness Analysis</p>
        <p>www.celloxen.co.uk</p>
    </div>
</body>
</html>"""
        
        # Generate PDF
        html = HTML(string=html_content)
        pdf_bytes = html.write_pdf()
        
        return pdf_bytes
        
    finally:
        await conn.close()


async def generate_iridology_report_buffer(analysis_id: int):
    """Generate PDF and return as BytesIO buffer for streaming"""
    pdf_bytes = await generate_iridology_pdf(analysis_id)
    buffer = io.BytesIO(pdf_bytes)
    buffer.seek(0)
    return buffer
