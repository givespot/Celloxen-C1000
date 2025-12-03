"""
CELLOXEN HEALTH PORTAL - REPORT GENERATOR
Generates comprehensive wellness assessment PDF reports
Created: November 14, 2025
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import asyncpg
import json
import os

async def generate_wellness_report(assessment_id: int) -> str:
    """
    Generate comprehensive wellness report PDF
    Returns: path to generated PDF file
    """
    
    # Connect to database and fetch all data
    conn = await asyncpg.connect(
        host="localhost", port=5432, user="celloxen_user",
        password=os.getenv("DB_PASSWORD"), database="celloxen_portal"
    )
    
    # Get assessment data with patient info
    assessment = await conn.fetchrow("""
        SELECT 
            a.*,
            p.first_name, p.last_name, p.email, p.date_of_birth,
            p.patient_number
        FROM comprehensive_assessments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.id = $1
    """, assessment_id)
    
    await conn.close()
    
    if not assessment:
        raise Exception(f"Assessment {assessment_id} not found")
    
    # Create PDF
    filename = f"/var/www/celloxen-portal/reports/wellness_report_{assessment_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    
    # Container for PDF elements
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=12,
        spaceBefore=20
    )
    
    # PAGE 1: COVER & EXECUTIVE SUMMARY
    story.append(Spacer(1, 1*inch))
    story.append(Paragraph("Comprehensive Wellness Assessment Report", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Patient Information
    patient_info = f"""
    <b>Patient:</b> {assessment['first_name']} {assessment['last_name']}<br/>
    <b>Patient ID:</b> {assessment['patient_number']}<br/>
    <b>Assessment Date:</b> {assessment['assessment_date'].strftime('%B %d, %Y')}<br/>
    <b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y')}
    """
    story.append(Paragraph(patient_info, styles['Normal']))
    story.append(Spacer(1, 0.5*inch))
    
    # Overall Wellness Score - Big Number
    score_table_data = [[
        Paragraph(f"<font size=48 color='#7C3AED'><b>{assessment['overall_wellness_score']}%</b></font>", styles['Normal'])
    ]]
    score_table = Table(score_table_data, colWidths=[6*inch])
    score_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#7C3AED')),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F3E8FF')),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
    ]))
    story.append(score_table)
    story.append(Paragraph("<b>Overall Wellness Score</b>", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Key Findings Summary
    story.append(Paragraph("Executive Summary", heading_style))
    
    scores = json.loads(assessment['questionnaire_scores']) if assessment['questionnaire_scores'] else {}
    
    # Determine priority areas (lowest scores)
    sorted_domains = sorted(scores.items(), key=lambda x: x[1]['score'])
    
    summary_text = f"""
    This comprehensive wellness assessment evaluated {assessment['first_name']}'s health across five key wellness domains. 
    The overall wellness score of <b>{assessment['overall_wellness_score']}%</b> indicates areas where targeted support may be beneficial.
    <br/><br/>
    <b>Priority Areas for Attention:</b><br/>
    """
    
    for domain_key, domain_data in sorted_domains[:3]:  # Top 3 priority areas
        summary_text += f"• {domain_data['domain_name']}: {domain_data['score']}%<br/>"
    
    story.append(Paragraph(summary_text, styles['Normal']))
    
    # PAGE 2: DOMAIN SCORES DETAILED
    story.append(PageBreak())
    story.append(Paragraph("Wellness Domain Analysis", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Create table for domain scores
    domain_table_data = [['Domain', 'Therapy Code', 'Score', 'Status']]
    
    for domain_key, domain_data in scores.items():
        score = domain_data['score']
        
        # Determine status
        if score >= 75:
            status = "Good"
            status_color = colors.green
        elif score >= 50:
            status = "Moderate"
            status_color = colors.orange
        else:
            status = "Needs Support"
            status_color = colors.red
        
        domain_table_data.append([
            domain_data['domain_name'],
            domain_data['therapy_code'],
            f"{score}%",
            status
        ])
    
    domain_table = Table(domain_table_data, colWidths=[2.5*inch, 1*inch, 0.8*inch, 1.5*inch])
    domain_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')])
    ]))
    story.append(domain_table)
    
    # PAGE 3: IRIDOLOGY ANALYSIS (if available)
    if assessment['iridology_completed']:
        story.append(PageBreak())
        story.append(Paragraph("Iridology Analysis", title_style))
        story.append(Spacer(1, 0.3*inch))
        
        iridology_data = json.loads(assessment['iridology_data']) if assessment['iridology_data'] else {}
        
        iridology_text = f"""
        <b>Constitutional Type:</b> {assessment['constitutional_type']}<br/>
        <b>Constitutional Strength:</b> {assessment['constitutional_strength']}<br/><br/>
        <b>Findings:</b><br/>
        """
        
        if 'findings' in iridology_data:
            for system, finding in iridology_data['findings'].items():
                iridology_text += f"• {system.replace('_', ' ').title()}: {finding}<br/>"
        
        if 'recommendations' in iridology_data:
            iridology_text += "<br/><b>AI Recommendations:</b><br/>"
            for rec in iridology_data['recommendations']:
                iridology_text += f"• {rec}<br/>"
        
        story.append(Paragraph(iridology_text, styles['Normal']))
    
    # PAGE 4: THERAPY RECOMMENDATIONS
    story.append(PageBreak())
    story.append(Paragraph("Recommended Wellness Support", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    recommendations_text = """
    Based on your wellness assessment scores, the following Celloxen therapies are recommended to support your holistic health:
    <br/><br/>
    """
    
    # Recommend therapies based on low scores
    for domain_key, domain_data in sorted_domains:
        if domain_data['score'] < 60:  # Below 60% needs support
            therapy_code = domain_data['therapy_code']
            domain_name = domain_data['domain_name']
            
            # Suggest session count based on score
            if domain_data['score'] < 40:
                sessions = "20-24 sessions"
            elif domain_data['score'] < 50:
                sessions = "16-20 sessions"
            else:
                sessions = "12-16 sessions"
            
            recommendations_text += f"""
            <b>{therapy_code} - {domain_name}</b><br/>
            Recommended Course: {sessions}<br/>
            Your Score: {domain_data['score']}%<br/><br/>
            """
    
    story.append(Paragraph(recommendations_text, styles['Normal']))
    
    # PAGE 5: IMPORTANT INFORMATION & DISCLAIMER
    story.append(PageBreak())
    story.append(Paragraph("Important Information", title_style))
    story.append(Spacer(1, 0.3*inch))
    
    disclaimer_text = """
    <b>HOLISTIC WELLNESS DISCLAIMER</b><br/><br/>
    
    This assessment provides holistic wellness guidance and does NOT constitute medical diagnosis or treatment. 
    Celloxen therapies are complementary wellness interventions designed to support overall health and wellbeing.<br/><br/>
    
    <b>Important Notes:</b><br/>
    • This is NOT a medical diagnosis<br/>
    • Results are for wellness guidance only<br/>
    • Please consult your GP for any medical concerns<br/>
    • Celloxen therapies complement, not replace, medical care<br/><br/>
    
    <b>Next Steps:</b><br/>
    1. Review these findings with your practitioner<br/>
    2. Discuss recommended therapies<br/>
    3. Create a personalized wellness plan<br/>
    4. Schedule therapy sessions<br/><br/>
    
    <b>Contact Information:</b><br/>
    For questions or to book sessions, please contact your clinic directly.
    """
    
    story.append(Paragraph(disclaimer_text, styles['Normal']))
    
    # Build PDF
    doc.build(story)
    
    return filename

# Test function
if __name__ == "__main__":
    import asyncio
    # Test with assessment ID 1
    result = asyncio.run(generate_wellness_report(1))
    print(f"Report generated: {result}")
