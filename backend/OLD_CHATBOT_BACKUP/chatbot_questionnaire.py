"""
Chatbot #1: Guided Wellness Questionnaire
35 questions across 5 Celloxen therapy domains
"""

from typing import List, Dict
import json

# 35 Wellness Questions across 5 domains
WELLNESS_QUESTIONS = {
    "energy_vitality": [
        {
            "id": "ev1",
            "question": "How would you rate your overall energy levels throughout the day?",
            "type": "scale",
            "options": ["Very Low (1)", "Low (2)", "Moderate (3)", "Good (4)", "Excellent (5)"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "ev2",
            "question": "Do you experience afternoon energy crashes?",
            "type": "choice",
            "options": ["Daily", "Several times a week", "Occasionally", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "ev3",
            "question": "How many hours of sleep do you typically get per night?",
            "type": "choice",
            "options": ["Less than 5", "5-6 hours", "6-7 hours", "7-8 hours", "8+ hours"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "ev4",
            "question": "Do you feel refreshed when you wake up?",
            "type": "choice",
            "options": ["Never", "Rarely", "Sometimes", "Often", "Always"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "ev5",
            "question": "How often do you feel fatigued during physical activities?",
            "type": "choice",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "ev6",
            "question": "Do you rely on caffeine or energy drinks to get through the day?",
            "type": "choice",
            "options": ["Multiple times daily", "Daily", "Several times a week", "Occasionally", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "ev7",
            "question": "How would you describe your mental clarity and focus?",
            "type": "scale",
            "options": ["Very Poor (1)", "Poor (2)", "Fair (3)", "Good (4)", "Excellent (5)"],
            "score_map": [1, 2, 3, 4, 5]
        }
    ],
    
    "pain_mobility": [
        {
            "id": "pm1",
            "question": "Do you experience chronic pain or discomfort?",
            "type": "choice",
            "options": ["Constant (daily)", "Frequent (several times a week)", "Occasional", "Rare", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "pm2",
            "question": "How would you rate your joint flexibility?",
            "type": "scale",
            "options": ["Very Limited (1)", "Limited (2)", "Moderate (3)", "Good (4)", "Excellent (5)"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "pm3",
            "question": "Do you experience back pain?",
            "type": "choice",
            "options": ["Severe daily", "Moderate frequently", "Mild occasionally", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "pm4",
            "question": "How easily can you perform daily physical tasks?",
            "type": "scale",
            "options": ["Very Difficult (1)", "Difficult (2)", "Moderate (3)", "Easy (4)", "Very Easy (5)"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "pm5",
            "question": "Do you experience muscle tension or stiffness?",
            "type": "choice",
            "options": ["Constantly", "Frequently", "Sometimes", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "pm6",
            "question": "How often do headaches or migraines affect you?",
            "type": "choice",
            "options": ["Daily", "Several times a week", "Weekly", "Monthly", "Rarely/Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "pm7",
            "question": "Can you exercise without pain or significant discomfort?",
            "type": "choice",
            "options": ["No, always painful", "Usually uncomfortable", "Sometimes", "Usually comfortable", "Yes, always"],
            "score_map": [1, 2, 3, 4, 5]
        }
    ],
    
    "stress_management": [
        {
            "id": "sm1",
            "question": "How would you rate your current stress levels?",
            "type": "scale",
            "options": ["Overwhelming (1)", "High (2)", "Moderate (3)", "Low (4)", "Very Low (5)"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sm2",
            "question": "How often do you feel anxious or worried?",
            "type": "choice",
            "options": ["Constantly", "Daily", "Several times a week", "Occasionally", "Rarely"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sm3",
            "question": "Do you have difficulty relaxing or unwinding?",
            "type": "choice",
            "options": ["Always", "Often", "Sometimes", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sm4",
            "question": "How well do you handle unexpected challenges?",
            "type": "scale",
            "options": ["Very Poorly (1)", "Poorly (2)", "Moderately (3)", "Well (4)", "Very Well (5)"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sm5",
            "question": "Do you practice any stress-reduction techniques?",
            "type": "choice",
            "options": ["Never", "Rarely", "Occasionally", "Regularly", "Daily practice"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sm6",
            "question": "How often do you feel emotionally balanced?",
            "type": "choice",
            "options": ["Never", "Rarely", "Sometimes", "Often", "Almost always"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sm7",
            "question": "Do you experience mood swings?",
            "type": "choice",
            "options": ["Very frequently", "Frequently", "Occasionally", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        }
    ],
    
    "metabolic_balance": [
        {
            "id": "mb1",
            "question": "How would you describe your digestion?",
            "type": "choice",
            "options": ["Very problematic", "Often uncomfortable", "Sometimes issues", "Generally good", "Excellent"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "mb2",
            "question": "Do you experience bloating or gas?",
            "type": "choice",
            "options": ["Daily/severe", "Frequently", "Occasionally", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "mb3",
            "question": "How stable is your weight?",
            "type": "choice",
            "options": ["Fluctuates significantly", "Often changes", "Somewhat stable", "Stable", "Very stable"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "mb4",
            "question": "Do you experience sugar cravings?",
            "type": "choice",
            "options": ["Constantly", "Daily", "Several times a week", "Occasionally", "Rarely/Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "mb5",
            "question": "How regular are your bowel movements?",
            "type": "choice",
            "options": ["Very irregular", "Irregular", "Somewhat regular", "Regular", "Very regular"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "mb6",
            "question": "Do you follow a balanced, nutritious diet?",
            "type": "choice",
            "options": ["Rarely", "Sometimes", "Often", "Usually", "Always"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "mb7",
            "question": "How often do you feel hungry between meals?",
            "type": "choice",
            "options": ["Constantly", "Very frequently", "Moderately", "Occasionally", "Rarely"],
            "score_map": [1, 2, 3, 4, 5]
        }
    ],
    
    "sleep_quality": [
        {
            "id": "sq1",
            "question": "How long does it take you to fall asleep?",
            "type": "choice",
            "options": ["Over 60 mins", "30-60 mins", "15-30 mins", "5-15 mins", "Under 5 mins"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sq2",
            "question": "How often do you wake up during the night?",
            "type": "choice",
            "options": ["Multiple times", "2-3 times", "Once", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sq3",
            "question": "Do you snore or experience breathing difficulties while sleeping?",
            "type": "choice",
            "options": ["Severely/always", "Frequently", "Sometimes", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sq4",
            "question": "How would you rate your overall sleep quality?",
            "type": "scale",
            "options": ["Very Poor (1)", "Poor (2)", "Fair (3)", "Good (4)", "Excellent (5)"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sq5",
            "question": "Do you have a consistent sleep schedule?",
            "type": "choice",
            "options": ["No, very irregular", "Somewhat irregular", "Moderately consistent", "Mostly consistent", "Very consistent"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sq6",
            "question": "Do you use sleeping aids or medications?",
            "type": "choice",
            "options": ["Daily/essential", "Frequently", "Occasionally", "Rarely", "Never"],
            "score_map": [1, 2, 3, 4, 5]
        },
        {
            "id": "sq7",
            "question": "How rested do you feel after sleeping?",
            "type": "scale",
            "options": ["Exhausted (1)", "Tired (2)", "Somewhat rested (3)", "Rested (4)", "Fully refreshed (5)"],
            "score_map": [1, 2, 3, 4, 5]
        }
    ]
}


def get_all_questions() -> Dict:
    """Get all questions organized by domain"""
    return WELLNESS_QUESTIONS


def calculate_domain_score(responses: List[int]) -> float:
    """Calculate score for a domain (0-100)"""
    if not responses:
        return 0.0
    
    # Each question scored 1-5, convert to 0-100
    max_possible = len(responses) * 5
    actual_score = sum(responses)
    
    return round((actual_score / max_possible) * 100, 1)


def calculate_all_scores(answers: Dict) -> Dict:
    """
    Calculate wellness scores from chatbot answers
    
    Args:
        answers: Dict with question_id as key and answer_index as value
        
    Returns:
        Dict with domain scores and overall score
    """
    
    domain_scores = {}
    
    for domain, questions in WELLNESS_QUESTIONS.items():
        domain_responses = []
        
        for q in questions:
            if q['id'] in answers:
                answer_index = answers[q['id']]
                score = q['score_map'][answer_index]
                domain_responses.append(score)
        
        domain_scores[domain] = calculate_domain_score(domain_responses)
    
    # Overall score is average of all domains
    overall_score = round(sum(domain_scores.values()) / len(domain_scores), 1)
    
    return {
        'overall_score': overall_score,
        'energy_vitality': domain_scores['energy_vitality'],
        'pain_mobility': domain_scores['pain_mobility'],
        'stress_management': domain_scores['stress_management'],
        'metabolic_balance': domain_scores['metabolic_balance'],
        'sleep_quality': domain_scores['sleep_quality']
    }
