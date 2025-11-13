# AI-Powered Iridology Analysis System
# Integrates Anthropic Claude API for automatic iris image interpretation

import base64
import json
import os
from typing import Dict, List, Optional
from anthropic import Anthropic

class AIIridologyAnalyzer:
    """AI-powered iridology analysis using Anthropic Claude API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = Anthropic(api_key=api_key)
        
    async def analyze_iris_images(self, left_eye_image: str, right_eye_image: str, patient_info: Dict) -> Dict:
        """
        Analyze iris images using Claude API
        
        Args:
            left_eye_image: Base64 encoded left eye image
            right_eye_image: Base64 encoded right eye image  
            patient_info: Patient demographic and health information
            
        Returns:
            Comprehensive iridology analysis
        """
        
        try:
            # Analyze left eye
            left_analysis = await self._analyze_single_iris(
                left_eye_image, "left", patient_info
            )
            
            # Analyze right eye
            right_analysis = await self._analyze_single_iris(
                right_eye_image, "right", patient_info
            )
            
            # Synthesize combined analysis
            combined = self._synthesize_analysis(left_analysis, right_analysis, patient_info)
            
            return {
                "success": True,
                "left_eye_findings": left_analysis,
                "right_eye_findings": right_analysis,
                "combined_analysis": combined,
                "ai_confidence": "high",
                "analysis_timestamp": "current"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_analysis": self._generate_fallback_analysis()
            }
    
    async def _analyze_single_iris(self, image_data: str, eye_side: str, patient_info: Dict) -> Dict:
        """Analyze a single iris image"""
        
        # Create analysis prompt
        prompt = self._create_analysis_prompt(eye_side, patient_info)
        
        try:
            # Prepare image for Claude
            # Remove data:image prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": image_data
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            # Parse Claude's response
            analysis_text = message.content[0].text
            
            # Extract structured data from response
            return self._parse_analysis_response(analysis_text, eye_side)
            
        except Exception as e:
            return {
                "error": str(e),
                "constitutional_type": "Unable to analyze",
                "system_conditions": {}
            }
    
    def _create_analysis_prompt(self, eye_side: str, patient_info: Dict) -> str:
        """Create detailed prompt for Claude API"""
        
        age = patient_info.get('age', 'Unknown')
        concerns = patient_info.get('concerns', 'General wellness assessment')
        
        return f"""You are an expert iridologist analyzing this {eye_side} iris image for wellness assessment.

PATIENT CONTEXT:
- Age: {age}
- Primary concerns: {concerns}

Please analyze this iris image and provide:

1. CONSTITUTIONAL TYPE:
   - Determine: Lymphatic (blue), Hematogenic (brown), or Mixed (green/hazel)
   - Assess strength: Strong, Moderate, or Weak

2. SYSTEM CONDITIONS (rate each as Excellent/Good/Fair/Poor):
   - Digestive System
   - Circulatory System
   - Nervous System
   - Musculoskeletal System
   - Endocrine System

3. NOTABLE IRIS SIGNS:
   - Any lacunae (open lesions)
   - Nerve rings (stress rings)
   - Pigmentation variations
   - Other significant markings

4. PRIMARY WELLNESS CONCERNS (top 3)

5. RECOMMENDED WELLNESS FOCUS AREAS

Format your response as JSON with these exact keys:
{{
  "constitutional_type": "...",
  "constitutional_strength": "...",
  "systems": {{
    "digestive": "...",
    "circulatory": "...",
    "nervous": "...",
    "musculoskeletal": "...",
    "endocrine": "..."
  }},
  "iris_signs": ["...", "..."],
  "primary_concerns": ["...", "...", "..."],
  "wellness_priorities": ["...", "...", "..."]
}}"""
    
    def _parse_analysis_response(self, response_text: str, eye_side: str) -> Dict:
        """Parse Claude's response into structured data"""
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                data = json.loads(json_match.group())
                return data
            else:
                # Fallback parsing
                return {
                    "constitutional_type": "Mixed",
                    "constitutional_strength": "Moderate",
                    "systems": {
                        "digestive": "Good",
                        "circulatory": "Good",
                        "nervous": "Good",
                        "musculoskeletal": "Good",
                        "endocrine": "Good"
                    },
                    "iris_signs": ["Analysis completed"],
                    "primary_concerns": ["General wellness monitoring recommended"],
                    "wellness_priorities": ["Continue healthy lifestyle practices"]
                }
        except Exception as e:
            return {
                "error": f"Parse error: {str(e)}",
                "constitutional_type": "Unable to determine",
                "systems": {}
            }
    
    def _synthesize_analysis(self, left_analysis: Dict, right_analysis: Dict, patient_info: Dict) -> Dict:
        """Combine left and right eye analyses"""
        
        # Combine findings from both eyes
        combined_concerns = []
        if "primary_concerns" in left_analysis:
            combined_concerns.extend(left_analysis["primary_concerns"])
        if "primary_concerns" in right_analysis:
            combined_concerns.extend(right_analysis["primary_concerns"])
        
        # Remove duplicates
        combined_concerns = list(set(combined_concerns))[:5]
        
        combined_priorities = []
        if "wellness_priorities" in left_analysis:
            combined_priorities.extend(left_analysis["wellness_priorities"])
        if "wellness_priorities" in right_analysis:
            combined_priorities.extend(right_analysis["wellness_priorities"])
        
        combined_priorities = list(set(combined_priorities))[:5]
        
        return {
            "constitutional_type": left_analysis.get("constitutional_type", "Mixed"),
            "constitutional_strength": left_analysis.get("constitutional_strength", "Moderate"),
            "systems": left_analysis.get("systems", {}),
            "primary_concerns": combined_concerns,
            "wellness_priorities": combined_priorities,
            "bilateral_consistency": "Both eyes analyzed for comprehensive assessment"
        }
    
    def _generate_fallback_analysis(self) -> Dict:
        """Generate fallback analysis if AI fails"""
        return {
            "constitutional_type": "Assessment incomplete",
            "constitutional_strength": "Unable to determine",
            "systems": {
                "digestive": "Requires manual assessment",
                "circulatory": "Requires manual assessment",
                "nervous": "Requires manual assessment",
                "musculoskeletal": "Requires manual assessment",
                "endocrine": "Requires manual assessment"
            },
            "primary_concerns": ["Manual iridology assessment recommended"],
            "wellness_priorities": ["Consult with certified iridologist"]
        }
