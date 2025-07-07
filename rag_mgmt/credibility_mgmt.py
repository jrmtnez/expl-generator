import numpy as np
import whois
import sys
import json
import logging
from datetime import datetime
from os.path import join, exists
sys.path.append('.')
from pipeline.config import ROOT_LOGGER_ID
from rag_mgmt.search_engine_mgmt import get_base_url, search_news, search_text
from pipeline.config import CREDIBILITY_DATA_PATH, DATA_PATH, ALL_NEWS_ITEMS_FILE_NAME, QUESTION_SEARCH_CACHE_FILE_NAME
from pipeline.config import CRED_SCORE_SITES_DATA_FILE_NAME, CRED_SCORE_TRUSTED_SITES_FILE_NAME, CRED_SCORE_TRUSTED_DOMAIN_FILE_NAME
from pipeline.config import CRED_SCORE_FACT_CHECKING_SITES_FILE_NAME, CRED_SCORE_UNIVERSITY_SITES_FILE_NAME, CRED_SCORE_NAIVE_FC_SITES_FILE_NAME
from pipeline.config import SITES_SEARCH_CACHE_FILE_NAME, CRED_SCORE_IFFY_SITES_FILE_NAME, CRED_SCORE_TRUSTED_L2_SITES_FILE_NAME


logger = logging.getLogger(ROOT_LOGGER_ID)


def get_whois_information(url):
    return whois.whois(url)


def check_url_credibility(url, topic, type="text", use_calc_search_based_site_credibility=False):

    base_url = get_base_url(url)

    # reliable domains (gov, edu, ...)
    if is_a_trusted_domain(base_url):
        return 1, "trusted domain"

    # fact cheking verification sites
    if exist_site_in(base_url, CRED_SCORE_FACT_CHECKING_SITES_FILE_NAME):
        return 0, "neutral"

    # hand-crafted reliable sites list
    if exist_site_in(base_url, CRED_SCORE_TRUSTED_DOMAIN_FILE_NAME):
        return 1, "trusted site"

    if exist_site_in(base_url, CRED_SCORE_TRUSTED_L2_SITES_FILE_NAME, use_l2=True):
        return 1, "trusted site"

    # almost 2000 unreliable sites
    if exist_site_in(base_url, CRED_SCORE_IFFY_SITES_FILE_NAME):
        return -1, "iffy list site"

    # more than 10000 university-type sites (reliable)
    if exist_site_in(base_url, CRED_SCORE_UNIVERSITY_SITES_FILE_NAME):
        return 1, "university-type site"

    # credibility score based on corpus data
    exists_site, score = get_fc_site_score(url)
    if exists_site:
        return score, "in corpus"

    # # another attempt to measure credibility
    # if exist_site_in(base_url, CRED_SCORE_NAIVE_FC_SITES_FILE_NAME):
    #     return -1, "naive fc checked site"

    # credibility score based on a naive query to duckduckgo
    if use_calc_search_based_site_credibility:
        return calc_search_based_site_credibility(url, base_url, topic, type=type), " naive search calculation"

    return 0, "not found"


def update_website_data():
    with open(join(DATA_PATH, ALL_NEWS_ITEMS_FILE_NAME), "r", encoding="utf-8") as read_file:
        items = json.load(read_file)

    item_dict = {}

    for item in items:
        url = item["url"]
        if item["url_2"] != "":
            url = item["url_2"]

        base_url = get_base_url(url)

        t_count = 0
        pf_count = 0
        f_count = 0
        if item["item_class"] == "T":
            t_count = 1
        if item["item_class"] == "PF":
            pf_count = 1
        if item["item_class"] == "F":
            f_count = 1

        if item_dict.get(base_url):
            item_dict[base_url]["t_count"] += t_count
            item_dict[base_url]["pf_count"] += pf_count
            item_dict[base_url]["f_count"] += f_count
        else:
            item_data_dict = {}
            item_data_dict["t_count"] = t_count
            item_data_dict["pf_count"] = pf_count
            item_data_dict["f_count"] = f_count
            item_dict[base_url] = item_data_dict

    with open(join(CREDIBILITY_DATA_PATH, CRED_SCORE_SITES_DATA_FILE_NAME), "w", encoding="utf-8") as write_file:
        json.dump(item_dict, write_file, indent=4, separators=(",", ": "))


def is_a_trusted_domain(url):
    with open(join(CREDIBILITY_DATA_PATH, CRED_SCORE_TRUSTED_DOMAIN_FILE_NAME), "r", encoding="utf-8") as read_file:
        urls = json.load(read_file)

    domain = url.split(".")[-1]

    found = False
    if urls.get(domain):
        found = True

    return found


def exist_site_in(base_url, sites_file, use_l2=False):
    with open(join(CREDIBILITY_DATA_PATH, sites_file), "r", encoding="utf-8") as read_file:
        urls = json.load(read_file)

    if use_l2:
        l2_url = ".".join(base_url.split(".")[-2:])
        if urls.get(l2_url):
            return True
    else:
        if urls.get(base_url):
            return True

    return False


def get_fc_site_score(url):

    with open(join(CREDIBILITY_DATA_PATH, CRED_SCORE_SITES_DATA_FILE_NAME), "r", encoding="utf-8") as read_file:
        urls = json.load(read_file)

    exist_site = False
    score = 0
    if urls.get(url):
        exist_site = True

        # positive counts = true_counts
        # negative counts = partially_false_counts * 0.5 + false_counts
        all_counts = [urls[url]["t_count"], urls[url]["pf_count"] * 0.5 + urls[url]["f_count"]]
        softmax_values = softmax(all_counts)

        # after softmax of positive counts and negative counts, score is calculated to return values in [1, -1]
        score = softmax_values[0] * 1 + softmax_values[1] * -1
    return exist_site, score


def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


def check_site_search(url, topic, type="text"):
    site_search_file = join(CREDIBILITY_DATA_PATH, SITES_SEARCH_CACHE_FILE_NAME)
    if exists(site_search_file):
        with open(site_search_file, "r", encoding="utf-8") as read_file:
            urls = json.load(read_file)
    else:
        urls = {}

    if urls.get(url):
        search_results = urls[url]["search_result"]
    else:
        query = url + " " + topic
        if type == "text":
            search_results = search_text(query)
        if type == "news":
            search_results = search_news(query)

        url_data = {}
        url_data["query"] = query
        url_data["search_result"] = search_results
        url_data["last update"] = str(datetime.now())
        urls[url] = url_data

        with open(site_search_file, "w", encoding="utf-8") as write_file:
            json.dump(urls, write_file, indent=4, separators=(",", ": "))

    return search_results


def get_iffy_site_score(url):

    with open(join(CREDIBILITY_DATA_PATH, CRED_SCORE_IFFY_SITES_FILE_NAME), "r", encoding="utf-8") as read_file:
        urls = json.load(read_file)

    exist_site = False
    score = 0
    if urls.get(url):
        exist_site = True

        # positive counts = true_counts
        # negative counts = partially_false_counts * 0.5 + false_counts
        all_counts = [urls[url]["t_count"], urls[url]["pf_count"] * 0.5 + urls[url]["f_count"]]
        softmax_values = softmax(all_counts)

        # after softmax of positive counts and negative counts, score is calculated to return values in [1, -1]
        score = softmax_values[0] * 1 + softmax_values[1] * -1
    return exist_site, score


def calc_search_based_site_credibility(url, base_url, topic, type="text"):

    logging.debug("Base URL: %s", base_url)

    search_results = check_site_search(url, topic, type=type)

    credibility_score = 0

    position = 0
    for result in search_results:
        if type == "text":
            related_url = get_base_url(result['href'])
        if type == "news":
            related_url = get_base_url(result['url'])

        logging.debug(">> Related URL: %s", related_url)

        if base_url == related_url:
            credibility_score += (10 - position)

        position += 1

    # si buscampos "bbc.com/ruta_hacia_la_página misinformation" las primeras urls son de la bbc
    # si buscampos "naturalnews.com/ruta_hacia_la_página misinformation" las primeras urls son de sitios que hacen referencia a noticias falsas, etc., no de naturalnews.com
    # sistema para puntuar negativamente si el primer resultado no es la propia web

    # credibility_score = int(credibility_score / 55 * 100)
    credibility_score = credibility_score / 55

    # según las pruebas realizadas con un límite situado en >=35 tenemos una F1 de 0.748

    # ajuste para centrar en 35 los valores (ahora son positivos y negativos)
    # el cálculo de F1 anterior se ha hecho sin este ajuste
    # credibility_score = credibility_score - 35

    credibility_score = credibility_score - 0.35

    logging.debug(">> Credibility score: %s", credibility_score)

    return credibility_score


if __name__ == '__main__':
    # with open(join(DATA_PATH, QUESTION_SEARCH_FILE_NAME), "r", encoding="utf-8") as read_file:
    #     questions = json.load(read_file)

    # for question in questions:
    #     search_results = questions.get(question)["search_result"]

    #     for search_result in search_results:
    #         url = search_result["href"]

    #         base_url = get_base_url(url)

    #         neutral_site = is_a_neutral_site(base_url)
    #         trusted_domain = is_a_trusted_domain(base_url)
    #         trusted_site = is_a_trusted_site(base_url)
    #         university_site = is_a_university_site(base_url)

    #         print(f"neutral: {neutral_site}, trusted domain: {trusted_domain}, trusted site: {trusted_site}, university site: {university_site}, url: {url[:50]}")


    urls_to_check = ["https://health.clevelandclinic.org/b-vitamin-benefits"]

    for url in urls_to_check:
        base_url = get_base_url(url)

        site_list = [CRED_SCORE_TRUSTED_L2_SITES_FILE_NAME]
        for site in site_list:
            exist_site = exist_site_in(base_url, site)
            print(f"url: {url}\nbase_url: {base_url}\n{site}: {exist_site}\n\n")



        # neutral_site = is_a_neutral_site(base_url)
        # trusted_domain = is_a_trusted_domain(base_url)
        # trusted_site = is_a_trusted_site(base_url)
        # university_site = is_a_university_site(base_url)
        # iffy_site = is_a_iffy_site(base_url)

        # print(f"url: {url}\nbase_url: {base_url}\nneutral: {neutral_site}\ntrusted domain: {trusted_domain}\ntrusted site: {trusted_site}\nuniversity site: {university_site}\nuniversity site: {university_site}\nuniversity site: {university_site}\n")
