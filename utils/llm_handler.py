"""
LLM Handler for TalentScout Hiring Assistant.
Manages conversation with multiple LLM providers: OpenAI, Google Gemini, and Groq.
"""

from typing import Optional, Tuple
import re
import sys

from config import Config
from .prompts import SYSTEM_PROMPT, get_technical_questions_prompt, get_fallback_prompt, get_closing_prompt


class LLMHandler:
    """
    Handles all interactions with LLM providers.
    Supports OpenAI, Google Gemini, and Groq.
    Manages conversation context and generates appropriate responses.
    """
    
    def __init__(self, api_key: str = None, provider: str = "groq", model: str = None):
        """
        Initialize the LLM handler with the specified provider configuration.
        
        Args:
            api_key: API key for the provider. If not provided, falls back to Config.
            provider: LLM provider to use ('openai', 'gemini', 'groq')
            model: Specific model to use. If not provided, uses default for the provider.
        """
        self.provider = provider.lower()
        self.api_key = api_key or Config.get_api_key(self.provider)
        self.is_configured = bool(self.api_key and self.api_key not in [
            "your_openai_api_key_here",
            "your_gemini_api_key_here", 
            "your_groq_api_key_here"
        ])
        self.client = None
        self.model_name = model or Config.get_default_model(self.provider)
        self.conversation_history = []
        
        if self.is_configured:
            self._initialize_client()
    
    def _initialize_client(self):
        """Configure and initialize the LLM client based on provider."""
        try:
            if self.provider == "openai":
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
                
            elif self.provider == "gemini":
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(
                    model_name=self.model_name,
                    system_instruction=SYSTEM_PROMPT
                )
                
            elif self.provider == "groq":
                from groq import Groq
                self.client = Groq(api_key=self.api_key)
                
            else:
                raise ValueError(f"Unsupported provider: {self.provider}")
            
            # Initialize conversation with system prompt (for non-Gemini providers)
            if self.provider != "gemini":
                self.conversation_history = [
                    {"role": "system", "content": SYSTEM_PROMPT}
                ]
            else:
                # Gemini uses chat sessions
                self.conversation_history = []
                
        except ImportError as e:
            print(f"Error importing {self.provider} library: {e}", file=sys.stderr, flush=True)
            self.is_configured = False
        except Exception as e:
            print(f"Error initializing {self.provider} client: {e}", file=sys.stderr, flush=True)
            self.is_configured = False
    
    def start_conversation(self) -> str:
        """
        Start a new conversation and return the initial greeting.
        
        Returns:
            Initial greeting message from the assistant
        """
        if not self.is_configured:
            return self._get_api_key_error_message()
        
        # Reset conversation history
        if self.provider != "gemini":
            self.conversation_history = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]
        else:
            self.conversation_history = []
        
        # Generate initial greeting
        try:
            initial_prompt = """Start the conversation by greeting the candidate and introducing yourself as TalentScout's AI Hiring Assistant. 
Briefly explain the screening process, then ask for ALL of the following information in ONE message:
- Full name
- Email address
- Phone number
- Years of experience in tech
- Desired position(s)
- Current location
- Tech stack (programming languages, frameworks, databases, tools they work with)

Make it friendly and professional. Format it clearly so they know what information to provide."""
            
            if self.provider == "openai":
                return self._get_openai_response(initial_prompt)
            elif self.provider == "gemini":
                return self._get_gemini_response(initial_prompt)
            elif self.provider == "groq":
                return self._get_groq_response(initial_prompt)
                
        except Exception as e:
            print(f"Error in start_conversation: {str(e)}", file=sys.stderr, flush=True)
            return self._get_fallback_greeting()
    
    def _get_openai_response(self, user_message: str) -> str:
        """Get response from OpenAI API."""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.conversation_history,
            temperature=0.7,
            max_tokens=1024
        )
        
        assistant_message = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def _get_gemini_response(self, user_message: str) -> str:
        """Get response from Google Gemini API."""
        # Convert history to Gemini format and start chat
        gemini_history = []
        for msg in self.conversation_history:
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [msg["content"]]})
        
        chat = self.client.start_chat(history=gemini_history)
        response = chat.send_message(user_message)
        
        # Store in our format for context
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response.text})
        
        return response.text
    
    def _get_groq_response(self, user_message: str) -> str:
        """Get response from Groq API."""
        self.conversation_history.append({"role": "user", "content": user_message})
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.conversation_history,
            temperature=0.7,
            max_tokens=1024
        )
        
        assistant_message = response.choices[0].message.content
        self.conversation_history.append({"role": "assistant", "content": assistant_message})
        
        return assistant_message
    
    def _get_fallback_greeting(self) -> str:
        """Return a fallback greeting when API fails."""
        return (
            "👋 Hello! I'm TalentScout's AI Hiring Assistant. I'll be conducting your initial screening today.\n\n"
            "To get started, please provide the following information:\n\n"
            "1. **Full Name**\n"
            "2. **Email Address**\n"
            "3. **Phone Number**\n"
            "4. **Years of Experience** in tech\n"
            "5. **Desired Position(s)** you're applying for\n"
            "6. **Current Location**\n"
            "7. **Tech Stack** (programming languages, frameworks, databases, tools)\n\n"
            "Feel free to share all the details in your response!"
        )
    
    def send_message(self, user_message: str, candidate_info: dict = None) -> Tuple[str, bool]:
        """
        Send a message to the LLM and get a response.
        
        Args:
            user_message: The candidate's message
            candidate_info: Current collected candidate information
        
        Returns:
            Tuple of (response_text, is_conversation_ended)
        """
        if not self.is_configured:
            return self._get_api_key_error_message(), False
        
        if not self.conversation_history:
            # Start conversation if not already started
            self.start_conversation()
        
        # Check for exit keywords
        if self._check_exit_keywords(user_message):
            candidate_name = candidate_info.get("full_name", "there") if candidate_info else "there"
            return get_closing_prompt(candidate_name), True
        
        # Check which fields are still missing
        missing_fields = []
        if candidate_info:
            for field in Config.REQUIRED_FIELDS:
                if not candidate_info.get(field):
                    missing_fields.append(field.replace('_', ' ').title())
        
        try:
            # Build context-aware message
            context_message = self._build_context_message(user_message, candidate_info)
            
            if self.provider == "openai":
                response = self._get_openai_response(context_message)
            elif self.provider == "gemini":
                response = self._get_gemini_response(context_message)
            elif self.provider == "groq":
                response = self._get_groq_response(context_message)
            else:
                response = "Unsupported provider"
            
            # Update technical question counter
            if candidate_info.get("_technical_questions_started"):
                # Initialize matching app.py logic
                if "_tech_question_count" not in candidate_info:
                    candidate_info["_tech_question_count"] = 1
                else:
                    candidate_info["_tech_question_count"] += 1
            
            # CODE-LEVEL ENFORCEMENT: Detect premature closing and override
            if self._is_closing_message(response):
                if missing_fields:
                    # LLM tried to end conversation prematurely - ask for missing fields
                    next_field = missing_fields[0]
                    response = self._get_next_question_for_field(next_field, candidate_info)
                elif not candidate_info.get("_technical_questions_started"):
                    # All info collected but no technical questions asked yet - start them
                    tech_stack = candidate_info.get("tech_stack", "")
                    if tech_stack:
                        response = self._generate_first_technical_question(tech_stack, candidate_info)
                        candidate_info["_technical_questions_started"] = True
                        candidate_info["_tech_question_count"] = 1
                elif candidate_info.get("_tech_question_count", 0) < 3:
                     # Tech questions started but not enough asked (min 3)
                     current_count = candidate_info.get("_tech_question_count", 1)
                     tech_stack = candidate_info.get("tech_stack", "")
                     response = self._generate_next_technical_question(current_count + 1, tech_stack)
            
            return response, False
            
        except Exception as e:
            error_details = str(e)
            print(f"Error in send_message: {error_details}", file=sys.stderr, flush=True)
            return f"⚠️ Error communicating with AI: {error_details}", False
    
    def _is_closing_message(self, response: str) -> bool:
        """Check if the response is a closing/goodbye message."""
        response_lower = response.lower()
        closing_indicators = [
            "thank you so much for taking the time",
            "thank you for taking the time",
            "good luck with your application",
            "best of luck with your application",
            "we appreciate your interest",
            "here's what happens next",
            "our recruitment team will review",
            "have a great day",
            "screening is complete",
            "all the information needed"
        ]
        return any(indicator in response_lower for indicator in closing_indicators)
    
    def _get_next_question_for_field(self, field_name: str, candidate_info: dict) -> str:
        """Generate a question for missing fields or start technical questions."""
        candidate_name = candidate_info.get("full_name", "") if candidate_info else ""
        
        # Count how many fields are still missing
        missing_count = 0
        if candidate_info:
            for field in Config.REQUIRED_FIELDS:
                if not candidate_info.get(field):
                    missing_count += 1
        
        # If multiple fields are missing, ask for all remaining info
        if missing_count > 1:
            return (
                f"Thanks{', ' + candidate_name if candidate_name else ''}! I still need a few more details. "
                f"Could you please provide the following:\n\n"
                + "\n".join([f"- {field.replace('_', ' ').title()}" for field in Config.REQUIRED_FIELDS if not candidate_info.get(field)])
            )
        
        # If only one field missing, ask specifically for it
        field_questions = {
            "Full Name": "Could you please tell me your full name?",
            "Email": f"Thanks{', ' + candidate_name if candidate_name else ''}! Could you please share your email address?",
            "Phone": f"What's the best phone number to reach you?",
            "Years Of Experience": f"How many years of experience do you have in the tech industry?",
            "Desired Positions": f"What position(s) are you interested in applying for?",
            "Current Location": f"Where are you currently located?",
            "Tech Stack": f"Could you tell me about your tech stack? (programming languages, frameworks, databases, and tools)"
        }
        return field_questions.get(field_name, f"Could you please provide your {field_name.lower()}?")
    
    def _generate_first_technical_question(self, tech_stack: str, candidate_info: dict) -> str:
        """Generate the first technical question based on the candidate's tech stack."""
        candidate_name = candidate_info.get("full_name", "")
        name_greeting = f"{candidate_name}, " if candidate_name else ""
        
        # Parse tech stack to get the first technology
        techs = [t.strip() for t in tech_stack.split(',')]
        first_tech = techs[0] if techs else "your primary technology"
        
        return (
            f"Thank you for sharing your details{', ' + candidate_name if candidate_name else ''}! "
            f"I can see you have experience with {tech_stack}. Let's do a quick technical assessment.\n\n"
            f"**Question 1 (Basic):** Can you explain what {first_tech} is and what it's primarily used for?"
        )
    
    def _generate_next_technical_question(self, count: int, tech_stack: str) -> str:
        """Generate the next technical question based on count and tech stack."""
        techs = [t.strip() for t in tech_stack.split(',')]
        # Rotate through techs or stick to primary
        
        question_types = {
            2: "Intermediate",
            3: "Advanced",
            4: "Scenario-based",
            5: "Optimization"
        }
        level = question_types.get(count, "Follow-up")
        
        return (
            f"Thanks for that explanation! Let's move to the next question.\n\n"
            f"**Question {count} ({level}):** Please describe a challenging situation you encountered when working with {tech_stack.split(',')[0]}, and how you resolved it."
        )
    
    def _build_context_message(self, user_message: str, candidate_info: dict = None) -> str:
        """
        Build a context-aware message including current candidate state.
        
        Args:
            user_message: The candidate's message
            candidate_info: Current collected candidate information
        
        Returns:
            Context-enhanced message string
        """
        context = f"Candidate's message: {user_message}\n\n"
        
        if candidate_info:
            # Add context about what we already know
            collected = []
            missing = []
            
            for field in Config.REQUIRED_FIELDS:
                if candidate_info.get(field):
                    collected.append(f"- {field.replace('_', ' ').title()}: {candidate_info[field]}")
                else:
                    missing.append(field.replace('_', ' ').title())
            
            if collected:
                context += "Information already collected:\n" + "\n".join(collected) + "\n\n"
            
            if missing:
                context += f"⚠️ STILL NEED TO COLLECT (DO NOT END CONVERSATION): {', '.join(missing)}\n"
                context += "You MUST ask for the next missing piece of information. Do NOT skip any fields.\n\n"
            
            # If ALL info collected and tech stack is provided, prompt for technical questions
            if not missing and candidate_info.get("tech_stack"):
                if not candidate_info.get("_technical_questions_started"):
                    years = candidate_info.get("years_of_experience", 0)
                    try:
                        years = int(years)
                    except (ValueError, TypeError):
                        years = 0
                    
                    tech_stack = candidate_info["tech_stack"]
                    if isinstance(tech_stack, str):
                        tech_stack = [t.strip() for t in tech_stack.split(",")]
                    
                    context += "✅ All basic information collected! Now you MUST ask technical questions.\n"
                    context += get_technical_questions_prompt(tech_stack, years)
            elif candidate_info.get("tech_stack") and missing:
                # Tech stack provided but other fields missing - continue collecting first
                context += "Note: Tech stack is provided but other required information is still missing. "
                context += "Continue collecting the missing information before asking technical questions.\n\n"
        
        context += "\nRespond appropriately to continue the screening process. Ask for the NEXT missing piece of information."
        return context
    
    def _check_exit_keywords(self, message: str) -> bool:
        """
        Check if the message contains exit keywords.
        
        Args:
            message: User message to check
        
        Returns:
            True if exit keyword found, False otherwise
        """
        message_lower = message.lower().strip()
        
        for keyword in Config.EXIT_KEYWORDS:
            if keyword in message_lower:
                return True
        return False
    
    def _get_api_key_error_message(self) -> str:
        """Get error message when API key is not configured."""
        provider_links = {
            "openai": "[OpenAI Platform](https://platform.openai.com/api-keys)",
            "gemini": "[Google AI Studio](https://makersuite.google.com/app/apikey)",
            "groq": "[Groq Console](https://console.groq.com/keys)"
        }
        link = provider_links.get(self.provider, "the provider's website")
        
        return (
            f"⚠️ **API Key Not Configured**\n\n"
            f"To use this chatbot with {self.provider.upper()}, please enter your API key in the sidebar.\n\n"
            f"You can get an API key from {link}"
        )
    
    def _get_error_response(self, error: str) -> str:
        """Get a graceful error response."""
        return (
            "I apologize, but I encountered a brief technical issue. "
            "Could you please repeat your last response? "
            "I want to make sure I capture everything correctly."
        )
    
    def extract_candidate_info(self, message: str, current_info: dict) -> dict:
        """
        Extract candidate information from their message using pattern matching.
        Handles all-at-once format like: 'jane gw@kk.in 1234567896 2 frontend delhi react'
        
        Args:
            message: The candidate's message
            current_info: Current collected information
        
        Returns:
            Updated candidate information dictionary
        """
        updated_info = current_info.copy()
        
        # Clean up the message
        message_clean = message.strip()
        
        # Email extraction using regex
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        email_match = re.search(email_pattern, message_clean)
        if email_match and not updated_info.get("email"):
            updated_info["email"] = email_match.group()
            # Remove email from message for further processing
            message_clean = message_clean.replace(email_match.group(), ' ')
        
        # Phone extraction using regex (10+ digit numbers)
        phone_pattern = r'\b(\d{10,})\b'
        phone_match = re.search(phone_pattern, message_clean)
        if phone_match and not updated_info.get("phone"):
            updated_info["phone"] = phone_match.group(1)
            # Remove phone from message for further processing
            message_clean = message_clean.replace(phone_match.group(), ' ')
        
        # Years of experience extraction (matches < 50)
        exp_patterns = [
            r'\b(\d{1,2})\s*(?:\+)?\s*years?\b',
            r'\bexperience[:\s]+(\d{1,2})\b',
            r'\b(\d{1,2})\s*yrs?\b',
            r'\b(\d{1,2})\b'
        ]
        for pattern in exp_patterns:
            exp_match = re.search(pattern, message_clean.lower())
            if exp_match and not updated_info.get("years_of_experience"):
                years = exp_match.group(1)
                if int(years) <= 50:
                    updated_info["years_of_experience"] = years
                    # Remove from message
                    message_clean = re.sub(r'\b' + years + r'\b', ' ', message_clean, count=1)
                    break
        
        # Split remaining message into words
        words = message_clean.split()
        
        # Tech stack keywords (extended)
        tech_keywords = ['react', 'node', 'python', 'java', 'javascript', 'typescript', 'angular', 
                        'vue', 'django', 'flask', 'spring', 'docker', 'kubernetes', 'aws', 'sql',
                        'postgresql', 'mongodb', 'redis', 'frontend', 'backend', 'fullstack',
                        'developer', 'engineer', 'senior', 'junior', 'lead', 'manager',
                        'c++', 'c#', 'ruby', 'go', 'rust', 'swift', 'kotlin', 'php', 'html', 'css',
                        'git', 'linux', 'cloud', 'azure', 'gcp', 'devops', 'machine', 'learning']
                        
        # Location keywords (common cities/countries)
        location_keywords = ['delhi', 'mumbai', 'bangalore', 'bengaluru', 'hyderabad', 'chennai', 
                            'pune', 'kolkata', 'noida', 'gurgaon', 'gurugram', 'uk', 'usa', 'united states',
                            'india', 'london', 'new york', 'san francisco', 'california', 'texas',
                            'berlin', 'toronto', 'canada', 'australia', 'germany', 'remote',
                            'bangkok', 'singapore', 'dubai', 'paris', 'tokyo']
        
        name_words = []
        remaining_words = []
        found_location = None
        
        for i, word in enumerate(words):
            word_lower = word.lower().strip()
            # Skip empty or single char words
            if len(word_lower) < 2:
                continue
                
            # Check if it's a known location
            if word_lower in location_keywords or (i > 0 and (words[i-1].lower() + " " + word_lower) in location_keywords):
                if not updated_info.get("current_location"):
                    # Capitalize properly
                    updated_info["current_location"] = word.title()
                    continue
            
            # If it looks like a name (no digits, not a tech term, appears early)
            # And STRICTLY not in location_keywords
            if (not any(c.isdigit() for c in word) and 
                word_lower not in tech_keywords and
                word_lower not in location_keywords and
                len(name_words) < 3 and
                i < 4):
                name_words.append(word)
            else:
                remaining_words.append(word)
        
        if name_words and not updated_info.get("full_name"):
            updated_info["full_name"] = ' '.join(name_words).title()
            
        # If we found location during loop, good. If not, check remaining words
        if not updated_info.get("current_location"):
            # Try to identify city names in remaining words
            for word in remaining_words:
                if word.lower() in location_keywords:
                    updated_info["current_location"] = word.title()
                    break
        
        # From remaining words, try to identify position, location, tech stack
        # Position keywords
        position_keywords = ['frontend', 'backend', 'fullstack', 'full stack', 'devops', 'developer', 
                           'engineer', 'senior', 'junior', 'lead', 'manager', 'architect', 'qa', 
                           'tester', 'data', 'ml', 'ai', 'mobile', 'ios', 'android', 'web']
        
        # Check for position
        for word in remaining_words:
            if word.lower() in position_keywords and not updated_info.get("desired_positions"):
                # Find related position words
                pos_words = [w for w in remaining_words if w.lower() in position_keywords]
                updated_info["desired_positions"] = ' '.join(pos_words).title()
                break
        
        # Tech stack - common technologies
        tech_stack_keywords = ['react', 'node', 'nodejs', 'python', 'java', 'javascript', 'typescript',
                              'angular', 'vue', 'django', 'flask', 'spring', 'docker', 'kubernetes',
                              'aws', 'azure', 'gcp', 'sql', 'postgresql', 'mysql', 'mongodb', 'redis',
                              'graphql', 'rest', 'express', 'next', 'nextjs', 'nuxt', 'svelte',
                              'tailwind', 'css', 'html', 'go', 'golang', 'rust', 'c++', 'cpp', 'c#',
                              'ruby', 'rails', 'php', 'laravel', 'swift', 'kotlin', 'flutter', 'dart']
        
        tech_found = []
        for word in remaining_words:
            if word.lower() in tech_stack_keywords:
                tech_found.append(word.title())
        
        if tech_found and not updated_info.get("tech_stack"):
            updated_info["tech_stack"] = ', '.join(tech_found)
        
        # Location - try to identify city names (what's left after removing tech and position)
        location_candidates = [w for w in remaining_words 
                              if w.lower() not in tech_stack_keywords 
                              and w.lower() not in position_keywords
                              and len(w) > 2
                              and not any(c.isdigit() for c in w)]
        
        if location_candidates and not updated_info.get("current_location"):
            updated_info["current_location"] = ' '.join(location_candidates).title()
        
        return updated_info

