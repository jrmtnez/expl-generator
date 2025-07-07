import re
from urllib.parse import urlparse
from duckduckgo_search import DDGS
from duckduckgo_search.exceptions import RatelimitException, TimeoutException


def search_text(query):
    results = DDGS().text(query, region="wt-wt", safesearch="off", timelimit="y", max_results=25)
    return results


def search_news(query):
    results = DDGS().news(query, region="wt-wt", safesearch="off", timelimit="y", max_results=25)
    return results


def get_base_url(full_url):

    url_appearances = re.findall(r"(http|https)://", full_url)
    if len(url_appearances) == 2:
        url_list = full_url.split(f"{url_appearances[1]}://")
        full_url = f"{url_appearances[1]}://" + url_list[-1]

    base_url = urlparse(full_url).netloc

    if base_url[:4] == "www.":
        base_url = base_url[4:]

    return base_url

def get_rate_limit_exception():
    return RatelimitException


def get_timeout_exception():
    return TimeoutException
