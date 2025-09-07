# 📖 Usage Guide

This comprehensive guide explains how to use the AI News Analyzer effectively to get the best insights from news analysis.

## 🎯 Overview

The AI News Analyzer is designed to help you:
- Monitor news trends on any topic
- Analyze sentiment and market impact
- Extract key insights from multiple sources
- Generate comprehensive topic assessments
- Export data for further analysis

## 🚀 Getting Started

### 1. Launch the Application
```bash
streamlit run app.py
```
Access the interface at `http://localhost:8501`

### 2. Interface Overview
- **Sidebar**: Controls and filters
- **Main Area**: Results dashboard and article details
- **Header**: Application title and description

## 🛠️ Step-by-Step Usage

### Step 1: Configure Date Range
1. In the sidebar, locate the "Date Range" section
2. Set **"From"** date (default: 7 days ago)
3. Set **"To"** date (default: today)
4. **Tip**: Shorter date ranges provide more focused results

### Step 2: Select News Sources
1. Find the "News Sources" multiselect box
2. Choose from available options:
   - **General News**: BBC, Reuters, CNN, AP News, Yahoo, Google News
   - **Tech Sources**: TechCrunch, The Verge, Ars Technica, Wired, Engadget
3. **Recommended**: Select 3-5 sources for balanced coverage
4. **Default**: Google News, TechCrunch, The Verge

### Step 3: Enter Search Topic
1. In the "Search Topic" field, enter your topic of interest
2. **Examples**:
   - Single terms: `iPhone`, `Bitcoin`, `AI`
   - Multiple terms: `climate change, renewable energy`
   - Specific topics: `iPhone 15 Pro`, `Tesla earnings`
3. **Tips**:
   - Use specific keywords for focused results
   - Avoid overly broad terms like "news"
   - Separate multiple keywords with commas

### Step 4: Scrape & Analyze
1. Click **"🔍 Scrape & Analyze News"**
2. Wait for the scraping process (usually 30-60 seconds)
3. Progress indicators will show:
   - Article scraping progress
   - AI analysis progress
4. **Note**: Processing time depends on the number of articles found

## 📊 Understanding the Results

### Summary Metrics
The dashboard displays four key metrics:
- **Total Articles**: Number of articles analyzed
- **Positive Sentiment**: Articles with positive outlook
- **Negative Sentiment**: Articles with negative outlook
- **Neutral Sentiment**: Articles with balanced/neutral tone

### Overall Topic Analysis
- AI-generated comprehensive assessment
- Covers sentiment trends, key factors, and outlook
- Based on analysis of all retrieved articles
- Provides high-level insights and takeaways

### Article Filters
Use filters to focus on specific content:
- **Sentiment Filter**: Show only positive, negative, or neutral articles
- **Search Filter**: Find articles containing specific keywords in title/content

### Individual Article Analysis
Each article shows:
- **Source and Publication Info**: Origin and date
- **Sentiment with Confidence**: AI sentiment classification with confidence level
- **AI Summary**: Concise 2-3 sentence summary
- **Key Insights**: Bullet points of important findings
- **Original Content**: Full article text (expandable)

## 💡 Best Practices

### Topic Selection
- **Specific is Better**: "Tesla stock price" vs "Tesla"
- **Current Events**: Recent topics yield more articles
- **Multiple Angles**: Try related keywords for comprehensive coverage
- **Industry Terms**: Use terminology specific to your domain

### Source Selection
- **Balanced Mix**: Combine general and specialized sources
- **Quality over Quantity**: 3-5 good sources better than 10 random ones
- **Topic Relevance**: Tech sources for tech topics, financial sources for finance

### Date Range Optimization
- **Breaking News**: 1-3 days for recent events
- **Trend Analysis**: 1-2 weeks for topic trends
- **Comprehensive View**: 1 month for thorough analysis
- **Avoid**: Very long ranges may include outdated information

### Analysis Interpretation
- **Confidence Scores**: Higher confidence (>0.7) indicates more reliable sentiment
- **Multiple Sources**: Cross-reference insights across different sources
- **Context Matters**: Consider external factors affecting sentiment
- **Market Impact**: High impact articles warrant deeper investigation

## 📈 Advanced Features

### Export Functionality
1. After analysis, click **"📥 Export Results"**
2. Click **"Download CSV"** to save results
3. CSV includes all analyzed data:
   - Article metadata (title, source, date, author, URL)
   - AI analysis (sentiment, confidence, market impact)
   - Summaries and key insights
   - Content statistics

### CSV Data Structure
```
Title, Source, Published Date, Author, URL, Sentiment, 
Confidence Score, Market Impact, Summary, Key Insights, Content Length
```

### Data Analysis Tips
- Import CSV into Excel/Google Sheets for further analysis
- Create pivot tables for sentiment distribution
- Filter by confidence scores for reliable data
- Use market impact for prioritization

## 🎨 Customization Options

### Search Strategies
1. **Broad to Narrow**: Start general, then refine
2. **Competitor Analysis**: Compare sentiment across companies
3. **Event Impact**: Before/after major announcements
4. **Seasonal Trends**: Holiday shopping, earnings seasons

### Source Combinations
- **Tech Analysis**: All tech sources + Google News
- **Financial News**: Reuters + AP News + Google News  
- **Comprehensive**: Mix of all general sources
- **Niche Topics**: Select sources relevant to your domain

## 🔍 Troubleshooting Usage Issues

### Few or No Articles Found
- **Broaden Keywords**: Try more general terms
- **Extend Date Range**: Look back further
- **Check Spelling**: Verify topic keywords
- **Try Alternatives**: Use synonyms or related terms

### Analysis Errors
- **Network Issues**: Check internet connection
- **API Limits**: Wait and try again if rate limited
- **Content Issues**: Some articles may be behind paywalls

### Performance Issues
- **Reduce Sources**: Select fewer news sources
- **Shorter Date Range**: Limit time period
- **Specific Topics**: Avoid overly broad searches
- **Clear Cache**: Refresh the page if needed

## 💼 Use Cases and Examples

### Business Intelligence
**Topic**: `"Apple quarterly earnings"`
**Sources**: Reuters, AP News, Google News
**Date Range**: Last 7 days around earnings announcement
**Goal**: Understand market reaction to financial results

### Market Research
**Topic**: `"electric vehicle sales"`
**Sources**: TechCrunch, The Verge, Reuters
**Date Range**: Last 30 days
**Goal**: Track industry trends and consumer sentiment

### Competitive Analysis
**Topic**: `"ChatGPT vs Google Bard"`
**Sources**: TechCrunch, Wired, Ars Technica
**Date Range**: Last 14 days
**Goal**: Compare public perception of competing products

### Crisis Monitoring
**Topic**: `"data breach security"`
**Sources**: All tech sources + CNN
**Date Range**: Last 3 days
**Goal**: Monitor security incident developments

## 📚 Tips for Better Results

### Keyword Strategies
- Use brand names: `"Microsoft"` instead of `"software company"`
- Include context: `"iPhone 15 camera"` vs just `"camera"`
- Try abbreviations: Both `"AI"` and `"artificial intelligence"`
- Consider variations: `"crypto"`, `"cryptocurrency"`, `"Bitcoin"`

### Timing Considerations
- **US News**: Analyze during US business hours
- **Global Events**: Consider timezone differences
- **Weekend News**: May have different sentiment patterns
- **Holiday Periods**: Reduced news volume

### Quality Assessment
- **Cross-Reference**: Compare similar articles from different sources
- **Confidence Scores**: Focus on high-confidence analyses
- **Source Credibility**: Weight established sources more heavily
- **Recency**: More recent articles may be more relevant

## 🚀 Next Steps

After mastering basic usage:
1. **Experiment** with different topic combinations
2. **Export** data for deeper analysis in spreadsheet tools
3. **Monitor** topics regularly for trend analysis
4. **Combine** with other research methods for comprehensive insights
5. **Share** findings with teams using exported CSV data

## 🤝 Getting Help

If you need assistance:
- Review this usage guide thoroughly
- Check the [Installation Guide](INSTALLATION.md) for setup issues
- Refer to [API Documentation](API.md) for technical details
- Report bugs or request features via GitHub issues