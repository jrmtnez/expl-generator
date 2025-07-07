import requests


def search(query, language="fr_FR"):
    session = requests.Session()

    homepage_url = "https://www.qwant.com/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    session.get(homepage_url, headers=headers)

    search_url = "https://api.qwant.com/v3/search/web"
    params = {
        "q": query,
        "count": 10,
        "locale": language,
        "offset": 0,
        "device": "desktop",
        "tgp": 1,
        "safesearch": 0,
        "displayed": "true",
        "llm": "true"
    }
    search_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Referer": "https://www.qwant.com/",
    }
    response = session.get(search_url, params=params, headers=search_headers)

    if response.status_code == 200:
        try:
            json_response = response.json()
            return json_response
        except Exception as e:
            raise Exception("An error occurred while processing the Qwant search.") from e
    else:
        raise Exception(f"Qwant search error: {response.status_code}")


QUERY = "Do bananas improve your immune system?"

response_json = search(QUERY, language="en_US")


for mainline in response_json["data"]["result"]["items"]["mainline"]:
    if mainline["type"] == "web":
        for item in mainline["items"]:
            print(item["title"])
            print(item["url"])
            print(item["desc"])
            print()
