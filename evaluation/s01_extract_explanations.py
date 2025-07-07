import logging
import json
import sys
from os.path import join
sys.path.append('.')

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from  llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL
from llm_mgmt.llm_ollama_mgmt import O_GEMMA3_27B_LABEL
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL
from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH, RESULTS_FILE_NAME, ROOT_LOGGER_ID
from pipeline.openai_loop import GPT_MODEL_LABEL

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL, baseline_model=False):

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % evaluated_model_label)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    true_items = 0
    sentences_to_evaluate = 0
    true_sentences = 0
    triplets_to_evaluate = 0

    results = []
    for item in items:
        item_dict = {}
        item_dict["item_id"] = item["item_id"]
        item_dict["claim"] = item["claim"]
        item_dict["item_class"] = item["item_class"]
        item_dict["original_reasoning_text"] = item["original_reasoning_text"]

        if item_dict["item_class"] == "T":
            true_items += 1

        if not baseline_model:
            sentence_list = []

            sentences = item["fr_sentences"]
            for sentence in sentences:
                sentences_to_evaluate += 1

                sentence_dict = {}
                sentence_dict["sentence_id"] = sentence["sentence_id"]
                sentence_dict["sentence_text"] = sentence["sentence_text"]
                sentence_dict["sencente_class"] = sentence["sentence_class"]

                if sentence_dict["sencente_class"] == "T":
                    true_sentences += 1

                triplet_list = []

                triplets = sentence["triplets"]
                for triplet in triplets:

                    triplets_to_evaluate += 1

                    triplet_dict = {}
                    triplet_dict["claim"] = triplet["subject"] + " " + triplet["predicate"] + " " + triplet["object"]

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

                        search_result_dict[search_result_id] = search_result["body"]

                    triplet_dict["evidence"] = search_result_dict

                    triplet_dict["explanation"] = triplet["reasoning_for_the_answer_given"]

                    # triplet_dict["non_contradiction"] = "NOK"
                    # triplet_dict["additional_elements_error"] = "NOK"
                    # triplet_dict["misuse_unreliable_evidence"] = "NOK"

                    triplet_list.append(triplet_dict)

                sentence_dict["triplets"] = triplet_list
                sentence_list.append(sentence_dict)

            item_dict["fr_sentences"] = sentence_list

        item_dict["justification"] = item["justification"]
        item_dict["no_redundancy"] = "NOK"
        item_dict["non_contradiction"] = "NOK"
        item_dict["coverage"] = "NOK"
        # item_dict["reasoning_coherence"] = "NOK"
        # item_dict["no_overgeneralization"] = "NOK"
        item_dict["readability"] = "NOK"

        results.append(item_dict)

    with open(join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_model_label, evaluator_model_label)), "w", encoding="utf-8") as write_file:
        json.dump(results, write_file, indent=4, separators=(",", ": "))

    logger.info("Items to evaluate: %s", len(items))
    logger.info("Sentences to evaluate: %s", sentences_to_evaluate)
    logger.info("Triplets to evaluate: %s", triplets_to_evaluate)

    logger.info("True items: %s", true_items)
    logger.info("False items: %s", len(items) - true_items)
    logger.info("True sentences: %s", true_sentences)
    logger.info("False sentences: %s", sentences_to_evaluate - true_sentences)


if __name__ == '__main__':

    export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL)
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL)

    export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL)
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL)

    export_results(evaluated_model_label=GPT_MODEL_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL, baseline_model=True)
    export_results(evaluated_model_label=GPT_MODEL_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, baseline_model=True)
