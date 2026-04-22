#!/usr/bin/env python3
"""Test parsing a single project"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs

def parse_project(url: str, context):
  """Test version of parse_project with debug output"""
  page_obj = context.new_page()
  
  try:
    print(f"Fetching {url}...")
    page_obj.goto(url, wait_until="networkidle", timeout=30000)
    html = page_obj.content()
    print(f"  Got {len(html)} chars of HTML")
  except Exception as e:
    print(f"Error fetching {url}: {e}")
    page_obj.close()
    return None
  
  soup = bs(html, "html.parser")

  # title and tagline
  title = soup.find("h1", id="app-title")
  print(f"  Title: {title.get_text(strip=True) if title else 'NOT FOUND'}")
  
  # Check other fields
  builtwith = soup.find("div", id="built-with")
  if builtwith:
    items = [li.get_text(strip=True) for li in builtwith.find_all("li")]
    print(f"  Built-with ({len(items)} items): {items[:3]}...")
  else:
    print(f"  Built-with: NOT FOUND")
  
  page_obj.close()
  
  return {
     "url": url,
     "title": title.get_text(strip=True) if title else None,
  }

# Test
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    result = parse_project("https://devpost.com/software/sous-chef-g36fn9", context)
    print(f"\nFinal result: {result}")
    
    browser.close()
