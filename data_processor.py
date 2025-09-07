"""
Data Processor Module

This module provides data processing and manipulation capabilities for news articles.
It handles conversion between different data formats, statistical analysis,
filtering operations, and derived metric calculations.

The module is designed to work with analyzed article data and provide
structured outputs suitable for display, analysis, and export.

Author: AI News Analyzer Team
"""

import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import re

class DataProcessor:
    """
    Data processing and manipulation class for news articles.
    
    This class provides comprehensive data processing capabilities including:
    - Converting article lists to pandas DataFrames
    - Generating sentiment and statistical summaries
    - Filtering articles based on various criteria
    - Extracting top insights across multiple articles
    - Calculating market impact scores
    
    The processor handles both raw article data and analyzed articles with
    AI-generated insights, providing structured outputs for visualization
    and further analysis.
    
    Example:
        >>> processor = DataProcessor()
        >>> df = processor.process_articles_to_dataframe(articles)
        >>> summary = processor.get_sentiment_summary(articles)
        >>> filtered = processor.filter_articles(articles, sentiment="positive")
    """
    
    def __init__(self):
        """
        Initialize the DataProcessor.
        
        Simple initialization with no configuration parameters required.
        The processor is designed to be stateless and work with data passed
        to its methods.
        """
        pass
    
    
    def process_articles_to_dataframe(self, articles: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert articles list to pandas DataFrame with derived metrics for analysis.
        
        This method transforms raw article data into a structured DataFrame
        suitable for statistical analysis, visualization, and export. It handles
        both basic article metadata and AI analysis results.
        
        Args:
            articles (List[Dict[str, Any]]): List of article dictionaries containing
                basic info (title, source, url, etc.) and optionally AI analysis results
                (sentiment, confidence_score, summary, etc.)
                
        Returns:
            pd.DataFrame: Structured DataFrame with columns:
                Basic Info:
                - title, source, url, published_date, author, content_length
                Analysis Results:
                - sentiment, confidence_score, summary, market_impact
                - key_insights_count, key_insights (concatenated)
                Derived Metrics:
                - sentiment_score (-1, 0, 1 for negative, neutral, positive)
                - weighted_sentiment (sentiment_score * confidence_score)
                
        Note:
            - Returns empty DataFrame if no articles provided
            - Handles missing fields gracefully with default values
            - Date parsing is performed to standardize date formats
            - Key insights are joined with semicolons for CSV compatibility
            
        Example:
            >>> articles = [{'title': 'News Title', 'sentiment': 'positive', ...}]
            >>> df = processor.process_articles_to_dataframe(articles)
            >>> print(df[['title', 'sentiment', 'weighted_sentiment']].head())
        """
        if not articles:
            return pd.DataFrame()
        
        # Flatten the data structure for DataFrame creation
        processed_data = []
        
        for article in articles:
            processed_article = {
                # Basic article information
                'title': article.get('title', 'No Title'),
                'source': article.get('source', 'Unknown'),
                'url': article.get('url', ''),
                'published_date': self._parse_date(article.get('published_date')),
                'author': article.get('author', 'Unknown'),
                'content_length': len(article.get('content', '')),
                
                # AI analysis results
                'sentiment': article.get('sentiment', 'neutral'),
                'confidence_score': article.get('confidence_score', 0.0),
                'summary': article.get('summary', ''),
                'market_impact': article.get('market_impact', 'unknown'),
                'key_insights_count': len(article.get('key_insights', [])),
                'key_insights': '; '.join(article.get('key_insights', []))  # Join for CSV compatibility
            }
            processed_data.append(processed_article)
        
        df = pd.DataFrame(processed_data)
        
        # Add derived columns for analysis
        df['sentiment_score'] = df['sentiment'].map({
            'positive': 1,
            'neutral': 0,
            'negative': -1
        })
        
        # Weighted sentiment combines sentiment direction with confidence
        df['weighted_sentiment'] = df['sentiment_score'] * df['confidence_score']
        
        return df
    
    
    def _parse_date(self, date_str: str) -> str:
        """
        Parse and standardize date strings from various formats.
        
        This method handles the variety of date formats that can come from
        different news sources and RSS feeds, converting them to a standardized
        YYYY-MM-DD format for consistency.
        
        Args:
            date_str (str): Date string in various possible formats
            
        Returns:
            str: Standardized date string (YYYY-MM-DD) or current date if parsing fails
            
        Supported Formats:
            - ISO format: 2024-01-01T12:00:00Z
            - Date only: 2024-01-01
            - US format: 01/01/2024
            - European format: 01/01/2024
            
        Note:
            - Strips timezone information for simplicity
            - Falls back to current date if all parsing attempts fail
            - Handles both string and non-string inputs gracefully
        """
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Handle various date formats from different sources
            if isinstance(date_str, str):
                # Remove timezone info and clean up common formats
                clean_date = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)  # Remove timezone
                clean_date = clean_date.replace('T', ' ').replace('Z', '')  # Clean ISO format
                
                # Try different date formats commonly found in RSS feeds
                date_formats = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(clean_date[:19], fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            
            # If all parsing fails, return current date
            return datetime.now().strftime('%Y-%m-%d')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def get_sentiment_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate comprehensive summary statistics of sentiment analysis across articles.
        
        This method provides a statistical overview of the sentiment analysis
        results, including distribution, confidence metrics, and metadata summary.
        
        Args:
            articles (List[Dict[str, Any]]): List of analyzed articles
            
        Returns:
            Dict[str, Any]: Summary statistics containing:
                - total_articles (int): Total number of articles
                - sentiment_distribution (dict): Count of each sentiment type
                - average_confidence (float): Mean confidence score
                - overall_sentiment_score (float): Weighted average sentiment
                - sources (list): Unique news sources in the dataset
                - date_range (dict): Earliest and latest publication dates
                
        Note:
            - Returns zero values and empty lists if no articles provided
            - Uses weighted sentiment (sentiment * confidence) for overall score
            - Provides both absolute counts and relative measures
            
        Example:
            >>> summary = processor.get_sentiment_summary(articles)
            >>> print(f"Overall sentiment: {summary['overall_sentiment_score']:.2f}")
            >>> print(f"Positive articles: {summary['sentiment_distribution']['positive']}")
        """
        df = self.process_articles_to_dataframe(articles)
        
        # Handle empty dataset
        if df.empty:
            return {
                'total_articles': 0,
                'sentiment_distribution': {},
                'average_confidence': 0.0,
                'overall_sentiment_score': 0.0
            }
        
        sentiment_counts = df['sentiment'].value_counts().to_dict()
        
        return {
            'total_articles': len(df),
            'sentiment_distribution': sentiment_counts,
            'average_confidence': df['confidence_score'].mean(),
            'overall_sentiment_score': df['weighted_sentiment'].mean(),
            'sources': df['source'].unique().tolist(),
            'date_range': {
                'earliest': df['published_date'].min(),
                'latest': df['published_date'].max()
            }
        }
    
    
    def filter_articles(self, articles: List[Dict[str, Any]], 
                       sentiment: str = None, 
                       source: str = None,
                       min_confidence: float = None) -> List[Dict[str, Any]]:
        """
        Filter articles based on various criteria for focused analysis.
        
        This method provides flexible filtering capabilities to help users
        focus on specific subsets of articles based on sentiment, source,
        or confidence thresholds.
        
        Args:
            articles (List[Dict[str, Any]]): List of articles to filter
            sentiment (str, optional): Filter by sentiment ("positive", "negative", "neutral", "all")
            source (str, optional): Filter by news source name ("all" for no filtering)
            min_confidence (float, optional): Minimum confidence score threshold (0.0-1.0)
            
        Returns:
            List[Dict[str, Any]]: Filtered list of articles matching all specified criteria
            
        Note:
            - Returns copy of original list, doesn't modify input
            - "all" or None values disable that filter criterion
            - Filters are applied cumulatively (AND logic)
            - Case-insensitive sentiment matching
            
        Example:
            >>> # Get high-confidence positive articles from specific source
            >>> filtered = processor.filter_articles(
            ...     articles,
            ...     sentiment="positive", 
            ...     source="TechCrunch",
            ...     min_confidence=0.8
            ... )
        """
        filtered = articles.copy()
        
        # Filter by sentiment if specified
        if sentiment and sentiment.lower() != 'all':
            filtered = [a for a in filtered if a.get('sentiment', '').lower() == sentiment.lower()]
        
        # Filter by source if specified
        if source and source.lower() != 'all':
            filtered = [a for a in filtered if a.get('source', '') == source]
        
        # Filter by minimum confidence if specified
        if min_confidence is not None:
            filtered = [a for a in filtered if a.get('confidence_score', 0) >= min_confidence]
        
        return filtered
    
    def get_top_insights(self, articles: List[Dict[str, Any]], top_n: int = 10) -> List[str]:
        """
        Extract and rank the most common insights across all articles.
        
        This method aggregates insights from all articles, normalizes them
        for comparison, and returns the most frequently occurring insights
        to identify common themes and important points.
        
        Args:
            articles (List[Dict[str, Any]]): List of analyzed articles with key_insights
            top_n (int, optional): Number of top insights to return. Defaults to 10.
            
        Returns:
            List[str]: Top N most frequent insights, sorted by frequency
            
        Processing Steps:
            1. Extract all insights from all articles
            2. Normalize insight text for better comparison
            3. Count frequency of similar insights  
            4. Return most common insights sorted by frequency
            
        Note:
            - Uses text normalization to group similar insights
            - Removes common prefixes/suffixes for better matching
            - Returns empty list if no articles have insights
            
        Example:
            >>> insights = processor.get_top_insights(articles, top_n=5)
            >>> for i, insight in enumerate(insights, 1):
            ...     print(f"{i}. {insight}")
        """
        all_insights = []
        
        # Extract all insights from all articles
        for article in articles:
            insights = article.get('key_insights', [])
            all_insights.extend(insights)
        
        # Count frequency of similar insights using normalization
        insight_counts = {}
        for insight in all_insights:
            # Normalize insight text for comparison
            normalized = self._normalize_insight(insight)
            insight_counts[normalized] = insight_counts.get(normalized, 0) + 1
        
        # Sort by frequency and return top N
        sorted_insights = sorted(insight_counts.items(), key=lambda x: x[1], reverse=True)
        return [insight for insight, count in sorted_insights[:top_n]]
    
    def _normalize_insight(self, insight: str) -> str:
        """
        Normalize insight text for better comparison and grouping.
        
        This helper method standardizes insight text to improve matching
        of similar insights that may be phrased slightly differently.
        
        Args:
            insight (str): Original insight text
            
        Returns:
            str: Normalized insight text
            
        Normalization Steps:
            - Convert to lowercase
            - Remove extra whitespace
            - Remove common article prefixes (the, a, an)
            - Remove terminal punctuation
            
        Note:
            Used internally by get_top_insights() to group similar insights
        """
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', insight.lower().strip())
        # Remove common prefixes/suffixes that don't affect meaning
        normalized = re.sub(r'^(the |a |an )', '', normalized)
        normalized = re.sub(r'(\.|\!|\?)$', '', normalized)
        return normalized
    
    
    def calculate_market_impact_score(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate an overall market impact score based on all articles.
        
        This method analyzes market impact assessments across all articles
        to generate an aggregate impact score and identify the most significant
        contributing factors.
        
        Args:
            articles (List[Dict[str, Any]]): List of analyzed articles with market_impact data
            
        Returns:
            Dict[str, Any]: Market impact analysis containing:
                - score (float): Numerical impact score (0.0-3.0 scale)
                - level (str): Overall impact level ("high", "medium", "low", "minimal")
                - factors (List[Dict]): Top contributing articles with impact details
                
        Scoring Method:
            - Weights impact levels: high=3.0, medium=2.0, low=1.0, minimal=0.5, unknown=1.0
            - Multiplies by confidence score for reliability weighting
            - Averages across all articles for final score
            
        Level Classification:
            - high: score >= 2.5 (major industry impact expected)
            - medium: score >= 1.5 (notable sectoral impact)
            - low: score >= 0.7 (minor influence expected)
            - minimal: score < 0.7 (little to no impact)
            
        Note:
            - Returns minimal impact if no articles provided
            - Factors list includes up to 5 highest-impact articles
            - Factors are sorted by confidence score for reliability
            
        Example:
            >>> impact = processor.calculate_market_impact_score(articles)
            >>> print(f"Overall impact: {impact['level']} (score: {impact['score']})")
            >>> print(f"Key factors: {len(impact['factors'])}")
        """
        if not articles:
            return {'score': 0.0, 'level': 'minimal', 'factors': []}
        
        # Define impact level weights for scoring
        impact_weights = {
            'high': 3.0,
            'medium': 2.0,
            'low': 1.0,
            'minimal': 0.5,
            'unknown': 1.0  # Neutral weight for unknown impact
        }
        
        total_score = 0
        total_weight = 0
        impact_factors = []
        
        # Calculate weighted impact score across all articles
        for article in articles:
            impact = article.get('market_impact', 'unknown')
            confidence = article.get('confidence_score', 0.5)
            
            # Weight impact by confidence score for reliability
            weight = impact_weights.get(impact, 1.0) * confidence
            total_score += weight
            total_weight += 1
            
            # Track high and medium impact articles as factors
            if impact in ['high', 'medium']:
                impact_factors.append({
                    'title': article.get('title', 'Unknown'),
                    'impact': impact,
                    'confidence': confidence
                })
        
        # Calculate average impact score
        average_score = total_score / total_weight if total_weight > 0 else 0
        
        # Determine overall impact level based on score
        if average_score >= 2.5:
            level = 'high'
        elif average_score >= 1.5:
            level = 'medium'
        elif average_score >= 0.7:
            level = 'low'
        else:
            level = 'minimal'
        
        return {
            'score': round(average_score, 2),
            'level': level,
            'factors': sorted(impact_factors, key=lambda x: x['confidence'], reverse=True)[:5]
        }
