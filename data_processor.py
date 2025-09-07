import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
import re

class DataProcessor:
    def __init__(self):
        pass
    
    def process_articles_to_dataframe(self, articles: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert articles list to pandas DataFrame for easier manipulation
        """
        if not articles:
            return pd.DataFrame()
        
        # Flatten the data structure
        processed_data = []
        
        for article in articles:
            processed_article = {
                'title': article.get('title', 'No Title'),
                'source': article.get('source', 'Unknown'),
                'url': article.get('url', ''),
                'published_date': self._parse_date(article.get('published_date')),
                'author': article.get('author', 'Unknown'),
                'content_length': len(article.get('content', '')),
                'sentiment': article.get('sentiment', 'neutral'),
                'confidence_score': article.get('confidence_score', 0.0),
                'summary': article.get('summary', ''),
                'market_impact': article.get('market_impact', 'unknown'),
                'key_insights_count': len(article.get('key_insights', [])),
                'key_insights': '; '.join(article.get('key_insights', []))
            }
            processed_data.append(processed_article)
        
        df = pd.DataFrame(processed_data)
        
        # Add derived columns
        df['sentiment_score'] = df['sentiment'].map({
            'positive': 1,
            'neutral': 0,
            'negative': -1
        })
        
        df['weighted_sentiment'] = df['sentiment_score'] * df['confidence_score']
        
        return df
    
    def _parse_date(self, date_str: str) -> str:
        """
        Parse and standardize date strings
        """
        if not date_str:
            return datetime.now().strftime('%Y-%m-%d')
        
        try:
            # Handle various date formats
            if isinstance(date_str, str):
                # Remove timezone info and parse
                clean_date = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)
                clean_date = clean_date.replace('T', ' ').replace('Z', '')
                
                # Try different date formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
                    try:
                        parsed_date = datetime.strptime(clean_date[:19], fmt)
                        return parsed_date.strftime('%Y-%m-%d')
                    except ValueError:
                        continue
            
            return datetime.now().strftime('%Y-%m-%d')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d')
    
    def get_sentiment_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary statistics of sentiment analysis
        """
        df = self.process_articles_to_dataframe(articles)
        
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
        Filter articles based on various criteria
        """
        filtered = articles.copy()
        
        if sentiment and sentiment.lower() != 'all':
            filtered = [a for a in filtered if a.get('sentiment', '').lower() == sentiment.lower()]
        
        if source and source.lower() != 'all':
            filtered = [a for a in filtered if a.get('source', '') == source]
        
        if min_confidence is not None:
            filtered = [a for a in filtered if a.get('confidence_score', 0) >= min_confidence]
        
        return filtered
    
    def get_top_insights(self, articles: List[Dict[str, Any]], top_n: int = 10) -> List[str]:
        """
        Extract and rank the most common insights across all articles
        """
        all_insights = []
        
        for article in articles:
            insights = article.get('key_insights', [])
            all_insights.extend(insights)
        
        # Count frequency of similar insights
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
        Normalize insight text for better comparison
        """
        # Convert to lowercase and remove extra whitespace
        normalized = re.sub(r'\s+', ' ', insight.lower().strip())
        # Remove common prefixes/suffixes
        normalized = re.sub(r'^(the |a |an )', '', normalized)
        normalized = re.sub(r'(\.|\!|\?)$', '', normalized)
        return normalized
    
    def calculate_market_impact_score(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate an overall market impact score based on all articles
        """
        if not articles:
            return {'score': 0.0, 'level': 'minimal', 'factors': []}
        
        impact_weights = {
            'high': 3.0,
            'medium': 2.0,
            'low': 1.0,
            'minimal': 0.5,
            'unknown': 1.0
        }
        
        total_score = 0
        total_weight = 0
        impact_factors = []
        
        for article in articles:
            impact = article.get('market_impact', 'unknown')
            confidence = article.get('confidence_score', 0.5)
            
            weight = impact_weights.get(impact, 1.0) * confidence
            total_score += weight
            total_weight += 1
            
            if impact in ['high', 'medium']:
                impact_factors.append({
                    'title': article.get('title', 'Unknown'),
                    'impact': impact,
                    'confidence': confidence
                })
        
        average_score = total_score / total_weight if total_weight > 0 else 0
        
        # Determine overall impact level
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
