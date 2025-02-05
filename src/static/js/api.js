/**
 * API client for Wikipedia Article Summarizer
 */

/**
 * Fetch article from Wikipedia
 * @param {string} title - Article title
 * @returns {Promise<Object>} Article data
 */
export async function fetchArticle(title) {
    const response = await fetch('/api/fetch-article', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title }),
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to fetch article');
    }
    
    return response.json();
}

/**
 * Get summary of text
 * @param {string} text - Text to summarize
 * @returns {Promise<Object>} Summary data
 */
export async function getSummary(text) {
    const response = await fetch('/api/summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
    });
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Failed to generate summary');
    }
    
    return response.json();
}
