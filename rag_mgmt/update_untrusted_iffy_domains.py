# https://iffy.news/index/
# https://docs.google.com/spreadsheets/d/1ck1_FZC-97uDLIlvRJDTrGqBk0FuDe9yHkluROgpGS8/edit?gid=1144285784#gid=1144285784


import sys
import json
import pandas as pd
from os.path import join, exists
sys.path.append('.')
from rag_mgmt.search_engine_mgmt import get_base_url
from pipeline.config import CREDIBILITY_DATA_PATH, CRED_SCORE_IFFY_SITES_FILE_NAME

SOURCE_FILE = "Iffy.news2024-04-Iffy-news.tsv"
SOURCE_FILE = "Iffy.news2025-01-Iffy-news.tsv"


if __name__ == '__main__':

    sites_df = pd.read_csv(join(CREDIBILITY_DATA_PATH, SOURCE_FILE), sep="\t")

    sites_dict = {}

    for i, line in sites_df.iterrows():
        domain = get_base_url(line["URL"])
        if not sites_dict.get(domain):
            sites_dict[domain] = -1

    with open(join(CREDIBILITY_DATA_PATH, CRED_SCORE_IFFY_SITES_FILE_NAME), "w", encoding="utf-8") as write_file:
        json.dump(sites_dict, write_file, indent=4, separators=(",", ": "))