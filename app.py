import os
import platform
import time
import json
import random
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from bs4 import BeautifulSoup
import html2text
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# Determine the path for the Edge WebDriver based on the OS
if platform.system() == "Windows":
    EDGE_DRIVER_PATH = './msedgedriver.exe'
else:
    EDGE_DRIVER_PATH = './msedgedriver'

OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME") or 'gpt-4o-mini'
API_VERSION = os.getenv("API_VERSION") or '2024-09-01-preview'
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))

'''
This part is for Azure OpenAI which i had access to
client = AzureOpenAI(
    endpoint=OPENAI_ENDPOINT,
    api_key=OPENAI_API_KEY,
    api_version=API_VERSION,
)
'''
#This is for OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# List of user agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
]

def setup_selenium():
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--inprivate")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    
    # Select a random user agent
    random_user_agent = random.choice(user_agents)
    options.add_argument(f"user-agent={random_user_agent}")

    service = Service(executable_path=EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    return driver

def fetch_html_selenium(url):
    driver = setup_selenium()
    try:
        driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
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
                max_tokens=4000,
                messages=[{"role": "system", "content": '''You are a helpful assistant that extracts review details from web content.
                        Format the reviews like this in JSON:
                        {
                            "reviews": [
                                {
                                    "title": "Review Title",
                                    "body": "Review content",
                                    "rating": 5,
                                    "reviewer": "Reviewer Name"
                                }
                            ]
                        }'''},
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