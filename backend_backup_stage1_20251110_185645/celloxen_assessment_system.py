"""
Celloxen Assessment System - Core Logic
Handles questionnaire scoring, therapy recommendations, and iridology integration
"""

# 5 Celloxen Therapy Domains with 7 Questions Each
ASSESSMENT_QUESTIONS = {
    "c102_vitality_energy": {
        "domain_name": "Vitality & Energy Support (C-102)",
        "description": "Advanced metabolic support for sustained energy and vitality",
        "questions": [
            {
                "id": "q1",
                "text": "How would you rate your overall energy levels throughout the day?",
                "type": "scale",
                "options": ["Very Low", "Low", "Moderate", "Good", "Excellent"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q2",
                "text": "How often do you experience fatigue or tiredness?",
                "type": "frequency",
                "options": ["Constantly", "Daily", "Few times a week", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q3",
                "text": "Do you experience afternoon energy crashes?",
                "type": "frequency",
                "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q4",
                "text": "How well do you recover after physical activity?",
                "type": "scale",
                "options": ["Very Poorly", "Poorly", "Moderately", "Well", "Very Well"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q5",
                "text": "How would you describe your mental clarity and focus?",
                "type": "scale",
                "options": ["Very Foggy", "Foggy", "Average", "Clear", "Very Clear"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q6",
                "text": "How many hours of quality sleep do you get per night?",
                "type": "scale",
                "options": ["Less than 5", "5-6 hours", "6-7 hours", "7-8 hours", "8+ hours"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q7",
                "text": "How often do you feel motivated to engage in daily activities?",
                "type": "frequency",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
                "weights": [0, 25, 50, 75, 100]
            }
        ]
    },
    
    "c104_comfort_mobility": {
        "domain_name": "Comfort & Mobility Support (C-104)",
        "description": "Joint health and chronic pain management support",
        "questions": [
            {
                "id": "q1",
                "text": "How would you rate your current pain levels?",
                "type": "scale",
                "options": ["Severe", "Moderate-Severe", "Moderate", "Mild", "None"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q2",
                "text": "How does pain affect your daily activities?",
                "type": "impact",
                "options": ["Severely limits", "Significantly limits", "Moderately limits", "Slightly limits", "No limitation"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q3",
                "text": "How stiff do your joints feel in the morning?",
                "type": "severity",
                "options": ["Extremely stiff", "Very stiff", "Moderately stiff", "Slightly stiff", "Not stiff"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q4",
                "text": "How is your range of motion in affected areas?",
                "type": "scale",
                "options": ["Very Limited", "Limited", "Moderate", "Good", "Excellent"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q5",
                "text": "How often do you experience muscle tension or spasms?",
                "type": "frequency",
                "options": ["Constantly", "Daily", "Few times a week", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q6",
                "text": "How well can you perform physical tasks (walking, climbing stairs, etc.)?",
                "type": "ability",
                "options": ["Very Difficult", "Difficult", "Manageable", "Easy", "Very Easy"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q7",
                "text": "How much does discomfort interfere with your sleep?",
                "type": "impact",
                "options": ["Severely", "Significantly", "Moderately", "Slightly", "Not at all"],
                "weights": [0, 25, 50, 75, 100]
            }
        ]
    },
    
    "c105_circulation_heart": {
        "domain_name": "Circulation & Heart Wellness (C-105)",
        "description": "Cardiovascular health and circulation support",
        "questions": [
            {
                "id": "q1",
                "text": "How often do you experience cold hands or feet?",
                "type": "frequency",
                "options": ["Constantly", "Very Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q2",
                "text": "Do you experience swelling in your legs, ankles, or feet?",
                "type": "frequency",
                "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q3",
                "text": "How would you describe your energy during physical exertion?",
                "type": "scale",
                "options": ["Extremely Limited", "Very Limited", "Moderate", "Good", "Excellent"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q4",
                "text": "How often do you experience shortness of breath during normal activities?",
                "type": "frequency",
                "options": ["Very Often", "Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q5",
                "text": "Do you experience irregular heartbeat or palpitations?",
                "type": "frequency",
                "options": ["Frequently", "Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q6",
                "text": "How would you rate your overall cardiovascular fitness?",
                "type": "scale",
                "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q7",
                "text": "How often do you feel dizzy or lightheaded when standing?",
                "type": "frequency",
                "options": ["Very Often", "Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            }
        ]
    },
    
    "c107_stress_relaxation": {
        "domain_name": "Stress & Relaxation Support (C-107)",
        "description": "Sleep, cognitive wellness, and stress management",
        "questions": [
            {
                "id": "q1",
                "text": "How would you rate your current stress levels?",
                "type": "scale",
                "options": ["Extreme", "High", "Moderate", "Low", "Very Low"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q2",
                "text": "How often do you feel anxious or worried?",
                "type": "frequency",
                "options": ["Constantly", "Very Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q3",
                "text": "How well do you fall asleep at night?",
                "type": "quality",
                "options": ["Very Poorly", "Poorly", "Moderately", "Well", "Very Well"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q4",
                "text": "How often do you wake up feeling refreshed?",
                "type": "frequency",
                "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q5",
                "text": "How would you describe your ability to relax?",
                "type": "ability",
                "options": ["Very Difficult", "Difficult", "Moderate", "Easy", "Very Easy"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q6",
                "text": "How often do you experience tension headaches?",
                "type": "frequency",
                "options": ["Daily", "Several times a week", "Weekly", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q7",
                "text": "How well can you concentrate and focus on tasks?",
                "type": "ability",
                "options": ["Very Poorly", "Poorly", "Moderately", "Well", "Very Well"],
                "weights": [0, 25, 50, 75, 100]
            }
        ]
    },
    
    "c108_metabolic_balance": {
        "domain_name": "Metabolic Balance Support (C-108)",
        "description": "Glycaemic control and metabolic wellness",
        "questions": [
            {
                "id": "q1",
                "text": "How stable are your energy levels after meals?",
                "type": "stability",
                "options": ["Very Unstable", "Unstable", "Moderate", "Stable", "Very Stable"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q2",
                "text": "How often do you experience sugar cravings?",
                "type": "frequency",
                "options": ["Constantly", "Very Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q3",
                "text": "How would you describe your appetite regulation?",
                "type": "quality",
                "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q4",
                "text": "How often do you feel thirsty or have a dry mouth?",
                "type": "frequency",
                "options": ["Constantly", "Very Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q5",
                "text": "How is your weight management over the past 6 months?",
                "type": "trend",
                "options": ["Very Difficult", "Difficult", "Moderate", "Easy", "Very Easy"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q6",
                "text": "How often do you experience bloating or digestive discomfort?",
                "type": "frequency",
                "options": ["Very Often", "Often", "Sometimes", "Rarely", "Never"],
                "weights": [0, 25, 50, 75, 100]
            },
            {
                "id": "q7",
                "text": "How would you rate your overall metabolic health?",
                "type": "scale",
                "options": ["Very Poor", "Poor", "Fair", "Good", "Excellent"],
                "weights": [0, 25, 50, 75, 100]
            }
        ]
    }
}

# Therapy Protocol Specifications
THERAPY_PROTOCOLS = {
    "C-102": {
        "name": "Vitality & Energy Support",
        "description": "Advanced metabolic support for sustained energy",
        "recommended_sessions": 12,
        "session_frequency": "3 times per week",
        "session_duration": "30 minutes",
        "key_benefits": [
            "Enhanced cellular energy production",
            "Improved mental clarity and focus",
            "Better stress resilience",
            "Optimized metabolic function"
        ]
    },
    "C-104": {
        "name": "Comfort & Mobility Support",
        "description": "Joint health and chronic pain management",
        "recommended_sessions": 15,
        "session_frequency": "3-4 times per week",
        "session_duration": "30-40 minutes",
        "key_benefits": [
            "Reduced pain and inflammation",
            "Improved joint mobility",
            "Enhanced muscle recovery",
            "Better physical function"
        ]
    },
    "C-105": {
        "name": "Circulation & Heart Wellness",
        "description": "Cardiovascular health optimization",
        "recommended_sessions": 12,
        "session_frequency": "3 times per week",
        "session_duration": "30 minutes",
        "key_benefits": [
            "Improved circulation",
            "Enhanced cardiovascular function",
            "Better oxygen delivery",
            "Reduced peripheral symptoms"
        ]
    },
    "C-107": {
        "name": "Stress & Relaxation Support",
        "description": "Sleep quality and stress management",
        "recommended_sessions": 10,
        "session_frequency": "2-3 times per week",
        "session_duration": "30 minutes",
        "key_benefits": [
            "Improved sleep quality",
            "Reduced stress and anxiety",
            "Enhanced relaxation response",
            "Better cognitive function"
        ]
    },
    "C-108": {
        "name": "Metabolic Balance Support",
        "description": "Glycaemic control and metabolic optimization",
        "recommended_sessions": 12,
        "session_frequency": "3 times per week",
        "session_duration": "30 minutes",
        "key_benefits": [
            "Improved glucose regulation",
            "Better energy stability",
            "Enhanced metabolic efficiency",
            "Optimized weight management"
        ]
    }
}

def calculate_assessment_score(domain, responses):
    """
    Calculate score for a specific domain based on responses
    Returns: dict with score, severity, and analysis
    """
    questions = ASSESSMENT_QUESTIONS.get(domain, {}).get("questions", [])
    
    if not questions or not responses:
        return {"score": 0, "severity": "incomplete", "total_possible": 0}
    
    total_score = 0
    total_possible = len(questions) * 100
    answered = 0
    
    for question in questions:
        q_id = question["id"]
        if q_id in responses:
            response_index = int(responses[q_id])
            score = question["weights"][response_index]
            total_score += score
            answered += 1
    
    if answered == 0:
        return {"score": 0, "severity": "incomplete", "total_possible": total_possible}
    
    # Calculate percentage score
    percentage = (total_score / total_possible) * 100
    
    # Determine severity and priority (lower score = higher need)
    if percentage < 40:
        severity = "High Priority"
        priority_level = "High"
    elif percentage < 65:
        severity = "Moderate Priority"
        priority_level = "Moderate"
    else:
        severity = "Low Priority"
        priority_level = "Low"
    
    return {
        "score": round(percentage, 2),
        "raw_score": total_score,
        "total_possible": total_possible,
        "questions_answered": answered,
        "total_questions": len(questions),
        "severity": severity,
        "priority_level": priority_level,
        "wellness_status": get_wellness_status(percentage)
    }

def get_wellness_status(percentage):
    """Convert percentage to wellness status"""
    if percentage >= 80:
        return "Excellent"
    elif percentage >= 65:
        return "Good"
    elif percentage >= 50:
        return "Fair"
    elif percentage >= 35:
        return "Poor"
    else:
        return "Needs Attention"

def generate_therapy_recommendations(domain, score_result):
    """Generate therapy recommendations based on assessment scores"""
    therapy_code = domain.upper().replace("_", "-").split("-")[0] + "-" + domain.split("_")[1][:3].upper()
    
    # Map domain codes to therapy codes
    domain_to_therapy = {
        "c102_vitality_energy": "C-102",
        "c104_comfort_mobility": "C-104",
        "c105_circulation_heart": "C-105",
        "c107_stress_relaxation": "C-107",
        "c108_metabolic_balance": "C-108"
    }
    
    therapy_code = domain_to_therapy.get(domain, "C-102")
    protocol = THERAPY_PROTOCOLS.get(therapy_code, {})
    
    priority = score_result.get("priority_level", "Moderate")
    score = score_result.get("score", 50)
    
    # Adjust session recommendations based on priority
    base_sessions = protocol.get("recommended_sessions", 12)
    if priority == "High":
        recommended_sessions = base_sessions + 3
        frequency = "4-5 times per week (intensive)"
    elif priority == "Moderate":
        recommended_sessions = base_sessions
        frequency = protocol.get("session_frequency", "3 times per week")
    else:
        recommended_sessions = max(6, base_sessions - 3)
        frequency = "2-3 times per week (maintenance)"
    
    return {
        "therapy_code": therapy_code,
        "therapy_name": protocol.get("name", ""),
        "priority_level": priority,
        "recommended": priority in ["High", "Moderate"],
        "recommended_sessions": recommended_sessions,
        "session_frequency": frequency,
        "session_duration": protocol.get("session_duration", "30 minutes"),
        "estimated_duration": f"{recommended_sessions // 3} weeks",
        "key_benefits": protocol.get("key_benefits", []),
        "rationale": generate_recommendation_rationale(domain, score, priority)
    }

def generate_recommendation_rationale(domain, score, priority):
    """Generate explanation for therapy recommendation"""
    domain_name = ASSESSMENT_QUESTIONS[domain]["domain_name"]
    
    if priority == "High":
        return f"Based on your assessment, {domain_name} shows significant areas for improvement (score: {score}%). This therapy is highly recommended to address your wellness needs."
    elif priority == "Moderate":
        return f"Your assessment indicates moderate wellness in {domain_name} (score: {score}%). This therapy is recommended to enhance your wellbeing and prevent future concerns."
    else:
        return f"Your {domain_name} assessment shows good wellness (score: {score}%). This therapy can help maintain and further optimize your current health status."

def generate_multi_domain_recommendations(all_scores):
    """
    Generate prioritized recommendations across all domains
    Returns: sorted list of therapy recommendations
    """
    recommendations = []
    
    for domain, score_result in all_scores.items():
        if score_result.get("questions_answered", 0) > 0:
            recommendation = generate_therapy_recommendations(domain, score_result)
            recommendation["domain"] = domain
            recommendation["score"] = score_result.get("score", 0)
            recommendations.append(recommendation)
    
    # Sort by priority (High > Moderate > Low) then by score (lower score = higher priority)
    priority_order = {"High": 0, "Moderate": 1, "Low": 2}
    recommendations.sort(key=lambda x: (priority_order.get(x["priority_level"], 3), x["score"]))
    
    return recommendations
