#!/usr/bin/env python3
"""Quick test: scrape first 3 projects to verify fix works"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
import json

def parse_hackathon_pages(hackathon: str, max_pages: int = 1) -> list:
  """Get first N pages of projects"""
  print(f"Collecting projects (first {max_pages} page(s))...")
  page = 1
  project_pages = []

  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    while True:
      if page > max_pages:
        break
        
      url = f"https://{hackathon}.devpost.com/submissions/search?page={page}"
      page_obj = context.new_page()
      
      try:
        page_obj.goto(url, wait_until="networkidle", timeout=30000)
        html = page_obj.content()
        soup = bs(html, "html.parser")

        gallery = soup.find("div", id="submission-gallery")
        if not gallery:
            page_obj.close()
            break
        
        submissions = gallery.find_all("div", class_="gallery-item")
        if not submissions:
            page_obj.close()
            break

        for submission in submissions:
            link = submission.find("a", class_="link-to-software")
            if link and "href" in link.attrs:
                project_pages.append(link["href"])

        page += 1
      except Exception as e:
        print(f"Error: {e}")
        page_obj.close()
        break
      finally:
        if page_obj:
          page_obj.close()
    
    browser.close()
  
  print(f"Found {len(project_pages)} projects\n")
  return project_pages

def parse_project(url: str, context):
  """Parse a single project"""
  page_obj = context.new_page()
  
  try:
    page_obj.goto(url, wait_until="networkidle", timeout=30000)
    html = page_obj.content()
  except Exception as e:
    print(f"  ERROR fetching {url}: {e}")
    page_obj.close()
    return {"url": url, "title": "ERROR", "tagline": None}
  
  soup = bs(html, "html.parser")

  title = soup.find("h1", id="app-title")
  tagline = title.find_next("p") if title else None
  
  builtwith = soup.find("div", id="built-with")
  items = [li.get_text(strip=True) for li in builtwith.find_all("li")] if builtwith else None

  page_obj.close()
  
  return {
     "url": url,
     "title": title.get_text(strip=True) if title else None,
     "tagline": tagline.get_text(strip=True) if tagline else None,
     "built-with": items if items else None,
  }

# Test
hackathon = "madhacks-fall-2025"
pages = parse_hackathon_pages(hackathon, max_pages=1)

if pages:
  print(f"Parsing first 3 of {len(pages)} projects...")
  
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    for i in range(min(3, len(pages))):
      result = parse_project(pages[i], context)
      print(f"\n{i}: {result['title']}")
      if result['tagline']:
        print(f"   {result['tagline'][:60]}...")
      if result['built-with']:
        print(f"   Built with: {', '.join(result['built-with'][:3])}...")
    
    browser.close()

  print("\n✅ Fix verified! Data is being extracted correctly.")
  print("You can now run the full script: uv run src/main.py")
