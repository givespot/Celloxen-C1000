"""
AI Response Handler for Chatbot Assessment
Interprets user messages and generates contextual responses
"""

import json
import re
from datetime import datetime

class AIResponseHandler:
    def __init__(self):
        self.stages = {
            'introduction': 'greeting',
            'questionnaire_review': 'reviewing questionnaire',
            'follow_up_questions': 'asking follow-up questions',
            'iridology_prep': 'preparing for iridology',
            'iridology_capture': 'capturing iris images',
            'analysis': 'analyzing results',
            'completion': 'completing assessment'
        }
        
    def get_response(self, user_message, session_data, patient_data):
        """
        Generate AI response based on user message and context
        """
        current_stage = session_data.get('current_stage', 'introduction')
        
        # Analyze user intent
        intent = self._analyze_intent(user_message)
        
        # Generate contextual response based on stage
        if current_stage == 'introduction':
            return self._handle_introduction(user_message, intent, patient_data)
        elif current_stage == 'questionnaire_review':
            return self._handle_questionnaire_review(user_message, intent, patient_data)
        elif current_stage == 'follow_up_questions':
            return self._handle_follow_up(user_message, intent, patient_data)
        elif current_stage == 'iridology_prep':
            return self._handle_iridology_prep(user_message, intent)
        else:
            return self._handle_general(user_message, intent)
    
    def _analyze_intent(self, message):
        """
        Analyze user message to determine intent
        """
        message_lower = message.lower().strip()
        
        # Affirmative responses
        if any(word in message_lower for word in ['yes', 'sure', 'okay', 'ok', 'ready', 'let\'s go', 'proceed']):
            return 'affirmative'
        
        # Negative responses
        if any(word in message_lower for word in ['no', 'not yet', 'wait', 'hold on', 'stop']):
            return 'negative'
        
        # Questions
        if any(word in message_lower for word in ['what', 'how', 'why', 'when', 'where', 'who', '?']):
            return 'question'
        
        # Concern or worry
        if any(word in message_lower for word in ['worried', 'concerned', 'nervous', 'anxious', 'scared']):
            return 'concern'
        
        # Gratitude
        if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
            return 'gratitude'
        
        return 'informative'
    
    def _handle_introduction(self, message, intent, patient_data):
        """
        Handle introduction stage responses
        """
        if intent == 'affirmative':
            response = {
                'message': f"Wonderful! Let's begin by reviewing your wellness questionnaire.\n\n" +
                          f"I can see you completed your pre-registration assessment. " +
                          f"Let me pull up your responses...\n\n" +
                          f"✓ Questionnaire loaded!\n\n" +
                          f"Based on your responses, I'd like to explore a few areas in more depth. " +
                          f"Are you comfortable discussing your health concerns today?",
                'next_stage': 'questionnaire_review'
            }
        elif intent == 'question':
            response = {
                'message': "Great question! During this assessment, I'll:\n" +
                          "• Review your wellness questionnaire responses\n" +
                          "• Ask clarifying questions about your health\n" +
                          "• Guide you through iris imaging (iridology)\n" +
                          "• Help create a personalized therapy plan\n\n" +
                          "The whole process takes about 20-30 minutes. Ready to begin?",
                'next_stage': 'introduction'
            }
        elif intent == 'concern':
            response = {
                'message': "I understand this might feel new or uncertain. Don't worry - " +
                          "I'm here to guide you every step of the way, and your practitioner is " +
                          "right here with you.\n\n" +
                          "Everything we discuss is confidential, and you can take breaks anytime you need. " +
                          "Shall we start gently?",
                'next_stage': 'introduction'
            }
        else:
            response = {
                'message': "Thank you for sharing that. When you're ready, we can begin your " +
                          "comprehensive wellness assessment. Just let me know!",
                'next_stage': 'introduction'
            }
        
        return response
    
    def _handle_questionnaire_review(self, message, intent, patient_data):
        """
        Handle questionnaire review stage
        """
        if intent == 'affirmative':
            response = {
                'message': "Thank you for being open. Looking at your questionnaire, I notice " +
                          "you mentioned experiencing:\n\n" +
                          "• Low energy levels\n" +
                          "• Digestive concerns\n" +
                          "• Sleep difficulties\n\n" +
                          "Can you tell me which of these affects your daily life the most?",
                'next_stage': 'follow_up_questions'
            }
        elif intent == 'question':
            response = {
                'message': "Your questionnaire responses help us understand your overall wellness " +
                          "and identify areas that might benefit from therapy.\n\n" +
                          "We look at five key areas:\n" +
                          "1. Energy & Vitality\n" +
                          "2. Digestive Health\n" +
                          "3. Stress & Mental Wellbeing\n" +
                          "4. Metabolic Balance\n" +
                          "5. Sleep Quality\n\n" +
                          "Are you ready to discuss these areas?",
                'next_stage': 'questionnaire_review'
            }
        else:
            response = {
                'message': "I understand. Let's take this at your pace. " +
                          "Would you like to start with your most pressing health concern?",
                'next_stage': 'questionnaire_review'
            }
        
        return response
    
    def _handle_follow_up(self, message, intent, patient_data):
        """
        Handle follow-up questions stage
        """
        # Extract meaningful information from user's response
        response = {
            'message': f"Thank you for sharing that with me. Understanding '{message}' " +
                      f"helps me get a clearer picture of your wellness needs.\n\n" +
                      f"Based on what you've told me, I believe we should focus on " +
                      f"supporting your body's natural healing processes.\n\n" +
                      f"Now, let's move to the next part of your assessment - iridology. " +
                      f"This is where we'll capture images of your iris to analyze your " +
                      f"constitutional health.\n\n" +
                      f"Your practitioner will help position the camera. Are you ready to proceed?",
            'next_stage': 'iridology_prep'
        }
        
        return response
    
    def _handle_iridology_prep(self, message, intent):
        """
        Handle iridology preparation stage
        """
        if intent == 'affirmative':
            response = {
                'message': "Perfect! Let's start with your LEFT eye.\n\n" +
                          "📸 Instructions:\n" +
                          "• Look directly at the camera\n" +
                          "• Keep your eye wide open\n" +
                          "• Try not to blink\n" +
                          "• Hold very still\n\n" +
                          "Your practitioner will guide you through the positioning.\n" +
                          "Let me know when you're ready to capture!",
                'next_stage': 'iridology_capture'
            }
        elif intent == 'question':
            response = {
                'message': "Iridology is a fascinating technique! We analyze the iris of your eye, " +
                          "which can reveal information about your constitutional health, " +
                          "organ systems, and potential areas of concern.\n\n" +
                          "The process is:\n" +
                          "• Completely non-invasive\n" +
                          "• Painless\n" +
                          "• Takes just a few minutes\n" +
                          "• Provides valuable health insights\n\n" +
                          "Ready to give it a try?",
                'next_stage': 'iridology_prep'
            }
        else:
            response = {
                'message': "No worries! Take your time. When you feel comfortable, " +
                          "we can proceed with the iris imaging. Just let me know!",
                'next_stage': 'iridology_prep'
            }
        
        return response
    
    def _handle_general(self, message, intent):
        """
        Handle general conversation
        """
        if intent == 'gratitude':
            response = {
                'message': "You're very welcome! I'm here to help make this assessment " +
                          "as comfortable and informative as possible for you. " +
                          "What would you like to know or discuss next?",
                'next_stage': None
            }
        elif intent == 'question':
            response = {
                'message': "That's a good question! Let me help you with that. " +
                          "Could you provide a bit more detail about what you'd like to know?",
                'next_stage': None
            }
        else:
            response = {
                'message': "Thank you for sharing that information. " +
                          "Your insights help me better understand your health journey. " +
                          "Is there anything else you'd like to add?",
                'next_stage': None
            }
        
        return response

