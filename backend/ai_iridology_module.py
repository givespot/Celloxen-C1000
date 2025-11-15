"""
CELLOXEN HEALTH PORTAL - AI IRIDOLOGY ANALYSIS MODULE
Integrates Anthropic Claude for iris image analysis
Created: November 14, 2025
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import asyncpg
import json
import os
import anthropic

router = APIRouter(prefix="/api/v1/iridology", tags=["Iridology"])

# Initialize Anthropic client
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class IridologyAnalysis(BaseModel):
    assessment_id: int
    left_eye_image: str  # Base64 encoded
    right_eye_image: str  # Base64 encoded

# ============================================================================
# AI ANALYSIS FUNCTIONS
# ============================================================================

async def analyze_iris_with_claude(left_eye_base64: str, right_eye_base64: str) -> dict:
    """
    Analyze iris images using Anthropic Claude with vision
    Returns constitutional type, findings, and recommendations
    """
    
    try:
        prompt = """You are an expert in holistic iridology analysis. Analyze these iris images and provide:

1. Constitutional Type: Classify as one of:
   - Lymphatic (blue/gray iris, prone to lymphatic congestion)
   - Hematogenic (brown iris, prone to blood/liver issues)
   - Mixed (combination, varied patterns)

2. Body System Indicators: Identify potential areas of concern in:
   - Digestive system (vitality_energy domain)
   - Circulatory system (circulation_heart domain)
   - Nervous system (stress_relaxation domain)
   - Immune system (immune_digestive domain)
   - Musculoskeletal system (comfort_mobility domain)

3. Wellness Observations:
   - Stress indicators (nerve rings, white areas)
   - Inflammation signs (darker spots)
   - Circulation patterns (radial furrows)
   - Constitutional strength (density, clarity)

4. Holistic Recommendations: Suggest 3-5 wellness support areas

IMPORTANT: 
- This is for holistic wellness guidance only
- NOT medical diagnosis
- Focus on preventive wellness support
- Use gentle, supportive language

Respond in JSON format:
{
    "constitutional_type": "Lymphatic|Hematogenic|Mixed",
    "constitutional_strength": "Strong|Moderate|Weak",
    "findings": {
        "vitality_energy": "observation here",
        "circulation_heart": "observation here",
        "stress_relaxation": "observation here",
        "immune_digestive": "observation here",
        "comfort_mobility": "observation here"
    },
    "stress_indicators": ["indicator1", "indicator2"],
    "recommendations": ["recommendation1", "recommendation2", "recommendation3"]
}"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": left_eye_base64
                            }
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": right_eye_base64
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
        
        # Get the response text
        result_text = message.content[0].text
        
        # Extract JSON from markdown code blocks if present
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        return result
        
    except Exception as e:
        print(f"Error in Claude analysis: {str(e)}")
        # Return a default structure if AI fails
        return {
            "constitutional_type": "Analysis Pending",
            "constitutional_strength": "Moderate",
            "findings": {
                "vitality_energy": "Analysis in progress",
                "circulation_heart": "Analysis in progress",
                "stress_relaxation": "Analysis in progress",
                "immune_digestive": "Analysis in progress",
                "comfort_mobility": "Analysis in progress"
            },
            "stress_indicators": ["Analysis pending"],
            "recommendations": ["Please consult with practitioner for detailed analysis"]
        }

# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post("/analyze")
async def analyze_iridology(data: IridologyAnalysis):
    """
    Analyze iris images using Claude AI and store results
    """
    try:
        # Validate images are not empty
        if not data.left_eye_image or not data.right_eye_image:
            raise HTTPException(status_code=400, detail="Both left and right eye images required")
        
        # Run AI analysis with Claude
        print(f"Starting Claude AI analysis for assessment {data.assessment_id}...")
        ai_result = await analyze_iris_with_claude(data.left_eye_image, data.right_eye_image)
        
        # Connect to database
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        # Update assessment with iridology data
        await conn.execute(
            """UPDATE comprehensive_assessments
               SET iris_images = $2::jsonb,
                   constitutional_type = $3,
                   constitutional_strength = $4,
                   iridology_data = $5::jsonb,
                   iridology_completed = true,
                   updated_at = NOW()
               WHERE id = $1""",
            data.assessment_id,
            json.dumps({
                "left_eye": "stored",
                "right_eye": "stored"
            }),
            ai_result.get("constitutional_type", "Unknown"),
            ai_result.get("constitutional_strength", "Moderate"),
            json.dumps(ai_result)
        )
        
        await conn.close()
        
        return {
            "success": True,
            "assessment_id": data.assessment_id,
            "constitutional_type": ai_result.get("constitutional_type"),
            "constitutional_strength": ai_result.get("constitutional_strength"),
            "findings": ai_result.get("findings"),
            "recommendations": ai_result.get("recommendations")
        }
        
    except Exception as e:
        import traceback
        print(f"ERROR in iridology analysis: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{assessment_id}")
async def get_iridology_results(assessment_id: int):
    """
    Get stored iridology analysis results
    """
    try:
        conn = await asyncpg.connect(
            host="localhost", port=5432, user="celloxen_user",
            password="CelloxenSecure2025", database="celloxen_portal"
        )
        
        result = await conn.fetchrow(
            """SELECT 
                constitutional_type,
                constitutional_strength,
                iridology_data,
                iridology_completed
               FROM comprehensive_assessments
               WHERE id = $1""",
            assessment_id
        )
        
        await conn.close()
        
        if not result:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        if not result['iridology_completed']:
            raise HTTPException(status_code=404, detail="Iridology analysis not yet completed")
        
        return {
            "success": True,
            "constitutional_type": result['constitutional_type'],
            "constitutional_strength": result['constitutional_strength'],
            "iridology_data": result['iridology_data']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test")
async def test_iridology():
    """Test endpoint to verify module is loaded"""
    return {"status": "Iridology module operational (Claude AI)", "version": "1.0"}
