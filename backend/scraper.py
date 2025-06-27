# scraper.py
from playwright.sync_api import sync_playwright
import time
import os
from typing import List, Dict
import json

def fetch_uscis_page(url: str, timeout: int = 60000) -> str:
    """Fetch page content from a URL using Playwright."""
    content = ""
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Set user agent to avoid blocks
            page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            })
            
            page.goto(url, timeout=timeout)
            page.wait_for_load_state("networkidle", timeout=30000)
            
            # Remove navigation, footer, and other non-content elements
            page.evaluate("""
                // Remove common navigation and footer elements
                const selectors = ['nav', 'footer', '.navigation', '.nav', '.menu', '.sidebar', '.ads'];
                selectors.forEach(selector => {
                    document.querySelectorAll(selector).forEach(el => el.remove());
                });
            """)
            
            # Get main content - try multiple selectors
            content_selectors = [
                'main',
                '.content',
                '.main-content', 
                '#content',
                '.page-content',
                'body'
            ]
            
            for selector in content_selectors:
                try:
                    content = page.text_content(selector)
                    if content and len(content.strip()) > 100:  # Minimum content threshold
                        break
                except:
                    continue
            
            if not content:
                content = page.text_content("body")
            
            browser.close()
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    
    return content.strip() if content else ""

def chunk_text(text: str, max_tokens: int = 500, overlap: int = 50) -> List[str]:
    """Split text into overlapping chunks of approximately max_tokens tokens."""
    if not text.strip():
        return []
    
    # Simple word-based chunking (approximating tokens)
    words = text.split()
    chunks = []
    i = 0
    
    while i < len(words):
        chunk_words = words[i : i + max_tokens]
        chunk = " ".join(chunk_words)
        
        # Only add non-empty chunks with meaningful content
        if len(chunk.strip()) > 50:  # Minimum chunk size
            chunks.append(chunk.strip())
        
        i += max_tokens - overlap  # Move index for next chunk with overlap
        
        if i >= len(words):
            break
    
    return chunks

def scrape_immigration_content() -> List[Dict[str, str]]:
    """Scrape content from key immigration websites"""
    
    # Key immigration URLs to scrape
    urls = [
        # USCIS Policy Manual and key pages
        "https://www.uscis.gov/policy-manual/volume-7-part-a-chapter-2",  # Naturalization eligibility
        "https://www.uscis.gov/policy-manual/volume-7-part-a-chapter-3",  # Naturalization requirements  
        "https://www.uscis.gov/citizenship/learn-about-citizenship/citizenship-and-naturalization/naturalization-process",
        "https://www.uscis.gov/green-card/green-card-eligibility/green-card-for-immediate-relatives-of-us-citizen",
        "https://www.uscis.gov/working-in-the-united-states/h-1b-specialty-occupations",
        "https://www.uscis.gov/family/family-of-us-citizens/bringing-spouses-to-live-in-the-united-states-as-permanent-residents",
        
        # State Department visa information
        "https://travel.state.gov/content/travel/en/us-visas/immigrate/family-immigration.html",
        "https://travel.state.gov/content/travel/en/us-visas/immigrate/employment-based-immigrant-visas.html",
        "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/visa-bulletin.html",
        
        # Common USCIS FAQ pages
        "https://www.uscis.gov/citizenship/learn-about-citizenship/citizenship-and-naturalization/i-am-married-to-a-us-citizen",
        "https://www.uscis.gov/green-card/after-green-card-granted/international-travel-as-permanent-resident",
    ]
    
    all_content = []
    
    for url in urls:
        print(f"Scraping: {url}")
        try:
            content = fetch_uscis_page(url)
            if content:
                # Clean and chunk the content
                chunks = chunk_text(content, max_tokens=400, overlap=50)
                
                for i, chunk in enumerate(chunks):
                    all_content.append({
                        "text": chunk,
                        "source_url": url,
                        "chunk_id": f"{url}_{i}",
                        "source_type": "official_immigration"
                    })
                
                print(f"  -> Created {len(chunks)} chunks")
            else:
                print(f"  -> No content extracted")
            
            # Be respectful to servers
            time.sleep(2)
            
        except Exception as e:
            print(f"Error processing {url}: {e}")
            continue
    
    print(f"Total content pieces scraped: {len(all_content)}")
    return all_content

def save_scraped_content(content: List[Dict[str, str]], filename: str = "scraped_content.json"):
    """Save scraped content to a JSON file"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(content)} content pieces to {filename}")
    except Exception as e:
        print(f"Error saving content: {e}")

def load_scraped_content(filename: str = "scraped_content.json") -> List[Dict[str, str]]:
    """Load previously scraped content from JSON file"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = json.load(f)
            print(f"Loaded {len(content)} content pieces from {filename}")
            return content
        else:
            print(f"File {filename} not found")
            return []
    except Exception as e:
        print(f"Error loading content: {e}")
        return []

if __name__ == "__main__":
    print("Starting immigration content scraping...")
    
    # Check if we already have scraped content
    existing_content = load_scraped_content()
    
    if existing_content:
        print("Found existing scraped content. Use it? (y/n)")
        choice = input().lower().strip()
        if choice == 'y':
            content = existing_content
        else:
            content = scrape_immigration_content()
            save_scraped_content(content)
    else:
        content = scrape_immigration_content()
        save_scraped_content(content)
    
    print(f"Ready to index {len(content)} content pieces into vector database.") 