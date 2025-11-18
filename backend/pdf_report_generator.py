"""
Professional PDF Report Generator using WeasyPrint
Generates pixel-perfect wellness assessment reports from HTML/CSS
"""

from weasyprint import HTML, CSS
from datetime import datetime
import io

# Therapy Information Database (from manuals)
THERAPY_INFO = {
    'C-102': {
        'name': 'Vitality & Energy Support',
        'code': 'C-102',
        'overview': 'Advanced metabolic support protocol utilising cutting-edge bioelectronic systems to support comprehensive cellular energy production and enhance overall vitality.',
        'sessions': 16,
        'frequency': 'Daily sessions',
        'duration': '30-40 minutes per session',
        'short_benefits': [
            'Stabilised energy levels and reduced fatigue',
            'Improved fluid balance and hydration',
            'Better glucose regulation and fewer energy crashes',
            'Enhanced sleep quality and restorative rest',
            'Improved mental clarity and concentration'
        ],
        'long_benefits': [
            'Optimised metabolic efficiency and cellular energy',
            'Enhanced glucose tolerance and metabolic flexibility',
            'Improved weight management and body composition',
            'Better stress resilience and recovery capacity',
            'Increased overall vitality and quality of life'
        ]
    },
    'C-104': {
        'name': 'Comfort & Mobility Support',
        'code': 'C-104',
        'overview': 'Advanced bioelectronic technology to support natural comfort and movement wellness. Optimises joint function, supports tissue health, and promotes natural mobility.',
        'sessions': 12,
        'frequency': 'Daily sessions',
        'duration': '30-40 minutes per session',
        'short_benefits': [
            'Improved joint comfort and ease of movement',
            'Enhanced flexibility and range of motion',
            'Reduced morning stiffness',
            'Better activity tolerance',
            'Increased daily movement confidence'
        ],
        'long_benefits': [
            'Sustained joint comfort and function',
            'Enhanced mobility and movement quality',
            'Improved tissue health and resilience',
            'Better adaptation to activity demands',
            'Greater quality of life through improved mobility'
        ]
    },
    'C-105': {
        'name': 'Circulation & Heart Wellness',
        'code': 'C-105',
        'overview': 'Advanced bioelectronic technology supporting optimal cardiovascular function and healthy circulation. Optimises heart function and enhances vascular health.',
        'sessions': 16,
        'frequency': '2-3 sessions per week',
        'duration': '30-40 minutes per session',
        'short_benefits': [
            'Improved circulation and warmth in extremities',
            'Enhanced heart rhythm stability',
            'Better cardiovascular response to activity',
            'Reduced circulation-related discomfort',
            'Improved exercise tolerance'
        ],
        'long_benefits': [
            'Optimised cardiovascular function and efficiency',
            'Enhanced vascular health and flexibility',
            'Improved blood pressure regulation',
            'Better microcirculation and tissue oxygenation',
            'Sustained cardiovascular wellness and vitality'
        ]
    },
    'C-107': {
        'name': 'Stress & Relaxation Support',
        'code': 'C-107',
        'overview': 'Advanced bioelectronic technology supporting natural relaxation response and mental wellness. Restores nervous system balance while supporting healthy sleep patterns.',
        'sessions': 16,
        'frequency': 'Daily sessions',
        'duration': '30-40 minutes per session',
        'short_benefits': [
            'Enhanced relaxation response',
            'Improved sleep onset and quality',
            'Reduced mental restlessness',
            'Better emotional balance',
            'Increased daily calmness'
        ],
        'long_benefits': [
            'Sustained stress resilience',
            'Optimised sleep architecture',
            'Enhanced cognitive clarity',
            'Improved emotional regulation',
            'Natural anxiety management'
        ]
    },
    'C-108': {
        'name': 'Metabolic Balance Support',
        'code': 'C-108',
        'overview': 'Advanced bioelectronic technology supporting natural metabolic regulation and blood sugar balance. Optimises glucose metabolism while supporting endocrine function.',
        'sessions': 16,
        'frequency': '2-3 times per week',
        'duration': '30-40 minutes per session',
        'short_benefits': [
            'Stabilised energy levels throughout the day',
            'Improved metabolic responsiveness',
            'Better glucose regulation patterns',
            'Enhanced cellular energy production',
            'Reduced fatigue and improved vitality'
        ],
        'long_benefits': [
            'Optimised metabolic efficiency',
            'Sustained blood sugar balance',
            'Enhanced insulin sensitivity',
            'Improved metabolic flexibility',
            'Enhanced overall metabolic wellness'
        ]
    }
}

def get_score_status(score):
    """Get status and color for a score"""
    if score >= 75:
        return 'Excellent', '#10b981', '#d1fae5'
    elif score >= 50:
        return 'Moderate', '#f59e0b', '#fef3c7'
    elif score >= 25:
        return 'Needs Support', '#ef4444', '#fee2e2'
    else:
        return 'Critical', '#dc2626', '#fecaca'

def generate_html_report(patient_data, assessment_data):
    """Generate HTML content for the PDF report"""
    
    # Get therapy recommendations (lowest scores = highest priority)
    scores = {
        'C-102': assessment_data['energy_score'],
        'C-104': assessment_data['comfort_score'],
        'C-105': assessment_data['circulation_score'],
        'C-107': assessment_data['stress_score'],
        'C-108': assessment_data['metabolic_score']
    }
    
    # Sort by score (lowest first)
    recommended = sorted(scores.items(), key=lambda x: x[1])[:3]  # Top 3 priorities
    
    # Build therapy recommendation HTML
    therapy_html = ""
    for therapy_code, score in recommended:
        therapy = THERAPY_INFO[therapy_code]
        status, color, bg_color = get_score_status(score)
        
        therapy_html += f"""
        <div class="therapy-section">
            <div class="therapy-header" style="background: {bg_color}; border-left: 4px solid {color};">
                <h2>{therapy['code']}: {therapy['name']}</h2>
                <div class="priority-badge" style="background: {color};">
                    Score: {score:.0f}% | Priority: {status}
                </div>
            </div>
            
            <div class="therapy-content">
                <h3>Therapy Overview</h3>
                <p>{therapy['overview']}</p>
                
                <h3>Why This Therapy Was Selected</h3>
                <p>Your {therapy['name']} domain scored <strong>{score:.0f}%</strong>, indicating a need for targeted support. 
                This therapy addresses the specific wellness concerns identified in your assessment.</p>
                
                <div class="treatment-protocol">
                    <table>
                        <tr>
                            <th>Sessions</th>
                            <th>Frequency</th>
                            <th>Duration</th>
                        </tr>
                        <tr>
                            <td>{therapy['sessions']} sessions</td>
                            <td>{therapy['frequency']}</td>
                            <td>{therapy['duration']}</td>
                        </tr>
                    </table>
                </div>
                
                <h3>Anticipated Benefits</h3>
                
                <div class="benefits-grid">
                    <div class="benefits-column">
                        <h4>Short-term (Weeks 1-4)</h4>
                        <ul>
                            {''.join([f'<li>{b}</li>' for b in therapy['short_benefits']])}
                        </ul>
                    </div>
                    <div class="benefits-column">
                        <h4>Long-term (Weeks 4-16)</h4>
                        <ul>
                            {''.join([f'<li>{b}</li>' for b in therapy['long_benefits']])}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        """
    
    # Domain scores HTML
    domain_scores_html = ""
    for code, score in [
        ('C-102', assessment_data['energy_score']),
        ('C-104', assessment_data['comfort_score']),
        ('C-105', assessment_data['circulation_score']),
        ('C-107', assessment_data['stress_score']),
        ('C-108', assessment_data['metabolic_score'])
    ]:
        status, color, bg_color = get_score_status(score)
        therapy_name = THERAPY_INFO[code]['name']
        
        domain_scores_html += f"""
        <tr>
            <td>{code}: {therapy_name}</td>
            <td style="text-align: center; font-weight: bold;">{score:.0f}%</td>
            <td style="text-align: center;">
                <span class="status-badge" style="background: {bg_color}; color: {color}; padding: 4px 12px; border-radius: 12px; font-weight: 600;">
                    {status}
                </span>
            </td>
        </tr>
        """
    
    # Overall score
    overall_score = assessment_data['overall_score']
    overall_status, overall_color, overall_bg = get_score_status(overall_score)
    
    # Full HTML document
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Wellness Assessment Report</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: 'Helvetica', 'Arial', sans-serif;
                color: #1f2937;
                line-height: 1.6;
                font-size: 10pt;
            }}
            
            .header {{
                text-align: center;
                border-bottom: 3px solid #1e3a8a;
                padding-bottom: 20px;
                margin-bottom: 30px;
            }}
            
            .header h1 {{
                color: #1e3a8a;
                font-size: 24pt;
                margin: 0 0 10px 0;
            }}
            
            .header h2 {{
                color: #3b82f6;
                font-size: 14pt;
                margin: 0;
                font-weight: normal;
            }}
            
            .patient-info {{
                background: #f9fafb;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            
            .patient-info table {{
                width: 100%;
                border-collapse: collapse;
            }}
            
            .patient-info td {{
                padding: 8px;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            .patient-info td:first-child {{
                font-weight: bold;
                width: 40%;
                color: #4b5563;
            }}
            
            .overall-score {{
                background: linear-gradient(135deg, #3b82f6 0%, #1e3a8a 100%);
                color: white;
                padding: 25px;
                border-radius: 12px;
                text-align: center;
                margin: 20px 0;
            }}
            
            .overall-score h2 {{
                margin: 0 0 10px 0;
                font-size: 16pt;
            }}
            
            .overall-score .score {{
                font-size: 48pt;
                font-weight: bold;
                margin: 10px 0;
            }}
            
            .overall-score .status {{
                font-size: 14pt;
                margin-top: 10px;
            }}
            
            .section-title {{
                color: #1e3a8a;
                font-size: 16pt;
                margin: 30px 0 15px 0;
                padding-bottom: 8px;
                border-bottom: 2px solid #3b82f6;
            }}
            
            table.scores {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            
            table.scores th {{
                background: #1e3a8a;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }}
            
            table.scores td {{
                padding: 12px;
                border-bottom: 1px solid #e5e7eb;
            }}
            
            table.scores tr:nth-child(even) {{
                background: #f9fafb;
            }}
            
            .therapy-section {{
                page-break-inside: avoid;
                margin: 20px 0;
            }}
            
            .therapy-header {{
                padding: 15px;
                border-radius: 8px 8px 0 0;
                margin-bottom: 0;
            }}
            
            .therapy-header h2 {{
                margin: 0 0 8px 0;
                color: #1e3a8a;
                font-size: 14pt;
            }}
            
            .priority-badge {{
                display: inline-block;
                color: white;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 8.5pt;
            }}
            
            .therapy-content {{
                border: 1px solid #e5e7eb;
                border-top: none;
                padding: 20px;
                border-radius: 0 0 8px 8px;
            }}
            
            .therapy-content h3 {{
                color: #1e3a8a;
                font-size: 11pt;
                margin: 15px 0 10px 0;
            }}
            
            .therapy-content h4 {{
                color: #4b5563;
                font-size: 10pt;
                margin: 10px 0 5px 0;
            }}
            
            .treatment-protocol table {{
                width: 100%;
                margin: 15px 0;
                border-collapse: collapse;
            }}
            
            .treatment-protocol th {{
                background: #f3f4f6;
                padding: 10px;
                border: 1px solid #e5e7eb;
                font-size: 9pt;
            }}
            
            .treatment-protocol td {{
                padding: 10px;
                border: 1px solid #e5e7eb;
                text-align: center;
                font-size: 9pt;
            }}
            
            .benefits-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin: 15px 0;
            }}
            
            .benefits-column ul {{
                margin: 5px 0;
                padding-left: 20px;
            }}
            
            .benefits-column li {{
                margin: 5px 0;
                font-size: 9pt;
            }}
            
            .disclaimer {{
                background: #fef3c7;
                border: 2px solid #f59e0b;
                padding: 20px;
                border-radius: 8px;
                margin-top: 30px;
                page-break-inside: avoid;
            }}
            
            .disclaimer h3 {{
                color: #92400e;
                margin-top: 0;
                font-size: 12pt;
            }}
            
            .disclaimer p {{
                margin: 10px 0;
                font-size: 9pt;
                line-height: 1.5;
            }}
            
            .footer {{
                text-align: center;
                color: #6b7280;
                font-size: 8pt;
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #e5e7eb;
            }}
        </style>
    </head>
    <body>
        <!-- PAGE 1: COVER & SUMMARY -->
        <div class="header">
            <h1>CELLOXEN HEALTH PORTAL</h1>
            <h2>Comprehensive Wellness Assessment Report</h2>
        </div>
        
        <div class="patient-info">
            <table>
                <tr>
                    <td>Patient Name:</td>
                    <td>{patient_data['first_name']} {patient_data['last_name']}</td>
                </tr>
                <tr>
                    <td>Patient Number:</td>
                    <td>{patient_data['patient_number']}</td>
                </tr>
                <tr>
                    <td>Date of Birth:</td>
                    <td>{patient_data.get('date_of_birth', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Assessment Date:</td>
                    <td>{datetime.now().strftime('%d %B %Y')}</td>
                </tr>
                <tr>
                    <td>Report Generated:</td>
                    <td>{datetime.now().strftime('%d %B %Y at %H:%M')}</td>
                </tr>
            </table>
        </div>
        
        <div class="overall-score">
            <h2>Overall Wellness Score</h2>
            <div class="score">{overall_score:.0f}%</div>
            <div class="status">{overall_status}</div>
        </div>
        
        <h1 class="section-title">Wellness Domain Scores</h1>
        
        <table class="scores">
            <tr>
                <th>Domain</th>
                <th style="text-align: center;">Score</th>
                <th style="text-align: center;">Status</th>
            </tr>
            {domain_scores_html}
        </table>
        
        <!-- PAGE 2+: THERAPY RECOMMENDATIONS -->
        <div style="page-break-before: always;"></div>
        
        <h1 class="section-title">Recommended Therapies</h1>
        
        <p style="margin-bottom: 20px;">Based on your assessment results, we recommend the following therapies to support your wellness goals:</p>
        
        {therapy_html}
        
        <!-- DISCLAIMER PAGE -->
        <div style="page-break-before: always;"></div>
        
        <div class="disclaimer">
            <h3>⚠️ WELLNESS ASSESSMENT DISCLAIMER</h3>
            
            <p><strong>This assessment provides holistic wellness guidance based on your questionnaire responses and is NOT a medical diagnosis or treatment plan.</strong></p>
            
            <p>Celloxen therapies are complementary wellness interventions designed to support overall wellbeing. They do not claim to treat, cure, or prevent any disease or medical condition.</p>
            
            <p>This report is for informational purposes only and should not replace professional medical advice, diagnosis, or treatment.</p>
            
            <p><strong>IMPORTANT:</strong> Please consult your GP or qualified healthcare provider for any medical concerns or before making significant changes to your health regimen.</p>
        </div>
        
        <div class="footer">
            <p>Report Generated: {datetime.now().strftime('%d %B %Y at %H:%M')} | Assessment ID: {assessment_data.get('id', 'N/A')}</p>
            <p>Aberdeen Wellness Centre | Tel: 01224 123456 | Email: info@aberdeenwellness.co.uk</p>
            <p>www.celloxen.co.uk</p>
        </div>
    </body>
    </html>
    """
    
    return html_content

def generate_pdf_report(patient_data, assessment_data):
    """
    Generate professional PDF report using WeasyPrint
    
    Args:
        patient_data: dict with patient information
        assessment_data: dict with assessment scores
        
    Returns:
        bytes: PDF file content
    """
    
    # Generate HTML
    html_content = generate_html_report(patient_data, assessment_data)
    
    # Convert to PDF
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()
    
    return pdf_bytes

