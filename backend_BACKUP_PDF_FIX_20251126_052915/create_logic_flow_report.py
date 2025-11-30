#!/usr/bin/env python3
"""
Celloxen Health Portal - Complete Logic Flow Report Generator
Generates comprehensive PDF documentation of the entire patient journey
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime

def create_logic_flow_report():
    """Generate the complete logic flow PDF report"""
    
    # Create PDF
    filename = f"/tmp/CELLOXEN_COMPLETE_LOGIC_FLOW_REPORT_{datetime.now().strftime('%Y%m%d')}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for content
    story = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#7C3AED'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading1_style = ParagraphStyle(
        'CustomHeading1',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#3B82F6'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold'
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6366F1'),
        spaceAfter=10,
        spaceBefore=15,
        fontName='Helvetica-Bold'
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=12,
        textColor=colors.HexColor('#8B5CF6'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY
    )
    
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        leftIndent=20,
        spaceAfter=8,
        fontName='Courier'
    )
    
    # Title Page
    story.append(Spacer(1, 2*inch))
    story.append(Paragraph("CELLOXEN HEALTH PORTAL", title_style))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Complete Patient Journey Logic Flow", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Technical Documentation & System Architecture", body_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%d %B %Y')}", body_style))
    story.append(Paragraph("<b>Version:</b> 1.0", body_style))
    story.append(Paragraph("<b>Status:</b> Production System Documentation", body_style))
    story.append(Paragraph("<b>Location:</b> Aberdeen, Glasgow, Edinburgh, Manchester (UK)", body_style))
    story.append(PageBreak())
    
    # Table of Contents
    story.append(Paragraph("TABLE OF CONTENTS", heading1_style))
    story.append(Spacer(1, 0.2*inch))
    
    toc_data = [
        ["Section", "Page"],
        ["1. Executive Summary", "3"],
        ["2. System Overview", "4"],
        ["3. Phase 1: Patient Onboarding", "5"],
        ["4. Phase 2: Pre-Assessment Questionnaire", "7"],
        ["5. Phase 3: Comprehensive In-Clinic Assessment", "10"],
        ["6. Phase 4: Therapy Planning", "18"],
        ["7. Phase 5: Patient Portal Access", "19"],
        ["8. Phase 6: Ongoing Therapy", "20"],
        ["9. Technical Architecture", "21"],
        ["10. Current Status & Roadmap", "23"],
    ]
    
    toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(toc_table)
    story.append(PageBreak())
    
    # Executive Summary
    story.append(Paragraph("1. EXECUTIVE SUMMARY", heading1_style))
    story.append(Paragraph(
        "The Celloxen Health Portal is a comprehensive multi-tenant clinic management platform "
        "designed for holistic wellness therapy services across UK clinics. This document details "
        "the complete patient journey from initial contact through therapy completion, including "
        "technical implementation details and system architecture.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Key Features:</b>", heading3_style))
    features = [
        "Multi-tenant architecture supporting multiple clinics",
        "35-question wellness assessment system",
        "AI-powered iridology analysis (Anthropic Claude API)",
        "Professional PDF report generation",
        "Patient portal with secure authentication",
        "Comprehensive therapy management (in development)",
        "Email notification system (IONOS SMTP)"
    ]
    for feature in features:
        story.append(Paragraph(f"• {feature}", body_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Current Status:</b> 45% Complete (Phase 2: 90% Complete)", heading3_style))
    story.append(PageBreak())
    
    # System Overview
    story.append(Paragraph("2. SYSTEM OVERVIEW", heading1_style))
    story.append(Paragraph("2.1 Core Therapy Domains", heading2_style))
    
    domains_data = [
        ["Code", "Therapy Domain", "Focus Area"],
        ["C-102", "Vitality & Energy Support", "Energy, fatigue, metabolic function"],
        ["C-104", "Comfort & Mobility Support", "Pain, inflammation, joint mobility"],
        ["C-105", "Stress & Anxiety Relief", "Mental wellness, relaxation, mood"],
        ["C-107", "Metabolic Wellness", "Weight, blood sugar, metabolism"],
        ["C-108", "Digestive Health", "Digestion, gut health, comfort"],
    ]
    
    domains_table = Table(domains_data, colWidths=[0.8*inch, 2.5*inch, 2.5*inch])
    domains_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(domains_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("2.2 System Architecture", heading2_style))
    story.append(Paragraph(
        "<b>Backend:</b> Python FastAPI + PostgreSQL + asyncpg<br/>"
        "<b>Frontend:</b> React 18 + Tailwind CSS<br/>"
        "<b>Infrastructure:</b> Ubuntu 24.04 + Nginx + SSL<br/>"
        "<b>AI Integration:</b> Anthropic Claude API<br/>"
        "<b>Email:</b> IONOS SMTP<br/>"
        "<b>Authentication:</b> JWT tokens + RBAC",
        body_style
    ))
    story.append(PageBreak())
    
    # Phase 1: Patient Onboarding
    story.append(Paragraph("3. PHASE 1: PATIENT ONBOARDING", heading1_style))
    story.append(Paragraph("3.1 Initial Contact", heading2_style))
    story.append(Paragraph(
        "Patient contacts clinic via phone, email, or walk-in. Receptionist gathers basic "
        "information and books initial consultation appointment.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("3.2 Patient Registration in System", heading2_style))
    story.append(Paragraph("<b>Process Flow:</b>", heading3_style))
    registration_steps = [
        "1. Clinic staff logs into Clinic Portal",
        "2. Navigates to: Dashboard → Patients → Add New Patient",
        "3. Completes registration form:",
        "   • Personal Information (Name, DOB, Address, Phone, Email)",
        "   • Medical History (Conditions, Medications, Allergies)",
        "   • Emergency Contact Details",
        "4. Clicks 'Save Patient'",
        "5. System generates unique Patient Number (e.g., CLX-ABD-00010)",
        "6. Patient record created in database"
    ]
    for step in registration_steps:
        story.append(Paragraph(step, body_style))
    
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Database:</b> patients table", code_style))
    story.append(Paragraph("<b>Status:</b> ✅ Fully Operational (9 active patients)", code_style))
    story.append(PageBreak())
    
    # Phase 2: Pre-Assessment
    story.append(Paragraph("4. PHASE 2: PRE-ASSESSMENT QUESTIONNAIRE", heading1_style))
    story.append(Paragraph("4.1 Email Invitation System", heading2_style))
    story.append(Paragraph(
        "Clinic staff sends secure email invitation containing unique registration token and "
        "link to online wellness assessment portal.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Email Template:</b>", heading3_style))
    story.append(Paragraph(
        "Dear [Patient Name],<br/><br/>"
        "Welcome to Celloxen Health Portal. Please complete your wellness assessment by clicking "
        "the secure link below:<br/><br/>"
        "https://celloxen.com/register?token=abc123xyz...<br/><br/>"
        "This assessment takes approximately 10-15 minutes and will help us provide personalized "
        "wellness therapy recommendations.<br/><br/>"
        "Best regards,<br/>"
        "Aberdeen Wellness Centre Team",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Technical Implementation:</b>", heading3_style))
    story.append(Paragraph("• IONOS SMTP integration", body_style))
    story.append(Paragraph("• Unique token generation (UUID)", body_style))
    story.append(Paragraph("• Token expiration: 7 days", body_style))
    story.append(Paragraph("• Database logging of all email events", body_style))
    story.append(Paragraph("<b>Status:</b> ✅ Fully Operational", code_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("4.2 Patient Online Registration", heading2_style))
    story.append(Paragraph(
        "Patient clicks email link and arrives at secure registration portal. Token is "
        "validated, and patient sees personalized welcome message.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("4.3 35-Question Wellness Chatbot", heading2_style))
    story.append(Paragraph(
        "Interactive chatbot guides patient through comprehensive wellness assessment covering "
        "five therapy domains. Each domain contains 7 questions scored on 1-5 scale.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    # Questionnaire Structure Table
    story.append(Paragraph("<b>Questionnaire Structure:</b>", heading3_style))
    questionnaire_data = [
        ["Domain", "Code", "Questions", "Max Score"],
        ["Vitality & Energy Support", "C-102", "7", "35"],
        ["Comfort & Mobility Support", "C-104", "7", "35"],
        ["Stress & Anxiety Relief", "C-105", "7", "35"],
        ["Metabolic Wellness", "C-107", "7", "35"],
        ["Digestive Health", "C-108", "7", "35"],
        ["TOTAL", "", "35", "175"],
    ]
    
    questionnaire_table = Table(questionnaire_data, colWidths=[2.2*inch, 0.8*inch, 1*inch, 1*inch])
    questionnaire_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366F1')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E0E7FF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(questionnaire_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Scoring Algorithm:</b>", heading3_style))
    story.append(Paragraph("Raw Score = Sum of all answers (35 to 175)", code_style))
    story.append(Paragraph("Wellness Score = ((Raw Score - 35) / 140) × 100", code_style))
    story.append(Paragraph("Example: 105/175 → 50% wellness score", code_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status:</b> ✅ Fully Operational", code_style))
    story.append(PageBreak())
    
    # Phase 3: Comprehensive Assessment
    story.append(Paragraph("5. PHASE 3: COMPREHENSIVE IN-CLINIC ASSESSMENT", heading1_style))
    story.append(Paragraph("5.1 Smart Assessment Dashboard", heading2_style))
    story.append(Paragraph(
        "When practitioner opens Smart Assessment and selects a patient, the system displays "
        "comprehensive assessment interface with aviation-style wellness domain dials, progress "
        "monitoring, and integrated AI wellness consultant.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Dashboard Components:</b>", heading3_style))
    dashboard_components = [
        "<b>Patient Overview Card:</b> Name, ID, contact details, full record link",
        "<b>Assessment Progress Monitor:</b> Visual progress bar with module status",
        "<b>Wellness Domain Dials:</b> Five aviation-style analogue gauges (0-7 scale)",
        "<b>Assessment Modules:</b> Four cards (Questionnaire, Iridology, Analysis, Report)",
        "<b>Therapy & Appointments Panel:</b> Current therapy, previous assessments, upcoming appointments",
        "<b>AI Wellness Consultant:</b> Integrated chat panel for real-time guidance"
    ]
    for component in dashboard_components:
        story.append(Paragraph(f"• {component}", body_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Current Implementation Status:</b>", heading3_style))
    story.append(Paragraph("✅ Dashboard UI: 100% complete", body_style))
    story.append(Paragraph("⚠️ Data Integration: Uses mock data (needs API connection)", body_style))
    story.append(Paragraph("⚠️ AI Consultant: UI complete, backend not connected", body_style))
    story.append(PageBreak())
    
    story.append(Paragraph("5.2 Iridology Image Capture & AI Analysis", heading2_style))
    story.append(Paragraph(
        "Practitioner captures iris images using either live camera or file upload. System "
        "sends both images to Anthropic Claude API for professional iridology analysis.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Capture Methods:</b>", heading3_style))
    story.append(Paragraph(
        "<b>Option 1: Camera Capture</b><br/>"
        "• Live webcam or specialized iris camera<br/>"
        "• Real-time video preview<br/>"
        "• Capture left eye, then right eye<br/>"
        "• Images stored as base64<br/><br/>"
        "<b>Option 2: File Upload</b><br/>"
        "• Select pre-captured images<br/>"
        "• Supports JPG, PNG formats<br/>"
        "• Left and right eye images<br/>"
        "• Automatic resizing and optimization",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>AI Analysis Components:</b>", heading3_style))
    ai_analysis_data = [
        ["Component", "Description", "Output"],
        ["Constitutional Type", "Lymphatic, Hematogenic, or Mixed based on iris color", "Type classification"],
        ["Constitutional Strength", "Fiber density and integrity assessment", "Score 1-10"],
        ["Body Systems", "5 major systems (Digestive, Nervous, Circulatory, Lymphatic, Structural)", "Severity 0-10 each"],
        ["Iris Signs", "Lacunae, nerve rings, crypts, pigment spots, etc.", "List of identified signs"],
        ["Primary Concerns", "Top 3 wellness areas needing attention", "Prioritized list"],
        ["Recommendations", "Diet, lifestyle, stress management suggestions", "Actionable advice"],
    ]
    
    ai_analysis_table = Table(ai_analysis_data, colWidths=[1.5*inch, 2.5*inch, 1.8*inch])
    ai_analysis_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8B5CF6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(ai_analysis_table)
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Technical Implementation:</b>", heading3_style))
    story.append(Paragraph("• API: Anthropic Claude (claude-sonnet-4-20250514)", body_style))
    story.append(Paragraph("• Cost: ~$0.03 per analysis (~£0.02)", body_style))
    story.append(Paragraph("• Processing time: 10-15 seconds", body_style))
    story.append(Paragraph("• Database: iridology_findings table", body_style))
    story.append(Paragraph("• Status: ✅ Backend fully operational (built 12 Nov 2025)", code_style))
    story.append(Paragraph("• Status: ⚠️ Frontend needs connection", code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("5.3 Integrated Recommendations Engine", heading2_style))
    story.append(Paragraph(
        "System combines questionnaire scores and iridology findings to generate personalized "
        "therapy recommendations for each of the five wellness domains.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Recommendation Generation Process:</b>", heading3_style))
    recommendation_steps = [
        "1. Analyze questionnaire domain scores (0-7 scale)",
        "2. Review iridology constitutional type and strength",
        "3. Assess body system conditions and severity",
        "4. Calculate priority level (High/Moderate/Low) for each domain",
        "5. Determine if therapy is recommended (Yes/No)",
        "6. Calculate session requirements:",
        "   • Number of sessions (typically 12-18)",
        "   • Session frequency (2-3× per week)",
        "   • Total duration (4-8 weeks)",
        "   • Session length (30-45 minutes)",
        "7. Generate key benefits list (4-5 points)",
        "8. Create personalized rationale explaining recommendation",
        "9. Store integrated recommendations in database"
    ]
    for step in recommendation_steps:
        story.append(Paragraph(step, body_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Example Recommendation Output:</b>", heading3_style))
    story.append(Paragraph(
        "<b>C-102 Vitality & Energy Support</b><br/>"
        "Priority: HIGH (Critical wellness level)<br/>"
        "Recommended: YES<br/>"
        "Sessions: 12 sessions<br/>"
        "Frequency: 3× per week<br/>"
        "Duration: 4 weeks<br/>"
        "Session Length: 30 minutes<br/><br/>"
        "<b>Key Benefits:</b><br/>"
        "• Enhanced cellular energy production<br/>"
        "• Improved mental clarity and focus<br/>"
        "• Better stress resilience<br/>"
        "• Optimized metabolic function<br/><br/>"
        "<b>Rationale:</b> Your assessment shows critical energy levels (score: 2.1/7) combined "
        "with weak constitutional strength (8/10). C-102 therapy is recommended to enhance your "
        "vitality and prevent future health concerns.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status:</b> ✅ Fully Operational (built 12 Nov 2025)", code_style))
    story.append(PageBreak())
    
    story.append(Paragraph("5.4 Professional PDF Report Generation", heading2_style))
    story.append(Paragraph(
        "System generates comprehensive multi-page PDF report containing all assessment results, "
        "iridology findings, and therapy recommendations in professional format.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Report Structure:</b>", heading3_style))
    report_structure = [
        "<b>Page 1: Cover & Patient Information</b>",
        "• Celloxen Health Portal branding",
        "• Report title and date",
        "• Patient details (name, ID, DOB)",
        "• Practitioner and clinic information",
        "",
        "<b>Page 2: Assessment Results</b>",
        "• Overall wellness score (0-100%)",
        "• Questionnaire results table (5 domains with scores and priorities)",
        "• Iridology findings summary",
        "• Constitutional type and strength",
        "• Primary body systems affected",
        "• Key iris signs identified",
        "",
        "<b>Page 3: Therapy Recommendations</b>",
        "• Detailed recommendations for each therapy domain",
        "• Priority classification (High/Moderate/Low)",
        "• Session requirements and frequency",
        "• Key benefits for each therapy",
        "• Personalized rationale",
        "",
        "<b>Page 4: Legal Disclaimer</b>",
        "• Wellness assessment disclaimer",
        "• Medical advice disclaimer",
        "• Complementary therapy statement",
        "• GP consultation recommendation"
    ]
    for item in report_structure:
        if item:
            story.append(Paragraph(item, body_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Technical Specifications:</b>", heading3_style))
    story.append(Paragraph("• Library: ReportLab (Python)", body_style))
    story.append(Paragraph("• Format: PDF version 1.4", body_style))
    story.append(Paragraph("• Pages: 3-4 pages typical", body_style))
    story.append(Paragraph("• File size: 5-10KB", body_style))
    story.append(Paragraph("• Language: British English throughout", body_style))
    story.append(Paragraph("• Branding: Celloxen colour scheme (purple/blue)", body_style))
    story.append(Paragraph("<b>Status:</b> ✅ Fully Operational (tested 12 Nov 2025)", code_style))
    story.append(Paragraph("<b>Test Result:</b> 3-page report generated (5.2KB)", code_style))
    story.append(PageBreak())
    
    # Phase 4: Therapy Planning
    story.append(Paragraph("6. PHASE 4: THERAPY PLANNING", heading1_style))
    story.append(Paragraph("6.1 Therapy Plan Creation", heading2_style))
    story.append(Paragraph(
        "Following assessment completion and report review, practitioner creates customized "
        "therapy plan based on recommendations. Patient provides consent before therapy begins.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status:</b> ❌ Not Built (Phase 3 - Pending)", code_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("6.2 Appointment Booking System", heading2_style))
    story.append(Paragraph(
        "Bulk booking system for scheduling multiple therapy sessions across several weeks. "
        "Integrates with clinic calendar and sends automated reminders.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status:</b> ❌ Not Built (Phase 3 - Pending)", code_style))
    story.append(PageBreak())
    
    # Phase 5: Patient Portal
    story.append(Paragraph("7. PHASE 5: PATIENT PORTAL ACCESS", heading1_style))
    story.append(Paragraph(
        "Patients can log into secure portal to view assessment results, therapy plans, "
        "appointments, and download reports.",
        body_style
    ))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("<b>Available Features:</b>", heading3_style))
    story.append(Paragraph("• Secure login with JWT authentication", body_style))
    story.append(Paragraph("• Dashboard with wellness score", body_style))
    story.append(Paragraph("• View assessment summary", body_style))
    story.append(Paragraph("• Download PDF reports", body_style))
    story.append(Paragraph("• Profile management", body_style))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status:</b> ⚠️ 95% Complete (mostly functional)", code_style))
    story.append(PageBreak())
    
    # Phase 6: Ongoing Therapy
    story.append(Paragraph("8. PHASE 6: ONGOING THERAPY", heading1_style))
    story.append(Paragraph("8.1 Session Tracking", heading2_style))
    story.append(Paragraph(
        "System to track therapy session attendance, practitioner notes, and patient progress "
        "throughout treatment programme.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status:</b> ❌ Not Built (Phase 3 - Pending)", code_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("8.2 Progress Monitoring & Re-Assessment", heading2_style))
    story.append(Paragraph(
        "Mid-course reviews and re-assessments after 3-6 months to measure improvement and "
        "adjust therapy plans as needed.",
        body_style
    ))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("<b>Status:</b> ❌ Not Built (Future Feature)", code_style))
    story.append(PageBreak())
    
    # Technical Architecture
    story.append(Paragraph("9. TECHNICAL ARCHITECTURE", heading1_style))
    story.append(Paragraph("9.1 System Components", heading2_style))
    
    tech_stack_data = [
        ["Component", "Technology", "Version/Details"],
        ["Operating System", "Ubuntu Server", "24.04 LTS"],
        ["Web Server", "Nginx", "Reverse proxy + SSL"],
        ["SSL Certificates", "Let's Encrypt", "Auto-renewal"],
        ["Backend Framework", "Python FastAPI", "Async/await support"],
        ["Database", "PostgreSQL", "Version 15"],
        ["Database Driver", "asyncpg", "Async PostgreSQL driver"],
        ["Frontend Framework", "React", "Version 18 (CDN)"],
        ["CSS Framework", "Tailwind CSS", "Version 3"],
        ["Authentication", "JWT Tokens", "Bearer token auth"],
        ["Access Control", "RBAC", "Role-based permissions"],
        ["AI Integration", "Anthropic Claude", "claude-sonnet-4-20250514"],
        ["Email Service", "IONOS SMTP", "Production SMTP"],
        ["PDF Generation", "ReportLab", "Python library"],
    ]
    
    tech_stack_table = Table(tech_stack_data, colWidths=[2*inch, 2*inch, 2*inch])
    tech_stack_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(tech_stack_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("9.2 Database Schema", heading2_style))
    story.append(Paragraph("<b>Core Tables:</b>", heading3_style))
    db_tables = [
        "<b>patients</b> - Patient demographics and medical history (9 records)",
        "<b>users</b> - System user accounts with authentication",
        "<b>comprehensive_assessments</b> - Assessment responses and scores (25 records)",
        "<b>iridology_findings</b> - AI analysis results and constitutional data",
        "<b>therapy_correlations</b> - Mapping between assessments and therapies",
        "<b>invitation_tokens</b> - Secure registration tokens",
        "<b>chatbot_sessions</b> - AI consultant conversation sessions",
        "<b>chatbot_messages</b> - Individual chat messages and responses"
    ]
    for table in db_tables:
        story.append(Paragraph(f"• {table}", body_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("9.3 API Endpoints", heading2_style))
    story.append(Paragraph("<b>Authentication:</b>", heading3_style))
    story.append(Paragraph("• POST /api/v1/auth/login - User authentication", code_style))
    story.append(Paragraph("• GET /api/v1/auth/me - Get current user", code_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Assessment System:</b>", heading3_style))
    story.append(Paragraph("• POST /api/v1/assessments/comprehensive - Create assessment", code_style))
    story.append(Paragraph("• POST /api/v1/assessments/{id}/iridology - AI iridology analysis", code_style))
    story.append(Paragraph("• GET /api/v1/assessments/{id}/complete - Get full assessment data", code_style))
    story.append(Paragraph("• GET /api/v1/assessments/{id}/report - Generate PDF report", code_style))
    story.append(Spacer(1, 0.1*inch))
    
    story.append(Paragraph("<b>Patient Management:</b>", heading3_style))
    story.append(Paragraph("• GET /api/v1/clinic/patients - List all patients", code_style))
    story.append(Paragraph("• GET /api/v1/patients/{id} - Get patient details", code_style))
    story.append(Paragraph("• POST /api/v1/patients - Create new patient", code_style))
    story.append(PageBreak())
    
    # Current Status & Roadmap
    story.append(Paragraph("10. CURRENT STATUS & ROADMAP", heading1_style))
    story.append(Paragraph("10.1 Project Status Overview", heading2_style))
    
    status_data = [
        ["Phase", "Component", "Status", "Progress"],
        ["1", "Foundation & Infrastructure", "✅ Complete", "100%"],
        ["2", "Health Assessment System", "⚠️ Almost Complete", "90%"],
        ["", "• Email Invitations", "✅ Complete", ""],
        ["", "• Patient Registration", "✅ Complete", ""],
        ["", "• 35-Q Questionnaire", "✅ Complete", ""],
        ["", "• AI Iridology", "✅ Backend Complete", ""],
        ["", "• PDF Reports", "✅ Complete", ""],
        ["", "• Frontend Integration", "⚠️ Needs Wiring", ""],
        ["3", "Therapy Management", "❌ Not Started", "0%"],
        ["4", "Notifications", "⚠️ Partial", "40%"],
        ["5", "Patient Portal", "⚠️ Mostly Done", "60%"],
        ["6", "Analytics & Reporting", "❌ Not Started", "0%"],
        ["7", "Polish & Optimization", "❌ Not Started", "0%"],
        ["8", "Launch Preparation", "❌ Not Started", "0%"],
    ]
    
    status_table = Table(status_data, colWidths=[0.5*inch, 2.5*inch, 1.5*inch, 1*inch])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7C3AED')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("10.2 Key Achievements (12 November 2025)", heading2_style))
    achievements = [
        "✅ Integrated Anthropic Claude AI for iridology analysis",
        "✅ Built professional PDF report generator (ReportLab)",
        "✅ Created recommendation engine combining questionnaire + iridology",
        "✅ Completed 4 new backend API endpoints",
        "✅ Successfully tested with real patient data (Bassam Khalil)",
        "✅ Generated first complete assessment report (3 pages, 5.2KB)"
    ]
    for achievement in achievements:
        story.append(Paragraph(achievement, body_style))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("10.3 Immediate Next Steps", heading2_style))
    story.append(Paragraph("<b>Priority 1: Frontend Integration (3-4 hours)</b>", heading3_style))
    next_steps = [
        "1. Connect loadPatientAssessment() to real API",
        "2. Wire iridology upload to backend endpoint",
        "3. Add onClick handler to 'CONTINUE ASSESSMENT' button",
        "4. Connect AI consultant to chatbot backend",
        "5. Test complete end-to-end flow"
    ]
    for step in next_steps:
        story.append(Paragraph(step, body_style))
    
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Priority 2: Build Therapy Management (3-4 weeks)</b>", heading3_style))
    therapy_steps = [
        "1. Design therapy plan creation UI",
        "2. Build appointment booking system",
        "3. Implement session tracking",
        "4. Create progress monitoring",
        "5. Build mid-course review functionality"
    ]
    for step in therapy_steps:
        story.append(Paragraph(step, body_style))
    
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("10.4 Timeline to Production", heading2_style))
    
    timeline_data = [
        ["Milestone", "Duration", "Target"],
        ["Fix Frontend Integration", "1 week", "Week 1"],
        ["Build Therapy Management", "3-4 weeks", "Weeks 2-5"],
        ["Complete Notifications", "2 weeks", "Weeks 6-7"],
        ["Finish Patient Portal", "2 weeks", "Weeks 8-9"],
        ["Essential Reporting", "1-2 weeks", "Weeks 10-11"],
        ["Testing & Polish", "2-3 weeks", "Weeks 12-14"],
        ["PRODUCTION READY", "", "Week 14"],
    ]
    
    timeline_table = Table(timeline_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    timeline_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#D1FAE5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    story.append(timeline_table)
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("<b>Estimated Time to Production: 10-14 weeks</b>", heading3_style))
    story.append(PageBreak())
    
    # Appendix
    story.append(Paragraph("APPENDIX: SYSTEM CREDENTIALS & REFERENCES", heading1_style))
    story.append(Paragraph("<b>⚠️ CONFIDENTIAL INFORMATION - DO NOT DISTRIBUTE</b>", heading3_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("A.1 Database Credentials", heading2_style))
    story.append(Paragraph("Host: localhost", code_style))
    story.append(Paragraph("Port: 5432", code_style))
    story.append(Paragraph("Database: celloxen_portal", code_style))
    story.append(Paragraph("User: celloxen_user", code_style))
    story.append(Paragraph("Password: CelloxenSecure2025", code_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("A.2 Clinic User Credentials", heading2_style))
    story.append(Paragraph("Email: staff@aberdeenwellness.co.uk", code_style))
    story.append(Paragraph("Password: Staff123!", code_style))
    story.append(Paragraph("Role: clinic_user", code_style))
    story.append(Spacer(1, 0.2*inch))
    
    story.append(Paragraph("A.3 API Keys", heading2_style))
    story.append(Paragraph("Anthropic Claude: Configured in /var/www/celloxen-portal/backend/.env", code_style))
    story.append(Paragraph("IONOS SMTP: Configured in backend", code_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("A.4 File Locations", heading2_style))
    story.append(Paragraph("Backend: /var/www/celloxen-portal/backend/", code_style))
    story.append(Paragraph("Frontend: /var/www/celloxen-portal-new/frontend/", code_style))
    story.append(Paragraph("Logs: /var/log/celloxen-backend.log", code_style))
    story.append(Spacer(1, 0.3*inch))
    
    story.append(Paragraph("A.5 Current Live Data", heading2_style))
    story.append(Paragraph("Active Patients: 9", code_style))
    story.append(Paragraph("Completed Assessments: 25", code_style))
    story.append(Paragraph("Generated Reports: 1 (test)", code_style))
    story.append(Paragraph("Active Clinics: 1 (Aberdeen Wellness Centre)", code_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Footer
    story.append(Paragraph("=" * 80, code_style))
    story.append(Paragraph(
        "<b>END OF DOCUMENT</b><br/>"
        "Celloxen Health Portal - Complete Logic Flow Report<br/>"
        f"Generated: {datetime.now().strftime('%d %B %Y at %H:%M GMT')}<br/>"
        "Version: 1.0<br/>"
        "© 2025 Celloxen Health Portal. All Rights Reserved.",
        body_style
    ))
    
    # Build PDF
    doc.build(story)
    print(f"✅ PDF Report generated: {filename}")
    return filename

if __name__ == "__main__":
    try:
        pdf_file = create_logic_flow_report()
        print(f"\n📄 Report Location: {pdf_file}")
        print("📊 Ready to download!")
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()

