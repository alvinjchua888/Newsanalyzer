"""
Utilities Module

This module provides utility functions for data export, text formatting,
validation, and helper operations used throughout the AI News Analyzer application.

The utilities are designed to be stateless and reusable, providing common
functionality for CSV export, date formatting, text cleaning, and validation.

Author: AI News Analyzer Team
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any
import re

def export_to_csv(articles: List[Dict[str, Any]]) -> str:
    """
    Export analyzed articles to CSV format for download or external analysis.
    
    This function converts a list of analyzed articles into a CSV string
    suitable for download or import into spreadsheet applications and
    data analysis tools.
    
    Args:
        articles (List[Dict[str, Any]]): List of article dictionaries with analysis results
        
    Returns:
        str: CSV data as string, empty string if no articles provided
        
    CSV Structure:
        - Title: Article headline
        - Source: News source name
        - Published Date: Formatted publication date
        - Author: Article author
        - URL: Article URL
        - Sentiment: AI sentiment classification
        - Confidence Score: Sentiment confidence (0.0-1.0)
        - Market Impact: Impact level assessment
        - Summary: AI-generated summary
        - Key Insights: Semicolon-separated insights
        - Content Length: Character count of original content
        
    Note:
        - Text is cleaned for CSV compatibility (quotes escaped, etc.)
        - Dates are formatted for readability
        - Key insights are joined with semicolons for single-cell storage
        
    Example:
        >>> csv_data = export_to_csv(analyzed_articles)
        >>> with open('analysis.csv', 'w') as f:
        ...     f.write(csv_data)
    """
    if not articles:
        return ""
    
    output = io.StringIO()
    
    # Define CSV headers with comprehensive analysis data
    headers = [
        'Title', 'Source', 'Published Date', 'Author', 'URL',
        'Sentiment', 'Confidence Score', 'Market Impact',
        'Summary', 'Key Insights', 'Content Length'
    ]
    
    writer = csv.writer(output)
    writer.writerow(headers)
    
    # Write article data rows
    for article in articles:
        row = [
            article.get('title', ''),
            article.get('source', ''),
            format_date(article.get('published_date', '')),
            article.get('author', ''),
            article.get('url', ''),
            article.get('sentiment', ''),
            article.get('confidence_score', 0),
            article.get('market_impact', ''),
            clean_text_for_csv(article.get('summary', '')),
            '; '.join(article.get('key_insights', [])),  # Join insights for single cell
            len(article.get('content', ''))
        ]
        writer.writerow(row)
    
    return output.getvalue()

def format_date(date_str: str) -> str:
    """
    Format date strings for consistent and readable display.
    
    This function handles various date formats from different news sources
    and converts them to a standardized, human-readable format.
    
    Args:
        date_str (str): Date string in various possible formats
        
    Returns:
        str: Formatted date string (YYYY-MM-DD HH:MM) or "Unknown" if parsing fails
        
    Supported Input Formats:
        - ISO format: 2024-01-01T12:00:00Z
        - ISO with timezone: 2024-01-01T12:00:00+00:00
        - Date only: 2024-01-01
        
    Output Format:
        - Standard: YYYY-MM-DD HH:MM (2024-01-01 12:00)
        - Date only if no time available
        
    Note:
        - Handles timezone information by removing it for simplicity
        - Falls back to original string representation if all parsing fails
        - Returns "Unknown" for empty or None input
    """
    if not date_str:
        return "Unknown"
    
    try:
        # Handle ISO format dates with timezone information
        if 'T' in date_str:
            # Remove timezone and parse as ISO format
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Try parsing as date only
            date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
        
        return date_obj.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        # Return original string if parsing fails
        return str(date_str)

def clean_text(text: str) -> str:
    """
    Clean text content by removing extra whitespace and problematic characters.
    
    This function standardizes text content by normalizing whitespace,
    removing URLs and email addresses, and cleaning up formatting issues
    common in web-scraped content.
    
    Args:
        text (str): Raw text content to clean
        
    Returns:
        str: Cleaned text content, empty string if input is None/empty
        
    Cleaning Operations:
        - Normalize whitespace (multiple spaces -> single space)
        - Convert line breaks to spaces
        - Remove URLs (http/https links)
        - Remove email addresses
        - Strip leading/trailing whitespace
        
    Note:
        - Preserves text meaning while improving readability
        - Safe for use in CSV exports and display
        - Does not remove punctuation or alter sentence structure
        
    Example:
        >>> text = "This is   a\\n\\ntest with   http://example.com"
        >>> clean_text(text)
        'This is a test with'
    """
    if not text:
        return ""
    
    # Remove extra whitespace and normalize spacing
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Convert line breaks to spaces for single-line display
    cleaned = cleaned.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    
    # Remove URLs to clean up content
    cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
    
    # Remove email addresses for privacy/cleanliness
    cleaned = re.sub(r'\S+@\S+', '', cleaned)
    
    return cleaned.strip()

def clean_text_for_csv(text: str) -> str:
    """
    Clean text specifically for CSV export compatibility.
    
    This function extends the basic text cleaning with additional
    CSV-specific formatting to ensure proper parsing in spreadsheet
    applications.
    
    Args:
        text (str): Text content to clean for CSV
        
    Returns:
        str: CSV-safe text content
        
    CSV-Specific Operations:
        - Applies all standard text cleaning
        - Escapes double quotes by doubling them ("" for ")
        - Ensures proper CSV field formatting
        
    Note:
        - Essential for preventing CSV parsing errors
        - Maintains text integrity while ensuring compatibility
        - Used specifically in export_to_csv function
        
    Example:
        >>> text = 'This "quote" needs escaping'
        >>> clean_text_for_csv(text)
        'This ""quote"" needs escaping'
    """
    if not text:
        return ""
    
    # Apply standard text cleaning first
    cleaned = clean_text(text)
    
    # Escape quotes for CSV compatibility (double quotes become double-double quotes)
    cleaned = cleaned.replace('"', '""')
    
    return cleaned

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis for display purposes.
    
    This function shortens long text content for display in UIs or summaries
    while indicating that content has been truncated.
    
    Args:
        text (str): Text content to truncate
        max_length (int, optional): Maximum character length. Defaults to 100.
        
    Returns:
        str: Truncated text with "..." if shortened, original text if within limit
        
    Behavior:
        - Returns empty string for None/empty input
        - Returns original text if shorter than or equal to max_length
        - Adds "..." to truncated text (counted in max_length)
        - Truncates at max_length-3 to accommodate ellipsis
        
    Note:
        - Useful for UI display where space is limited
        - Preserves text readability with clear truncation indication
        - Does not attempt to truncate at word boundaries
        
    Example:
        >>> long_text = "This is a very long article title that needs shortening"
        >>> truncate_text(long_text, 30)
        'This is a very long arti...'
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes for given text content.
    
    This function provides reading time estimates to help users understand
    the time investment required for reading articles.
    
    Args:
        text (str): Text content to analyze
        words_per_minute (int, optional): Average reading speed. Defaults to 200.
        
    Returns:
        int: Estimated reading time in minutes (minimum 1 minute)
        
    Calculation Method:
        - Splits text into words using whitespace
        - Divides word count by reading speed
        - Rounds up to minimum of 1 minute
        
    Default Reading Speed:
        - 200 WPM: Average adult reading speed for general content
        - Adjust based on content complexity or target audience
        
    Note:
        - Returns 0 for empty text
        - Always returns at least 1 minute for non-empty content
        - Reading speed can be adjusted for different audiences
        
    Example:
        >>> article_text = "This is a sample article with many words..."
        >>> reading_time = calculate_reading_time(article_text)
        >>> print(f"Estimated reading time: {reading_time} minutes")
    """
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = max(1, word_count // words_per_minute)
    
    return reading_time

def extract_php_mentions(text: str) -> List[str]:
    """
    Extract specific mentions of Philippine peso from text content.
    
    This function identifies and extracts currency-related mentions
    specifically for Philippine peso analysis, useful for financial
    news analysis.
    
    Args:
        text (str): Text content to search for peso mentions
        
    Returns:
        List[str]: Unique peso-related mentions found in text
        
    Search Patterns:
        - PHP [amount]: PHP 50.25, PHP 1,234.56
        - peso [amount]: peso 45.30
        - ₱ [amount]: ₱50.25
        - [amount] per dollar: 55.50 per dollar
        - [amount] to the dollar: 55.50 to the dollar
        
    Note:
        - Case-insensitive matching
        - Returns unique mentions (duplicates removed)
        - Handles common currency formatting (commas, decimals)
        - Specific to Philippine peso use case
        - Empty list for no matches or empty input
        
    Example:
        >>> text = "The PHP 55.50 per dollar rate shows peso weakening"
        >>> mentions = extract_php_mentions(text)
        >>> print(mentions)  # ['php 55.50', '55.50 per dollar']
    """
    if not text:
        return []
    
    # Patterns to look for PHP/peso mentions with amounts
    patterns = [
        r'PHP\s*[0-9,.]+',      # PHP 50.25, PHP 1,234
        r'peso\s*[0-9,.]+',     # peso 50.25
        r'₱\s*[0-9,.]+',        # ₱50.25
        r'[0-9,.]+\s*per\s*dollar',    # 55.50 per dollar
        r'[0-9,.]+\s*to\s*the\s*dollar'  # 55.50 to the dollar
    ]
    
    mentions = []
    text_lower = text.lower()
    
    # Search for all patterns and collect matches
    for pattern in patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        mentions.extend(matches)
    
    return list(set(mentions))  # Remove duplicates and return

def validate_article_data(article: Dict[str, Any]) -> bool:
    """
    Validate that article data contains required fields and meets quality standards.
    
    This function ensures article data is complete and suitable for analysis
    by checking for required fields and minimum content quality.
    
    Args:
        article (Dict[str, Any]): Article dictionary to validate
        
    Returns:
        bool: True if article meets validation criteria, False otherwise
        
    Validation Criteria:
        Required Fields:
        - title: Article must have a headline
        - content: Article must have text content  
        - source: Article must have source attribution
        
        Quality Standards:
        - Content length >= 100 characters (minimum for meaningful analysis)
        
    Note:
        - Used to filter out incomplete or low-quality articles
        - Helps ensure consistent data quality for analysis
        - Can be extended with additional validation rules as needed
        
    Example:
        >>> article = {'title': 'News Title', 'content': 'Article content...', 'source': 'BBC'}
        >>> is_valid = validate_article_data(article)
        >>> if is_valid:
        ...     # Process article
    """
    required_fields = ['title', 'content', 'source']
    
    # Check for required fields
    for field in required_fields:
        if not article.get(field):
            return False
    
    # Additional validation: minimum content length for meaningful analysis
    if len(article.get('content', '')) < 100:
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations across different operating systems.
    
    This function cleans up filenames to ensure they are safe for use
    on various file systems and don't contain problematic characters.
    
    Args:
        filename (str): Original filename to sanitize
        
    Returns:
        str: Sanitized filename safe for file operations
        
    Sanitization Operations:
        - Replace invalid characters (<>:"/\\|?*) with underscores
        - Collapse multiple consecutive dots to single dot
        - Replace multiple spaces with single underscore
        - Limit length to 200 characters
        - Remove leading/trailing dots
        
    Note:
        - Safe for Windows, macOS, and Linux file systems
        - Preserves file extension and general structure
        - Prevents file system errors and security issues
        
    Example:
        >>> filename = 'Article: "Breaking News" | Important?.txt'
        >>> safe_name = sanitize_filename(filename)
        >>> print(safe_name)  # 'Article__Breaking_News___Important_.txt'
    """
    # Remove or replace invalid characters for file systems
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove extra spaces and dots that can cause issues
    sanitized = re.sub(r'\.+', '.', sanitized)  # Multiple dots -> single dot
    sanitized = re.sub(r'\s+', '_', sanitized)   # Spaces -> underscores
    
    # Limit length to prevent file system issues
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    # Remove leading/trailing dots which can be problematic
    return sanitized.strip('.')

def get_sentiment_emoji(sentiment: str) -> str:
    """
    Get emoji representation of sentiment for visual display.
    
    This function provides intuitive visual indicators for sentiment
    classifications, useful in user interfaces and reports.
    
    Args:
        sentiment (str): Sentiment classification string
        
    Returns:
        str: Corresponding emoji character
        
    Emoji Mapping:
        - positive: 📈 (upward trend)
        - negative: 📉 (downward trend)  
        - neutral: ➡️ (sideways arrow)
        - unknown: ❓ (question mark)
        - default: ❓ (for unrecognized sentiments)
        
    Note:
        - Case-insensitive matching
        - Provides consistent visual representation
        - Falls back to question mark for unknown values
        
    Example:
        >>> emoji = get_sentiment_emoji("positive")
        >>> print(f"Sentiment: {emoji}")  # Sentiment: 📈
    """
    emoji_map = {
        'positive': '📈',   # Upward trending chart
        'negative': '📉',   # Downward trending chart  
        'neutral': '➡️',    # Right arrow for neutral/sideways
        'unknown': '❓'     # Question mark for unknown
    }
    
    return emoji_map.get(sentiment.lower(), '❓')

def format_confidence_score(score: float) -> str:
    """
    Format confidence score as a readable percentage string.
    
    This function converts numerical confidence scores (0.0-1.0)
    to human-readable percentage format for display purposes.
    
    Args:
        score (float): Confidence score between 0.0 and 1.0
        
    Returns:
        str: Formatted percentage string with one decimal place
        
    Formatting:
        - Converts 0.0-1.0 to 0.0%-100.0%
        - One decimal place precision
        - Returns "N/A" for None values
        - Handles edge cases gracefully
        
    Note:
        - Assumes input is in 0.0-1.0 range
        - Provides consistent formatting across the application
        - Safe for display in various contexts
        
    Example:
        >>> score = 0.856
        >>> formatted = format_confidence_score(score)
        >>> print(formatted)  # "85.6%"
    """
    if score is None:
        return "N/A"
    
    return f"{score * 100:.1f}%"
