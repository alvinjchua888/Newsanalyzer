# 📦 Installation Guide

This guide provides detailed instructions for setting up the AI News Analyzer on different platforms.

## 📋 Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Internet connection for news scraping
- 512MB+ RAM recommended

## 🔧 Environment Setup

### 1. Python Environment

**Option A: Using Virtual Environment (Recommended)**
```bash
# Create virtual environment
python -m venv newsanalyzer-env

# Activate virtual environment
# On Windows:
newsanalyzer-env\Scripts\activate
# On macOS/Linux:
source newsanalyzer-env/bin/activate
```

**Option B: Using Conda**
```bash
# Create conda environment
conda create -n newsanalyzer python=3.11
conda activate newsanalyzer
```

### 2. Clone Repository

```bash
git clone https://github.com/alvinjchua888/Newsanalyzer.git
cd Newsanalyzer
```

## 📦 Dependencies Installation

### Method 1: Using UV (Fastest - Recommended)
```bash
# Install uv package manager
pip install uv

# Install dependencies
uv sync
```

### Method 2: Using pip with pyproject.toml
```bash
pip install -e .
```

### Method 3: Manual Installation
```bash
pip install streamlit>=1.49.1
pip install openai>=1.106.1
pip install pandas>=2.3.2
pip install requests>=2.32.5
pip install trafilatura>=2.0.0
pip install feedparser>=6.0.11
pip install anthropic>=0.66.0
```

## 🔐 API Key Configuration

### OpenAI API Key Setup

1. **Get API Key**:
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create an account or sign in
   - Generate a new API key

2. **Set Environment Variable**:

**Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=your_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your_api_key_here"
```

**macOS/Linux (Bash):**
```bash
export OPENAI_API_KEY="your_api_key_here"
```

3. **Persistent Configuration**:

**Windows (.env file):**
Create `.env` file in project root:
```
OPENAI_API_KEY=your_api_key_here
```

**macOS/Linux (.bashrc/.zshrc):**
```bash
echo 'export OPENAI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

## 🚀 Running the Application

### Development Mode
```bash
streamlit run app.py
```

### Production Mode
```bash
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

### Custom Configuration
```bash
streamlit run app.py --server.port 8501 --server.headless true
```

## 🐳 Docker Installation (Optional)

### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync

COPY . .

EXPOSE 5000

CMD ["streamlit", "run", "app.py", "--server.port", "5000", "--server.address", "0.0.0.0"]
```

### 2. Build and Run
```bash
# Build image
docker build -t newsanalyzer .

# Run container
docker run -p 5000:5000 -e OPENAI_API_KEY=your_key_here newsanalyzer
```

## ☁️ Cloud Deployment

### Streamlit Cloud
1. Fork the repository on GitHub
2. Connect to [Streamlit Cloud](https://streamlit.io/cloud)
3. Add `OPENAI_API_KEY` in secrets management
4. Deploy from your forked repository

### Replit (Current Setup)
1. Fork the Replit project
2. Set `OPENAI_API_KEY` in Secrets tab
3. Click Run to start the application

### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_key_here
   git push heroku main
   ```

## ✅ Verification

### 1. Test Installation
```bash
python -c "import streamlit; import openai; import pandas; print('All dependencies installed successfully!')"
```

### 2. Test API Key
```bash
python -c "import os; print('API Key configured:', bool(os.getenv('OPENAI_API_KEY')))"
```

### 3. Launch Application
```bash
streamlit run app.py
```
Navigate to `http://localhost:8501` and verify the interface loads correctly.

## 🔧 Troubleshooting

### Common Issues

**Issue: ModuleNotFoundError**
```bash
# Solution: Reinstall dependencies
pip install --upgrade -r requirements.txt
```

**Issue: OpenAI API Key Error**
```bash
# Solution: Verify environment variable
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows
```

**Issue: Streamlit Port Already in Use**
```bash
# Solution: Use different port
streamlit run app.py --server.port 8502
```

**Issue: Web Scraping Failures**
- Check internet connection
- Some news sources may block automated requests
- Try different news sources in the interface

### Performance Optimization

1. **Increase RAM** if processing many articles
2. **Use SSD storage** for better I/O performance
3. **Stable internet connection** for API calls
4. **Consider API rate limits** for OpenAI usage

## 🆘 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review the [Usage Guide](USAGE.md)
3. Check existing GitHub issues
4. Create a new issue with:
   - Python version
   - Operating system
   - Error messages
   - Steps to reproduce

## 📚 Next Steps

After successful installation:
- Read the [Usage Guide](USAGE.md)
- Explore the [API Documentation](API.md)
- Try analyzing different news topics
- Customize the news sources for your needs