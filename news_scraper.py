"""
News Scraper Module

This module provides functionality to scrape news articles from multiple RSS feeds 
and Google News search. It handles content extraction, deduplication, and relevance 
filtering to provide high-quality news data for analysis.

Author: AI News Analyzer Team
"""

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
    """
    A comprehensive news scraping class that fetches articles from RSS feeds and Google News.
    
    This class provides methods to:
    - Scrape articles from multiple news sources
    - Extract clean text content from web pages
    - Filter articles based on relevance to search terms
    - Remove duplicate articles
    - Handle both general news and technology-focused sources
    
    Attributes:
        headers (dict): HTTP headers used for web requests to mimic browser behavior
        rss_sources (dict): Dictionary mapping general news source names to RSS URLs
        tech_rss_sources (dict): Dictionary mapping tech news source names to RSS URLs
    """
    
    def __init__(self):
        """
        Initialize the NewsScraper with predefined RSS sources and HTTP headers.
        
        Sets up:
        - HTTP headers to avoid being blocked by websites
        - General news RSS sources (BBC, Reuters, CNN, etc.)
        - Technology-focused RSS sources (TechCrunch, The Verge, etc.)
        """
        # HTTP headers to mimic a real browser and avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # General news sources with their RSS feed URLs
        self.rss_sources = {
            'BBC News': 'http://feeds.bbci.co.uk/news/rss.xml',
            'Reuters': 'https://feeds.reuters.com/reuters/topNews',
            'CNN': 'http://rss.cnn.com/rss/edition.rss',
            'AP News': 'https://feeds.apnews.com/apnews/topnews',
            'Yahoo News': 'https://www.yahoo.com/news/rss',
            'Google News': 'https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en'
        }
        
        # Technology-focused RSS sources for specialized tech coverage
        self.tech_rss_sources = {
            'TechCrunch': 'https://techcrunch.com/feed/',
            'The Verge': 'https://www.theverge.com/rss/index.xml',
            'Ars Technica': 'http://feeds.arstechnica.com/arstechnica/index',
            'Wired': 'https://www.wired.com/feed/rss',
            'Engadget': 'https://www.engadget.com/rss.xml'
        }
    
    def scrape_news(self, search_terms: List[str], sources: List[str], 
                   start_date: datetime, end_date: datetime, max_articles: int = 20) -> List[Dict[str, Any]]:
        """
        Scrape news articles from multiple sources using RSS feeds and Google News search.
        
        This method orchestrates the entire news scraping process by:
        1. Searching Google News for topic-specific articles
        2. Scraping RSS feeds from selected news sources
        3. Filtering articles for relevance to search terms
        4. Removing duplicate articles
        5. Limiting results to the specified maximum
        
        Args:
            search_terms (List[str]): Keywords to search for in articles
            sources (List[str]): Names of news sources to scrape from
            start_date (datetime): Start date for article filtering
            end_date (datetime): End date for article filtering
            max_articles (int, optional): Maximum number of articles to return. Defaults to 20.
            
        Returns:
            List[Dict[str, Any]]: List of article dictionaries containing:
                - title (str): Article headline
                - content (str): Full article text content
                - source (str): Name of the news source
                - url (str): Article URL
                - published_date (str): Publication date in ISO format
                - author (str): Article author (if available)
                
        Example:
            >>> scraper = NewsScraper()
            >>> articles = scraper.scrape_news(
            ...     search_terms=["artificial intelligence", "AI"],
            ...     sources=["TechCrunch", "The Verge"],
            ...     start_date=datetime(2024, 1, 1),
            ...     end_date=datetime(2024, 1, 7),
            ...     max_articles=10
            ... )
            >>> print(f"Found {len(articles)} articles")
        """
        articles = []
        search_query = ' '.join(search_terms)
        
        # First, try Google News search for specific topics
        try:
            google_articles = self._search_google_news(search_query, max_articles // 2)
            articles.extend(google_articles)
        except Exception as e:
            print(f"Error searching Google News: {str(e)}")
        
        # Then, search through RSS feeds from selected sources
        for source in sources:
            try:
                # Check if it's a regular RSS source or tech source
                if source in self.rss_sources:
                    source_articles = self._scrape_rss_source(source, search_terms, start_date, end_date)
                elif source in self.tech_rss_sources:
                    source_articles = self._scrape_tech_rss_source(source, self.tech_rss_sources[source], search_terms, start_date, end_date)
                else:
                    print(f"Unknown source: {source}")
                    continue
                    
                articles.extend(source_articles)
                time.sleep(1)  # Be respectful to servers - rate limiting
                
                # Stop if we have enough articles
                if len(articles) >= max_articles:
                    break
            except Exception as e:
                print(f"Error scraping {source}: {str(e)}")
                continue
        
        # Remove duplicates based on title similarity
        articles = self._remove_duplicates(articles)
        
        print(f"Total articles found after deduplication: {len(articles)}")
        return articles[:max_articles]
    
    
    def _search_google_news(self, search_query: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """
        Search Google News for articles matching the query using RSS feed.
        
        This method queries Google News RSS API with the search terms and processes
        the results to extract full article content. It performs relevance checking
        on article titles before extracting full content to optimize performance.
        
        Args:
            search_query (str): Combined search terms as a single string
            max_articles (int, optional): Maximum articles to retrieve. Defaults to 10.
            
        Returns:
            List[Dict[str, Any]]: List of article dictionaries with extracted content
            
        Note:
            Google News URLs often redirect through Google's servers. This method
            attempts to extract the real article URLs when possible.
        """
        articles = []
        
        try:
            # Use Google News RSS search with URL-encoded query
            encoded_query = urllib.parse.quote_plus(search_query)
            google_news_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
            
            print(f"Searching Google News for: {search_query}")
            print(f"URL: {google_news_url}")
            
            # Fetch the RSS feed
            response = requests.get(google_news_url, headers=self.headers, timeout=15)
            print(f"Google News response status: {response.status_code}")
            
            if response.status_code == 200:
                # Parse the RSS feed
                feed = feedparser.parse(response.content)
                print(f"Found {len(feed.entries)} entries in Google News feed")
                
                for i, entry in enumerate(feed.entries[:max_articles]):
                    try:
                        title = entry.title if hasattr(entry, 'title') else 'No title'
                        print(f"Processing entry {i+1}: {title[:100]}")
                        
                        # Quick relevance check on title first (performance optimization)
                        title_relevant = any(term.lower() in title.lower() for term in search_query.split() if term.strip())
                        
                        if title_relevant:
                            print(f"Title seems relevant, extracting full content...")
                            
                            # Extract the real article URL from Google News redirect
                            article_url = entry.link
                            if 'news.google.com' in article_url:
                                article_url = self._extract_real_url(entry.link)
                            
                            if article_url:
                                print(f"Extracting content from: {article_url[:100]}...")
                                article_data = self._extract_article_content(article_url, 'Google News')
                                if article_data:
                                    # Use RSS entry data to supplement extracted content
                                    if hasattr(entry, 'title') and not article_data.get('title'):
                                        article_data['title'] = entry.title
                                    if hasattr(entry, 'published'):
                                        article_data['published_date'] = entry.published
                                        
                                    articles.append(article_data)
                                    print(f"Successfully added article: {article_data['title'][:50]}...")
                                else:
                                    print(f"Failed to extract content from {article_url}")
                        else:
                            print(f"Title not relevant to search terms, skipping content extraction")
                                
                    except Exception as e:
                        print(f"Error processing Google News entry {i+1}: {str(e)}")
                        continue
            else:
                print(f"Failed to fetch Google News feed. Status: {response.status_code}")
                        
        except Exception as e:
            print(f"Error searching Google News: {str(e)}")
            
        print(f"Google News search returned {len(articles)} articles")
        return articles
    
    
    def _scrape_rss_source(self, source: str, search_terms: List[str], 
                          start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Scrape articles from general news RSS feeds.
        
        This method fetches RSS feeds from general news sources and processes
        each entry to extract full article content. It filters articles based
        on relevance to the search terms.
        
        Args:
            source (str): Name of the news source (must exist in rss_sources)
            search_terms (List[str]): Keywords to filter articles by relevance
            start_date (datetime): Start date filter (currently not enforced)
            end_date (datetime): End date filter (currently not enforced)
            
        Returns:
            List[Dict[str, Any]]: List of relevant articles from this source
            
        Note:
            The method limits processing to 10 entries per source to optimize
            performance and respect rate limiting.
        """
        articles = []
        
        if source not in self.rss_sources:
            print(f"Source {source} not found in RSS sources")
            return articles
            
        try:
            rss_url = self.rss_sources[source]
            print(f"Fetching RSS feed from {source}: {rss_url}")
            
            # Fetch the RSS feed
            response = requests.get(rss_url, headers=self.headers, timeout=15)
            print(f"RSS response status for {source}: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                print(f"Found {len(feed.entries)} entries in {source} RSS feed")
                
                # Process each RSS entry (limited to 10 per source)
                for i, entry in enumerate(feed.entries[:10]):
                    try:
                        print(f"Processing RSS entry {i+1} from {source}: {entry.title[:50] if hasattr(entry, 'title') else 'No title'}...")
                        
                        # Extract full article content
                        article_data = self._extract_article_content(entry.link, source)
                        if article_data:
                            # Use RSS metadata if article extraction didn't get it
                            if hasattr(entry, 'title') and not article_data.get('title'):
                                article_data['title'] = entry.title
                            if hasattr(entry, 'published'):
                                article_data['published_date'] = entry.published
                                
                            # Check if article is relevant to search terms
                            if self._is_relevant_article(article_data['content'], search_terms):
                                articles.append(article_data)
                                print(f"Added relevant article from {source}: {article_data['title'][:50]}...")
                            else:
                                print(f"Article not relevant to search terms: {search_terms}")
                        else:
                            print(f"Failed to extract content from RSS entry: {entry.link}")
                            
                    except Exception as e:
                        print(f"Error processing RSS entry {i+1} from {source}: {str(e)}")
                        continue
            else:
                print(f"Failed to fetch RSS feed from {source}. Status: {response.status_code}")
                        
        except Exception as e:
            print(f"Error fetching RSS from {source}: {str(e)}")
            
        print(f"RSS scraping from {source} returned {len(articles)} relevant articles")
        return articles
    
    
    def _extract_real_url(self, google_news_url: str) -> str:
        """
        Extract the real article URL from Google News redirect URL.
        
        Google News often provides redirect URLs that go through their servers.
        This method attempts to resolve the actual article URL by following
        redirects or parsing URL parameters.
        
        Args:
            google_news_url (str): Google News URL (may be a redirect)
            
        Returns:
            str: Real article URL if successfully extracted, otherwise original URL
            
        Note:
            Uses multiple strategies:
            1. Follow HTTP redirects
            2. Parse 'url=' query parameter
            3. Return original URL as fallback
        """
        try:
            if not google_news_url:
                return None
                
            # If it's already a direct URL (not a Google redirect), return as is
            if not 'news.google.com' in google_news_url:
                return google_news_url
                
            # Try to follow the redirect to get the real URL
            try:
                response = requests.head(google_news_url, headers=self.headers, timeout=10, allow_redirects=True)
                if response.url and response.url != google_news_url:
                    return response.url
            except:
                pass
                
            # Fallback: try to extract URL from query parameters
            if 'url=' in google_news_url:
                url_start = google_news_url.find('url=') + 4
                url_end = google_news_url.find('&', url_start)
                if url_end == -1:
                    url_end = len(google_news_url)
                real_url = urllib.parse.unquote(google_news_url[url_start:url_end])
                return real_url
                
            return google_news_url
            
        except Exception as e:
            print(f"Error extracting real URL from {google_news_url}: {str(e)}")
            return google_news_url
    
    def _extract_article_content(self, url: str, source: str) -> Dict[str, Any]:
        """
        Extract content from a single article URL using Trafilatura.
        
        This method downloads the webpage and extracts clean text content,
        metadata, and other article information using the Trafilatura library.
        
        Args:
            url (str): Article URL to scrape content from
            source (str): Name of the news source for attribution
            
        Returns:
            Dict[str, Any]: Article data dictionary containing:
                - title (str): Article headline
                - content (str): Clean text content
                - source (str): News source name
                - url (str): Article URL
                - published_date (str): Publication date
                - author (str): Article author
            Returns None if extraction fails.
            
        Note:
            Uses Trafilatura for robust content extraction that handles
            various website layouts and removes boilerplate content.
        """
        try:
            if not url or not url.startswith(('http://', 'https://')):
                print(f"Invalid URL: {url}")
                return None
                
            print(f"Downloading content from: {url}")
            
            # Download the webpage with optimized settings
            downloaded = trafilatura.fetch_url(url, config=trafilatura.settings.use_config())
            
            if not downloaded:
                print(f"Failed to download content from {url}")
                return None
            
            # Extract text content with comprehensive settings
            text = trafilatura.extract(downloaded, 
                                    include_comments=False,  # Exclude comment sections
                                    include_tables=True,     # Include table content
                                    include_formatting=False) # Remove formatting markup
            
            # Validate extracted content
            if not text or len(text.strip()) < 100:
                print(f"Insufficient content extracted from {url} (length: {len(text) if text else 0})")
                return None
            
            # Extract metadata (title, date, author)
            metadata = trafilatura.extract_metadata(downloaded)
            
            # Create structured article data
            article_data = {
                'title': metadata.title if metadata and metadata.title else self._extract_title_from_text(text),
                'content': text,
                'source': source,
                'url': url,
                'published_date': metadata.date if metadata and metadata.date else datetime.now().isoformat(),
                'author': metadata.author if metadata and metadata.author else 'Unknown'
            }
            
            print(f"Successfully extracted article: {article_data['title'][:50]}... ({len(text)} chars)")
            return article_data
            
        except Exception as e:
            print(f"Error extracting content from {url}: {str(e)}")
            return None
    
    
    def _extract_title_from_text(self, text: str) -> str:
        """
        Extract title from text content when metadata is not available.
        
        This fallback method attempts to identify the article title by
        examining the first few lines of text content.
        
        Args:
            text (str): Article text content
            
        Returns:
            str: Extracted title or "Untitled Article" if none found
            
        Note:
            Looks for lines that are:
            - Between 10 and 150 characters (reasonable title length)
            - Located in the first 5 lines of the content
        """
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            if len(line.strip()) > 10 and len(line.strip()) < 150:
                return line.strip()
        return "Untitled Article"
    
    def _is_relevant_article(self, content: str, search_terms: List[str]) -> bool:
        """
        Check if article content is relevant to search terms.
        
        This method performs content-based relevance filtering by checking
        if any of the search terms appear in the article content.
        
        Args:
            content (str): Article text content
            search_terms (List[str]): List of keywords to search for
            
        Returns:
            bool: True if article contains any search term, False otherwise
            
        Note:
            - Performs case-insensitive matching
            - Returns False for very short articles (< 50 characters)
            - Considers article relevant if ANY search term is found
        """
        if not content or len(content) < 50:
            print(f"Article too short or empty (length: {len(content) if content else 0})")
            return False
            
        content_lower = content.lower()
        
        # Count how many search terms are found
        relevance_score = 0
        found_terms = []
        
        for term in search_terms:
            term_lower = term.lower().strip()
            if term_lower and term_lower in content_lower:
                relevance_score += 1
                found_terms.append(term)
        
        print(f"Relevance check: {relevance_score}/{len(search_terms)} terms found: {found_terms}")
        
        # Consider article relevant if it contains any search term
        return relevance_score > 0
    
    def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate articles based on title similarity.
        
        This method uses Jaccard similarity to identify and remove duplicate
        articles that may come from different sources but cover the same story.
        
        Args:
            articles (List[Dict[str, Any]]): List of article dictionaries
            
        Returns:
            List[Dict[str, Any]]: Deduplicated list of articles
            
        Algorithm:
            1. Convert titles to lowercase and extract words
            2. Calculate Jaccard similarity between word sets
            3. Remove articles with >70% similarity to previously seen titles
            
        Note:
            Uses a 70% similarity threshold to catch near-duplicates while
            avoiding false positives from similar but distinct articles.
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
                # Calculate Jaccard similarity coefficient
                similarity = len(title_words & seen_words) / len(title_words | seen_words) if title_words | seen_words else 0
                
                if similarity > 0.7:  # 70% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
                seen_titles.add(title)
        
        return unique_articles
    
    
    def _scrape_tech_rss_source(self, source_name: str, source_url: str, search_terms: List[str], 
                               start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Scrape articles from technology-focused RSS feeds.
        
        Similar to general RSS scraping but optimized for tech sources with
        enhanced relevance checking on both titles and descriptions.
        
        Args:
            source_name (str): Name of the technology news source
            source_url (str): URL of the RSS feed
            search_terms (List[str]): Keywords to filter articles by relevance
            start_date (datetime): Start date filter (currently not enforced)
            end_date (datetime): End date filter (currently not enforced)
            
        Returns:
            List[Dict[str, Any]]: List of relevant articles from this tech source
            
        Features:
            - Processes up to 15 entries per source (more than general sources)
            - Checks both title and description/summary for relevance
            - Optimized for technology-specific content patterns
            
        Note:
            Tech sources often have richer metadata and more structured content,
            so this method can afford to process more entries while maintaining
            good relevance filtering.
        """
        articles = []
        
        try:
            print(f"Fetching tech RSS feed from {source_name}: {source_url}")
            
            # Fetch the technology RSS feed
            response = requests.get(source_url, headers=self.headers, timeout=15)
            print(f"Tech RSS response status for {source_name}: {response.status_code}")
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                print(f"Found {len(feed.entries)} entries in {source_name} RSS feed")
                
                # Process more entries from tech sources (up to 15)
                for i, entry in enumerate(feed.entries[:15]):
                    try:
                        title = entry.title if hasattr(entry, 'title') else 'No title'
                        print(f"Processing tech entry {i+1} from {source_name}: {title[:70]}...")
                        
                        # Quick relevance check on title first
                        title_relevant = any(term.lower() in title.lower() for term in search_terms if term.strip())
                        
                        if title_relevant:
                            print(f"Title relevant! Extracting content...")
                            article_data = self._extract_article_content(entry.link, source_name)
                            if article_data:
                                # Use RSS metadata if available
                                if hasattr(entry, 'title') and not article_data.get('title'):
                                    article_data['title'] = entry.title
                                if hasattr(entry, 'published'):
                                    article_data['published_date'] = entry.published
                                    
                                articles.append(article_data)
                                print(f"Added tech article: {article_data['title'][:50]}...")
                            else:
                                print(f"Failed to extract content from tech article: {entry.link}")
                        else:
                            # Also check description/summary for relevance (tech articles often have good summaries)
                            description = getattr(entry, 'summary', '') or getattr(entry, 'description', '')
                            desc_relevant = any(term.lower() in description.lower() for term in search_terms if term.strip())
                            
                            if desc_relevant:
                                print(f"Description relevant! Extracting content...")
                                article_data = self._extract_article_content(entry.link, source_name)
                                if article_data and self._is_relevant_article(article_data['content'], search_terms):
                                    if hasattr(entry, 'title') and not article_data.get('title'):
                                        article_data['title'] = entry.title
                                    if hasattr(entry, 'published'):
                                        article_data['published_date'] = entry.published
                                        
                                    articles.append(article_data)
                                    print(f"Added tech article from description match: {article_data['title'][:50]}...")
                            else:
                                print(f"Not relevant to search terms, skipping")
                            
                    except Exception as e:
                        print(f"Error processing tech entry {i+1} from {source_name}: {str(e)}")
                        continue
            else:
                print(f"Failed to fetch tech RSS feed from {source_name}. Status: {response.status_code}")
                        
        except Exception as e:
            print(f"Error fetching tech RSS from {source_name}: {str(e)}")
            
        print(f"Tech RSS scraping from {source_name} returned {len(articles)} relevant articles")
        return articles
