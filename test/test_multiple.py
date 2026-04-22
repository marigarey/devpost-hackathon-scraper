#!/usr/bin/env python3
"""Test parsing multiple projects"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs

urls = [
    "https://devpost.com/software/sous-chef-g36fn9",
    "https://devpost.com/software/gnostic-7t9hbc",
    "https://devpost.com/software/capcoach",
]

def parse_project(url: str, context):
  """Parse a single project"""
  page_obj = context.new_page()
  
  try:
    page_obj.goto(url, wait_until="networkidle", timeout=30000)
    html = page_obj.content()
  except Exception as e:
    print(f"Error fetching {url}: {e}")
    page_obj.close()
    return {"url": url, "title": None}
  
  soup = bs(html, "html.parser")
  title = soup.find("h1", id="app-title")
  page_obj.close()
  
  return {
     "url": url,
     "title": title.get_text(strip=True) if title else None,
  }

# Test with context reuse (like the main script does)
print("Testing with context reuse...")
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    for i, url in enumerate(urls):
        result = parse_project(url, context)
        print(f"{i}: {result['title']}")
    
    browser.close()

print("Done!")
