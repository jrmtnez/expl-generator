import sys
import json
from os.path import join
sys.path.append('.')
from pipeline.config import DATA_PATH, QUESTION_SEARCH_CACHE_FILE_NAME
from rag_mgmt.search_results_mgmt import get_base_url

if __name__ == '__main__':

    with open(join(DATA_PATH, QUESTION_SEARCH_CACHE_FILE_NAME), "r", encoding="utf-8") as read_file:
        data = json.load(read_file)

    sites_dict = {}

    for key in data:
        for search_result in data[key]["search_result"]:
            base_url = get_base_url(search_result["href"])
            if not sites_dict.get(base_url):
                sites_dict[base_url] = 1
            else:
                sites_dict[base_url] = sites_dict[base_url] + 1

    with open(join(DATA_PATH, "domains_occurrences.json"), "w", encoding="utf-8") as write_file:
        json.dump(sites_dict, write_file, indent=4, separators=(",", ": "))