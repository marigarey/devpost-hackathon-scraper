# Devpost Hackathon Scraper
Collects the project submissions from a specific hackathon

## Setting Up Dependencies
This project uses uv to help with dependencies, to install all the proper dependencies on your local version run the following:
```zsh
uv venv <environment name>
# macOS/Linux
source .venv/bin/activate
# windows
.venv\Scripts\activate

# installing dependencies
uv pip install -r pyproject.toml
```

## Running the Script
Give the hackathon you want to scrape, find the subdomain of the hackathon on devpost. For example: the subdomain of `madhacks-fall-2025.devpost.com` is `madhacks-fall-2025`.

Once the subdomain is found we can run the script!
```zsh
uv run src/main.py "<subdomain_name>"

# example
uv run src/main.py "madhacks-fall-2025"
```

The output of the data will be found in `/data/<subdomain_name>.json`

## Testing
To verify the scraper is working correctly, you can run the included test files:

```zsh
# Test parsing a single project
uv run test/test_single.py

# Test parsing multiple projects
uv run test/test_multiple.py

# Test with full data extraction logic
uv run test/test_full.py
```

These tests will fetch and parse sample projects to confirm the scraper is functioning properly.
