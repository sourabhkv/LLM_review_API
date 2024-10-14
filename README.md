# LLM_review_API
AI scrape reviews
# Review Scraper API

This project is a FastAPI-based web scraper designed to extract and format reviews from a given webpage. Using Selenium for web scraping and OpenAI's API for processing, it outputs structured JSON data.

## Solution Approach

- **Deep Content Extraction:** To access deeply embedded information on webpages, the project utilizes Selenium with the Edge WebDriver. The configuration mimics a typical desktop environment to minimize the risk of IP blocking. Scrolling is implemented to ensure all dynamic content is fully loaded.

- **Content Cleaning:** Irrelevant elements such as headers, footers, scripts, and styles are removed to focus on the essential content. This helps in reducing noise and improving data quality.

- **Content Conversion for LLMs:** Large Language Models (LLMs) perform better with plain text rather than HTML or CSS. Therefore, HTML content is converted to Markdown, which is more readable and easier for LLMs to process.

- **Chunking for Efficiency:** To avoid exceeding the context length limits of the LLM, the Markdown content is divided into chunks of 6000 characters. This ensures that each part is manageable and can be processed efficiently without losing information.

- **Model Utilization:** The `gpt-4o-mini` model is used for extracting structured review data from the text. This choice balances performance and resource constraints, providing accurate extraction while managing computational load.

This approach ensures efficient data extraction and processing, leveraging Selenium for dynamic content handling and LLMs for intelligent information retrieval.
  
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
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup Microsoft Edge WebDriver**:
   - Download the WebDriver from the official site and place it in the project directory.
   - Ensure the path is correctly set in the code (default: `./msedgedriver.exe`).

4. **Configure Environment Variables**:
   - Set `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `DEPLOYMENT_NAME`, and `API_VERSION` with your OpenAI credentials.

## Usage

1. **Run the FastAPI Server**:
   ```bash
   uvicorn app:app --reload
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
