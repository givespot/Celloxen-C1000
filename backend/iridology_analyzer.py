"""
Iridology Analyzer - Claude AI Integration
Uses Anthropic Claude API for iris image analysis
British English throughout - NO medical diagnosis
VERSION 2.0 - UK Compliant (No Supplement Recommendations)
Updated: 26 November 2025
"""

import anthropic
import json
import os
from typing import Dict, Optional
from datetime import datetime

def clean_base64_image(base64_string: str) -> str:
    """Remove data URL prefix from base64 string if present"""
    if "," in base64_string and base64_string.startswith("data:"):
        return base64_string.split(",", 1)[1]
    return base64_string


class IridologyAnalyzer:
    """Claude AI-powered iridology analysis - Wellness insights only"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"

    def create_analysis_prompt(self, patient_info: Dict) -> str:
        """Create British English analysis prompt - NO diagnosis, NO supplements"""

        return f"""You are an expert iridology analyst providing wellness insights for a UK holistic health clinic.

CRITICAL INSTRUCTIONS:
1. Use BRITISH ENGLISH ONLY (analyse, colour, fibre, centre, optimise, whilst, programme)
2. NEVER diagnose medical conditions - use "may suggest", "patterns often associated with", "could indicate"
3. ALWAYS recommend GP consultation for concerning findings
4. Use warm, supportive, accessible language with helpful analogies
5. Focus on LIFESTYLE recommendations - NOT supplement recommendations
6. DO NOT recommend specific supplements (UK regulatory compliance)

PATIENT CONTEXT:
- Name: {patient_info.get('name', 'Patient')}
- Age: {patient_info.get('age', 'Unknown')} years
- Gender: {patient_info.get('gender', 'Unknown')}

ANALYSIS REQUIREMENTS:

1. CONSTITUTIONAL TYPE (REQUIRED - never return "Unknown"):
   - Determine from iris colour: Lymphatic (blue/grey), Haematogenic (brown), or Mixed (green/hazel)
   - Constitutional Strength: Strong, Moderate, or Weak (based on fibre density)
   - Provide a warm, accessible explanation using a house/building foundation analogy

2. BODY SYSTEMS ASSESSMENT (rate each: Excellent, Good, Fair, Needs Support):
   a) Digestive System - check stomach ring, intestinal zones
   b) Circulatory System - check heart zone, circulation patterns
   c) Nervous System - look for NERVE RINGS (stress rings) around pupil
   d) Musculoskeletal System - check structural zones
   e) Endocrine/Metabolic System - CRITICAL: examine pancreatic zone at 7 o'clock (left eye), 5 o'clock (right eye)

3. IRIS SIGNS (describe in plain British English):
   - Lacunae (open lesions), crypts, pigmentation variations
   - Nerve rings (stress indicators), scurf rim, radii solaris
   - Use accessible language - explain what each sign means

4. CELLOXEN THERAPY PRIORITIES (rank 1-5, where 1 is highest priority):
   - C-102: Vitality & Energy Support
   - C-104: Comfort & Mobility Support  
   - C-105: Circulation & Heart Wellness
   - C-107: Stress & Relaxation Support (prioritise if nerve rings present)
   - C-108: Metabolic Balance Support (prioritise if pancreatic zone patterns seen)

5. LIFESTYLE RECOMMENDATIONS (NO supplements - UK compliance):
   - Nutrition approach (food-based, not supplements)
   - Daily habits and routines
   - Stress management techniques
   - Physical activity suggestions
   - Sleep hygiene recommendations

6. GP CONSULTATION GUIDANCE:
   - If pancreatic patterns → "We recommend discussing metabolic health with your GP, including HbA1c testing"
   - If circulation concerns → "Consider discussing cardiovascular wellness with your GP"
   - Always frame as supportive guidance, not diagnosis

7. BIG PICTURE SUMMARY:
   - Use a car, garden, or house analogy to explain overall findings
   - Focus on strengths and positive potential
   - Provide encouraging, actionable next steps

OUTPUT FORMAT (British English JSON):
{{
  "constitutional_type": "Lymphatic|Haematogenic|Mixed",
  "constitutional_strength": "Strong|Moderate|Weak",
  "constitutional_explanation": "Warm, accessible explanation with analogy...",
  "body_systems": {{
    "digestive": {{"rating": "Good", "findings": ["finding1", "finding2"], "explanation": "..."}},
    "circulatory": {{"rating": "Fair", "findings": [...], "explanation": "..."}},
    "nervous": {{"rating": "Needs Support", "findings": [...], "stress_rings_present": true, "explanation": "..."}},
    "musculoskeletal": {{"rating": "Good", "findings": [...], "explanation": "..."}},
    "endocrine_metabolic": {{"rating": "...", "findings": [...], "pancreatic_patterns": false, "explanation": "..."}}
  }},
  "iris_signs": [
    {{"sign": "Nerve rings", "location": "Around pupil", "significance": "Indicates accumulated stress"}}
  ],
  "therapy_priorities": [
    {{"code": "C-107", "name": "Stress & Relaxation Support", "priority": 1, "reason": "Nerve rings indicate chronic stress patterns"}}
  ],
  "lifestyle_recommendations": {{
    "nutrition": ["Eat regular balanced meals", "Include magnesium-rich foods like leafy greens"],
    "daily_habits": ["Morning stretching routine", "Regular meal times"],
    "stress_management": ["Daily breathing exercises", "Evening wind-down routine"],
    "physical_activity": ["Gentle walking after meals", "Yoga or stretching"],
    "sleep": ["Consistent bedtime", "Limit screens before bed"]
  }},
  "gp_consultation": {{
    "recommended": true,
    "reasons": ["Pancreatic zone patterns warrant professional evaluation"],
    "suggested_tests": ["HbA1c", "Fasting glucose"],
    "urgency": "Routine - within 2-4 weeks"
  }},
  "strengths": ["Good digestive foundation", "Strong constitutional base"],
  "areas_for_attention": ["Stress management", "Metabolic support"],
  "big_picture": "Think of your wellness like a well-built house that needs some maintenance attention..."
}}

REMEMBER:
- 100% British English spelling
- NO medical diagnoses
- NO supplement recommendations (UK regulatory compliance)
- Warm, supportive, empowering language
- Always recommend GP for concerning patterns
- Focus on what the patient CAN do (lifestyle, not pills)"""

    async def analyse_single_iris(
        self,
        image_base64: str,
        eye_side: str,
        patient_info: Dict
    ) -> Dict:
        """Analyse single iris image using Claude API"""

        prompt = self.create_analysis_prompt(patient_info)

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"{prompt}\n\nPlease analyse this {eye_side} iris image in detail:"
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_base64
                                }
                            }
                        ]
                    }
                ]
            )

            response_text = message.content[0].text

            # Try to parse as JSON
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # Clean markdown if present
                cleaned = response_text.replace('```json', '').replace('```', '').strip()
                try:
                    analysis = json.loads(cleaned)
                except:
                    analysis = {"raw_text": response_text, "parsed": False}

            return {
                "success": True,
                "eye_side": eye_side,
                "analysis": analysis,
                "model": self.model,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "eye_side": eye_side
            }

    async def analyse_bilateral(
        self,
        left_eye_base64: str,
        right_eye_base64: str,
        patient_info: Dict
    ) -> Dict:
        """Analyse both eyes and synthesise comprehensive report"""

        # Clean base64 images
        left_eye_base64 = clean_base64_image(left_eye_base64)
        right_eye_base64 = clean_base64_image(right_eye_base64)

        # Analyse left eye
        left_result = await self.analyse_single_iris(
            left_eye_base64,
            "left",
            patient_info
        )

        if not left_result["success"]:
            return left_result

        # Analyse right eye
        right_result = await self.analyse_single_iris(
            right_eye_base64,
            "right",
            patient_info
        )

        if not right_result["success"]:
            return right_result

        # Synthesise comprehensive narrative report
        synthesis_prompt = f"""Based on these bilateral iris analyses, create a COMPREHENSIVE WELLNESS REPORT in flowing narrative prose.

LEFT EYE FINDINGS:
{json.dumps(left_result.get('analysis', {}), indent=2)}

RIGHT EYE FINDINGS:
{json.dumps(right_result.get('analysis', {}), indent=2)}

PATIENT: {patient_info.get('name', 'Patient')}, Age: {patient_info.get('age', 'Unknown')}

Write a warm, professional wellness report with these sections (use markdown headings):

# Comprehensive Wellness Report - Bilateral Iris Analysis

## Constitutional Overview
- Explain constitutional type using accessible analogies (house foundation, car engine)
- Describe what this means for their wellness journey
- Highlight bilateral consistency

## Body Systems Assessment
For each system, include:
- Rating (Excellent/Good/Fair/Needs Support)
- Key findings in plain English
- What this means for daily life

Focus on: Digestive, Circulatory, Nervous, Musculoskeletal, Endocrine/Metabolic

## Priority Wellness Recommendations
List the Celloxen therapies in priority order with explanations:
- C-102, C-104, C-105, C-107, C-108
- Explain WHY each is recommended based on findings

## Comprehensive Wellness Plan

### Nutrition Approach
- Food-based recommendations (NO supplements)
- Eating patterns and timing
- Foods to emphasise

### Lifestyle Recommendations  
- Daily habits
- Stress management techniques
- Physical activity suggestions
- Sleep hygiene

## GP Consultation Priority
- What to discuss with GP
- Recommended tests if applicable
- Urgency level

## The Big Picture
- Encouraging summary using accessible analogy
- Key action steps
- Positive outlook

CRITICAL REQUIREMENTS:
1. 100% British English (analyse, colour, fibre, centre, whilst, programme)
2. NO supplement recommendations (UK regulatory compliance)
3. Warm, supportive, empowering tone
4. Accessible explanations with helpful analogies
5. Focus on lifestyle changes, not pills
6. Always recommend GP for concerning patterns
7. End with encouraging, actionable message

Write in flowing prose, not bullet points where possible. Make it feel like a caring practitioner explaining findings."""

        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=6000,
                messages=[
                    {
                        "role": "user",
                        "content": synthesis_prompt
                    }
                ]
            )

            synthesis_text = message.content[0].text

            # Extract constitutional type for header
            constitutional_type = "Mixed"  # Default
            constitutional_strength = "Moderate"  # Default
            
            left_analysis = left_result.get('analysis', {})
            right_analysis = right_result.get('analysis', {})
            
            # Try to get from left eye first, then right
            if isinstance(left_analysis, dict):
                constitutional_type = left_analysis.get('constitutional_type', constitutional_type)
                constitutional_strength = left_analysis.get('constitutional_strength', constitutional_strength)
            if isinstance(right_analysis, dict) and constitutional_type == "Mixed":
                constitutional_type = right_analysis.get('constitutional_type', constitutional_type)
                constitutional_strength = right_analysis.get('constitutional_strength', constitutional_strength)

            # Create synthesis object
            synthesis = {
                "raw_text": synthesis_text,
                "constitutional_type": constitutional_type,
                "constitutional_strength": constitutional_strength,
                "parsed": True
            }

            return {
                "success": True,
                "left_eye_analysis": left_result["analysis"],
                "right_eye_analysis": right_result["analysis"],
                "combined_analysis": synthesis,
                "constitutional_type": constitutional_type,
                "constitutional_strength": constitutional_strength,
                "confidence_score": self.calculate_confidence(left_analysis),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "partial_results": {
                    "left": left_result,
                    "right": right_result
                }
            }

    def calculate_confidence(self, analysis: Dict) -> float:
        """Calculate AI confidence score (0-100)"""
        if not isinstance(analysis, dict):
            return 50.0
            
        score = 50.0  # Base score

        if analysis.get("constitutional_type"):
            score += 10
        if analysis.get("body_systems"):
            score += 10
        if analysis.get("therapy_priorities"):
            score += 15
        if analysis.get("lifestyle_recommendations"):
            score += 10
        if analysis.get("big_picture"):
            score += 5

        return min(100.0, score)

# Create singleton instance
iridology_analyzer = None

def get_analyzer():
    global iridology_analyzer
    if iridology_analyzer is None:
        iridology_analyzer = IridologyAnalyzer()
    return iridology_analyzer
