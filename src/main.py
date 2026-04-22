from bs4 import BeautifulSoup as bs
import json
from playwright.sync_api import sync_playwright
import sys

def parse_hackathon(hackathon: str) -> list:
  """
  parse_hackathon creates a list of all project urls submitted to the given hackathon

  :param: str hackathon: Subdomain of devpost.com
  :return: list of project urls
  """
  print("Collecting Hackathon Submissions...")
  page = 1

  project_pages = []

  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    while True:
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
        print(f"Error fetching page {page}: {e}")
        page_obj.close()
        break
      finally:
        page_obj.close()
    
    browser.close()
  
  print(f"Found {len(project_pages)} submissions! \n")
  return project_pages

def parse_project(url: str, context) -> dict:
  """
  parse_project obtains the project information for a given project

  :param: str url: devpost url of the project
  :param: context: Playwright browser context instance
  :return: dict
  """
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
     "results": results if results else "Did Not Place"
  }

def build_project_info(pages: list) -> dict:
  """
  Parses each page and gathers project information

  :param: pages list: list of project urls
  :return: dict
  """
  projects = {}
  i = 0
  print("Beginning to parse each project")
  
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )
    
    for page in pages:
      try:
        result = parse_project(page, context)
        if result.get("title") is None and i < 5:
          print(f"  WARNING: Project {i} returned null title from {page}")
        projects[i] = result
        i += 1
        if i % 10 == 0:
          print(f"  Parsed {i}/{len(pages)} projects...")
      except Exception as e:
        print(f"Error parsing {page}: {e}")
        i += 1
    
    browser.close()

  print(f"All projects are parsed ({len(projects)})!")
  return projects

def save_to_json(data: dict, file_name: str):
  """
  saves all the project data to a file
  """
  with open(f"./data/{file_name}.json", "w") as f:
    json.dump(data, f, indent=2)
  print(f"Data written to /data/{file_name}.json")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Expected Behavior: uv run src/main.py <hackathon subdomain>")
  else:
    hackathon = sys.argv[1]
    pages = parse_hackathon(hackathon)
    projects = build_project_info(pages)
    save_to_json(projects, hackathon)

