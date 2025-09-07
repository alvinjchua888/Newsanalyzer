import json
import os
from openai import OpenAI
from typing import Dict, Any, List

class LLMAnalyzer:
    def __init__(self):
        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-5"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.client = OpenAI(api_key=api_key)
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single news article for Philippine peso forex insights
        """
        content = article.get('content', '')
        title = article.get('title', '')
        
        if not content:
            return {
                'sentiment': 'neutral',
                'confidence_score': 0.0,
                'summary': 'No content available for analysis',
                'key_insights': [],
                'market_impact': 'unknown'
            }
        
        try:
            # Generate summary
            summary = self._generate_summary(title, content)
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_sentiment(content)
            
            # Extract key insights
            key_insights = self._extract_key_insights(content)
            
            # Assess market impact
            market_impact = self._assess_market_impact(content)
            
            return {
                'sentiment': sentiment_analysis['sentiment'],
                'confidence_score': sentiment_analysis['confidence'],
                'summary': summary,
                'key_insights': key_insights,
                'market_impact': market_impact
            }
            
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'confidence_score': 0.0,
                'summary': f'Error analyzing article: {str(e)}',
                'key_insights': [],
                'market_impact': 'unknown'
            }
    
    def _generate_summary(self, title: str, content: str) -> str:
        """
        Generate a concise summary of the article focusing on PHP forex aspects
        """
        prompt = f"""
        Please provide a concise summary of this Philippine peso forex news article. 
        Focus on key points related to currency movements, economic factors, and market implications.
        
        Title: {title}
        Content: {content[:2000]}...
        
        Summary should be 2-3 sentences maximum.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate summary: {str(e)}"
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment specifically for Philippine peso forex implications
        """
        prompt = f"""
        Analyze the sentiment of this news article regarding the Philippine peso's performance and outlook.
        Consider factors like:
        - Currency strength/weakness indicators
        - Economic policy impacts
        - Market confidence signals
        - Future outlook implications
        
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
                        "content": "You are a financial analyst specializing in Philippine peso forex analysis. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                'sentiment': result.get('sentiment', 'neutral'),
                'confidence': max(0.0, min(1.0, result.get('confidence', 0.5))),
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
        Extract key insights relevant to Philippine peso forex trading
        """
        prompt = f"""
        Extract 3-5 key insights from this article that would be valuable for understanding Philippine peso forex movements.
        Focus on:
        - Specific economic indicators mentioned
        - Policy changes or announcements
        - Market driving factors
        - Technical or fundamental analysis points
        
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
                        "content": "You are a forex analyst. Extract actionable insights about Philippine peso. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('insights', [])
        except Exception as e:
            return [f"Error extracting insights: {str(e)}"]
    
    def _assess_market_impact(self, content: str) -> str:
        """
        Assess the potential market impact of the news
        """
        prompt = f"""
        Assess the potential market impact of this news on Philippine peso trading.
        
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
                        "content": "You are a market impact analyst. Assess news impact on Philippine peso. Respond only with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('impact', 'unknown')
        except Exception as e:
            return 'unknown'
    
    def generate_overall_analysis(self, analyzed_articles: List[Dict[str, Any]]) -> str:
        """
        Generate an overall market analysis based on all analyzed articles
        """
        if not analyzed_articles:
            return "No articles available for analysis."
        
        # Prepare summary data
        sentiments = [article.get('sentiment', 'neutral') for article in analyzed_articles]
        summaries = [article.get('summary', '') for article in analyzed_articles if article.get('summary')]
        
        sentiment_counts = {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral')
        }
        
        prompt = f"""
        Based on analysis of {len(analyzed_articles)} recent Philippine peso forex news articles, provide an overall market assessment.
        
        Sentiment Distribution:
        - Positive: {sentiment_counts['positive']} articles
        - Negative: {sentiment_counts['negative']} articles  
        - Neutral: {sentiment_counts['neutral']} articles
        
        Key Article Summaries:
        {chr(10).join(summaries[:5])}
        
        Provide a comprehensive 3-4 paragraph analysis covering:
        1. Overall market sentiment and trend direction
        2. Key factors driving Philippine peso movements
        3. Outlook and potential risks/opportunities
        4. Actionable insights for forex traders
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a senior forex analyst specializing in Philippine peso markets. Provide professional, actionable analysis."
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate overall analysis: {str(e)}"
