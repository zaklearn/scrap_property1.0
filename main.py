#!/usr/bin/env python3
"""
OnTheMarket Aligned Scraper - Fixed URL Structure
Properly aligned with OnTheMarket's actual URL patterns and parameters

Requirements:
    pip install streamlit requests beautifulsoup4 lxml fake-useragent pandas plotly

Usage:
    streamlit run onthemarket_aligned_scraper.py

Author: Senior Python Developer - URL Aligned Version
Date: September 2025
"""

import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
import random
import pandas as pd
import plotly.express as px
from datetime import datetime
from urllib.parse import urljoin, quote_plus, urlparse, parse_qs
from fake_useragent import UserAgent
import logging
import re
import json

# Configure page
st.set_page_config(
    page_title="OnTheMarket Aligned Scraper",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('onthemarket_aligned.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

class OnTheMarketAlignedScraper:
    """Scraper aligned with OnTheMarket's actual URL structure and parameters"""
    
    def __init__(self):
        self.base_url = "https://www.onthemarket.com"
        self.session = requests.Session()
        self.setup_session()
        self.debug_info = {
            'urls_tested': [],
            'selectors_performance': {},
            'properties_found': 0,
            'pages_scraped': 0
        }
        
    def setup_session(self):
        """Setup session with realistic browser headers"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        self.session.headers.update(headers)
        self.session.timeout = (15, 45)
        logger.info("Session configured with realistic browser headers")
    
    def parse_example_url(self, url):
        """Parse an example URL to understand OnTheMarket's parameter structure"""
        logger.info(f"Analyzing URL structure: {url}")
        
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        query_params = parse_qs(parsed.query)
        
        # Extract components
        analysis = {
            'property_type': path_parts[0] if len(path_parts) > 0 else 'for-sale',
            'location': path_parts[2] if len(path_parts) > 2 else '',
            'parameters': {k: v[0] if len(v) == 1 else v for k, v in query_params.items()}
        }
        
        logger.info(f"URL Analysis: {analysis}")
        return analysis
    
    def build_aligned_url(self, location="", property_type="for-sale", min_price="", max_price="", 
                         min_bedrooms="", max_bedrooms="", property_types=None, radius="1.0"):
        """Build URL that matches OnTheMarket's actual structure"""
        
        logger.info(f"Building aligned URL with parameters:")
        logger.info(f"  Location: '{location}'")
        logger.info(f"  Property type: '{property_type}'")
        logger.info(f"  Price range: £{min_price} - £{max_price}")
        logger.info(f"  Bedrooms: {min_bedrooms} - {max_bedrooms}")
        logger.info(f"  Radius: {radius}")
        
        # Build base path: /for-sale/property/location/
        location_clean = location.strip().lower().replace(' ', '')
        
        # Handle different location formats
        if re.match(r'^[a-z]{1,2}\d[a-z\d]?\s*\d[a-z]{2}$', location.replace(' ', ''), re.I):
            # It's a postcode - use first part only (e.g., SW1A 1AA -> sw1a)
            postcode_area = re.match(r'^([a-z]{1,2}\d[a-z\d]?)', location.replace(' ', ''), re.I)
            if postcode_area:
                location_clean = postcode_area.group(1).lower()
        
        # Build URL path
        url_path = f"/{property_type}/property/{location_clean}/"
        
        # Build query parameters (matching OnTheMarket's format)
        params = []
        
        if max_price:
            params.append(f"max-price={max_price}")
        
        if min_bedrooms:
            params.append(f"min-bedrooms={min_bedrooms}")
        
        if min_price:
            params.append(f"min-price={min_price}")
        
        if max_bedrooms and max_bedrooms != min_bedrooms:
            params.append(f"max-bedrooms={max_bedrooms}")
        
        # Add OnTheMarket-specific parameters
        params.append("more-like-this=true")
        params.append(f"radius={radius}")
        
        # Property types filter if specified
        if property_types:
            for prop_type in property_types:
                params.append(f"property-type={prop_type}")
        
        # Combine URL
        query_string = "&".join(params) if params else ""
        full_url = f"{self.base_url}{url_path}"
        if query_string:
            full_url += f"?{query_string}"
        
        logger.info(f"Built URL: {full_url}")
        self.debug_info['urls_tested'].append(full_url)
        
        return full_url
    
    def get_page_safe(self, url, max_retries=3):
        """Fetch page with error handling and respect for rate limits"""
        for attempt in range(max_retries):
            try:
                # Respectful delay
                delay = random.uniform(2, 4)
                logger.info(f"Waiting {delay:.2f}s before request (attempt {attempt + 1})")
                time.sleep(delay)
                
                logger.info(f"Fetching: {url}")
                response = self.session.get(url)
                
                logger.info(f"Response: {response.status_code} ({len(response.content)} bytes)")
                
                # Check for redirects
                if response.history:
                    logger.info(f"Redirects: {[r.url for r in response.history]}")
                
                response.raise_for_status()
                
                # Quick content check
                content_text = response.text.lower()
                if 'property' in content_text:
                    property_count = content_text.count('property')
                    logger.info(f"Found {property_count} occurrences of 'property' in page")
                
                # Check for common blocking indicators
                blocking_indicators = ['blocked', 'captcha', 'robot', 'access denied']
                found_blocks = [indicator for indicator in blocking_indicators if indicator in content_text]
                if found_blocks:
                    logger.warning(f"Potential blocking detected: {found_blocks}")
                
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"All attempts failed for {url}")
                    return None
                time.sleep(random.uniform(3, 6))
        
        return None
    
    def find_property_elements_comprehensive(self, soup):
        """Comprehensive property element detection with OnTheMarket specifics"""
        logger.info("=== COMPREHENSIVE PROPERTY ELEMENT SEARCH ===")
        
        # OnTheMarket specific selectors (most likely to work)
        onthemarket_selectors = [
            'li[data-test="search-result"]',
            'div[data-test="search-result"]',
            'article[data-test="search-result"]',
            '[data-test*="property"]',
            '[data-test*="result"]',
            '.search-result',
            '.property-result'
        ]
        
        # Generic property selectors
        generic_selectors = [
            '.property-card',
            '.property-item',
            '.listing-card', 
            '.listing-item',
            '.property-listing',
            '.result-item',
            'article[class*="property"]',
            'div[class*="property"]',
            'li[class*="property"]'
        ]
        
        # Structural fallbacks
        fallback_selectors = [
            'article',
            'li[class]',
            'div[class*="card"]',
            'div[class*="item"]'
        ]
        
        all_selectors = onthemarket_selectors + generic_selectors + fallback_selectors
        
        for selector in all_selectors:
            try:
                elements = soup.select(selector)
                logger.info(f"Selector '{selector}': {len(elements)} elements")
                
                if elements:
                    # Validate elements contain property data
                    valid_elements = []
                    for elem in elements:
                        text = elem.get_text().lower()
                        # Check for property indicators
                        indicators = ['£', 'bed', 'bath', 'bedroom', 'price', 'property']
                        if any(indicator in text for indicator in indicators):
                            valid_elements.append(elem)
                    
                    logger.info(f"Selector '{selector}': {len(valid_elements)} valid property elements")
                    self.debug_info['selectors_performance'][selector] = len(valid_elements)
                    
                    if valid_elements:
                        logger.info(f"SUCCESS: Using selector '{selector}' with {len(valid_elements)} elements")
                        return valid_elements
                        
            except Exception as e:
                logger.error(f"Error with selector '{selector}': {e}")
        
        # Fallback: search by content
        logger.warning("No elements found with selectors, searching by content...")
        
        # Find elements containing price patterns
        price_elements = soup.find_all(text=re.compile(r'£[\d,]+'))
        if price_elements:
            logger.info(f"Found {len(price_elements)} price elements")
            
            # Get container elements
            containers = []
            for price_elem in price_elements:
                container = price_elem.parent
                # Go up a few levels to find the property container
                for _ in range(3):
                    if container and container.parent:
                        container = container.parent
                    else:
                        break
                
                if container and container not in containers:
                    containers.append(container)
            
            logger.info(f"Found {len(containers)} potential property containers")
            return containers[:20]  # Reasonable limit
        
        logger.error("No property elements found with any method")
        return []
    
    def extract_property_data_enhanced(self, element, index):
        """Enhanced property data extraction"""
        logger.debug(f"Parsing property {index + 1}")
        
        try:
            data = {}
            
            # Price extraction (multiple strategies)
            price_selectors = [
                '.price', '[data-test="price"]', '.property-price', 
                'span[class*="price"]', 'div[class*="price"]',
                '.price-qualifier', '.asking-price'
            ]
            
            for selector in price_selectors:
                price_elem = element.select_one(selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    if price_text and ('£' in price_text or any(c.isdigit() for c in price_text)):
                        data['price'] = price_text
                        break
            
            # Fallback price extraction
            if 'price' not in data:
                price_match = re.search(r'£[\d,]+(?:\.\d{2})?', element.get_text())
                if price_match:
                    data['price'] = price_match.group(0)
            
            # Title and URL
            title_selectors = [
                'h2 a', 'h3 a', 'h4 a',
                'a[data-test*="title"]', 'a[data-test*="property"]',
                '.property-title a', '.listing-title a',
                'a[href*="/details/"]', 'a[href*="/property/"]'
            ]
            
            for selector in title_selectors:
                title_elem = element.select_one(selector)
                if title_elem:
                    title = title_elem.get_text(strip=True)
                    href = title_elem.get('href', '')
                    
                    if title:
                        data['title'] = title
                    if href:
                        data['url'] = urljoin(self.base_url, href)
                    
                    if title:  # Found title, stop looking
                        break
            
            # Address
            address_selectors = [
                '.address', '.property-address', '.location',
                '[data-test="address"]', '[data-test="location"]',
                'span[class*="address"]', 'div[class*="location"]'
            ]
            
            for selector in address_selectors:
                addr_elem = element.select_one(selector)
                if addr_elem:
                    addr_text = addr_elem.get_text(strip=True)
                    if addr_text:
                        data['address'] = addr_text
                        break
            
            # Bedrooms
            bedroom_selectors = [
                '.bedrooms', '.beds', '[data-test="bedrooms"]',
                'span[class*="bed"]', 'div[class*="bed"]'
            ]
            
            for selector in bedroom_selectors:
                bed_elem = element.select_one(selector)
                if bed_elem:
                    bed_text = bed_elem.get_text(strip=True)
                    if bed_text:
                        data['bedrooms'] = bed_text
                        break
            
            # Fallback bedroom extraction
            if 'bedrooms' not in data:
                bed_match = re.search(r'(\d+)\s*bed(?:room)?s?', element.get_text(), re.I)
                if bed_match:
                    data['bedrooms'] = f"{bed_match.group(1)} bed{'room' if bed_match.group(1) == '1' else 'rooms'}"
            
            # Property type
            type_selectors = [
                '.property-type', '.type', '[data-test="property-type"]',
                'span[class*="type"]'
            ]
            
            for selector in type_selectors:
                type_elem = element.select_one(selector)
                if type_elem:
                    type_text = type_elem.get_text(strip=True)
                    if type_text:
                        data['property_type'] = type_text
                        break
            
            # Agent
            agent_selectors = [
                '.agent', '.agent-name', '.estate-agent',
                '[data-test="agent"]', 'span[class*="agent"]'
            ]
            
            for selector in agent_selectors:
                agent_elem = element.select_one(selector)
                if agent_elem:
                    agent_text = agent_elem.get_text(strip=True)
                    if agent_text:
                        data['agent'] = agent_text
                        break
            
            # Image
            img = element.select_one('img')
            if img:
                src = img.get('src') or img.get('data-src') or img.get('data-original')
                if src:
                    data['image_url'] = src if src.startswith('http') else urljoin(self.base_url, src)
            
            logger.debug(f"Property {index + 1} data: {data}")
            return data if data else None
            
        except Exception as e:
            logger.error(f"Error parsing property {index + 1}: {e}")
            return None
    
    def scrape_properties_aligned(self, search_url, max_properties=20, progress_callback=None):
        """Scrape properties using aligned URL structure"""
        logger.info(f"=== STARTING ALIGNED SCRAPING ===")
        logger.info(f"Target: {max_properties} properties from {search_url}")
        
        properties = []
        page = 1
        max_pages = 10
        
        while len(properties) < max_properties and page <= max_pages:
            # Build page URL
            if page == 1:
                url = search_url
            else:
                separator = '&' if '?' in search_url else '?'
                url = f"{search_url}{separator}page={page}"
            
            if progress_callback:
                progress_callback(f"Scraping page {page}... ({len(properties)} found)")
            
            logger.info(f"=== PAGE {page} ===")
            
            # Fetch page
            response = self.get_page_safe(url)
            if not response:
                logger.error(f"Failed to fetch page {page}")
                break
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Save debug HTML
            with open(f'debug_aligned_page_{page}.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info(f"Saved debug HTML: debug_aligned_page_{page}.html")
            
            # Find property elements
            property_elements = self.find_property_elements_comprehensive(soup)
            
            if not property_elements:
                logger.warning(f"No property elements found on page {page}")
                break
            
            # Parse properties
            page_properties = []
            for i, element in enumerate(property_elements):
                if len(properties) + len(page_properties) >= max_properties:
                    break
                
                prop_data = self.extract_property_data_enhanced(element, len(properties) + i)
                if prop_data:
                    page_properties.append(prop_data)
            
            if page_properties:
                properties.extend(page_properties)
                logger.info(f"Page {page}: Found {len(page_properties)} properties. Total: {len(properties)}")
                self.debug_info['properties_found'] += len(page_properties)
            else:
                logger.warning(f"Page {page}: No valid properties parsed")
                break
            
            self.debug_info['pages_scraped'] = page
            page += 1
        
        logger.info(f"=== SCRAPING COMPLETED ===")
        logger.info(f"Total properties: {len(properties)}")
        logger.info(f"Pages scraped: {self.debug_info['pages_scraped']}")
        
        return properties[:max_properties]

def main():
    """Main Streamlit application"""
    
    st.title("🎯 OnTheMarket Aligned Scraper")
    st.markdown("### Properly Aligned with OnTheMarket's URL Structure")
    st.markdown("---")
    
    # Initialize scraper
    if 'scraper' not in st.session_state:
        st.session_state.scraper = OnTheMarketAlignedScraper()
    
    # URL Analysis Section
    with st.expander("🔍 URL Analysis Tool", expanded=True):
        st.markdown("**Test with a real OnTheMarket URL to verify alignment:**")
        
        example_url = st.text_input(
            "Paste OnTheMarket URL:",
            value="https://www.onthemarket.com/for-sale/property/tw7/?max-price=375000&min-bedrooms=1&min-price=230000&more-like-this=true&radius=1.0",
            help="Paste a real OnTheMarket search URL to analyze its structure"
        )
        
        if st.button("🔍 Analyze URL"):
            analysis = st.session_state.scraper.parse_example_url(example_url)
            st.json(analysis)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🎯 Aligned Search Parameters")
        
        # Location
        location = st.text_input(
            "📍 Location",
            value="TW7",
            placeholder="e.g., TW7, SW1A, London",
            help="Use postcode area (TW7) or city name"
        )
        
        # Property type
        property_type = st.selectbox(
            "🏘️ Property Type",
            ["for-sale", "to-rent"],
            format_func=lambda x: "For Sale 🏡" if x == "for-sale" else "To Rent 🏠"
        )
        
        # Price range (aligned with OnTheMarket parameters)
        st.markdown("**💰 Price Range**")
        col1, col2 = st.columns(2)
        
        with col1:
            min_price = st.selectbox(
                "Min Price",
                ["", "100000", "150000", "200000", "230000", "250000", "300000"],
                index=4,  # Default to 230000 like the example
                format_func=lambda x: "Any" if x == "" else f"£{int(x):,}"
            )
        
        with col2:
            max_price = st.selectbox(
                "Max Price",
                ["", "300000", "350000", "375000", "400000", "500000", "750000"],
                index=3,  # Default to 375000 like the example
                format_func=lambda x: "Any" if x == "" else f"£{int(x):,}"
            )
        
        # Bedrooms (aligned with min-bedrooms parameter)
        st.markdown("**🛏️ Bedrooms**")
        col1, col2 = st.columns(2)
        
        with col1:
            min_bedrooms = st.selectbox(
                "Min Bedrooms",
                ["", "1", "2", "3", "4", "5"],
                index=1,  # Default to 1 like the example
                format_func=lambda x: "Any" if x == "" else f"{x}+ bed{'room' if x == '1' else 'rooms'}"
            )
        
        with col2:
            max_bedrooms = st.selectbox(
                "Max Bedrooms",
                ["", "1", "2", "3", "4", "5", "6+"],
                format_func=lambda x: "Any" if x == "" else f"{x} bed{'room' if x == '1' else 'rooms'}"
            )
        
        # Additional OnTheMarket parameters
        radius = st.selectbox(
            "📍 Search Radius",
            ["0.25", "0.5", "1.0", "3.0", "5.0", "10.0", "15.0"],
            index=2,  # Default to 1.0 like the example
            format_func=lambda x: f"{x} miles"
        )
        
        # Property types filter
        property_types = st.multiselect(
            "🏠 Property Types",
            ["houses", "flats", "bungalows", "land", "commercial"],
            help="Leave empty for all types"
        )
        
        # Scraping options
        max_properties = st.slider(
            "📊 Properties to Scrape",
            min_value=5,
            max_value=50,
            value=20
        )
        
        # Search button
        search_button = st.button("🎯 Search Properties (Aligned)", type="primary")
    
    # Main content
    if search_button:
        if not location.strip():
            st.error("⚠️ Please enter a location")
            st.stop()
        
        # Build aligned URL
        search_url = st.session_state.scraper.build_aligned_url(
            location=location,
            property_type=property_type,
            min_price=min_price,
            max_price=max_price,
            min_bedrooms=min_bedrooms,
            max_bedrooms=max_bedrooms,
            property_types=property_types,
            radius=radius
        )
        
        st.info(f"🎯 Aligned URL: {search_url}")
        
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        def update_progress(message):
            status_text.text(message)
        
        # Scrape properties
        with st.spinner("🎯 Scraping with aligned URL structure..."):
            try:
                properties = st.session_state.scraper.scrape_properties_aligned(
                    search_url,
                    max_properties=max_properties,
                    progress_callback=update_progress
                )
                
                progress_bar.progress(1.0)
                status_text.text(f"✅ Found {len(properties)} properties!")
                
            except Exception as e:
                st.error(f"❌ Error: {e}")
                logger.error(f"Scraping failed: {e}", exc_info=True)
                st.stop()
        
        # Results
        if properties:
            st.session_state.properties = properties
            st.success(f"🎉 Successfully scraped {len(properties)} properties with aligned URL!")
            
            # Debug info
            with st.expander("🔧 Debug Information"):
                debug_info = st.session_state.scraper.debug_info
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Properties Found", debug_info['properties_found'])
                with col2:
                    st.metric("Pages Scraped", debug_info['pages_scraped'])
                with col3:
                    st.metric("URLs Tested", len(debug_info['urls_tested']))
                
                if debug_info['selectors_performance']:
                    st.subheader("Selector Performance")
                    perf_df = pd.DataFrame([
                        {'Selector': k, 'Elements Found': v} 
                        for k, v in debug_info['selectors_performance'].items()
                    ])
                    st.dataframe(perf_df)
                
                st.subheader("URLs Tested")
                for url in debug_info['urls_tested']:
                    st.code(url)
            
        else:
            st.warning("😔 No properties found with aligned URL structure")
            st.markdown("### 🔧 Debug Steps:")
            st.markdown("""
            1. **Check the generated URL** above - does it match OnTheMarket's format?
            2. **Try the URL manually** in your browser to see if it returns results
            3. **Check debug HTML files** saved in the current directory
            4. **Try different location formats** (e.g., 'TW7' vs 'Isleworth')
            """)
    
    # Display results if available
    if 'properties' in st.session_state and st.session_state.properties:
        properties = st.session_state.properties
        
        st.markdown("---")
        st.header("📊 Aligned Scraping Results")
        
        df = pd.DataFrame(properties)
        
        # Display tabs
        tab1, tab2, tab3 = st.tabs(["🏠 Properties", "📊 Data Quality", "📁 Export"])
        
        with tab1:
            # Property cards
            for i, prop in enumerate(properties):
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.markdown(f"**🏠 {prop.get('title', f'Property {i+1}')}**")
                        
                        if 'price' in prop:
                            st.markdown(f"💰 **{prop['price']}**")
                        
                        if 'bedrooms' in prop:
                            st.markdown(f"🛏️ {prop['bedrooms']}")
                        
                        if 'address' in prop:
                            st.markdown(f"📍 {prop['address']}")
                        
                        if 'property_type' in prop:
                            st.markdown(f"🏘️ {prop['property_type']}")
                        
                        if 'agent' in prop:
                            st.markdown(f"🏢 {prop['agent']}")
                        
                        if 'url' in prop:
                            st.markdown(f"[🔗 View Property]({prop['url']})")
                    
                    with col2:
                        if 'image_url' in prop:
                            try:
                                st.image(prop['image_url'], use_column_width=True)
                            except:
                                st.text("📷 Image not available")
                    
                    st.markdown("---")
        
        with tab2:
            # Data quality analysis
            st.subheader("📊 Data Quality Report")
            
            fields = ['title', 'price', 'bedrooms', 'address', 'property_type', 'agent', 'url', 'image_url']
            
            quality_data = []
            for field in fields:
                count = sum(1 for prop in properties if prop.get(field))
                percentage = (count / len(properties)) * 100 if properties else 0
                quality_data.append({
                    'Field': field,
                    'Count': count,
                    'Total': len(properties),
                    'Percentage': percentage
                })
            
            quality_df = pd.DataFrame(quality_data)
            
            # Display quality metrics
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    quality_df, 
                    x='Field', 
                    y='Percentage',
                    title="Field Completeness (%)",
                    color='Percentage',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Field Completeness:**")
                for _, row in quality_df.iterrows():
                    st.progress(
                        row['Percentage'] / 100,
                        text=f"{row['Field']}: {row['Count']}/{row['Total']} ({row['Percentage']:.1f}%)"
                    )
            
            # Overall quality score
            avg_completeness = quality_df['Percentage'].mean()
            st.metric(
                "Overall Data Quality Score",
                f"{avg_completeness:.1f}%",
                help="Average field completeness across all properties"
            )
            
            # Data sample
            st.subheader("📋 Data Sample")
            st.dataframe(df.head(10), use_container_width=True)
        
        with tab3:
            # Export options
            st.subheader("📁 Export Aligned Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # CSV download
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📊 Download CSV",
                    data=csv,
                    file_name=f"onthemarket_aligned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # JSON download
                json_data = df.to_json(orient='records', indent=2)
                st.download_button(
                    label="📋 Download JSON",
                    data=json_data,
                    file_name=f"onthemarket_aligned_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col3:
                # Debug log download
                try:
                    with open('onthemarket_aligned.log', 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    
                    st.download_button(
                        label="📋 Download Logs",
                        data=log_content,
                        file_name=f"onthemarket_aligned_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
                        mime="text/plain"
                    )
                except FileNotFoundError:
                    st.text("No log file available")
            
            # URL comparison
            st.subheader("🎯 URL Alignment Verification")
            st.markdown("**Generated URL vs Expected Format:**")
            
            if 'scraper' in st.session_state and st.session_state.scraper.debug_info['urls_tested']:
                generated_url = st.session_state.scraper.debug_info['urls_tested'][-1]
                st.code(generated_url, language='text')
                
                st.markdown("**Expected OnTheMarket Format:**")
                st.code("https://www.onthemarket.com/for-sale/property/tw7/?max-price=375000&min-bedrooms=1&min-price=230000&more-like-this=true&radius=1.0", language='text')
                
                # URL comparison analysis
                st.markdown("**URL Analysis:**")
                if 'more-like-this=true' in generated_url and 'radius=' in generated_url:
                    st.success("✅ URL includes OnTheMarket-specific parameters")
                else:
                    st.warning("⚠️ URL may be missing some OnTheMarket-specific parameters")
                
                if 'min-bedrooms=' in generated_url:
                    st.success("✅ URL uses correct bedroom parameter format")
                else:
                    st.warning("⚠️ URL may not use correct bedroom parameter format")

    # Instructions and tips
    if not ('properties' in st.session_state and st.session_state.properties):
        st.markdown("---")
        st.markdown("### 💡 Tips for Better Results:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **Location Format:**
            - Use postcode areas: `TW7`, `SW1A`, `M1`
            - Or city names: `London`, `Manchester`
            - Avoid full postcodes: `TW7 5DP` → use `TW7`
            """)
        
        with col2:
            st.markdown("""
            **Parameter Alignment:**
            - Min/Max prices match OnTheMarket format
            - Bedroom filters use `min-bedrooms` parameter
            - Includes `more-like-this=true` and `radius` parameters
            """)
        
        st.markdown("### 🔍 URL Structure Comparison:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**✅ Correct OnTheMarket Format:**")
            st.code("""
/for-sale/property/tw7/
?max-price=375000
&min-bedrooms=1
&min-price=230000
&more-like-this=true
&radius=1.0
            """)
        
        with col2:
            st.markdown("**❌ Common Mistakes:**")
            st.code("""
/for-sale/TW7+5DP/          # Wrong path
?bedrooms=1                 # Wrong parameter
&price_min=230000          # Wrong format
# Missing more-like-this
# Missing radius
            """)

if __name__ == "__main__":
    main()
                