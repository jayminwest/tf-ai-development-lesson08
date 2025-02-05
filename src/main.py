"""Main Flask application for Wikipedia Article Summarizer"""
from flask import Flask, jsonify, render_template, request, Response
from utils import init_nltk, get_wiki_article, BasicSummarizer
import asyncio
from functools import wraps
from typing import Union, Dict, Any, Callable
from config import config

app = Flask(__name__)
app.debug = config.FLASK_DEBUG

# Initialize NLTK components and summarizer
init_nltk()
summarizer = BasicSummarizer()

def async_route(f: Callable) -> Callable:
    """Decorator to handle async routes
    
    Args:
        f: Async function to wrap
        
    Returns:
        Wrapped function that runs in asyncio event loop
    """
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))
    return wrapper

def handle_errors(f: Callable) -> Callable:
    """Error handling middleware
    
    Args:
        f: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Response:
        try:
            return f(*args, **kwargs)
        except Exception as e:
            app.logger.error(f"Error in {f.__name__}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    return wrapper

@app.route('/')
@handle_errors
def home() -> str:
    """Render the main page
    
    Returns:
        str: Rendered HTML template
    """
    return render_template('index.html')

@app.route('/api/fetch-article', methods=['POST'])
@handle_errors
@async_route
async def fetch_article() -> tuple[Response, int]:
    """API endpoint to fetch Wikipedia article
    
    Returns:
        tuple: JSON response with article data and HTTP status code
        
    Raises:
        ValueError: If title is missing
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
        
    article_title = data.get('title')
    if not article_title:
        return jsonify({"error": "No title provided"}), 400
    
    article_data = await get_wiki_article(article_title)
    if "error" in article_data:
        return jsonify(article_data), 404
        
    return jsonify(article_data), 200

@app.route('/api/summarize', methods=['POST'])
@handle_errors
def summarize() -> tuple[Response, int]:
    """API endpoint to summarize text
    
    Returns:
        tuple: JSON response with summary and HTTP status code
        
    Raises:
        ValueError: If text is missing
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
        
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        summary = summarizer.summarize(text)
        return jsonify({"summary": summary}), 200
    except Exception as e:
        app.logger.error(f"Summarization error: {str(e)}")
        return jsonify({"error": "Summarization failed"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
