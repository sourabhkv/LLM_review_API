import os
import time
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bs4 import BeautifulSoup
import html2text
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from openai import OpenAI

# Create FastAPI app instance
app = FastAPI()

# Path to your Edge WebDriver executable
EDGE_DRIVER_PATH = './msedgedriver.exe'

# Environment variables for  OpenAI configuration
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME") or 'gpt-4o-mini'
API_VERSION = os.getenv("API_VERSION")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))

# Initialize  OpenAI client
client = OpenAI(
    _endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=API_VERSION,
)

def setup_selenium():
    """
    Setup Selenium WebDriver with Edge browser.

    Returns:
        WebDriver: Configured Selenium WebDriver instance.
    """
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--inprivate")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    service = Service(executable_path=EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    return driver

def fetch_html_selenium(url):
    """
    Fetch HTML content from a webpage using Selenium.

    Args:
        url (str): URL of the webpage to fetch.

    Returns:
        str: HTML content of the webpage.
    """
    driver = setup_selenium()
    try:
        driver.get(url)
        time.sleep(1)  # Simulate time for page to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        return html
    finally:
        driver.quit()

def clean_html(html_content):
    """
    Clean HTML content by removing unnecessary elements.

    Args:
        html_content (str): Raw HTML content.

    Returns:
        str: Cleaned HTML content as a string.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(['header', 'footer', 'script', 'style']):
        element.decompose()
    return str(soup)

def html_to_markdown_with_readability(html_content):
    """
    Convert cleaned HTML content to Markdown format.

    Args:
        html_content (str): Cleaned HTML content.

    Returns:
        str: Markdown content.
    """
    cleaned_html = clean_html(html_content)
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(cleaned_html)
    return markdown_content

def split_dom_content(dom_content, max_length=6000):
    """
    Split DOM content into manageable parts.

    Args:
        dom_content (str): DOM content in string format.
        max_length (int): Maximum length of each part.

    Returns:
        list: List of split DOM content strings.
    """
    return [
        dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)
    ]

@app.get("/api/reviews")
async def get_reviews(page: str):
    """
    API endpoint to get reviews from a webpage.

    Args:
        page (str): URL of the webpage to scrape reviews from.

    Returns:
        dict: JSON response containing reviews count and review details.
    """
    try:
        html_content = fetch_html_selenium(page)
        markdown_content = html_to_markdown_with_readability(html_content)
        dom_parts = split_dom_content(markdown_content)

        all_reviews = []

        for part in dom_parts:
            # Use OpenAI API to extract reviews
            completion = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[
                    {"role": "system", "content": '''You are a helpful assistant that helps get review information from a webpage. You will be delivered information of a webpage. Provide content in JSON like this:
                    "reviews": [{
                        "title": "Review Title",
                        "body": "Review body text",
                        "rating": 5,
                        "reviewer": "Reviewer Name"
                    },
                    ].'''},
                    {"role": "user", "content": part},
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.0,
                top_p=0.95,
                stream=False
            )
            content = completion.choices[0].message.content.strip()
            # Extract JSON content from formatted string
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()
            try:
                reviews_data = json.loads(content)
                all_reviews.extend(reviews_data.get("reviews", []))
            except json.JSONDecodeError:
                print("Error decoding JSON:", content)

        final_output = {
            "reviews_count": len(all_reviews),
            "reviews": all_reviews
        }
        
        return final_output
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8000)