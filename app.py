import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os
from news_scraper import NewsScraper
from llm_analyzer import LLMAnalyzer
from data_processor import DataProcessor
from utils import export_to_csv, format_date, clean_text

# Page configuration
st.set_page_config(
    page_title="AI News Analyzer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'analyzed_articles' not in st.session_state:
    st.session_state.analyzed_articles = []
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Initialize components
@st.cache_resource
def init_components():
    scraper = NewsScraper()
    analyzer = LLMAnalyzer()
    processor = DataProcessor()
    return scraper, analyzer, processor

scraper, analyzer, processor = init_components()

# Header
st.title("📰 AI News Analyzer")
st.markdown("Real-time analysis of news articles on any topic using AI-powered insights")

# Sidebar controls
with st.sidebar:
    st.header("🔧 Controls")
    
    # Date range selection
    st.subheader("Date Range")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "From",
            value=datetime.now() - timedelta(days=7),
            max_value=datetime.now()
        )
    with col2:
        end_date = st.date_input(
            "To",
            value=datetime.now(),
            max_value=datetime.now()
        )
    
    # News sources
    st.subheader("News Sources")
    selected_sources = st.multiselect(
        "Select sources:",
        options=["Google News", "BBC News", "Reuters", "CNN", "AP News", "Yahoo News", "TechCrunch", "The Verge", "Ars Technica", "Wired", "Engadget"],
        default=["Google News", "TechCrunch", "The Verge"]
    )
    
    # Search topic
    st.subheader("Search Topic")
    topic = st.text_input(
        "Enter the topic you want to analyze:",
        value="iPhone",
        help="Enter keywords related to the topic you want to search for"
    )
    
    # Action buttons
    st.subheader("Actions")
    if st.button("🔍 Scrape & Analyze News", type="primary"):
        if not topic.strip():
            st.error("Please enter a topic to search for.")
        else:
            with st.spinner("Scraping news articles..."):
                try:
                    # Scrape articles
                    search_terms = [term.strip() for term in topic.split(",")]
                    articles = scraper.scrape_news(
                        search_terms=search_terms,
                        sources=selected_sources,
                        start_date=start_date,
                        end_date=end_date
                    )
                    st.session_state.articles = articles
                
                    if articles:
                        st.success(f"Found {len(articles)} articles!")
                        
                        # Analyze articles
                        with st.spinner("Analyzing articles with AI..."):
                            analyzed_articles = []
                            progress_bar = st.progress(0)
                            
                            for i, article in enumerate(articles):
                                try:
                                    analysis = analyzer.analyze_article(article)
                                    analyzed_articles.append({
                                        **article,
                                        **analysis
                                    })
                                    progress_bar.progress((i + 1) / len(articles))
                                except Exception as e:
                                    st.error(f"Error analyzing article: {str(e)}")
                            
                            st.session_state.analyzed_articles = analyzed_articles
                            st.session_state.last_update = datetime.now()
                            st.success("Analysis complete!")
                    else:
                        st.warning("No articles found for the selected criteria.")
                        
                except Exception as e:
                    st.error(f"Error during scraping: {str(e)}")
    
    if st.session_state.analyzed_articles:
        if st.button("📥 Export Results"):
            csv_data = export_to_csv(st.session_state.analyzed_articles)
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name=f"php_forex_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# Main content area
if not st.session_state.analyzed_articles:
    st.info("👆 Use the sidebar to scrape and analyze news on any topic")
    
    # Show sample instructions
    with st.expander("ℹ️ How to use this application"):
        st.markdown("""
        1. **Set Date Range**: Choose the period for news analysis
        2. **Select Sources**: Pick reliable news sources
        3. **Enter Topic**: Type in the subject you want to analyze (e.g., "climate change", "artificial intelligence", "cryptocurrency")
        4. **Scrape & Analyze**: Click the button to fetch and analyze news
        5. **Review Results**: Explore insights in the dashboard below
        6. **Export Data**: Download results as CSV for further analysis
        """)
else:
    # Display results
    st.header("📊 Analysis Dashboard")
    
    if st.session_state.last_update:
        st.caption(f"Last updated: {st.session_state.last_update.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Articles", len(st.session_state.analyzed_articles))
    with col2:
        sentiments = [article.get('sentiment', 'neutral') for article in st.session_state.analyzed_articles]
        positive_count = sentiments.count('positive')
        st.metric("Positive Sentiment", positive_count)
    with col3:
        negative_count = sentiments.count('negative')
        st.metric("Negative Sentiment", negative_count)
    with col4:
        neutral_count = sentiments.count('neutral')
        st.metric("Neutral Sentiment", neutral_count)
    
    # Overall topic analysis
    st.subheader("🎯 Overall Topic Analysis")
    try:
        overall_analysis = analyzer.generate_overall_analysis(st.session_state.analyzed_articles)
        st.info(overall_analysis)
    except Exception as e:
        st.error(f"Error generating overall analysis: {str(e)}")
    
    # Filters for detailed view
    st.subheader("🔍 Detailed Articles")
    
    col1, col2 = st.columns(2)
    with col1:
        sentiment_filter = st.selectbox(
            "Filter by sentiment:",
            options=["All", "Positive", "Negative", "Neutral"]
        )
    with col2:
        search_filter = st.text_input("Search in titles/content:")
    
    # Filter articles
    filtered_articles = st.session_state.analyzed_articles.copy()
    
    if sentiment_filter != "All":
        filtered_articles = [
            article for article in filtered_articles 
            if article.get('sentiment', '').lower() == sentiment_filter.lower()
        ]
    
    if search_filter:
        search_lower = search_filter.lower()
        filtered_articles = [
            article for article in filtered_articles 
            if search_lower in article.get('title', '').lower() or 
               search_lower in article.get('content', '').lower()
        ]
    
    # Display filtered articles
    if filtered_articles:
        for i, article in enumerate(filtered_articles):
            with st.expander(f"📰 {article.get('title', 'No Title')}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Source:** {article.get('source', 'Unknown')}")
                    st.markdown(f"**Published:** {format_date(article.get('published_date'))}")
                    st.markdown(f"**URL:** [{article.get('url', 'N/A')}]({article.get('url', '#')})")
                
                with col2:
                    sentiment = article.get('sentiment', 'neutral')
                    sentiment_color = {
                        'positive': '🟢',
                        'negative': '🔴',
                        'neutral': '🟡'
                    }.get(sentiment, '⚪')
                    st.markdown(f"**Sentiment:** {sentiment_color} {sentiment.title()}")
                    
                    confidence = article.get('confidence_score', 0)
                    st.markdown(f"**Confidence:** {confidence:.2f}")
                
                # Article summary
                st.markdown("**AI Summary:**")
                st.write(article.get('summary', 'No summary available'))
                
                # Key insights
                if article.get('key_insights'):
                    st.markdown("**Key Insights:**")
                    for insight in article.get('key_insights', []):
                        st.write(f"• {insight}")
                
                # Original content preview
                if st.checkbox(f"Show original content", key=f"show_content_{i}"):
                    st.markdown("**Original Content:**")
                    content = article.get('content', 'No content available')
                    st.text_area("", value=content[:1000] + ("..." if len(content) > 1000 else ""), 
                               height=200, key=f"content_{i}")
    else:
        st.info("No articles match the current filters.")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit and OpenAI GPT-5 | Analyze any news topic with AI-powered insights")
