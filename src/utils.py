"""Utility functions for text processing and Wikipedia API interactions"""
from abc import ABC, abstractmethod
import aiohttp
import asyncio
import wikipediaapi
import nltk
from nltk.tokenize import sent_tokenize
from typing import Dict, List, Optional
import time
from functools import wraps

from config import config

# Rate limiting settings
RATE_LIMIT_CALLS = config.WIKI_RATE_LIMIT_CALLS
RATE_LIMIT_PERIOD = config.WIKI_RATE_LIMIT_PERIOD
_last_calls: List[float] = []

def rate_limit():
    """Rate limiting decorator"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            now = time.time()
            _last_calls[:] = [t for t in _last_calls if now - t < RATE_LIMIT_PERIOD]
            
            if len(_last_calls) >= RATE_LIMIT_CALLS:
                sleep_time = _last_calls[0] + RATE_LIMIT_PERIOD - now
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
            
            _last_calls.append(now)
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def init_nltk():
    """Initialize NLTK by downloading required packages"""
    nltk.download('punkt')

class BaseSummarizer(ABC):
    """Abstract base class for text summarization algorithms"""
    
    @abstractmethod
    def summarize(self, text: str, **kwargs) -> str:
        """Generate a summary of the input text
        
        Args:
            text: The text to summarize
            **kwargs: Additional algorithm-specific parameters
            
        Returns:
            str: The generated summary
        """
        pass

class BasicSummarizer(BaseSummarizer):
    """Simple extractive summarizer that returns first n sentences"""
    
    def summarize(self, text: str, num_sentences: int = 3) -> str:
        """Create a basic summary by extracting first few sentences
        
        Args:
            text: Text to summarize
            num_sentences: Number of sentences to include in summary
            
        Returns:
            str: Concatenated first n sentences
        """
        sentences = sent_tokenize(text)
        return " ".join(sentences[:num_sentences])

@rate_limit()
async def get_wiki_article(title: str) -> Dict[str, str]:
    """Fetch Wikipedia article content using Wikipedia-API asynchronously
    
    Args:
        title: The title of the Wikipedia article to fetch
        
    Returns:
        Dict containing article title, content, and URL or error message
        
    Raises:
        aiohttp.ClientError: If there's an error fetching the article
    """
    try:
        wiki = wikipediaapi.Wikipedia(
            config.WIKI_USER_AGENT,
            'en'
        )
        page = wiki.page(title)
        
        if not page.exists():
            return {"error": "Article not found"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(page.fullurl) as response:
                if response.status != 200:
                    return {"error": f"Failed to fetch article: HTTP {response.status}"}
                
                return {
                    "title": page.title,
                    "content": page.text,
                    "url": page.fullurl
                }
    except aiohttp.ClientError as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
