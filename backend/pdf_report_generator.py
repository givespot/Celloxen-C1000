"""
CELLOXEN HEALTH PORTAL - Professional Wellness Report Generator
VERSION 5.0 - Holistic Clinic Edition (British English, No Supplements)
Created: 26 November 2025
"""

from weasyprint import HTML
from datetime import datetime
import json


def get_score_status(score):
    """Get status label and colours for a wellness score."""
    if score >= 75:
        return 'Excellent', '#10b981', '#d1fae5'
    elif score >= 50:
        return 'Good Progress', '#f59e0b', '#fef3c7'
    elif score >= 35:
        return 'Needs Support', '#ef4444', '#fee2e2'
    else:
        return 'Requires Attention', '#dc2626', '#fecaca'


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


def generate_progress_bar_svg(score, width=120, height=12):
    """Generate an inline SVG progress bar for the score"""
    if score >= 75:
        fill_colour = '#10b981'
    elif score >= 50:
        fill_colour = '#f59e0b'
    elif score >= 35:
        fill_colour = '#ef4444'
    else:
        fill_colour = '#dc2626'
    
    fill_width = (score / 100) * width
    
    return f'''<svg width="{width}" height="{height}" style="vertical-align: middle;">
        <rect x="0" y="2" width="{width}" height="{height-4}" rx="4" fill="#e5e7eb"/>
        <rect x="0" y="2" width="{fill_width}" height="{height-4}" rx="4" fill="{fill_colour}"/>
    </svg>'''


def generate_html_report(patient_data, assessment_data):
    """Generate professional HTML content for wellness assessment report."""
    
    # Parse AI report if it exists
    ai_report = None
    if assessment_data.get('ai_report'):
        if isinstance(assessment_data['ai_report'], str):
            try:
                ai_report = json.loads(assessment_data['ai_report'])
            except:
                ai_report = None
        else:
            ai_report = assessment_data['ai_report']
    
    # Domain scores - extract from various possible sources
    scores = {}
    
    if assessment_data.get('questionnaire_scores'):
        qs = assessment_data['questionnaire_scores']
        if isinstance(qs, str):
            try:
                qs = json.loads(qs)
            except:
                qs = {}
        
        domain_mapping = {
            'c102_vitality_energy': ('C-102', 'Vitality & Energy Support'),
            'c104_comfort_mobility': ('C-104', 'Comfort & Mobility Support'),
            'c105_circulation_heart': ('C-105', 'Circulation & Heart Wellness'),
            'c107_stress_relaxation': ('C-107', 'Stress & Relaxation Support'),
            'c108_metabolic_balance': ('C-108', 'Metabolic Balance Support'),
            'energy': ('C-102', 'Vitality & Energy Support'),
            'comfort': ('C-104', 'Comfort & Mobility Support'),
            'circulation': ('C-105', 'Circulation & Heart Wellness'),
            'stress': ('C-107', 'Stress & Relaxation Support'),
            'metabolic': ('C-108', 'Metabolic Balance Support'),
        }
        
        for key, value in qs.items():
            if isinstance(value, dict) and 'score' in value:
                code = value.get('therapy_code', key)
                name = value.get('domain_name', key)
                scores[code] = {'name': name, 'score': float(value['score'])}
            elif key in domain_mapping:
                code, name = domain_mapping[key]
                scores[code] = {'name': name, 'score': float(value) if isinstance(value, (int, float)) else 0}
    
    if not scores:
        scores = {
            'C-102': {'name': 'Vitality & Energy Support', 'score': float(assessment_data.get('energy_score', 0))},
            'C-104': {'name': 'Comfort & Mobility Support', 'score': float(assessment_data.get('comfort_score', 0))},
            'C-105': {'name': 'Circulation & Heart Wellness', 'score': float(assessment_data.get('circulation_score', 0))},
            'C-107': {'name': 'Stress & Relaxation Support', 'score': float(assessment_data.get('stress_score', 0))},
            'C-108': {'name': 'Metabolic Balance Support', 'score': float(assessment_data.get('metabolic_score', 0))}
        }
    
    overall_score = float(assessment_data.get('overall_wellness_score', 0) or assessment_data.get('overall_score', 0))
    overall_status, overall_colour, overall_bg = get_score_status(overall_score)
    
    patient_name = f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}".strip()
    patient_number = patient_data.get('patient_number', 'N/A')
    date_of_birth_raw = patient_data.get('date_of_birth', 'N/A')
    # Convert to British format DD/MM/YYYY
    date_of_birth = 'N/A'
    if date_of_birth_raw and date_of_birth_raw != 'N/A':
        try:
            # Handle date objects from database
            if hasattr(date_of_birth_raw, 'strftime'):
                date_of_birth = date_of_birth_raw.strftime('%d/%m/%Y')
            # Handle string dates (YYYY-MM-DD format)
            elif isinstance(date_of_birth_raw, str):
                dob_str = str(date_of_birth_raw).split('T')[0]
                if '-' in dob_str and len(dob_str) >= 10:
                    parts = dob_str.split('-')
                    if len(parts) == 3 and len(parts[0]) == 4:
                        date_of_birth = f"{parts[2]}/{parts[1]}/{parts[0]}"
                    else:
                        date_of_birth = dob_str
                else:
                    date_of_birth = dob_str
            else:
                date_of_birth = str(date_of_birth_raw)
        except:
            date_of_birth = str(date_of_birth_raw) if date_of_birth_raw else 'N/A'

    assessment_id = assessment_data.get('id', 'N/A')
    assessment_date = assessment_data.get('assessment_date')
    report_date = format_british_date()
    report_datetime = format_british_datetime()
    assessment_date_formatted = format_british_date(assessment_date) if assessment_date else report_date
    
    # Build domain scores table
    domain_scores_html = ""
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]['score'])
    
    for code, data in scores.items():
        score = data['score']
        status, colour, bg_colour = get_score_status(score)
        progress_bar = generate_progress_bar_svg(score)
        domain_scores_html += f"""
        <tr>
            <td class="domain-name">{code}: {data['name']}</td>
            <td class="domain-bar">{progress_bar}</td>
            <td class="domain-score">{score:.0f}%</td>
            <td class="domain-status"><span class="status-badge" style="background: {bg_colour}; color: {colour};">{status}</span></td>
        </tr>"""
    
    # Executive Summary
    if ai_report and ai_report.get('executive_summary'):
        exec_summary_text = ai_report['executive_summary']
    else:
        priority_domains = [f"{code}: {data['name']} ({data['score']:.0f}%)" for code, data in sorted_scores[:3] if data['score'] < 60]
        if priority_domains:
            exec_summary_text = f"Based on your comprehensive wellness assessment, your overall wellness score is <strong>{overall_score:.0f}%</strong> ({overall_status}). The assessment identified several areas where targeted support may help improve your quality of life, particularly in: {', '.join(priority_domains)}."
        else:
            exec_summary_text = f"Based on your comprehensive wellness assessment, your overall wellness score is <strong>{overall_score:.0f}%</strong> ({overall_status}). Your results indicate a generally positive wellness profile."
    
    # Strengths and concerns
    strengths = []
    concerns = []
    if ai_report:
        wo = ai_report.get('wellness_overview', {})
        concerns = wo.get('primary_concerns', [])[:5]
        strengths = wo.get('positive_indicators', [])[:5]
    
    if not strengths:
        for code, data in scores.items():
            if data['score'] >= 60:
                strengths.append(f"Good foundation in {data['name'].lower()}")
        if not strengths:
            strengths = ["Proactive approach to wellness", "Commitment to health assessment"]
    
    if not concerns:
        for code, data in sorted_scores[:3]:
            if data['score'] < 50:
                concerns.append(f"{data['name']} may benefit from additional support")
    
    strengths_html = ''.join([f'<li>{s}</li>' for s in strengths[:5]])
    concerns_html = ''.join([f'<li>{c}</li>' for c in concerns[:5]])
    
    # Therapy recommendations
    therapy_html = ""
    therapies_found = False
    
    if ai_report and ai_report.get('therapy_recommendations'):
        for therapy in ai_report['therapy_recommendations'][:3]:
            therapies_found = True
            code = therapy.get('therapy_code', '')
            name = therapy.get('therapy_name', '')
            reason = therapy.get('recommendation_reason', '')
            priority = therapy.get('priority', 0)
            plan = therapy.get('treatment_plan', {})
            sessions = plan.get('sessions', '12-16')
            frequency = plan.get('frequency', 'As recommended')
            duration = plan.get('duration', '30-40 minutes')
            benefits = therapy.get('expected_benefits', [])
            benefits_html = ''.join([f'<li>{b}</li>' for b in benefits[:5]])
            therapy_score = scores.get(code, {}).get('score', 0)
            status, colour, bg_colour = get_score_status(therapy_score)
            
            therapy_html += f"""
            <div class="therapy-card">
                <div class="therapy-header" style="background: {bg_colour}; border-left: 4px solid {colour};">
                    <h3>{code}: {name}</h3>
                    <span class="priority-badge" style="background: {colour};">Priority {priority} - Score: {therapy_score:.0f}%</span>
                </div>
                <div class="therapy-body">
                    <h4>Why This Therapy May Help</h4>
                    <p>{reason}</p>
                    <table class="protocol-table">
                        <tr><th>Recommended Sessions</th><th>Suggested Frequency</th><th>Session Duration</th></tr>
                        <tr><td>{sessions}</td><td>{frequency}</td><td>{duration}</td></tr>
                    </table>
                    <h4>Potential Benefits</h4>
                    <ul class="benefits-list">{benefits_html}</ul>
                </div>
            </div>"""
    
    if not therapies_found:
        priority_num = 1
        for code, data in sorted_scores:
            if data['score'] < 60 and priority_num <= 3:
                status, colour, bg_colour = get_score_status(data['score'])
                if data['score'] < 35:
                    sessions, frequency = "16-20 sessions", "Daily or as tolerated"
                elif data['score'] < 50:
                    sessions, frequency = "12-16 sessions", "3-4 times per week"
                else:
                    sessions, frequency = "10-12 sessions", "2-3 times per week"
                
                therapy_html += f"""
                <div class="therapy-card">
                    <div class="therapy-header" style="background: {bg_colour}; border-left: 4px solid {colour};">
                        <h3>{code}: {data['name']}</h3>
                        <span class="priority-badge" style="background: {colour};">Priority {priority_num} - Score: {data['score']:.0f}%</span>
                    </div>
                    <div class="therapy-body">
                        <h4>Why This Therapy May Help</h4>
                        <p>Your assessment indicates this area would benefit from targeted support.</p>
                        <table class="protocol-table">
                            <tr><th>Recommended Sessions</th><th>Suggested Frequency</th><th>Session Duration</th></tr>
                            <tr><td>{sessions}</td><td>{frequency}</td><td>30-40 minutes</td></tr>
                        </table>
                        <h4>Potential Benefits</h4>
                        <ul class="benefits-list">
                            <li>Targeted support for identified concerns</li>
                            <li>Progressive improvement over the course</li>
                            <li>Enhanced overall wellbeing</li>
                        </ul>
                    </div>
                </div>"""
                priority_num += 1
    
    # Lifestyle recommendations
    lifestyle_html = ""
    if ai_report and ai_report.get('lifestyle_recommendations'):
        items = ''.join([f'<li>{r}</li>' for r in ai_report['lifestyle_recommendations'][:8]])
        lifestyle_html = f"""<div class="lifestyle-section"><h2 class="section-title">Lifestyle Recommendations</h2><ul class="lifestyle-list">{items}</ul></div>"""
    else:
        lifestyle_items = []
        for code, data in sorted_scores[:3]:
            if code == 'C-102' and data['score'] < 60:
                lifestyle_items.extend(["Maintain consistent sleep and wake times", "Consider gentle morning movement"])
            elif code == 'C-104' and data['score'] < 60:
                lifestyle_items.extend(["Incorporate gentle stretching daily", "Apply heat or cold to areas of discomfort"])
            elif code == 'C-105' and data['score'] < 60:
                lifestyle_items.extend(["Stay well-hydrated throughout the day", "Include regular gentle movement"])
            elif code == 'C-107' and data['score'] < 60:
                lifestyle_items.extend(["Practice deep breathing for 5-10 minutes daily", "Create a calming evening routine"])
            elif code == 'C-108' and data['score'] < 60:
                lifestyle_items.extend(["Maintain regular meal times", "Reduce refined sugar intake"])
        if lifestyle_items:
            items = ''.join([f'<li>{r}</li>' for r in lifestyle_items[:6]])
            lifestyle_html = f"""<div class="lifestyle-section"><h2 class="section-title">Lifestyle Recommendations</h2><ul class="lifestyle-list">{items}</ul></div>"""
    
    clinic_email = assessment_data.get('clinic_email', 'health@celloxen.co.uk')
    
    # Full HTML
    html_content = f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
    <meta charset="utf-8">
    <title>Wellness Assessment Report - {patient_name}</title>
    <style>
        @page {{size: A4; margin: 20mm 15mm 25mm 15mm;
            @top-center {{content: "CELLOXEN HEALTH - Comprehensive Wellness Assessment"; font-family: Helvetica, Arial, sans-serif; font-size: 8pt; color: #6b7280; border-bottom: 1px solid #e5e7eb; padding-bottom: 5mm;}}
            @bottom-left {{content: "{patient_name} | {patient_number}"; font-family: Helvetica, Arial, sans-serif; font-size: 7pt; color: #6b7280;}}
            @bottom-center {{content: "Page " counter(page) " of " counter(pages); font-family: Helvetica, Arial, sans-serif; font-size: 7pt; color: #6b7280;}}
            @bottom-right {{content: "www.celloxen.co.uk"; font-family: Helvetica, Arial, sans-serif; font-size: 7pt; color: #1e3a8a;}}
        }}
        @page :first {{@top-center {{content: ""; border-bottom: none;}}}}
        * {{box-sizing: border-box;}}
        body {{font-family: Helvetica, Arial, sans-serif; color: #1f2937; line-height: 1.5; font-size: 9.5pt; margin: 0; padding: 0;}}
        .report-header {{text-align: center; border-bottom: 3px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 15px;}}
        .report-header h1 {{color: #1e3a8a; font-size: 22pt; margin: 0 0 4px 0; letter-spacing: 1px; font-weight: 700;}}
        .report-header .subtitle {{color: #3b82f6; font-size: 11pt; margin: 0; font-weight: 400;}}
        .summary-row {{display: table; width: 100%; margin-bottom: 15px;}}
        .patient-col {{display: table-cell; width: 62%; vertical-align: top; padding-right: 15px;}}
        .score-col {{display: table-cell; width: 38%; vertical-align: top;}}
        .patient-info {{background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 12px 15px;}}
        .patient-info table {{width: 100%; border-collapse: collapse;}}
        .patient-info td {{padding: 5px 8px; border-bottom: 1px solid #e5e7eb; font-size: 9pt;}}
        .patient-info td:first-child {{font-weight: 600; color: #475569; width: 40%;}}
        .patient-info tr:last-child td {{border-bottom: none;}}
        .overall-score {{background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); color: white; padding: 18px 15px; border-radius: 10px; text-align: center;}}
        .overall-score .label {{font-size: 9pt; opacity: 0.9; margin-bottom: 5px;}}
        .overall-score .score-value {{font-size: 38pt; font-weight: 700; line-height: 1; margin: 8px 0;}}
        .overall-score .status {{font-size: 11pt; font-weight: 600;}}
        .executive-summary {{background: #eff6ff; border: 1px solid #bfdbfe; border-left: 4px solid #1e3a8a; border-radius: 0 8px 8px 0; padding: 15px 18px; margin: 15px 0; page-break-inside: avoid;}}
        .executive-summary h2 {{color: #1e3a8a; font-size: 12pt; margin: 0 0 10px 0;}}
        .executive-summary p {{margin: 0; font-size: 9.5pt; line-height: 1.6;}}
        .section-title {{color: #1e3a8a; font-size: 13pt; margin: 20px 0 12px 0; padding-bottom: 6px; border-bottom: 2px solid #3b82f6; font-weight: 600;}}
        table.scores {{width: 100%; border-collapse: collapse; margin: 12px 0; page-break-inside: avoid;}}
        table.scores th {{background: #1e3a8a; color: white; padding: 10px 12px; text-align: left; font-weight: 600; font-size: 9pt;}}
        table.scores td {{padding: 10px 12px; border-bottom: 1px solid #e5e7eb; font-size: 9pt; vertical-align: middle;}}
        table.scores tr:nth-child(even) {{background: #f9fafb;}}
        .domain-name {{font-weight: 500;}}
        .domain-bar {{width: 130px;}}
        .domain-score {{text-align: center; font-weight: 700; width: 60px;}}
        .domain-status {{text-align: center; width: 110px;}}
        .status-badge {{display: inline-block; padding: 3px 10px; border-radius: 12px; font-weight: 600; font-size: 8pt;}}
        .wellness-glance {{margin: 15px 0; page-break-inside: avoid;}}
        .glance-table {{width: 100%; border-collapse: separate; border-spacing: 12px 0;}}
        .glance-table td {{width: 50%; vertical-align: top; padding: 0;}}
        .glance-box {{padding: 15px; border-radius: 8px; height: 100%;}}
        .glance-box.strengths {{background: #f0fdf4; border: 1px solid #86efac;}}
        .glance-box.concerns {{background: #fef3c7; border: 1px solid #fcd34d;}}
        .glance-box h4 {{margin: 0 0 10px 0; font-size: 10pt;}}
        .glance-box.strengths h4 {{color: #166534;}}
        .glance-box.concerns h4 {{color: #92400e;}}
        .glance-box ul {{margin: 0; padding-left: 18px;}}
        .glance-box li {{font-size: 8.5pt; margin: 5px 0; line-height: 1.4;}}
        .therapy-card {{margin: 15px 0; page-break-inside: avoid; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}}
        .therapy-header {{padding: 12px 15px; display: flex; justify-content: space-between; align-items: center;}}
        .therapy-header h3 {{margin: 0; color: #1e3a8a; font-size: 11pt;}}
        .priority-badge {{color: white; padding: 4px 10px; border-radius: 4px; font-size: 7.5pt; font-weight: 600;}}
        .therapy-body {{padding: 15px; border: 1px solid #e5e7eb; border-top: none;}}
        .therapy-body h4 {{color: #1e3a8a; font-size: 10pt; margin: 12px 0 8px 0;}}
        .therapy-body h4:first-child {{margin-top: 0;}}
        .therapy-body p {{margin: 0 0 10px 0; font-size: 9pt; line-height: 1.5;}}
        .protocol-table {{width: 100%; border-collapse: collapse; margin: 10px 0;}}
        .protocol-table th {{background: #f3f4f6; padding: 8px 10px; border: 1px solid #e5e7eb; font-size: 8pt; font-weight: 600; text-align: center;}}
        .protocol-table td {{padding: 8px 10px; border: 1px solid #e5e7eb; text-align: center; font-size: 9pt;}}
        .benefits-list {{margin: 8px 0; padding-left: 20px;}}
        .benefits-list li {{margin: 4px 0; font-size: 8.5pt;}}
        .lifestyle-section {{margin: 20px 0; page-break-inside: avoid;}}
        .lifestyle-list {{margin: 10px 0; padding-left: 20px;}}
        .lifestyle-list li {{margin: 6px 0; font-size: 9pt; line-height: 1.4;}}
        .disclaimer {{background: #fef3c7; border: 2px solid #f59e0b; border-radius: 8px; padding: 15px 18px; margin-top: 20px; page-break-inside: avoid;}}
        .disclaimer h3 {{color: #92400e; margin: 0 0 10px 0; font-size: 11pt;}}
        .disclaimer p {{margin: 8px 0; font-size: 8.5pt; line-height: 1.5;}}
        .disclaimer ul {{margin: 8px 0; padding-left: 20px;}}
        .disclaimer li {{font-size: 8.5pt; margin: 4px 0;}}
        .report-footer {{text-align: center; color: #6b7280; font-size: 8pt; margin-top: 20px; padding-top: 12px; border-top: 1px solid #e5e7eb;}}
        .report-footer p {{margin: 3px 0;}}
        .report-footer .brand {{color: #1e3a8a; font-weight: 600;}}
        .page-break {{page-break-before: always;}}
    </style>
</head>
<body>
    <div class="report-header">
        <h1>CELLOXEN HEALTH</h1>
        <p class="subtitle">Comprehensive Wellness Assessment Report</p>
    </div>
    
    <div class="summary-row">
        <div class="patient-col">
            <div class="patient-info">
                <table>
                    <tr><td>Patient Name:</td><td>{patient_name}</td></tr>
                    <tr><td>Patient Number:</td><td>{patient_number}</td></tr>
                    <tr><td>Date of Birth:</td><td>{date_of_birth}</td></tr>
                    <tr><td>Assessment Date:</td><td>{assessment_date_formatted}</td></tr>
                    <tr><td>Report Generated:</td><td>{report_datetime}</td></tr>
                </table>
            </div>
        </div>
        <div class="score-col">
            <div class="overall-score">
                <div class="label">Overall Wellness Score</div>
                <div class="score-value">{overall_score:.0f}%</div>
                <div class="status">{overall_status}</div>
            </div>
        </div>
    </div>
    
    <div class="executive-summary">
        <h2>Executive Summary</h2>
        <p>{exec_summary_text}</p>
    </div>
    
    <div class="wellness-glance">
        <h2 class="section-title">Wellness at a Glance</h2>
        <table class="glance-table">
            <tr>
                <td><div class="glance-box strengths"><h4>Your Strengths</h4><ul>{strengths_html}</ul></div></td>
                <td><div class="glance-box concerns"><h4>Areas for Attention</h4><ul>{concerns_html}</ul></div></td>
            </tr>
        </table>
    </div>
    
    <div class="page-break"></div>
    
    <h2 class="section-title">Wellness Domain Analysis</h2>
    <p style="font-size: 9pt; margin-bottom: 12px;">Your wellness has been assessed across five key domains.</p>
    
    <table class="scores">
        <tr><th>Wellness Domain</th><th style="text-align: center;">Progress</th><th style="text-align: center;">Score</th><th style="text-align: center;">Status</th></tr>
        {domain_scores_html}
    </table>
    
    <div class="page-break"></div>
    
    <h2 class="section-title">Recommended Therapies</h2>
    <p style="font-size: 9pt; margin-bottom: 15px;">Based on your assessment, the following therapies are recommended:</p>
    
    {therapy_html}
    
    {lifestyle_html}
    
    <div class="disclaimer">
        <h3>Important Information</h3>
        <p><strong>This assessment provides holistic wellness guidance and does not constitute medical diagnosis or treatment.</strong></p>
        <p>Celloxen therapies are complementary wellness interventions designed to support overall wellbeing. They do not claim to treat, cure, or prevent any disease or medical condition.</p>
        <ul>
            <li>This assessment is for wellness guidance purposes only</li>
            <li>Please consult your GP for any medical concerns</li>
            <li>Inform your practitioner of any medications or health conditions</li>
        </ul>
        <p><strong>IMPORTANT:</strong> If you are experiencing acute symptoms, chest pain, or any medical emergency, please seek immediate medical attention.</p>
    </div>
    
    <div class="report-footer">
        <p>Report Generated: {report_datetime} | Assessment Reference: {assessment_id}</p>
        <p class="brand">Celloxen Health | Advanced Bioelectronic Wellness Solutions</p>
        <p>www.celloxen.co.uk | {clinic_email}</p>
    </div>
</body>
</html>"""
    
    return html_content


def generate_pdf_report(patient_data, assessment_data):
    """Generate professional PDF wellness report using WeasyPrint."""
    html_content = generate_html_report(patient_data, assessment_data)
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    return pdf_bytes


def generate_comprehensive_report(assessment_data, patient_data, iridology_data=None):
    """Wrapper function for compatibility with simple_auth_main.py endpoint."""
    from io import BytesIO
    if iridology_data:
        assessment_data['iridology_data'] = iridology_data
    pdf_bytes = generate_pdf_report(patient_data, assessment_data)
    return BytesIO(pdf_bytes)
