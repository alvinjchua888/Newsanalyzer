"""
LLM Analyzer Module

This module provides AI-powered analysis capabilities using OpenAI's GPT models.
It handles sentiment analysis, content summarization, key insight extraction,
and market impact assessment for news articles.

The module uses structured prompting and JSON responses to ensure consistent
and reliable analysis results across different types of content.

Author: AI News Analyzer Team
"""

import json
import os
from openai import OpenAI
from typing import Dict, Any, List

class LLMAnalyzer:
    """
    AI-powered news article analyzer using OpenAI's GPT models.
    
    This class provides comprehensive analysis capabilities including:
    - Sentiment analysis with confidence scoring
    - Article summarization 
    - Key insights extraction
    - Market impact assessment
    - Overall topic analysis across multiple articles
    
    The analyzer uses GPT-4o for optimal balance of performance and cost,
    with structured JSON responses to ensure consistent output formatting.
    
    Attributes:
        model (str): OpenAI model identifier ("gpt-4o")
        client (OpenAI): Configured OpenAI API client
        
    Raises:
        ValueError: If OPENAI_API_KEY environment variable is not set
        
    Example:
        >>> analyzer = LLMAnalyzer()
        >>> article = {'title': 'AI Breakthrough', 'content': 'Article content...'}
        >>> result = analyzer.analyze_article(article)
        >>> print(f"Sentiment: {result['sentiment']}")
    """
    
    def __init__(self):
        """
        Initialize the LLM analyzer with OpenAI client and model configuration.
        
        Sets up the OpenAI client using the API key from environment variables.
        Uses GPT-4o model for optimal balance of quality, speed, and cost.
        
        Raises:
            ValueError: If OPENAI_API_KEY environment variable is not set
        """
        # Using gpt-4o for better stability and compatibility
        self.model = "gpt-4o"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.client = OpenAI(api_key=api_key)
    
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive AI analysis of a single news article.
        
        This method orchestrates multiple AI analysis components to provide
        a complete assessment of the article including sentiment, summary,
        insights, and market impact.
        
        Args:
            article (Dict[str, Any]): Article dictionary containing:
                - content (str): Full article text
                - title (str): Article headline
                - Other metadata (optional)
                
        Returns:
            Dict[str, Any]: Analysis results containing:
                - sentiment (str): "positive", "negative", or "neutral"
                - confidence_score (float): Confidence level 0.0-1.0
                - summary (str): Concise 2-3 sentence summary
                - key_insights (List[str]): List of important insights
                - market_impact (str): Impact level ("high", "medium", "low", "minimal")
                
        Note:
            If analysis fails, returns default values with error message in summary.
            Content is truncated to optimize API usage and response time.
            
        Example:
            >>> article = {
            ...     'title': 'Major AI Breakthrough Announced',
            ...     'content': 'Researchers have developed...'
            ... }
            >>> analysis = analyzer.analyze_article(article)
            >>> print(f"Sentiment: {analysis['sentiment']} ({analysis['confidence_score']:.2f})")
        """
        content = article.get('content', '')
        title = article.get('title', '')
        
        # Handle missing or empty content
        if not content:
            return {
                'sentiment': 'neutral',
                'confidence_score': 0.0,
                'summary': 'No content available for analysis',
                'key_insights': [],
                'market_impact': 'unknown'
            }
        
        try:
            # Generate comprehensive analysis components
            summary = self._generate_summary(title, content)
            sentiment_analysis = self._analyze_sentiment(content)
            key_insights = self._extract_key_insights(content)
            market_impact = self._assess_market_impact(content)
            
            return {
                'sentiment': sentiment_analysis['sentiment'],
                'confidence_score': sentiment_analysis['confidence'],
                'summary': summary,
                'key_insights': key_insights,
                'market_impact': market_impact
            }
            
        except Exception as e:
            # Graceful fallback for API errors
            return {
                'sentiment': 'neutral',
                'confidence_score': 0.0,
                'summary': f'Error analyzing article: {str(e)}',
                'key_insights': [],
                'market_impact': 'unknown'
            }
    
    
    def _generate_summary(self, title: str, content: str) -> str:
        """
        Generate a concise AI summary of the article focusing on key aspects.
        
        Uses GPT to create a 2-3 sentence summary that captures the most
        important points, main events, and implications of the article.
        
        Args:
            title (str): Article headline for context
            content (str): Article content (truncated to 2000 chars for efficiency)
            
        Returns:
            str: Concise summary or error message if generation fails
            
        Note:
            - Content is truncated to first 2000 characters to optimize API usage
            - Uses low temperature (0.3) for consistent, focused summaries
            - Limits output to 150 tokens to ensure brevity
        """
        prompt = f"""
        Please provide a concise summary of this news article. 
        Focus on the key points, main events, and important implications mentioned in the article.
        
        Title: {title}
        Content: {content[:2000]}...
        
        Summary should be 2-3 sentences maximum.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3  # Low temperature for consistency
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate summary: {str(e)}"
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the news article with confidence scoring.
        
        Performs comprehensive sentiment analysis considering overall tone,
        outlook, implications, and impact on stakeholders. Returns structured
        results with confidence scoring and reasoning.
        
        Args:
            content (str): Article content (truncated to 2000 chars for efficiency)
            
        Returns:
            Dict[str, Any]: Sentiment analysis containing:
                - sentiment (str): "positive", "negative", or "neutral"
                - confidence (float): Confidence score 0.0-1.0
                - reasoning (str): Brief explanation of the sentiment assessment
                
        Note:
            - Uses JSON mode for structured output
            - Low temperature (0.2) for consistent classification
            - Considers multiple factors beyond simple positive/negative words
        """
        prompt = f"""
        Analyze the sentiment of this news article. Consider factors like:
        - Overall tone (positive, negative, or neutral)
        - Outlook and implications mentioned
        - Impact on stakeholders
        - Future prospects discussed
        
        Content: {content[:2000]}...
        
        Respond with JSON in this exact format:
        {{"sentiment": "positive/negative/neutral", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a news analyst specializing in sentiment analysis. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2  # Very low temperature for consistency
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'sentiment': result.get('sentiment', 'neutral'),
                'confidence': max(0.0, min(1.0, result.get('confidence', 0.5))),  # Clamp to valid range
                'reasoning': result.get('reasoning', '')
            }
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'reasoning': f'Error in sentiment analysis: {str(e)}'
            }
    
    
    def _extract_key_insights(self, content: str) -> List[str]:
        """
        Extract key insights from the article relevant to the topic being discussed.
        
        Uses AI to identify and extract 3-5 most valuable insights that would
        be useful for understanding the main topic, including specific facts,
        developments, trends, and expert opinions.
        
        Args:
            content (str): Article content (truncated to 2000 chars for efficiency)
            
        Returns:
            List[str]: List of key insights (3-5 items), empty list or error message if extraction fails
            
        Focus Areas:
            - Specific facts or data mentioned
            - Important developments or announcements  
            - Driving factors and trends
            - Analysis points and expert opinions
            
        Note:
            - Uses JSON mode for structured output
            - Moderate temperature (0.3) for creative but focused insight extraction
            - Returns error message in list if API call fails
        """
        prompt = f"""
        Extract 3-5 key insights from this article that would be valuable for understanding the main topic.
        Focus on:
        - Specific facts or data mentioned
        - Important developments or announcements
        - Driving factors and trends
        - Analysis points and expert opinions
        
        Content: {content[:2000]}...
        
        Respond with JSON in this format:
        {{"insights": ["insight 1", "insight 2", "insight 3"]}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a news analyst. Extract actionable insights from news articles. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3  # Moderate temperature for creative insights
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('insights', [])
        except Exception as e:
            return [f"Error extracting insights: {str(e)}"]
    
    def _assess_market_impact(self, content: str) -> str:
        """
        Assess the potential market or industry impact of the news.
        
        Analyzes the article to determine how significantly the news might
        affect relevant industries, markets, or stakeholders. Provides
        structured impact classification.
        
        Args:
            content (str): Article content (truncated to 1500 chars for efficiency)
            
        Returns:
            str: Impact level ("high", "medium", "low", "minimal") or "unknown" if assessment fails
            
        Impact Levels:
            - high: Major industry disruption, significant market effects
            - medium: Notable impact on specific sectors or companies
            - low: Minor influence, limited scope
            - minimal: Little to no market impact expected
            
        Note:
            - Uses JSON mode for structured output
            - Very low temperature (0.2) for consistent classification
            - Shorter content limit (1500 chars) as impact can often be determined from key points
        """
        prompt = f"""
        Assess the potential impact of this news on the relevant industry, market, or stakeholders.
        
        Content: {content[:1500]}...
        
        Classify the impact as one of: "high", "medium", "low", "minimal"
        
        Respond with JSON: {{"impact": "level", "explanation": "brief reason"}}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a news impact analyst. Assess the impact of news on relevant markets or stakeholders. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2  # Low temperature for consistent impact assessment
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('impact', 'unknown')
        except Exception as e:
            return 'unknown'
    
    
    def generate_overall_analysis(self, analyzed_articles: List[Dict[str, Any]]) -> str:
        """
        Generate a comprehensive overall topic analysis based on multiple analyzed articles.
        
        This method synthesizes insights from all analyzed articles to provide
        a high-level assessment of the topic, including sentiment trends,
        key driving factors, outlook, and strategic implications.
        
        Args:
            analyzed_articles (List[Dict[str, Any]]): List of articles with analysis results
                Each article should contain sentiment, summary, and other analysis data
                
        Returns:
            str: Multi-paragraph comprehensive analysis covering:
                - Overall sentiment and trend direction
                - Key factors and developments driving the narrative
                - Outlook and potential implications  
                - Key insights and takeaways
                Returns error message if analysis fails
                
        Analysis Structure:
            1. Sentiment distribution and trends
            2. Key developments and driving factors
            3. Future outlook and implications
            4. Strategic insights and recommendations
            
        Note:
            - Uses first 5 article summaries to maintain prompt length limits
            - Moderate temperature (0.4) for comprehensive but coherent analysis
            - Handles empty article list gracefully
            
        Example:
            >>> articles = [article1, article2, article3]  # With analysis results
            >>> overall = analyzer.generate_overall_analysis(articles)
            >>> print(overall)  # Multi-paragraph topic assessment
        """
        if not analyzed_articles:
            return "No articles available for analysis."
        
        # Prepare summary statistics for analysis
        sentiments = [article.get('sentiment', 'neutral') for article in analyzed_articles]
        summaries = [article.get('summary', '') for article in analyzed_articles if article.get('summary')]
        
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral')
        }
        
        prompt = f"""
        Based on analysis of {len(analyzed_articles)} recent news articles, provide an overall topic assessment.
        
        Sentiment Distribution:
        - Positive: {sentiment_counts['positive']} articles
        - Negative: {sentiment_counts['negative']} articles  
        - Neutral: {sentiment_counts['neutral']} articles
        
        Key Article Summaries:
        {chr(10).join(summaries[:5])}
        
        Provide a comprehensive 3-4 paragraph analysis covering:
        1. Overall sentiment and trend direction for this topic
        2. Key factors and developments driving the narrative
        3. Outlook and potential implications
        4. Key insights and takeaways
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior news analyst. Provide professional, comprehensive analysis based on multiple news sources."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.4  # Moderate temperature for comprehensive analysis
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate overall analysis: {str(e)}"
