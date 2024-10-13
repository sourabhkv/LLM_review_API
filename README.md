# LLM_review_API
AI scrape reviews
# Review Scraper API

This project is a FastAPI-based web scraper designed to extract and format reviews from a given webpage. Using Selenium for web scraping and OpenAI's API for processing, it outputs structured JSON data.

## Features

- **Web Scraping**: Utilizes Selenium to fetch and render HTML content from a specified webpage.
- **Review Processing**: Uses OpenAI's API to extract and format review information.
- **RESTful API**: Exposes a single endpoint to retrieve review data in JSON format.
  
## Prerequisites

- Python 3.10+
- Selenium
- FastAPI
- Uvicorn
- OpenAI API Key or Azure OpenAI key
- Microsoft Edge WebDriver

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sourabhkv/LLM_review_API.git
   cd repository-directory
   ```

2. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn selenium openai beautifulsoup4 html2text
   ```

3. **Setup Microsoft Edge WebDriver**:
   - Download the WebDriver from the official site and place it in the project directory.
   - Ensure the path is correctly set in the code (default: `./msedgedriver.exe`).

4. **Configure Environment Variables**:
   - Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `DEPLOYMENT_NAME`, and `API_VERSION` with your OpenAI credentials.

## Usage

1. **Run the FastAPI Server**:
   ```bash
   uvicorn main:app --reload
   ```

2. **Access the API**:
   - Endpoint: `/api/reviews`
   - Method: `GET`
   - Query Parameter: `page` (URL of the webpage to scrape)
   - Example: `http://localhost:8000/api/reviews?page=https://example.com`

## Response Format

```json
{
  "reviews_count": 100,
  "reviews": [
    {
      "title": "Review Title",
      "body": "Review body text",
      "rating": 5,
      "reviewer": "Reviewer Name"
    },
    ...
  ]
}
```
![image](https://github.com/user-attachments/assets/0c6435f0-4c49-4a01-b034-29f3cb418701)


## Error Handling

- Returns a 500 HTTP error if an exception occurs during the scraping or processing.

## License

This project is licensed under the MIT License.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## Contact

For any questions or support, please contact sourabhkv at sourabhkv96@gmail.com.
