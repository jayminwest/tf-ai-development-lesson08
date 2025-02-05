"""Configuration management for the Wikipedia Article Summarizer"""
from pathlib import Path
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Wikipedia API settings
    WIKI_USER_AGENT: str = os.getenv('WIKI_USER_AGENT', 'WikiSummarizer/1.0')
    WIKI_RATE_LIMIT_CALLS: int = int(os.getenv('WIKI_RATE_LIMIT_CALLS', '10'))
    WIKI_RATE_LIMIT_PERIOD: int = int(os.getenv('WIKI_RATE_LIMIT_PERIOD', '60'))
    
    # Flask settings
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def as_dict(cls) -> Dict[str, Any]:
        """Return configuration as dictionary"""
        return {
            key: value for key, value in cls.__dict__.items() 
            if not key.startswith('_')
        }

config = Config()
