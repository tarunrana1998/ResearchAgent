from langchain.tools import tool
from dotenv import load_dotenv
import requests,os,json
from rich import print

from bs4 import BeautifulSoup
from tavily import TavilyClient
load_dotenv()

tavily_client = TavilyClient(os.getenv("TAVILY_API_KEY"))

# @tool
def web_search(query: str) -> str:
    """
    Tool that uses the Tavily API to search the web.
    If cached results exist, use them instead of making a new request.
    """

    cache_file = "web_results.json"

    # Use cached data if it exists
    if os.path.exists(cache_file):
        print("Using cached web results...")
        with open(cache_file, "r", encoding="utf-8") as f:
            web_results = json.load(f)
    else:
        print("Searching Tavily...")
        web_results = tavily_client.search(
            query=query,
            max_results=5,
            country="india",
            include_images=True
        )

        # Save results to cache
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(web_results, f, indent=4, ensure_ascii=False)

    output = []

    for r in web_results["results"]:
        output.append(
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Content: {r['content']}\n"
        )
        output.append("-" * 50)

    return "\n".join(output)

# @tool
def scrape_url(url: str) -> str:
    """
    Tool that uses the requests library to get the content of a URL.
    Args:
        url: The URL to get the content of.
    Returns:
        The content of the URL.
    """
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching URL: {e}"
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove unwanted tags
    for unwanted in ['script', 'style', 'header', 'footer', 'nav', 'form', 'iframe']:
        for tag in soup.find_all(unwanted):
            tag.decompose()

    # Get main text content
    text = soup.get_text(separator='\n', strip=True)
    
    # Keep only top 800 lines
    lines = text.split('\n')
    truncated = '\n'.join(lines[:100])
    
    return truncated


# news = web_search("jantar mantar news in india")

# scraped_news = scrape_url("https://www.amarujala.com/video/india-news/jantar-mantar-protesters-delhi-government-s- major-decision-regarding-protesters-at-jantar-mantar-2026-07-30")
# print(scraped_news)