#!/usr/bin/env python3
"""Test with full parse_project logic"""
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as bs
import json

def parse_project(url: str, context):
  """Full parse_project from main.py"""
  page_obj = context.new_page()
  
  try:
    page_obj.goto(url, wait_until="networkidle", timeout=30000)
    html = page_obj.content()
  except Exception as e:
    print(f"Error fetching {url}: {e}")
    page_obj.close()
    return {
      "url": url,
      "title": None,
      "tagline": None,
      "description": None,
      "built-with": None,
      "video-link": None,
      "other-links": None,
      "results": "Error"
    }
  
  soup = bs(html, "html.parser")

  # title and tagline
  title = soup.find("h1", id="app-title")
  tagline = title.find_next("p") if title else None
  
  # get description, based on if there is a gallery at the top or not
  start = soup.find("div", id="gallery")
  if not start:
    start = soup.find("div", id="app-details-left")

  description = None
  if start:
    for sib in start.find_all_next("div"):
      if not sib.attrs:
        description = sib
        break

  # list of built with items
  builtwith = soup.find("div", id="built-with")
  items = [li.get_text(strip=True) for li in builtwith.find_all("li")] if builtwith else None

  # link to embeded video
  video = soup.find("iframe", class_="video-embed")

  # outside links, ie github etc
  ul = soup.find("ul", {"data-role": "software-urls"})
  other_links = []
  if ul:
    for li in ul.find_all("li"):
        a = li.find("a", href=True)
        if a:
            other_links.append(a["href"])

  # figure out if a winner
  container = soup.find("div", class_="software-list-content")
  results = []
  if container:
    ul = container.find("ul")
    if ul:
      for li in ul.find_all("li"):
        is_winner = li.find("span", class_="winner") is not None
        text = li.get_text(" ", strip=True)
        results.append({
            "text": text,
            "winner": is_winner
        })

  page_obj.close()
  
  return {
     "url": url,
     "title": title.get_text(strip=True) if title else None,
     "tagline": tagline.get_text(strip=True) if tagline else None,
     "description": description.get_text(strip=True) if description else None,
     "built-with": items if items else None,
     "video-link": video["src"] if video else None,
     "other-links": other_links if other_links else None,
     "results": results[0] if len(results) > 1 else "Did Not Place"
  }

# Test
urls = [
    "https://devpost.com/software/sous-chef-g36fn9",
    "https://devpost.com/software/gnostic-7t9hbc",
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    for i, url in enumerate(urls):
        result = parse_project(url, context)
        print(f"{i}: Title='{result['title']}', Built-with={len(result['built-with']) if result['built-with'] else 0} items")
        print(f"   Tagline: {result['tagline'][:50] if result['tagline'] else 'None'}...")
    
    browser.close()

print("Done!")
