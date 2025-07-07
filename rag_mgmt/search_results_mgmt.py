import json
import sys
from datetime import datetime
from os.path import join, exists
sys.path.append('.')
from pipeline.config import DATA_PATH, QUESTION_SEARCH_CACHE_FILE_NAME, CRED_SCORE_FACT_CHECKING_SITES_FILE_NAME, CRED_SCORE_IFFY_SITES_FILE_NAME
from rag_mgmt.credibility_mgmt import check_url_credibility, exist_site_in
from rag_mgmt.search_engine_mgmt import get_base_url, search_news, search_text


def get_body_results_list(query, type="text"):

    if type == "text":
        results = search_text(query)
    if type == "news":
        results = search_news(query)

    results_list = ""
    for result in results:
        results_list = results_list + "- " + result["body"] + "\n"

    return results_list


def get_base_url_and_body_results_list(query, type="text", topic="misinformation", min_body_lenght=100, max_results=10):
    question_search_file = join(DATA_PATH, QUESTION_SEARCH_CACHE_FILE_NAME)
    if exists(question_search_file):
        with open(question_search_file, "r", encoding="utf-8") as read_file:
            queries = json.load(read_file)
    else:
        queries = {}

    if queries.get(query):
        search_results = queries[query]["search_result"]
        last_update = queries[query]["last_update"]
    else:
        if type == "text":
            search_results = search_text(query)
        if type == "news":
            search_results = search_news(query)

        query_data = {}
        query_data["search_result"] = search_results
        query_data["last_update"] = str(datetime.now())
        queries[query] = query_data

        last_update = query_data["last_update"]

        with open(question_search_file, "w", encoding="utf-8") as write_file:
            json.dump(queries, write_file, indent=4, separators=(",", ": "))

    results_count = 0
    text_results_list = ""
    results_list = []
    for result in search_results:
        if results_count > max_results:
            break
        if len(result["body"]) >= min_body_lenght:

            if type == "text":
                url = result['href']
            if type == "news":
                url = result['url']

            if not exist_site_in(get_base_url(url), CRED_SCORE_FACT_CHECKING_SITES_FILE_NAME):

                results_count += 1

                url_credibility, credibility_from = check_url_credibility(url, topic, type=type)
                text_results_list = text_results_list + f"- {get_base_url(url)} ({url_credibility}): {result['body']}\n"

                id = f"search_result_{results_count}"
                result_element = {}
                result_element["id"] = id
                result_element["url"] = url
                result_element["url_credibility"] = url_credibility
                result_element["url_credibility_from"] = credibility_from
                result_element["last_update"] = last_update
                result_element["body"] = result['body']
                results_list.append(result_element)

    return text_results_list, results_list


def check_results_body_lenght():
    question_search_file = join(DATA_PATH, QUESTION_SEARCH_CACHE_FILE_NAME)
    with open(question_search_file, "r", encoding="utf-8") as read_file:
        queries = json.load(read_file)

    body_count = 0
    min_lenght = 1000000000
    max_lenght = 0
    total_lenght = 0
    for key in queries:
        for result in queries[key]["search_result"]:
            body_lenght = len(result["body"])
            body_count += 1
            total_lenght += body_lenght
            if body_lenght < min_lenght:
                min_lenght = body_lenght
            if body_lenght > max_lenght:
                max_lenght = body_lenght

    print(f"Min body lenght: {min_lenght}, max body lenght: {max_lenght}, average body lenght: {total_lenght / body_count}")


if __name__ == '__main__':
    # check_results_body_lenght()

    # base_url = get_base_url("https://science.feedback.org/claimreview/led-lights-arent-cause-cataracts-dont-cause-migraines-most-people-contrary-social-media-claims/")
    # print(base_url)
    # print(exist_site_in(base_url, CRED_SCORE_FACT_CHECKING_SITES_FILE_NAME))

    # base_url = get_base_url("https://americanpartisan.org/claimreview/led-lights-arent-cause-cataracts-dont-cause-migraines-most-people-contrary-social-media-claims/")
    # print(base_url)
    # print(exist_site_in(base_url, CRED_SCORE_IFFY_SITES_FILE_NAME))

    text_results_list, results_list = get_base_url_and_body_results_list("Can drinking just one diet soda per day triple your risk of dementia and stroke?", max_results=25)

    print(results_list)
