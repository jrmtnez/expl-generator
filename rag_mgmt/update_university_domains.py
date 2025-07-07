# https://github.com/Hipo/university-domains-list

import sys
import json
import urllib.request
from os.path import join, exists
sys.path.append('.')
from pipeline.config import CREDIBILITY_DATA_PATH, CRED_SCORE_UNIVERSITY_SITES_FILE_NAME

SOURCE_URL = "https://raw.githubusercontent.com/Hipo/university-domains-list/refs/heads/master"
SOURCE_FILE = "world_universities_and_domains.json"

if __name__ == '__main__':

    if not exists(join(CREDIBILITY_DATA_PATH, SOURCE_FILE)):
        urllib.request.urlretrieve(join(SOURCE_URL, SOURCE_FILE), join(CREDIBILITY_DATA_PATH, SOURCE_FILE))

    with open(join(CREDIBILITY_DATA_PATH, SOURCE_FILE), "r", encoding="utf-8") as read_file:
        universities = json.load(read_file)

    sites_dict = {}

    for university in universities:
        domains = university["domains"]
        for domain in domains:
            if not sites_dict.get(domain):
                sites_dict[domain] = 1

    with open(join(CREDIBILITY_DATA_PATH, CRED_SCORE_UNIVERSITY_SITES_FILE_NAME), "w", encoding="utf-8") as write_file:
        json.dump(sites_dict, write_file, indent=4, separators=(",", ": "))