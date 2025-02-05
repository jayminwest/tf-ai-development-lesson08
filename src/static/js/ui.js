/**
 * UI controller for Wikipedia Article Summarizer
 */
import { fetchArticle, getSummary } from './api.js';

// DOM Elements
const articleForm = document.getElementById('articleForm');
const articleContent = document.getElementById('articleContent');
const summaryContent = document.getElementById('summaryContent');
const errorAlert = document.getElementById('errorAlert');
const loadingSpinner = document.getElementById('loadingSpinner');
const summarizeBtn = document.getElementById('summarizeBtn');

/**
 * Show error message
 * @param {string} message - Error message to display
 */
function showError(message) {
    errorAlert.textContent = message;
    errorAlert.classList.remove('d-none');
    setTimeout(() => {
        errorAlert.classList.add('d-none');
    }, 5000);
}

/**
 * Toggle loading spinner
 * @param {boolean} show - Whether to show or hide spinner
 */
function toggleLoading(show) {
    if (show) {
        loadingSpinner.classList.remove('d-none');
    } else {
        loadingSpinner.classList.add('d-none');
    }
}

/**
 * Display article content
 * @param {Object} article - Article data
 */
function displayArticle(article) {
    document.getElementById('articleTitle').textContent = article.title;
    document.getElementById('articleText').textContent = article.content;
    articleContent.classList.remove('d-none');
}

/**
 * Display summary content
 * @param {Object} summary - Summary data
 */
function displaySummary(summary) {
    document.getElementById('summaryText').textContent = summary.summary;
    summaryContent.classList.remove('d-none');
}

// Event Listeners
articleForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const title = document.getElementById('articleTitle').value;
    
    try {
        toggleLoading(true);
        const article = await fetchArticle(title);
        displayArticle(article);
    } catch (error) {
        showError(error.message);
    } finally {
        toggleLoading(false);
    }
});

summarizeBtn.addEventListener('click', async () => {
    const text = document.getElementById('articleText').textContent;
    
    try {
        toggleLoading(true);
        const summary = await getSummary(text);
        displaySummary(summary);
    } catch (error) {
        showError(error.message);
    } finally {
        toggleLoading(false);
    }
});
