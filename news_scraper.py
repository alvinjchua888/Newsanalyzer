import requests
from datetime import datetime, timedelta
import trafilatura
from typing import List, Dict, Any
import time
import re

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.sources = {
            'Reuters': 'https://www.reuters.com',
            'Bloomberg': 'https://www.bloomberg.com',
            'CNN Philippines': 'https://www.cnnphilippines.com',
            'Rappler': 'https://www.rappler.com',
            'Inquirer': 'https://www.inquirer.net',
            'Manila Bulletin': 'https://mb.com.ph'
        }
    
    def scrape_news(self, search_terms: List[str], sources: List[str], 
                   start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Scrape news articles from multiple sources
        """
        articles = []
        
        for source in sources:
            if source not in self.sources:
                continue
                
            try:
                source_articles = self._scrape_source(source, search_terms, start_date, end_date)
                articles.extend(source_articles)
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                print(f"Error scraping {source}: {str(e)}")
                continue
        
        # Remove duplicates based on title similarity
        articles = self._remove_duplicates(articles)
        
        return articles
    
    def _scrape_source(self, source: str, search_terms: List[str], 
                      start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Scrape articles from a specific source
        """
        articles = []
        
        # For demonstration, we'll use Google News search for each source
        # In production, you might want to use specific APIs or RSS feeds
        search_query = ' OR '.join(search_terms)
        
        # Construct Google News search URL
        google_news_urls = self._get_google_news_urls(search_query, source, start_date, end_date)
        
        for url in google_news_urls:
            try:
                article_data = self._extract_article_content(url, source)
                if article_data and self._is_relevant_article(article_data['content'], search_terms):
                    articles.append(article_data)
                    
                if len(articles) >= 10:  # Limit per source
                    break
                    
            except Exception as e:
                print(f"Error processing URL {url}: {str(e)}")
                continue
        
        return articles
    
    def _get_google_news_urls(self, query: str, source: str, 
                             start_date: datetime, end_date: datetime) -> List[str]:
        """
        Get news URLs from Google News search
        """
        urls = []
        
        # Sample URLs for different sources - in production, use actual search APIs
        if source == "Reuters":
            urls = [
                "https://www.reuters.com/markets/currencies/philippine-peso-weakens-dollar-strength-2024-01-15/",
                "https://www.reuters.com/markets/currencies/philippine-central-bank-intervenes-support-peso-2024-01-16/",
                "https://www.reuters.com/world/asia-pacific/philippine-peso-slides-inflation-concerns-2024-01-17/",
            ]
        elif source == "Bloomberg":
            urls = [
                "https://www.bloomberg.com/news/articles/2024-01-15/philippine-peso-drops-amid-fed-policy-uncertainty",
                "https://www.bloomberg.com/news/articles/2024-01-16/philippines-forex-reserves-support-peso-stability",
            ]
        elif source == "CNN Philippines":
            urls = [
                "https://www.cnnphilippines.com/business/2024/1/15/peso-exchange-rate-analysis.html",
                "https://www.cnnphilippines.com/business/2024/1/16/bsp-monetary-policy-peso.html",
            ]
        
        # Filter URLs to only include those that might have recent content
        # In a real implementation, you would use proper news APIs or RSS feeds
        return urls[:5]  # Limit to avoid overwhelming
    
    def _extract_article_content(self, url: str, source: str) -> Dict[str, Any]:
        """
        Extract content from a single article URL using trafilatura
        """
        try:
            # Download the webpage
            downloaded = trafilatura.fetch_url(url)
            
            if not downloaded:
                return None
            
            # Extract text content
            text = trafilatura.extract(downloaded)
            
            if not text:
                return None
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(downloaded)
            
            # Create article data structure
            article_data = {
                'title': metadata.title if metadata and metadata.title else self._extract_title_from_text(text),
                'content': text,
                'source': source,
                'url': url,
                'published_date': metadata.date if metadata and metadata.date else datetime.now().isoformat(),
                'author': metadata.author if metadata and metadata.author else 'Unknown'
            }
            
            return article_data
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None
    
    def _extract_title_from_text(self, text: str) -> str:
        """
        Extract title from text content when metadata is not available
        """
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if len(line.strip()) > 10 and len(line.strip()) < 150:
                return line.strip()
        return "Untitled Article"
    
    def _is_relevant_article(self, content: str, search_terms: List[str]) -> bool:
        """
        Check if article content is relevant to our search terms
        """
        content_lower = content.lower()
        
        # Must contain at least one search term
        for term in search_terms:
            if term.lower() in content_lower:
                return True
        
        # Additional relevance checks for Philippine peso forex news
        forex_keywords = ['peso', 'php', 'exchange rate', 'currency', 'dollar', 'forex', 'bangko sentral']
        relevant_count = sum(1 for keyword in forex_keywords if keyword in content_lower)
        
        return relevant_count >= 2
    
    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate articles based on title similarity
        """
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title = article.get('title', '').lower()
            title_words = set(re.findall(r'\w+', title))
            
            # Check if this title is too similar to any we've seen
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(re.findall(r'\w+', seen_title))
                similarity = len(title_words & seen_words) / len(title_words | seen_words) if title_words | seen_words else 0
                
                if similarity > 0.7:  # 70% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(title)
        
        return unique_articles
