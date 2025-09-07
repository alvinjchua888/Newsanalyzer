import csv
import io
from datetime import datetime
from typing import List, Dict, Any
import re

def export_to_csv(articles: List[Dict[str, Any]]) -> str:
    """
    Export analyzed articles to CSV format
    """
    if not articles:
        return ""
    
    output = io.StringIO()
    
    # Define CSV headers
    headers = [
        'Title', 'Source', 'Published Date', 'Author', 'URL',
        'Sentiment', 'Confidence Score', 'Market Impact',
        'Summary', 'Key Insights', 'Content Length'
    ]
    
    writer = csv.writer(output)
    writer.writerow(headers)
    
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
            '; '.join(article.get('key_insights', [])),
            len(article.get('content', ''))
        ]
        writer.writerow(row)
    
    return output.getvalue()

def format_date(date_str: str) -> str:
    """
    Format date string for display
    """
    if not date_str:
        return "Unknown"
    
    try:
        # Handle ISO format dates
        if 'T' in date_str:
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        else:
            # Try parsing as date only
            date_obj = datetime.strptime(date_str[:10], '%Y-%m-%d')
        
        return date_obj.strftime('%Y-%m-%d %H:%M')
    except (ValueError, TypeError):
        return str(date_str)

def clean_text(text: str) -> str:
    """
    Clean text content by removing extra whitespace and special characters
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # Remove or replace problematic characters
    cleaned = cleaned.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
    
    # Remove URLs
    cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
    
    # Remove email addresses
    cleaned = re.sub(r'\S+@\S+', '', cleaned)
    
    return cleaned.strip()

def clean_text_for_csv(text: str) -> str:
    """
    Clean text specifically for CSV export
    """
    if not text:
        return ""
    
    cleaned = clean_text(text)
    
    # Escape quotes and commas for CSV
    cleaned = cleaned.replace('"', '""')
    
    return cleaned

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to specified length with ellipsis
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def calculate_reading_time(text: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time in minutes
    """
    if not text:
        return 0
    
    word_count = len(text.split())
    reading_time = max(1, word_count // words_per_minute)
    
    return reading_time

def extract_php_mentions(text: str) -> List[str]:
    """
    Extract specific mentions of Philippine peso from text
    """
    if not text:
        return []
    
    # Patterns to look for PHP/peso mentions
    patterns = [
        r'PHP\s*[0-9,.]+',
        r'peso\s*[0-9,.]+',
        r'₱\s*[0-9,.]+',
        r'[0-9,.]+\s*per\s*dollar',
        r'[0-9,.]+\s*to\s*the\s*dollar'
    ]
    
    mentions = []
    text_lower = text.lower()
    
    for pattern in patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        mentions.extend(matches)
    
    return list(set(mentions))  # Remove duplicates

def validate_article_data(article: Dict[str, Any]) -> bool:
    """
    Validate that article data contains required fields
    """
    required_fields = ['title', 'content', 'source']
    
    for field in required_fields:
        if not article.get(field):
            return False
    
    # Additional validation
    if len(article.get('content', '')) < 100:  # Minimum content length
        return False
    
    return True

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove extra spaces and dots
    sanitized = re.sub(r'\.+', '.', sanitized)
    sanitized = re.sub(r'\s+', '_', sanitized)
    
    # Limit length
    if len(sanitized) > 200:
        sanitized = sanitized[:200]
    
    return sanitized.strip('.')

def get_sentiment_emoji(sentiment: str) -> str:
    """
    Get emoji representation of sentiment
    """
    emoji_map = {
        'positive': '📈',
        'negative': '📉',
        'neutral': '➡️',
        'unknown': '❓'
    }
    
    return emoji_map.get(sentiment.lower(), '❓')

def format_confidence_score(score: float) -> str:
    """
    Format confidence score as percentage
    """
    if score is None:
        return "N/A"
    
    return f"{score * 100:.1f}%"
