import requests
from datetime import datetime, timedelta
import trafilatura
from typing import List, Dict, Any
import time
import re
import urllib.parse
import xml.etree.ElementTree as ET
import feedparser

class NewsScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.rss_sources = {
            'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
            'Reuters': 'https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best',
            'CNN': 'http://rss.cnn.com/rss/edition.rss',
            'AP News': 'https://rsshub.app/ap/topics/apf-topnews',
            'Yahoo News': 'https://www.yahoo.com/news/rss',
            'Google News': 'https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en'
        }
    
    def scrape_news(self, search_terms: List[str], sources: List[str], 
                   start_date: datetime, end_date: datetime, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape news articles from multiple sources using RSS feeds and Google News search
        """
        articles = []
        search_query = ' '.join(search_terms)
        
        # First, try Google News search for specific topics
        try:
            google_articles = self._search_google_news(search_query, max_articles // 2)
            articles.extend(google_articles)
        except Exception as e:
            print(f"Error searching Google News: {str(e)}")
        
        # Then, search through RSS feeds
        for source in sources:
            if source not in self.rss_sources:
                continue
                
            try:
                source_articles = self._scrape_rss_source(source, search_terms, start_date, end_date)
                articles.extend(source_articles)
                time.sleep(1)  # Be respectful to servers
                
                if len(articles) >= max_articles:
                    break
            except Exception as e:
                print(f"Error scraping {source}: {str(e)}")
                continue
        
        # Remove duplicates based on title similarity
        articles = self._remove_duplicates(articles)
        
        return articles[:max_articles]
    
    def _search_google_news(self, search_query: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Search Google News for articles matching the query
        """
        articles = []
        
        try:
            # Use Google News RSS search
            encoded_query = urllib.parse.quote_plus(search_query)
            google_news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            response = requests.get(google_news_url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:max_articles]:
                    try:
                        # Extract the actual article URL from Google News redirect
                        article_url = self._extract_real_url(entry.link)
                        if article_url:
                            article_data = self._extract_article_content(article_url, 'Google News')
                            if article_data:
                                articles.append(article_data)
                                
                    except Exception as e:
                        print(f"Error processing Google News entry: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error searching Google News: {str(e)}")
            
        return articles
    
    def _scrape_rss_source(self, source: str, search_terms: List[str], 
                          start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Scrape articles from RSS feeds
        """
        articles = []
        
        if source not in self.rss_sources:
            return articles
            
        try:
            rss_url = self.rss_sources[source]
            response = requests.get(rss_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:10]:  # Limit per source
                    try:
                        article_data = self._extract_article_content(entry.link, source)
                        if article_data and self._is_relevant_article(article_data['content'], search_terms):
                            articles.append(article_data)
                            
                    except Exception as e:
                        print(f"Error processing RSS entry: {str(e)}")
                        continue
                        
        except Exception as e:
            print(f"Error fetching RSS from {source}: {str(e)}")
            
        return articles
    
    def _extract_real_url(self, google_news_url: str) -> str:
        """
        Extract the real article URL from Google News redirect URL
        """
        try:
            # Google News URLs often contain the real URL in the query parameters
            if 'url=' in google_news_url:
                # Extract URL parameter
                url_start = google_news_url.find('url=') + 4
                url_end = google_news_url.find('&', url_start)
                if url_end == -1:
                    url_end = len(google_news_url)
                real_url = urllib.parse.unquote(google_news_url[url_start:url_end])
                return real_url
            else:
                # If it's already a direct URL, return as is
                return google_news_url
        except Exception as e:
            print(f"Error extracting real URL: {str(e)}")
            return google_news_url
    
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
        if not content or len(content) < 100:
            return False
            
        content_lower = content.lower()
        
        # Must contain at least one search term
        relevance_score = 0
        for term in search_terms:
            if term.lower() in content_lower:
                relevance_score += 1
        
        # Consider article relevant if it contains any search term
        return relevance_score > 0
    
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
