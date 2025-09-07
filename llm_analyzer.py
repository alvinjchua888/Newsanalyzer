import json
import os
from openai import OpenAI
from typing import Dict, Any, List

class LLMAnalyzer:
    def __init__(self):
        # Using gpt-4o for better stability and compatibility
        self.model = "gpt-4o"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")
        
        self.client = OpenAI(api_key=api_key)
    
    def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single news article for insights on any topic
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
        Generate a concise summary of the article focusing on key aspects
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
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate summary: {str(e)}"
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """
        Analyze sentiment of the news article for the topic being discussed
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
        Extract key insights from the article relevant to the topic being discussed
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
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('insights', [])
        except Exception as e:
            return [f"Error extracting insights: {str(e)}"]
    
    def _assess_market_impact(self, content: str) -> str:
        """
        Assess the potential impact of the news on the topic or relevant stakeholders
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
                temperature=0.2
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('impact', 'unknown')
        except Exception as e:
            return 'unknown'
    
    def generate_overall_analysis(self, analyzed_articles: List[Dict[str, Any]]) -> str:
        """
        Generate an overall topic analysis based on all analyzed articles
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
                temperature=0.4
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Unable to generate overall analysis: {str(e)}"
