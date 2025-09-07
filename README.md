# 📰 AI News Analyzer

A powerful Streamlit-based web application that provides real-time analysis of news articles on any topic using AI-powered insights. The application scrapes news from multiple sources, processes content using OpenAI's GPT models, and presents comprehensive sentiment analysis, market impact assessments, and key insights through an interactive dashboard.

## 🌟 Features

- **Multi-Source News Scraping**: Fetches articles from RSS feeds of major news outlets including BBC, Reuters, CNN, AP News, and technology-focused sources like TechCrunch and The Verge
- **AI-Powered Analysis**: Uses OpenAI's GPT-4o model for:
  - Sentiment analysis with confidence scoring
  - Article summarization
  - Key insights extraction
  - Market impact assessment
- **Interactive Dashboard**: User-friendly Streamlit interface with:
  - Date range filtering
  - Source selection
  - Real-time search and analysis
  - Export functionality
- **Data Processing**: Advanced text processing and deduplication
- **Export Capabilities**: Download analyzed results as CSV files

## 🏗️ Architecture

### Core Components

1. **NewsScraper**: Handles web scraping from RSS feeds and Google News
2. **LLMAnalyzer**: Processes articles through OpenAI's API for AI analysis
3. **DataProcessor**: Converts raw data into structured pandas DataFrames
4. **Streamlit App**: Interactive web interface for user interactions
5. **Utilities**: Helper functions for data export, formatting, and text processing

### Technology Stack

- **Frontend**: Streamlit (Interactive web framework)
- **Backend**: Python 3.11+
- **AI/ML**: OpenAI GPT-4o API
- **Data Processing**: Pandas, Trafilatura
- **Web Scraping**: Requests, Feedparser
- **Deployment**: Replit with auto-scaling support

## 🚀 Quick Start

1. **Set Environment Variables**:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   streamlit run app.py --server.port 5000
   ```

4. **Access the Interface**: Open your browser to `http://localhost:5000`

## 📋 Usage

1. **Set Date Range**: Choose the time period for news analysis
2. **Select Sources**: Pick from available news sources (General news or Tech-focused)
3. **Enter Topic**: Type the subject you want to analyze (e.g., "artificial intelligence", "climate change", "cryptocurrency")
4. **Scrape & Analyze**: Click the button to fetch and analyze news articles
5. **Review Results**: Explore insights in the comprehensive dashboard
6. **Export Data**: Download results as CSV for further analysis

## 📊 Analysis Features

- **Sentiment Analysis**: Classifies articles as positive, negative, or neutral with confidence scores
- **Market Impact**: Assesses potential impact on relevant industries or stakeholders
- **Key Insights**: Extracts actionable insights and important facts
- **Article Summaries**: AI-generated concise summaries of each article
- **Overall Analysis**: Comprehensive topic assessment based on all analyzed articles

## 🔧 Configuration

The application uses several configuration files:

- `.streamlit/config.toml`: Streamlit server configuration
- `pyproject.toml`: Project dependencies and metadata
- `.replit`: Replit deployment configuration

## 📚 API Documentation

The application consists of four main Python modules:

- `news_scraper.py`: News scraping functionality
- `llm_analyzer.py`: AI analysis using OpenAI
- `data_processor.py`: Data processing and manipulation
- `utils.py`: Utility functions and helpers

For detailed API documentation, see [API.md](API.md).

## 🎯 Supported News Sources

### General News Sources
- BBC News
- Reuters
- CNN
- AP News
- Yahoo News
- Google News

### Technology Sources
- TechCrunch
- The Verge
- Ars Technica
- Wired
- Engadget

## 🛠️ Development

The codebase follows Python best practices with:
- Type hints for better code documentation
- Comprehensive error handling
- Modular design for easy maintenance
- Caching for improved performance

## 🚨 Known Limitations

- Web scraping functionality may be affected by changes to news website structures
- Rate limiting is in place to respect news sources' servers
- OpenAI API key is required for AI analysis features
- Some news sources may require additional configuration

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style conventions
- Functions include proper docstrings
- Error handling is implemented
- Changes are tested thoroughly

## 📄 License

This project is available under the MIT License. See LICENSE file for details.

## 🔗 Links

- [Installation Guide](INSTALLATION.md)
- [Usage Guide](USAGE.md)
- [API Documentation](API.md)
