"""
Configuration module for TalentScout Hiring Assistant.
Handles environment variables and application settings.
Supports multiple LLM providers: OpenAI, Google Gemini, and Groq.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration settings."""
    
    # Supported LLM Providers
    SUPPORTED_PROVIDERS = ["openai", "gemini", "groq"]
    
    # API Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Default provider (can be changed by user in UI)
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "groq")
    
    # Model Configuration per provider
    MODELS = {
        "openai": {
            "default": "gpt-4o-mini",
            "options": ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "gemini": {
            "default": "gemini-1.5-flash",
            "options": ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        },
        "groq": {
            "default": "llama-3.3-70b-versatile",
            "options": ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
        }
    }
    
    # Conversation Settings
    MAX_HISTORY_LENGTH: int = 50  # Maximum messages to keep in context
    
    # Exit keywords that trigger conversation end
    EXIT_KEYWORDS: list = [
        "bye", "goodbye", "exit", "quit", "end", "stop",
        "thank you", "thanks", "done", "finish", "end conversation"
    ]
    
    # Required candidate information fields
    REQUIRED_FIELDS: list = [
        "full_name",
        "email",
        "phone",
        "years_of_experience",
        "desired_positions",
        "current_location",
        "tech_stack"
    ]
    
    # Application Info
    APP_NAME: str = "TalentScout Hiring Assistant"
    APP_VERSION: str = "1.0.0"
    
    @classmethod
    def get_api_key(cls, provider: str) -> str:
        """Get API key for the specified provider."""
        keys = {
            "openai": cls.OPENAI_API_KEY,
            "gemini": cls.GEMINI_API_KEY,
            "groq": cls.GROQ_API_KEY
        }
        return keys.get(provider, "")
    
    @classmethod
    def is_provider_configured(cls, provider: str) -> bool:
        """Check if a specific provider's API key is configured."""
        key = cls.get_api_key(provider)
        return bool(key and key not in ["your_openai_api_key_here", 
                                         "your_gemini_api_key_here", 
                                         "your_groq_api_key_here"])
    
    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Get the default model for a provider."""
        return cls.MODELS.get(provider, {}).get("default", "")
    
    @classmethod
    def get_model_options(cls, provider: str) -> list:
        """Get available model options for a provider."""
        return cls.MODELS.get(provider, {}).get("options", [])
