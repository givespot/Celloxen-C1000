# AI-Powered Wellness Assessment Analyzer
# Uses Anthropic Claude API for intelligent symptom analysis and therapy matching

import json
import os
from typing import Dict, List, Optional
from anthropic import Anthropic

class AIAssessmentAnalyzer:
    """comprehensive wellness assessment analysis using Anthropic Claude API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)
    
    async def generate_assessment_report(
        self, 
        patient_info: Dict,
        questions_and_answers: List[Dict],
        domain_scores: Dict,
        therapies: List[Dict]
    ) -> Dict:
        """
        Generate comprehensive comprehensive wellness assessment report
        
        Args:
            patient_info: Patient demographic information
            questions_and_answers: List of questions with patient's answers
            domain_scores: Calculated scores for each therapy domain
            therapies: Available Celloxen therapies from database
            
        Returns:
            Comprehensive assessment report with recommendations
        """
        
        try:
            # Create the analysis prompt
            prompt = self._create_assessment_prompt(
                patient_info, 
                questions_and_answers, 
                domain_scores, 
                therapies
            )
            
            # Call Claude API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Parse response
            response_text = message.content[0].text
            
            # Try to extract JSON from response
            report = self._parse_report_response(response_text)
            
            return {
                "success": True,
                "report": report,
                "raw_analysis": response_text
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "report": self._generate_fallback_report(domain_scores, therapies)
            }
    
    def _create_assessment_prompt(
        self,
        patient_info: Dict,
        questions_and_answers: List[Dict],
        domain_scores: Dict,
        therapies: List[Dict]
    ) -> str:
        """Create comprehensive prompt for Claude API"""
        
        # Format questions and answers
        qa_text = ""
        for i, qa in enumerate(questions_and_answers, 1):
            qa_text += f"\nQ{i}. {qa['question']}\n"
            qa_text += f"    Answer: {qa['answer']} (Score: {qa['score']}/100)\n"
        
        # Format therapies information
        therapies_text = ""
        for t in therapies:
            therapies_text += f"""
--- {t['therapy_code']}: {t['therapy_name']} ---
Subtitle: {t['subtitle']}
Description: {t['description']}
Client Indicators: {json.dumps(t['client_indicators'])}
Primary Support Areas: {json.dumps(t['primary_support_areas'])}
Short-term Benefits: {json.dumps(t['short_term_benefits'])}
Long-term Benefits: {json.dumps(t['long_term_benefits'])}
Treatment Protocol: {t['recommended_sessions']} sessions, {t['session_frequency']}, {t['session_duration']}
"""
        
        return f"""You are a senior wellness consultant at Celloxen Health, specialising in bioelectronic therapy assessment. 

PATIENT INFORMATION:
- Name: {patient_info.get('name', 'Patient')}
- Age: {patient_info.get('age', 'Not provided')}
- Gender: {patient_info.get('gender', 'Not provided')}

WELLNESS ASSESSMENT RESPONSES:
The patient completed a 35-question comprehensive wellness questionnaire covering 5 domains.
Scoring: 0 = Most concern, 100 = Optimal wellness

{qa_text}

DOMAIN SCORES (0-100, lower = more concern):
- Energy & Vitality (C-102): {domain_scores.get('energy', 0):.1f}%
- Comfort & Mobility (C-104): {domain_scores.get('comfort', 0):.1f}%
- Circulation & Heart (C-105): {domain_scores.get('circulation', 0):.1f}%
- Stress & Relaxation (C-107): {domain_scores.get('stress', 0):.1f}%
- Metabolic Balance (C-108): {domain_scores.get('metabolic', 0):.1f}%
- Overall Wellness: {domain_scores.get('overall', 0):.1f}%

AVAILABLE CELLOXEN THERAPIES:
{therapies_text}

ANALYSIS INSTRUCTIONS:
Based on the patient's responses and scores, provide a comprehensive wellness assessment report. Consider:
1. Lower scores indicate areas of greater concern that need attention
2. Patterns in responses that suggest underlying wellness challenges
3. Which Celloxen therapies would best address the identified concerns
4. The priority order for therapy recommendations

Generate a detailed report in the following JSON format:
{{
    "executive_summary": "A comprehensive 4-6 sentence summary that includes: (1) the patient's overall wellness score and status, (2) the most critical areas of concern identified, (3) key positive findings, (4) the primary recommended therapy and why, (5) expected outcomes from following the treatment plan. Write in a professional clinical tone without mentioning AI or artificial intelligence.",
    
    "wellness_overview": {{
        "overall_status": "Excellent/Good/Fair/Needs Attention/Requires Support",
        "primary_concerns": ["List of top 3-5 identified health concerns based on responses"],
        "positive_indicators": ["List of wellness areas showing strength"]
    }},
    
    "domain_analysis": {{
        "energy": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "comfort": {{
            "status": "Status description", 
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "circulation": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "stress": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }},
        "metabolic": {{
            "status": "Status description",
            "key_findings": ["Specific findings from responses"],
            "concern_level": "Low/Moderate/High"
        }}
    }},
    
    "therapy_recommendations": [
        {{
            "priority": 1,
            "therapy_code": "C-XXX",
            "therapy_name": "Name of therapy",
            "recommendation_reason": "Detailed explanation of why this therapy is recommended based on the patient's specific responses",
            "expected_benefits": ["List of expected benefits for this patient"],
            "treatment_plan": {{
                "sessions": number,
                "frequency": "frequency",
                "duration": "duration per session",
                "estimated_completion": "X weeks"
            }},
            "urgency": "Immediate/Soon/Maintenance"
        }}
    ],
    
    "lifestyle_recommendations": [
        "General wellness advice based on findings"
    ],
    
    "follow_up_notes": "When to reassess and what to monitor",
    
    "disclaimer": "This assessment is for wellness support purposes only and does not constitute medical diagnosis. Always consult with qualified healthcare professionals for medical concerns."
}}

Provide ONLY the JSON response, no additional text before or after."""

    def _parse_report_response(self, response_text: str) -> Dict:
        """Parse Claude's response into structured report"""
        
        try:
            # Try to find JSON in the response
            # Remove any markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            return json.loads(cleaned.strip())
            
        except json.JSONDecodeError:
            # Return raw text if JSON parsing fails
            return {
                "executive_summary": "Assessment completed. Please review the detailed analysis.",
                "raw_analysis": response_text,
                "parse_error": True
            }
    
    def _generate_fallback_report(self, domain_scores: Dict, therapies: List[Dict]) -> Dict:
        """Generate a basic report if AI fails"""
        
        # Sort domains by score (lowest first = highest concern)
        sorted_domains = sorted(
            [
                ('energy', domain_scores.get('energy', 50), 'C-102'),
                ('comfort', domain_scores.get('comfort', 50), 'C-104'),
                ('circulation', domain_scores.get('circulation', 50), 'C-105'),
                ('stress', domain_scores.get('stress', 50), 'C-107'),
                ('metabolic', domain_scores.get('metabolic', 50), 'C-108'),
            ],
            key=lambda x: x[1]
        )
        
        # Get top recommendations based on lowest scores
        recommendations = []
        for i, (domain, score, code) in enumerate(sorted_domains[:3]):
            therapy = next((t for t in therapies if t['therapy_code'] == code), None)
            if therapy:
                recommendations.append({
                    "priority": i + 1,
                    "therapy_code": code,
                    "therapy_name": therapy['therapy_name'],
                    "recommendation_reason": f"Based on your {domain} score of {score:.1f}%, this therapy may help address your wellness concerns in this area.",
                    "expected_benefits": therapy.get('short_term_benefits', [])[:3],
                    "treatment_plan": {
                        "sessions": therapy['recommended_sessions'],
                        "frequency": therapy['session_frequency'],
                        "duration": therapy['session_duration']
                    },
                    "urgency": "High" if score < 40 else "Moderate" if score < 60 else "Maintenance"
                })
        
        return {
            "executive_summary": f"Assessment completed with an overall wellness score of {domain_scores.get('overall', 50):.1f}%. Areas requiring attention have been identified.",
            "wellness_overview": {
                "overall_status": "Needs Attention" if domain_scores.get('overall', 50) < 50 else "Fair",
                "primary_concerns": [d[0] for d in sorted_domains[:3]],
                "positive_indicators": [d[0] for d in sorted_domains[-2:]]
            },
            "therapy_recommendations": recommendations,
            "disclaimer": "This assessment is for wellness support purposes only."
        }

