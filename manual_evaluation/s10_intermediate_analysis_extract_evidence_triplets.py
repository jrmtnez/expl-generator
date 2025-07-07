import logging
import json
import sys
from os.path import join
sys.path.append('.')
from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL

from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH, EVIDENCE_TRIPLETS_FILE_NAME, RESULTS_ANALYSIS_PATH, ROOT_LOGGER_ID

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def export_results(preferred_model_label=O_GEMMA_LABEL, include_selected_search_results=True):

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % preferred_model_label)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    triplets_to_evaluate = 0

    results = []
    for item in items:
        item_dict = {}
        item_dict["item_id"] = item["item_id"]
        item_dict["claim"] = item["claim"]
        item_dict["item_class"] = item["item_class"]

        sentence_list = []

        sentences = item["fr_sentences"]
        for sentence in sentences:
            sentence_dict = {}
            sentence_dict["sentence_id"] = sentence["sentence_id"]
            sentence_dict["sentence_text"] = sentence["sentence_text"]
            sentence_dict["sencente_class"] = sentence["sentence_class"]

            triplet_list = []

            triplets = sentence["triplets"]
            for triplet in triplets:

                triplets_to_evaluate += 1

                triplet_dict = {}
                triplet_dict["claim"] = triplet["subject"] + " - " + triplet["predicate"] + " - " + triplet["object"]

                search_result_dict = {}
                search_result_no = 0
                search_results = triplet["selected_search_results"]
                for search_result in search_results:
                    search_result_no += 1

                    credibility = "neutral"
                    if search_result["url_credibility"] > 0:
                        credibility = "reliable"
                    if search_result["url_credibility"] < 0:
                        credibility = "unreliable"

                    search_result_id = f"Source {search_result_no} ({credibility})"

                    search_result_triplets = search_result["search_result_triplets"]

                    search_triplet_no = 0
                    search_result_triplets_dict = {}
                    for search_result_triplet in search_result_triplets:
                        search_triplet_no += 1
                        search_triplet_id = f"Triplet {search_triplet_no}"
                        search_result_triplets_dict[search_triplet_id] = search_result_triplet["subject"] + ' - ' + search_result_triplet["predicate"]  + ' - ' +  search_result_triplet["object"]

                    search_result_dict[search_result_id] = search_result_triplets_dict

                triplet_dict["evidence"] = search_result_dict

                triplet_list.append(triplet_dict)

            sentence_dict["triplets"] = triplet_list
            sentence_list.append(sentence_dict)

        item_dict["fr_sentences"] = sentence_list
        results.append(item_dict)

    with open(join(RESULTS_ANALYSIS_PATH, EVIDENCE_TRIPLETS_FILE_NAME % preferred_model_label), "w", encoding="utf-8") as write_file:
        json.dump(results, write_file, indent=4, separators=(",", ": "))

    logger.info("Items to evaluate: %s", len(items))
    logger.info("Triplets to evaluate: %s", triplets_to_evaluate)


if __name__ == '__main__':
    export_results(preferred_model_label=O_GEMMA_LABEL)
    export_results(preferred_model_label=DEEPSEEK_R1_LABEL)
