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
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Path to your msedgedriver
EDGE_DRIVER_PATH = './msedgedriver.exe'

OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))

client = OpenAI(
    endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=API_VERSION,
)

def setup_selenium():
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
    driver = setup_selenium()
    try:
        driver.get(url)
        #time.sleep(1)  # Simulate time for page to load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        html = driver.page_source
        return html
    finally:
        driver.quit()

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    for element in soup.find_all(['header', 'footer', 'script', 'style']):
        element.decompose()
    return str(soup)

def html_to_markdown_with_readability(html_content):
    cleaned_html = clean_html(html_content)
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    markdown_content = markdown_converter.handle(cleaned_html)
    return markdown_content

def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)
    ]

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/reviews")
async def get_reviews(page: str):
    print(page)
    try:
        html_content = fetch_html_selenium(page)
        markdown_content = html_to_markdown_with_readability(html_content)
        dom_parts = split_dom_content(markdown_content)

        all_reviews = []

        for part in dom_parts:
            completion = client.chat.completions.create(  
            model=DEPLOYMENT_NAME,  
            messages=[{"role": "system", "content": '''You are a helpful assistant that extracts review details from web content.
                    Format the reviews like this:
                    {
                        "reviews": [
                            {
                                "title": "Review Title",
                                "body": "Review content",
                                "rating": 5,
                                "reviewer": "Reviewer Name"
                            }
                        ]
                    }.'''},
                    {"role": "user", "content": part}
                ], 
                )
            content = completion.choices[0].message.content.strip()
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
    uvicorn.run(app, host="0.0.0.0", port=8000)