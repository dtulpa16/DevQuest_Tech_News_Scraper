# Import the required Modules - 47h9ulphtz3ardhlmjk5el55r0luag7rz6q44o9e
import requests
import logging
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import os
import json

load_dotenv()

logging.basicConfig(level=logging.INFO)

def scrape_url(session, url, proxy):
    try:
        formatted_proxy_url = f'http://{proxy["username"]}:{proxy["password"]}@{proxy["proxy_address"]}:{proxy["port"]}'
        session.proxies = {"http": formatted_proxy_url, "https": formatted_proxy_url}
        response = session.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.RequestException as e:
        logging.error(f"Error accessing {url} with proxy {proxy}: {e}")
        return None

def save_articles_to_json(articles_data, filename="articles.json"):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(articles_data, f, ensure_ascii=False, indent=4)
        logging.info(f"Data successfully written to {filename}")
    except Exception as e:
        logging.error(f"Failed to write data to {filename}: {e}")
    


def fetch_article_details(session, article_data, proxy):
    article_url = article_data['href']
    category = article_data['category']
    article_soup = scrape_url(session, article_url, proxy)
    if not article_soup:
        return None
    try:
        if article_soup:
            # title, subtitle, and date
            title_group = article_soup.find('section', class_='title-group')
            title = title_group.find('h1').text.strip().replace("\xa0", " ").replace("\"","") if title_group else 'No title'
            subtitle = title_group.find('h2').text.strip().replace("\xa0", " ").replace("\"","") if title_group else 'No subtitle'
            time_tag = title_group.find('time')
            date = time_tag.find('span').text.strip() if time_tag else 'No date'

            # imgs and alt text
            image_tag = article_soup.find('img', class_='intro-image')
            thumbnail_url = image_tag['src'] if image_tag and image_tag.has_attr('src') else 'No thumbnail'
            image_alt = image_tag['alt'] if image_tag and image_tag.has_attr('alt') else 'No alt text'

            # tags
            tags_ul = article_soup.find('ul', class_="category-chicklets")
            tags = [a.get_text(strip=True) for a in tags_ul.find_all('a')] if tags_ul else []

            # body text
            body_div = article_soup.find('div', class_='articleBody')
            if body_div:
                body_paragraphs = body_div.find_all('p')
                body = '  <br/> <br/>'.join(p.text.strip() for p in body_paragraphs).replace("\"","")
                        
               
            iframes = body_div.find_all('iframe')
            for iframe in iframes:
                src = iframe['src']
                iframe_markdown = f"[Embedded content]({src})"
                body += f"  <br/>{iframe_markdown}  <br/>"  

            return {
                'title': f'# {title}',
                'subtitle': f'**{subtitle}**',
                'date': date,
                'tags': ', '.join(tags).upper(),
                'body': body,
                'url': article_url,
                'slug': title.lower().replace(" ", "-"),
                'thumbnailUrl': thumbnail_url,
                'imageAlt': image_alt,
                'category': category
            }
    except Exception as e:
        logging.error(f"Failed to process article {article_url}: {e}")
        return None


def fetch_articles(proxies, url_pool):
    articles_data = []
    # set to track URLs of processed articles - for preventing dupes
    seen_urls = set()  
    with ThreadPoolExecutor(max_workers=10) as executor:
        for category, target_url in url_pool.items():
            successful_fetch = False
            for proxy in proxies:
                if not proxy['valid']:
                    logging.info("Invalid Proxy")
                    continue
                # create one session per proxy
                session = requests.Session()  
                data = scrape_url(session, target_url, proxy)
                if data:
                    article_list = data.find('div', class_='post-list')
                    if article_list:
                        articles = article_list.find_all('article')
                        futures = []
                        for article in articles:
                            link = article.find('a')
                            if link and link.has_attr('href'):
                                future = executor.submit(fetch_article_details, session, {'href': link['href'], 'category': category}, proxy)
                                futures.append(future)

                        # collect results from futures
                        for future in futures:
                            article_data = future.result()
                            if article_data and article_data['url'] not in seen_urls:
                                articles_data.append(article_data)
                                seen_urls.add(article_data['url'])  # Add URL to the set - used for preventing dupe articles

                        successful_fetch = True
                        break  # bvreak if successful with proxy

            if not successful_fetch:
                logging.error(f"Failed to fetch articles for {category} from all proxies.")

    save_articles_to_json(articles_data)
    return articles_data


api_key = os.getenv('PROXY_API_SECRET')

# fetch proxy list
proxies = requests.get(
    "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=50",
    headers={"Authorization": f"Token {api_key}"}
)

proxies = proxies.json()['results']
url_pool = {
    "latest": os.getenv('LATEST_STORIES_URL'),
    "trending": os.getenv('TRENDING_STORIES_URL'),
    "ai": os.getenv('AI_STORIES_URL'),
    "coding": os.getenv('CODING_STORIES_URL'),
    "tech_culture": os.getenv('TECH_CULTURE_STORIES_URL'),
    "hacking": os.getenv('HACKING_STORIES_URL'),
    "security": os.getenv('SECURITY_STORIES_URL'),
    "linux": os.getenv('LINUX_STORIES_URL'),
    "windows": os.getenv('WINDOWS_STORIES_URL'),
    "tech_deals": os.getenv('TECH_DEALS_STORIES_URL'),
    "web": os.getenv('WEB_STORIES_URL'),
}

articles = fetch_articles(proxies,url_pool)