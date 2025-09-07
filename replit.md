# Philippine Peso Forex News Analyzer

## Overview

This is a Streamlit-based web application that provides real-time analysis of Philippine peso foreign exchange news using AI-powered insights. The application scrapes financial news from multiple sources, processes the content using OpenAI's GPT-5 model, and presents sentiment analysis, market impact assessments, and key insights through an interactive dashboard. Users can filter news by date range, sources, and search terms, then export analyzed data for further use.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Framework**: Single-page application with sidebar controls and main dashboard
- **Session State Management**: Uses Streamlit's session state to persist scraped articles and analysis results across user interactions
- **Caching Strategy**: Implements `@st.cache_resource` for component initialization to improve performance
- **Responsive Layout**: Wide layout with expandable sidebar for controls and filters

### Backend Architecture
- **Modular Component Design**: Separated into distinct classes for specific responsibilities:
  - `NewsScraper`: Handles web scraping from multiple news sources
  - `LLMAnalyzer`: Processes articles through OpenAI's GPT-5 for sentiment and insight extraction
  - `DataProcessor`: Converts raw article data into structured pandas DataFrames
- **Error Handling**: Graceful degradation when individual news sources fail or API calls timeout
- **Rate Limiting**: Built-in delays between requests to respect server limitations

### Data Processing Pipeline
- **Content Extraction**: Uses Trafilatura library for clean text extraction from web articles
- **Sentiment Analysis**: Multi-dimensional analysis including sentiment classification, confidence scoring, and market impact assessment
- **Duplicate Detection**: Title-similarity based deduplication across multiple sources
- **Data Transformation**: Converts unstructured news content into structured DataFrames with derived metrics

### AI Integration
- **OpenAI GPT-5**: Latest model for natural language processing and analysis
- **Multi-prompt Strategy**: Separate prompts for summary generation, sentiment analysis, key insight extraction, and market impact assessment
- **Structured Output**: Consistent JSON-formatted responses for reliable data processing

## External Dependencies

### Third-Party Services
- **OpenAI API**: GPT-5 model for article analysis and insight generation (requires `OPENAI_API_KEY` environment variable)

### News Sources
- **Financial News Websites**: Reuters, Bloomberg, CNN Philippines, Rappler, Inquirer, Manila Bulletin
- **Web Scraping**: Direct HTTP requests to news websites with respectful rate limiting

### Python Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis for structured article processing
- **Trafilatura**: Web content extraction and text cleaning
- **Requests**: HTTP client for web scraping operations
- **OpenAI**: Official client library for GPT API integration

### Data Export
- **CSV Export**: Built-in functionality to export analyzed articles in CSV format
- **Real-time Processing**: No persistent database - processes and analyzes articles on-demand