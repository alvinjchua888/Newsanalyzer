# 📚 API Documentation

This document provides comprehensive technical documentation for the AI News Analyzer's Python modules and classes.

## 🏗️ Architecture Overview

The application follows a modular design with four main components:

```
├── app.py              # Streamlit web interface
├── news_scraper.py     # News scraping functionality  
├── llm_analyzer.py     # AI analysis using OpenAI
├── data_processor.py   # Data processing and manipulation
└── utils.py           # Utility functions and helpers
```

---

## 📰 news_scraper.py

### Class: NewsScraper

Main class responsible for scraping news articles from various RSS feeds and Google News.

#### Constructor
```python
def __init__(self):
```
Initializes the scraper with predefined RSS sources and HTTP headers.

**Attributes:**
- `headers`: HTTP headers for web requests
- `rss_sources`: Dictionary of general news RSS feeds
- `tech_rss_sources`: Dictionary of technology-focused RSS feeds

#### Methods

##### scrape_news()
```python
def scrape_news(self, search_terms: List[str], sources: List[str], 
               start_date: datetime, end_date: datetime, max_articles: int = 20) -> List[Dict[str, Any]]
```

Scrapes news articles from multiple sources using RSS feeds and Google News search.

**Parameters:**
- `search_terms`: List of keywords to search for
- `sources`: List of news source names to scrape from
- `start_date`: Start date for article filtering
- `end_date`: End date for article filtering  
- `max_articles`: Maximum number of articles to return (default: 20)

**Returns:**
- List of article dictionaries containing:
  - `title`: Article headline
  - `content`: Full article text
  - `source`: News source name
  - `url`: Article URL
  - `published_date`: Publication date
  - `author`: Article author

**Example:**
```python
scraper = NewsScraper()
articles = scraper.scrape_news(
    search_terms=["artificial intelligence"],
    sources=["TechCrunch", "The Verge"],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 7),
    max_articles=10
)
```

##### _search_google_news()
```python
def _search_google_news(self, search_query: str, max_articles: int = 10) -> List[Dict[str, Any]]
```

Searches Google News for articles matching the query.

**Parameters:**
- `search_query`: Combined search terms as string
- `max_articles`: Maximum articles to retrieve from Google News

**Returns:**
- List of article dictionaries

##### _scrape_rss_source()
```python
def _scrape_rss_source(self, source: str, search_terms: List[str], 
                      start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]
```

Scrapes articles from general news RSS feeds.

**Parameters:**
- `source`: Name of the news source
- `search_terms`: Keywords to filter articles
- `start_date`: Start date filter
- `end_date`: End date filter

**Returns:**
- List of relevant articles from the source

##### _extract_article_content()
```python
def _extract_article_content(self, url: str, source: str) -> Dict[str, Any]
```

Extracts content from a single article URL using Trafilatura.

**Parameters:**
- `url`: Article URL to scrape
- `source`: News source name

**Returns:**
- Article dictionary or None if extraction fails

##### _remove_duplicates()
```python
def _remove_duplicates(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]
```

Removes duplicate articles based on title similarity.

**Parameters:**
- `articles`: List of article dictionaries

**Returns:**
- Deduplicated list of articles

---

## 🤖 llm_analyzer.py

### Class: LLMAnalyzer

Handles AI-powered analysis of news articles using OpenAI's GPT models.

#### Constructor
```python
def __init__(self):
```
Initializes the analyzer with OpenAI client and model configuration.

**Attributes:**
- `model`: OpenAI model name ("gpt-4o")
- `client`: OpenAI API client instance

**Raises:**
- `ValueError`: If OPENAI_API_KEY environment variable is not set

#### Methods

##### analyze_article()
```python
def analyze_article(self, article: Dict[str, Any]) -> Dict[str, Any]
```

Performs comprehensive analysis of a single news article.

**Parameters:**
- `article`: Article dictionary containing 'content' and 'title' keys

**Returns:**
- Analysis dictionary containing:
  - `sentiment`: "positive", "negative", or "neutral"
  - `confidence_score`: Float between 0.0 and 1.0
  - `summary`: Concise article summary (2-3 sentences)
  - `key_insights`: List of important insights
  - `market_impact`: "high", "medium", "low", or "minimal"

**Example:**
```python
analyzer = LLMAnalyzer()
article = {
    'title': 'AI Breakthrough Announced',
    'content': 'Long article content here...'
}
analysis = analyzer.analyze_article(article)
print(f"Sentiment: {analysis['sentiment']}")
print(f"Summary: {analysis['summary']}")
```

##### _generate_summary()
```python
def _generate_summary(self, title: str, content: str) -> str
```

Generates concise summary focusing on key aspects.

**Parameters:**
- `title`: Article title
- `content`: Article content (truncated to 2000 chars)

**Returns:**
- 2-3 sentence summary string

##### _analyze_sentiment()
```python
def _analyze_sentiment(self, content: str) -> Dict[str, Any]
```

Analyzes sentiment with confidence scoring.

**Parameters:**
- `content`: Article content (truncated to 2000 chars)

**Returns:**
- Dictionary with:
  - `sentiment`: Sentiment classification
  - `confidence`: Confidence score (0.0-1.0)
  - `reasoning`: Brief explanation

##### _extract_key_insights()
```python
def _extract_key_insights(self, content: str) -> List[str]
```

Extracts 3-5 key insights from the article.

**Parameters:**
- `content`: Article content (truncated to 2000 chars)

**Returns:**
- List of insight strings

##### _assess_market_impact()
```python
def _assess_market_impact(self, content: str) -> str
```

Assesses potential market/industry impact.

**Parameters:**
- `content`: Article content (truncated to 1500 chars)

**Returns:**
- Impact level: "high", "medium", "low", or "minimal"

##### generate_overall_analysis()
```python
def generate_overall_analysis(self, analyzed_articles: List[Dict[str, Any]]) -> str
```

Generates comprehensive analysis based on multiple articles.

**Parameters:**
- `analyzed_articles`: List of articles with analysis results

**Returns:**
- Multi-paragraph analysis string covering trends, factors, outlook, and insights

---

## 📊 data_processor.py

### Class: DataProcessor

Processes and manipulates article data, converting to structured formats.

#### Constructor
```python
def __init__(self):
```
Simple constructor with no initialization parameters.

#### Methods

##### process_articles_to_dataframe()
```python
def process_articles_to_dataframe(self, articles: List[Dict[str, Any]]) -> pd.DataFrame
```

Converts articles list to pandas DataFrame with derived metrics.

**Parameters:**
- `articles`: List of analyzed article dictionaries

**Returns:**
- pandas DataFrame with columns:
  - Basic info: title, source, url, published_date, author
  - Metrics: content_length, sentiment, confidence_score
  - Analysis: summary, market_impact, key_insights
  - Derived: sentiment_score, weighted_sentiment

**Example:**
```python
processor = DataProcessor()
df = processor.process_articles_to_dataframe(analyzed_articles)
print(df.columns.tolist())
print(f"Shape: {df.shape}")
```

##### get_sentiment_summary()
```python
def get_sentiment_summary(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]
```

Generates summary statistics of sentiment analysis.

**Parameters:**
- `articles`: List of analyzed articles

**Returns:**
- Summary dictionary with:
  - `total_articles`: Total article count
  - `sentiment_distribution`: Count of each sentiment type
  - `average_confidence`: Mean confidence score
  - `overall_sentiment_score`: Weighted sentiment average
  - `sources`: List of unique sources
  - `date_range`: Earliest and latest publication dates

##### filter_articles()
```python
def filter_articles(self, articles: List[Dict[str, Any]], 
                   sentiment: str = None, source: str = None,
                   min_confidence: float = None) -> List[Dict[str, Any]]
```

Filters articles based on various criteria.

**Parameters:**
- `articles`: List of articles to filter
- `sentiment`: Filter by sentiment type ("positive", "negative", "neutral")
- `source`: Filter by news source name
- `min_confidence`: Minimum confidence score threshold

**Returns:**
- Filtered list of articles

##### get_top_insights()
```python
def get_top_insights(self, articles: List[Dict[str, Any]], top_n: int = 10) -> List[str]
```

Extracts and ranks most common insights across all articles.

**Parameters:**
- `articles`: List of analyzed articles
- `top_n`: Number of top insights to return

**Returns:**
- List of most frequent insights

##### calculate_market_impact_score()
```python
def calculate_market_impact_score(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]
```

Calculates overall market impact score based on all articles.

**Parameters:**
- `articles`: List of analyzed articles

**Returns:**
- Dictionary with:
  - `score`: Numerical impact score
  - `level`: Impact level classification
  - `factors`: List of high-impact articles

---

## 🛠️ utils.py

Collection of utility functions for data processing, formatting, and export.

### Export Functions

##### export_to_csv()
```python
def export_to_csv(articles: List[Dict[str, Any]]) -> str
```

Exports analyzed articles to CSV format.

**Parameters:**
- `articles`: List of analyzed article dictionaries

**Returns:**
- CSV data as string

**CSV Structure:**
```
Title, Source, Published Date, Author, URL, Sentiment, 
Confidence Score, Market Impact, Summary, Key Insights, Content Length
```

### Formatting Functions

##### format_date()
```python
def format_date(date_str: str) -> str
```

Formats date strings for consistent display.

**Parameters:**
- `date_str`: Date string in various formats

**Returns:**
- Formatted date string (YYYY-MM-DD HH:MM)

##### clean_text()
```python
def clean_text(text: str) -> str
```

Cleans text content by removing extra whitespace and special characters.

**Parameters:**
- `text`: Raw text content

**Returns:**
- Cleaned text string

##### truncate_text()
```python
def truncate_text(text: str, max_length: int = 100) -> str
```

Truncates text to specified length with ellipsis.

**Parameters:**
- `text`: Text to truncate
- `max_length`: Maximum character length (default: 100)

**Returns:**
- Truncated text with "..." if needed

### Validation Functions

##### validate_article_data()
```python
def validate_article_data(article: Dict[str, Any]) -> bool
```

Validates that article data contains required fields.

**Parameters:**
- `article`: Article dictionary to validate

**Returns:**
- Boolean indicating if article is valid

**Validation Checks:**
- Required fields: title, content, source
- Minimum content length: 100 characters

##### sanitize_filename()
```python
def sanitize_filename(filename: str) -> str
```

Sanitizes filename for safe file operations.

**Parameters:**
- `filename`: Original filename

**Returns:**
- Sanitized filename with invalid characters replaced

### Analysis Helpers

##### calculate_reading_time()
```python
def calculate_reading_time(text: str, words_per_minute: int = 200) -> int
```

Calculates estimated reading time in minutes.

**Parameters:**
- `text`: Article text content
- `words_per_minute`: Reading speed (default: 200)

**Returns:**
- Estimated reading time in minutes

##### get_sentiment_emoji()
```python
def get_sentiment_emoji(sentiment: str) -> str
```

Returns emoji representation of sentiment.

**Parameters:**
- `sentiment`: Sentiment string

**Returns:**
- Corresponding emoji (📈 for positive, 📉 for negative, etc.)

##### format_confidence_score()
```python
def format_confidence_score(score: float) -> str
```

Formats confidence score as percentage.

**Parameters:**
- `score`: Confidence score (0.0-1.0)

**Returns:**
- Formatted percentage string (e.g., "75.5%")

---

## 🖥️ app.py

### Main Streamlit Application

The main application file orchestrates the user interface and component interactions.

#### Key Functions

##### init_components()
```python
@st.cache_resource
def init_components():
```

Initializes and caches the main application components.

**Returns:**
- Tuple of (NewsScraper, LLMAnalyzer, DataProcessor) instances

#### Session State Management

The application maintains state across user interactions:

- `st.session_state.articles`: Raw scraped articles
- `st.session_state.analyzed_articles`: Articles with AI analysis
- `st.session_state.last_update`: Timestamp of last analysis

#### User Interface Components

1. **Sidebar Controls**: Date range, source selection, topic input
2. **Action Buttons**: Scrape & analyze, export functionality
3. **Results Dashboard**: Metrics, overall analysis, article details
4. **Filtering**: Sentiment and keyword filters for articles

---

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Required for LLM analysis functionality

### Dependencies

Core dependencies as defined in `pyproject.toml`:
- `streamlit>=1.49.1`: Web application framework
- `openai>=1.106.1`: OpenAI API client
- `pandas>=2.3.2`: Data manipulation
- `requests>=2.32.5`: HTTP client
- `trafilatura>=2.0.0`: Web content extraction
- `feedparser>=6.0.11`: RSS feed parsing
- `anthropic>=0.66.0`: Alternative AI model support

---

## 🚨 Error Handling

All classes implement comprehensive error handling:

1. **Network Errors**: Timeout and connection failures
2. **API Errors**: Rate limiting and authentication issues  
3. **Data Errors**: Malformed content and parsing failures
4. **Validation Errors**: Invalid input parameters

Error messages are logged and graceful fallbacks are provided where possible.

---

## 🔄 Usage Patterns

### Basic Workflow
```python
# Initialize components
scraper = NewsScraper()
analyzer = LLMAnalyzer() 
processor = DataProcessor()

# Scrape articles
articles = scraper.scrape_news(
    search_terms=["your topic"],
    sources=["TechCrunch", "Reuters"],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 7)
)

# Analyze articles
analyzed_articles = []
for article in articles:
    analysis = analyzer.analyze_article(article)
    analyzed_articles.append({**article, **analysis})

# Process results
df = processor.process_articles_to_dataframe(analyzed_articles)
summary = processor.get_sentiment_summary(analyzed_articles)
```

### Advanced Usage
```python
# Filter high-confidence positive articles
high_conf_positive = processor.filter_articles(
    analyzed_articles,
    sentiment="positive",
    min_confidence=0.8
)

# Get market impact analysis
impact_analysis = processor.calculate_market_impact_score(analyzed_articles)

# Generate overall assessment
overall = analyzer.generate_overall_analysis(analyzed_articles)

# Export results
csv_data = export_to_csv(analyzed_articles)
```

---

## 📈 Performance Considerations

- **Rate Limiting**: Built-in delays between requests
- **Caching**: Streamlit resource caching for component initialization
- **Content Limits**: Text truncation for API efficiency
- **Batch Processing**: Articles analyzed individually with progress tracking
- **Memory Management**: Session state cleanup between runs

---

## 🧪 Testing Recommendations

For each module, consider testing:

1. **NewsScraper**: Mock HTTP responses, test RSS parsing
2. **LLMAnalyzer**: Mock OpenAI API calls, validate response formats
3. **DataProcessor**: Test data transformations with sample data
4. **Utils**: Unit tests for individual utility functions
5. **Integration**: End-to-end workflow testing

---

## 🔗 External Dependencies

### News Sources
- RSS feeds from major news outlets
- Google News API (via RSS)
- Content extraction via HTTP requests

### AI Services
- OpenAI GPT-4o API for text analysis
- Anthropic Claude (configured but not actively used)

### Python Libraries
See `pyproject.toml` for complete dependency specifications with version constraints.