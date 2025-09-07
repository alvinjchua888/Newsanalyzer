"""
News Scraper Module

This module provides functionality to scrape news articles from multiple RSS feeds 
and Google News search. It handles content extraction, deduplication, and relevance 
filtering to provide high-quality news data for analysis.

Author: AI News Analyzer Team

test

"""

import requests
from datetime import datetime, timedelta
import trafilatura
from typing import List, Dict, Any, Optional
import time
import re
import urllib.parse
import feedparser
from dataclasses import dataclass
from abc import ABC, abstractmethod

dataclass
class Article:
    """Data class representing a news article"""
    title: str
    content: str
    source: str
    url: str
    published_date: str
    author: str = 'Unknown'

class NewsSource(ABC):
    """Abstract base class for news sources"""
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
    
    @abstractmethod
    def fetch_articles(self, search_terms: List[str], max_articles: int = 10) -> List[Article]:
        """Fetch articles from this source"""
        pass

class RSSSource(NewsSource):
    """RSS-based news source"""
    
    def __init__(self, name: str, url: str, headers: dict, max_entries: int = 10):
        super().__init__(name, url)
        self.headers = headers
        self.max_entries = max_entries
    
    def fetch_articles(self, search_terms: List[str], max_articles: int = 10) -> List[Article]:
        """Fetch articles from RSS feed"""
        articles = []
        
        try:
            print(f"Fetching RSS feed from {self.name}: {self.url}")
            
            response = requests.get(self.url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch RSS feed from {self.name}. Status: {response.status_code}")
                return articles
            
            feed = feedparser.parse(response.content)
            print(f"Found {len(feed.entries)} entries in {self.name} RSS feed")
            
            for i, entry in enumerate(feed.entries[:min(self.max_entries, max_articles)]):
                try:
                    if self._is_entry_relevant(entry, search_terms):
                        article = self._extract_article_from_entry(entry)
                        if article:
                            articles.append(article)
                            print(f"Added article: {article.title[:50]}...")
                            
                except Exception as e:
                    print(f"Error processing entry {i+1} from {self.name}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching RSS from {self.name}: {str(e)}")
            
        return articles
    
    def _is_entry_relevant(self, entry, search_terms: List[str]) -> bool:
        """Check if RSS entry is relevant to search terms"""
        title = getattr(entry, 'title', '').lower()
        summary = getattr(entry, 'summary', '').lower()
        description = getattr(entry, 'description', '').lower()
        
        text_to_check = f"{title} {summary} {description}"
        
        return any(term.lower().strip() in text_to_check for term in search_terms if term.strip())
    
    def _extract_article_from_entry(self, entry) -> Optional[Article]:
        """Extract article from RSS entry"""
        try:
            content = self._extract_content_from_url(entry.link)
            if not content or len(content) < 100:
                return None
            
            return Article(
                title=getattr(entry, 'title', 'Untitled Article'),
                content=content,
                source=self.name,
                url=entry.link,
                published_date=getattr(entry, 'published', datetime.now().isoformat()),
                author=getattr(entry, 'author', 'Unknown')
            )
        except Exception as e:
            print(f"Error extracting article from {entry.link}: {str(e)}")
            return None
    
    def _extract_content_from_url(self, url: str) -> Optional[str]:
        """Extract content from URL using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url, config=trafilatura.settings.use_config())
            if not downloaded:
                return None
            
            text = trafilatura.extract(downloaded, 
                                    include_comments=False,
                                    include_tables=True,
                                    include_formatting=False)
            
            return text if text and len(text.strip()) >= 100 else None
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None

class GoogleNewsSource(NewsSource):
    """Google News search source"""
    
    def __init__(self, headers: dict):
        super().__init__("Google News", "https://news.google.com/rss/search")
        self.headers = headers
    
    def fetch_articles(self, search_terms: List[str], max_articles: int = 10) -> List[Article]:
        """Search Google News for articles"""
        articles = []
        
        try:
            search_query = ' '.join(search_terms)
            encoded_query = urllib.parse.quote_plus(search_query)
            url = f"{self.url}?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            print(f"Searching Google News for: {search_query}")
            
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code != 200:
                print(f"Failed to fetch Google News feed. Status: {response.status_code}")
                return articles
            
            feed = feedparser.parse(response.content)
            print(f"Found {len(feed.entries)} entries in Google News feed")
            
            for entry in feed.entries[:max_articles]:
                try:
                    real_url = self._extract_real_url(entry.link)
                    if real_url:
                        content = self._extract_content_from_url(real_url)
                        if content and len(content) >= 100:
                            article = Article(
                                title=getattr(entry, 'title', 'Untitled Article'),
                                content=content,
                                source=self.name,
                                url=real_url,
                                published_date=getattr(entry, 'published', datetime.now().isoformat())
                            )
                            articles.append(article)
                            print(f"Added Google News article: {article.title[:50]}...")
                            
                except Exception as e:
                    print(f"Error processing Google News entry: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"Error searching Google News: {str(e)}")
            
        return articles
    
    def _extract_real_url(self, google_url: str) -> Optional[str]:
        """Extract real URL from Google News redirect"""
        try:
            if not 'news.google.com' in google_url:
                return google_url;
                
            # Try following redirects
            response = requests.head(google_url, headers=self.headers, timeout=10, allow_redirects=True)
            if response.url and response.url != google_url:
                return response.url;
                
            # Try extracting from URL parameters
            if 'url=' in google_url:
                url_start = google_url.find('url=') + 4
                url_end = google_url.find('&', url_start)
                if url_end == -1:
                    url_end = len(google_url)
                return urllib.parse.unquote(google_url[url_start:url_end])
                
            return google_url;
                
        except Exception:
            return google_url
    
    def _extract_content_from_url(self, url: str) -> Optional[str]:
        """Extract content from URL using trafilatura"""
        try:
            downloaded = trafilatura.fetch_url(url, config=trafilatura.settings.use_config())
            if not downloaded:
                return None
            
            text = trafilatura.extract(downloaded, 
                                    include_comments=False,
                                    include_tables=True,
                                    include_formatting=False)
            
            return text if text and len(text.strip()) >= 100 else None
            
        except Exception:
            return None

class ArticleDeduplicator:
    """Handles article deduplication"""
    
    @staticmethod
    def remove_duplicates(articles: List[Article], similarity_threshold: float = 0.7) -> List[Article]:
        """Remove duplicate articles based on title similarity"""
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_words = set(re.findall(r'\w+', article.title.lower()))
            
            is_duplicate = False
            for seen_title in seen_titles:
                seen_words = set(re.findall(r'\w+', seen_title))
                if title_words | seen_words:  # Avoid division by zero
                    similarity = len(title_words & seen_words) / len(title_words | seen_words)
                    if similarity > similarity_threshold:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(article.title.lower())
        
        return unique_articles

class NewsScraper:
    """
    Simplified news scraper with pluggable sources
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        self.sources = self._initialize_sources()
        self.deduplicator = ArticleDeduplicator()
    
    def _initialize_sources(self) -> Dict[str, NewsSource]:
        """Initialize all news sources"""
        sources = {}
        
        # General RSS sources
        rss_feeds = {
            'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
            'Reuters': 'https://feeds.reuters.com/reuters/topNews',
            'CNN': 'http://rss.cnn.com/rss/edition.rss',
            'AP News': 'https://feeds.apnews.com/apnews/topnews',
            'Yahoo News': 'https://www.yahoo.com/news/rss',
        }
        
        for name, url in rss_feeds.items():
            sources[name] = RSSSource(name, url, self.headers, max_entries=10)
        
        # Tech RSS sources (with higher entry limit)
        tech_feeds = {
            'TechCrunch': 'https://techcrunch.com/feed/',
            'The Verge': 'https://www.theverge.com/rss/index.xml',
            'Ars Technica': 'http://feeds.arstechnica.com/arstechnica/index',
            'Wired': 'https://www.wired.com/feed/rss',
            'Engadget': 'https://www.engladget.com/rss.xml'
        }
        
        for name, url in tech_feeds.items():
            sources[name] = RSSSource(name, url, self.headers, max_entries=15)
        
        # Google News source
        sources['Google News'] = GoogleNewsSource(self.headers)
        
        return sources
    
    def scrape_news(self, search_terms: List[str], sources: List[str], 
                   start_date: datetime, end_date: datetime, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape news articles from specified sources
        
        Args:
            search_terms: Keywords to search for
            sources: List of source names to scrape from
            start_date: Start date (currently not used for filtering)
            end_date: End date (currently not used for filtering)
            max_articles: Maximum number of articles to return
            
        Returns:
            List of article dictionaries
        """
        all_articles = []
        articles_per_source = max(1, max_articles // len(sources)) if sources else max_articles
        
        # Always include Google News search
        google_source = self.sources.get('Google News')
        if google_source:
            google_articles = google_source.fetch_articles(search_terms, max_articles // 2)
            all_articles.extend(google_articles)
        
        # Fetch from specified sources
        for source_name in sources:
            if source_name in self.sources:
                try:
                    articles = self.sources[source_name].fetch_articles(search_terms, articles_per_source)
                    all_articles.extend(articles)
                    time.sleep(1)  # Rate limiting
                    
                    if len(all_articles) >= max_articles:
                        break
                        
                except Exception as e:
                    print(f"Error scraping {source_name}: {str(e)}")
                    continue
            else:
                print(f"Unknown source: {source_name}")
        
        # Remove duplicates and convert to dictionaries
        unique_articles = self.deduplicator.remove_duplicates(all_articles)
        result = [self._article_to_dict(article) for article in unique_articles[:max_articles]]
        
        print(f"Total articles found after deduplication: {len(result)}")
        return result
    
    def _article_to_dict(self, article: Article) -> Dict[str, Any]:
        """Convert Article dataclass to dictionary"""
        return {
            'title': article.title,
            'content': article.content,
            'source': article.source,
            'url': article.url,
            'published_date': article.published_date,
            'author': article.author
        }
    
    def get_available_sources(self) -> List[str]:
        """Get list of available source names"""
        return list(self.sources.keys())
