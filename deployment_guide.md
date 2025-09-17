# 🚀 OnTheMarket Scraper - Deployment Guide

## 📁 Project Structure

```
onthemarket-scraper/
├── 📄 requirements.txt
├── 📄 onthemarket_aligned_scraper.py  # Main application
├── 📄 README.md
├── 📄 .gitignore
├── 📁 .streamlit/
│   └── 📄 config.toml
├── 📁 docs/
│   └── 📄 deployment.md
└── 📁 examples/
    ├── 📄 sample_data.csv
    └── 📄 example_urls.txt
```

## 🛠️ Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/onthemarket-scraper.git
cd onthemarket-scraper
```

### 2. Create Virtual Environment
```bash
# Using venv
python -m venv onthemarket-env
source onthemarket-env/bin/activate  # On Windows: onthemarket-env\Scripts\activate

# Using conda
conda create -n onthemarket-env python=3.9
conda activate onthemarket-env
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Locally
```bash
streamlit run onthemarket_aligned_scraper.py
```

## ☁️ Streamlit Cloud Deployment

### 1. Prepare Repository

**Create these files in your repository:**

#### `.gitignore`
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Streamlit
.streamlit/secrets.toml

# Logs
*.log
debug_*.html

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data files (optional - include if you don't want to commit scraped data)
*.csv
*.json
data/
```

#### `README.md`
```markdown
# 🏠 OnTheMarket Property Scraper

An interactive Streamlit application for scraping UK property data from OnTheMarket.com with proper URL alignment and comprehensive debugging.

## 🚀 Features

- **Aligned URL Structure**: Properly matches OnTheMarket's actual URL format
- **Interactive Dashboard**: User-friendly interface with real-time progress
- **Comprehensive Data**: Extracts price, bedrooms, address, agent, and more
- **Export Options**: Download data as CSV or JSON
- **Debug Tools**: Detailed logging and HTML inspection

## 📊 Live Demo

🔗 **[Try the Live App](https://your-app-name.streamlit.app/)**

## 🛠️ Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/onthemarket-scraper.git
cd onthemarket-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run onthemarket_aligned_scraper.py
```

## 📋 Usage

1. **Enter Location**: Use postcode areas (TW7, SW1A) or city names
2. **Set Filters**: Configure price range, bedrooms, and radius
3. **Start Scraping**: Click "Search Properties" to begin
4. **Analyze Results**: View properties, analytics, and export data

## ⚠️ Important Notes

- **Respectful Scraping**: Includes rate limiting and delays
- **Terms of Service**: Please respect OnTheMarket's terms of use
- **Educational Purpose**: Designed for learning web scraping techniques
- **No Warranties**: Use at your own risk

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit changes (`git commit -am 'Add improvement'`)
4. Push to branch (`git push origin feature/improvement`)
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔧 Technical Details

- **Python**: 3.8+
- **Framework**: Streamlit
- **Scraping**: BeautifulSoup4 + Requests
- **Data**: Pandas + Plotly for visualization

## 🐛 Troubleshooting

- **No Properties Found**: Check URL alignment and website structure
- **Rate Limiting**: Increase delays between requests
- **Missing Data**: Verify CSS selectors in debug logs

## 📞 Support

If you encounter issues:
1. Check the [Issues](https://github.com/yourusername/onthemarket-scraper/issues) page
2. Enable debug logging for detailed information
3. Create a new issue with logs and reproduction steps
```

### 2. Deploy to Streamlit Cloud

1. **Push to GitHub**:
```bash
git add .
git commit -m "Initial commit: OnTheMarket scraper"
git push origin main
```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file: `onthemarket_aligned_scraper.py`
   - Click "Deploy!"

3. **Configuration**:
   - App will automatically use `requirements.txt`
   - Streamlit config in `.streamlit/config.toml` will be applied
   - App will be available at: `https://your-app-name.streamlit.app/`

## 🔧 Environment Variables (Optional)

If you need environment variables, create `.streamlit/secrets.toml`:

```toml
# .streamlit/secrets.toml (DO NOT COMMIT TO GIT)

[scraper]
user_agent = "Your Custom User Agent"
default_delay = 2
max_retries = 3

[app]
debug_mode = false
save_html = false
```

Access in code:
```python
import streamlit as st

# Access secrets
user_agent = st.secrets["scraper"]["user_agent"]
debug_mode = st.secrets["app"]["debug_mode"]
```

## 📱 Mobile Optimization

The app is automatically mobile-responsive, but you can enhance it:

```python
# Add to your Streamlit app
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    @media (max-width: 768px) {
        .main > div {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)
```

## 🚦 Performance Optimization

### For Streamlit Cloud:

1. **Caching**:
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_cached_data():
    return expensive_operation()
```

2. **Resource Management**:
```python
# Limit concurrent requests
import threading
semaphore = threading.Semaphore(2)  # Max 2 concurrent requests
```

3. **Memory Management**:
```python
# Clear large objects
import gc
del large_dataframe
gc.collect()
```

## 🔒 Security Best Practices

1. **Never commit sensitive data**:
   - Add secrets to `.streamlit/secrets.toml`
   - Include secrets.toml in `.gitignore`

2. **Rate limiting**:
   - Implement delays between requests
   - Respect robots.txt

3. **Error handling**:
   - Don't expose internal errors to users
   - Log errors securely

## 📈 Monitoring and Analytics

### Add analytics to your app:

```python
# Simple usage tracking
if "visits" not in st.session_state:
    st.session_state.visits = 0
st.session_state.visits += 1

# Display in sidebar
st.sidebar.info(f"Session visits: {st.session_state.visits}")
```

## 🎯 Custom Domain (Optional)

For custom domains:
1. Set up CNAME record pointing to your Streamlit app
2. Contact Streamlit support for custom domain setup
3. Update app settings in Streamlit Cloud dashboard

## 🔄 Automated Updates

Set up GitHub Actions for automated testing:

```yaml
# .github/workflows/test.yml
name: Test App
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Test imports
      run: |
        python -c "import streamlit; import requests; import beautifulsoup4"
```

## 📞 Getting Help

- **Streamlit Docs**: [docs.streamlit.io](https://docs.streamlit.io)
- **Community Forum**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: For app-specific problems

## 🎉 Success!

Your OnTheMarket scraper should now be live and accessible worldwide! 

**Next Steps**:
1. Test the deployed app thoroughly
2. Share the link with users
3. Monitor usage and performance
4. Iterate based on feedback

---

**Remember**: Always respect website terms of service and implement responsible scraping practices! 🤝