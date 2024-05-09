# DevQuest Tech News Scraper

Welcome to the DevQuest Tech News Scraper repository. This project is designed for scraping news articles for the DevQuest Careers website. It showcases advanced Python scripting capabilities, including the use of multithreading to efficiently scrape multiple URLs.

### Repository Link

[DevQuest Tech News Scraper](https://github.com/dtulpa16/DevQuest_Tech_News_Scraper)

### Website

[DevQuest Careers](https://devquestcareers.com/)

## Features

- **Multithreading**: Utilizes `ThreadPoolExecutor` from Python's `concurrent.futures` module to handle multiple scraping tasks simultaneously, greatly improving the scraping efficiency.
- **Dynamic Proxy Usage**: Implements rotating proxies to prevent IP bans and manage request load, ensuring reliable access to web resources.
- **Environment Variables**: Leverages environment variables to securely manage sensitive data such as API keys and URLs, keeping the configuration external and secure.
- **Robust Error Handling**: Includes comprehensive error handling to manage network issues, proxy failures, and data parsing errors effectively.
- **JSON Output**: Scraped data is saved in a JSON file, making it easy to use for web applications or further processing.

## Usage

### Setup

Clone the repository and install the required Python packages:

```bash
git clone https://github.com/dtulpa16/DevQuest_Tech_News_Scraper.git
cd DevQuest_Tech_News_Scraper
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root directory with the following variables set:

```plaintext
PROXY_API_SECRET=your_proxy_api_secret
LATEST_STORIES_URL=https://example.com/latest
TRENDING_STORIES_URL=https://example.com/trending
... # other URLs listed in url_pool dictionary
```

### Running the Scraper

Execute the script to start scraping:

```bash
python main.py
```

The results will be saved in `articles.json` in the project directory.

## File Structure

- **main.py**: Contains the main script for scraping news articles.


## License

This project is licensed under the MIT License - see the LICENSE file for details.
