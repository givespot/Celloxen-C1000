# PDF Report Generator for Comprehensive Assessments

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io
import json

class AssessmentReportGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Create custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#4F46E5'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#4F46E5')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#374151'),
            spaceBefore=10,
            spaceAfter=5
        ))
    
    def generate_comprehensive_report(self, assessment_data: dict, patient_data: dict, iridology_data: dict = None) -> io.BytesIO:
        """Generate comprehensive assessment PDF report"""
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        
        # Header with logo placeholder
        story.append(Paragraph("CELLOXEN HEALTH PORTAL", self.styles['CustomTitle']))
        story.append(Paragraph("Comprehensive Wellness Assessment Report", self.styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Patient Information Section
        story.append(Paragraph("Patient Information", self.styles['SectionHeader']))
        
        patient_info_data = [
            ["Patient Name:", f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}"],
            ["Patient ID:", patient_data.get('patient_number', 'N/A')],
            ["Date of Birth:", str(patient_data.get('date_of_birth', 'N/A'))],
            ["Assessment Date:", datetime.now().strftime("%d %B %Y")],
            ["Assessment ID:", f"ASS-{assessment_data.get('id', 'N/A')}"]
        ]
        
        patient_table = Table(patient_info_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
        ]))
        
        story.append(patient_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Overall Wellness Score
        overall_score = assessment_data.get('overall_wellness_score', 0)
        story.append(Paragraph("Overall Wellness Score", self.styles['SectionHeader']))
        story.append(Paragraph(
            f"<font size=16 color='#4F46E5'><b>{overall_score:.1f}%</b></font>",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        # Questionnaire Results
        story.append(Paragraph("Wellness Questionnaire Results", self.styles['SectionHeader']))
        story.append(Paragraph(
            "Assessment across 5 Celloxen therapy domains (35 comprehensive questions)",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.1*inch))
        
        # Domain scores table
        questionnaire_scores = assessment_data.get('questionnaire_scores', {})
        if questionnaire_scores:
            scores_data = [["Therapy Domain", "Score", "Status", "Priority"]]
            
            for domain_key, domain_info in questionnaire_scores.items():
                if isinstance(domain_info, dict):
                    domain_name = domain_info.get('domain_name', domain_key)
                    score = domain_info.get('score', 0)
                    status = domain_info.get('wellness_status', 'N/A')
                    priority = domain_info.get('priority_level', 'N/A')
                    
                    scores_data.append([
                        domain_name,
                        f"{score:.1f}%",
                        status,
                        priority
                    ])
            
            scores_table = Table(scores_data, colWidths=[2.5*inch, 1*inch, 1.5*inch, 1*inch])
            scores_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F9FAFB')])
            ]))
            
            story.append(scores_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Iridology Results (if available)
        if iridology_data:
            story.append(PageBreak())
            story.append(Paragraph("Iridology Analysis Results", self.styles['SectionHeader']))
            story.append(Paragraph(
                "Professional iris image analysis for constitutional typing and system assessment",
                self.styles['Normal']
            ))
            story.append(Spacer(1, 0.1*inch))
            
            irid_info = [
                ["Constitutional Type:", iridology_data.get('constitutional_type', 'N/A')],
                ["Constitutional Strength:", iridology_data.get('constitutional_strength', 'N/A')],
                ["Digestive System:", iridology_data.get('digestive_system_condition', 'N/A')],
                ["Circulatory System:", iridology_data.get('circulatory_system_condition', 'N/A')],
                ["Nervous System:", iridology_data.get('nervous_system_condition', 'N/A')],
                ["Musculoskeletal System:", iridology_data.get('musculoskeletal_system_condition', 'N/A')],
                ["Endocrine System:", iridology_data.get('endocrine_system_condition', 'N/A')]
            ]
            
            irid_table = Table(irid_info, colWidths=[2.5*inch, 3.5*inch])
            irid_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(irid_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Primary concerns from iridology
            primary_concerns = iridology_data.get('primary_concerns', [])
            if primary_concerns and isinstance(primary_concerns, list) and len(primary_concerns) > 0:
                story.append(Paragraph("Primary Wellness Concerns Identified:", self.styles['SubSection']))
                for concern in primary_concerns:
                    story.append(Paragraph(f"• {concern}", self.styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
        
        # Therapy Recommendations
        story.append(PageBreak())
        story.append(Paragraph("Recommended Therapy Plan", self.styles['SectionHeader']))
        story.append(Paragraph(
            "Personalized Celloxen therapy recommendations based on your comprehensive assessment",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        
        recommendations = assessment_data.get('recommendations', [])
        for idx, rec in enumerate(recommendations, 1):
            # Therapy header
            story.append(Paragraph(
                f"<b>{idx}. {rec.get('therapy_name', 'N/A')}</b>",
                self.styles['SubSection']
            ))
            
            # Details table
            rec_details = [
                ["Priority Level:", rec.get('priority_level', 'N/A')],
                ["Recommended Sessions:", str(rec.get('recommended_sessions', 'N/A'))],
                ["Session Frequency:", rec.get('session_frequency', 'N/A')],
                ["Session Duration:", rec.get('session_duration', 'N/A')],
                ["Estimated Duration:", rec.get('estimated_duration', 'N/A')]
            ]
            
            rec_table = Table(rec_details, colWidths=[2*inch, 4*inch])
            rec_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#EEF2FF')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6)
            ]))
            
            story.append(rec_table)
            story.append(Spacer(1, 0.1*inch))
            
            # Rationale
            story.append(Paragraph("<b>Rationale:</b>", self.styles['Normal']))
            story.append(Paragraph(rec.get('rationale', 'N/A'), self.styles['Normal']))
            story.append(Spacer(1, 0.1*inch))
            
            # Key Benefits
            key_benefits = rec.get('key_benefits', [])
            if key_benefits:
                story.append(Paragraph("<b>Key Benefits:</b>", self.styles['Normal']))
                for benefit in key_benefits:
                    story.append(Paragraph(f"• {benefit}", self.styles['Normal']))
            
            story.append(Spacer(1, 0.2*inch))
        
        # Footer / Disclaimer
        story.append(PageBreak())
        story.append(Paragraph("Important Notice", self.styles['SectionHeader']))
        story.append(Paragraph(
            "This assessment is for wellness and educational purposes only. It is not intended to diagnose, "
            "treat, cure, or prevent any disease. Celloxen therapies are complementary wellness approaches. "
            "Always consult with qualified healthcare professionals regarding your health concerns.",
            self.styles['Normal']
        ))
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph(
            f"Report Generated: {datetime.now().strftime('%d %B %Y at %H:%M')}",
            self.styles['Normal']
        ))
        story.append(Paragraph("Celloxen Health Portal - Comprehensive Wellness Solutions", self.styles['Normal']))
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
