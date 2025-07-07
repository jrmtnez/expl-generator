import logging
import json
import sys
from os.path import join
sys.path.append('.')
from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL
from pipeline.config import RESULTS_FILE_NAME, RESULTS_ANALYSIS_PATH
from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH
from pipeline.config import COMBINED_EVIDENCE_TRIPLETS_FILE_NAME
from pipeline.config import ROOT_LOGGER_ID
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL, O_GEMMA3_27B_LABEL


LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)

results = []


def export_results(evaluated_model_label=O_GEMMA_LABEL,
                   evaluator_model_1=None,
                   measure_name=None,
                   max_items=14):

    results_items_dict_1 = {}

    if evaluator_model_1 is not None:
        data_file_1 = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_model_label, evaluator_model_1))

        with open(data_file_1, encoding="utf-8") as json_file:
            items = json.load(json_file)

            for item in items:
                results_triplets_dict = {}

                fr_sentences = item["fr_sentences"]
                for sentence in fr_sentences:
                    triplets = sentence["triplets"]
                    for triplet in triplets:
                        triplet_evaluations = {}
                        triplet_evaluations["evidence"] = triplet["evidence"]
                        if triplet.get(evaluator_model_1 + measure_name):
                            triplet_evaluations[evaluator_model_1 + measure_name] = triplet.get(evaluator_model_1 + measure_name)
                        # if triplet.get(evaluator_model_1 + measure_reasoning):
                        #     triplet_evaluations[evaluator_model_1 + measure_reasoning] = triplet.get(evaluator_model_1 + measure_reasoning)

                        results_triplets_dict[triplet["claim"]] = triplet_evaluations

                results_items_dict_1[item["item_id"]] = results_triplets_dict

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % evaluated_model_label)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    triplets_to_evaluate = 0

    for item in items[:max_items]:
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

                    search_result_triplets = search_result["search_result_triplets"]

                    search_triplet_no = 0
                    search_result_triplets_dict = {}
                    for search_result_triplet in search_result_triplets:
                        search_triplet_no += 1
                        search_triplet_id = f"Triplet {search_triplet_no}"
                        search_result_triplets_dict[search_triplet_id] = search_result_triplet["subject"] + ' - ' + search_result_triplet["predicate"]  + ' - ' +  search_result_triplet["object"]

                    search_result_dict[search_result_id] = search_result_triplets_dict

                # triplet_dict["evidence"] = search_result_dict

                if results_items_dict_1.get(item["item_id"]):
                    if results_items_dict_1.get(item["item_id"]).get(triplet_dict["claim"]):
                        # triplet_dict["measures"] = results_items_dict_1.get(item["item_id"]).get(triplet_dict["claim"])
                        triplet_evaluation = results_items_dict_1.get(item["item_id"]).get(triplet_dict["claim"])

                        if triplet_evaluation.get("evidence"):
                            triplet_dict["evidence"] = triplet_evaluation.get("evidence")

                        triplet_dict["explanation"] = triplet["reasoning_for_the_answer_given"]

                        if triplet_evaluation.get(evaluator_model_1 + measure_name):
                            evaluation_measure_1 = triplet_evaluation.get(evaluator_model_1 + measure_name)
                        #     triplet_dict[evaluator_model_1 + measure_name] = triplet_evaluation.get(evaluator_model_1 + measure_name)
                        # if triplet_evaluation.get(evaluator_model_1 + measure_reasoning):
                        #     triplet_dict[evaluator_model_1 + measure_reasoning] = triplet_evaluation.get(evaluator_model_1 + measure_reasoning)

                        triplet_dict["generating model"] = evaluated_model_label

                        if evaluation_measure_1 == "NOK":
                            results.append(triplet_dict)

                triplet_list.append(triplet_dict)


            sentence_dict["triplets"] = triplet_list
            sentence_list.append(sentence_dict)

        item_dict["fr_sentences"] = sentence_list

        # results.append(item_dict)

    logger.info("Items to evaluate: %s", len(items))
    logger.info("Triplets to evaluate: %s", triplets_to_evaluate)


if __name__ == '__main__':

    # non_contradiction

    # MEASURE_NAME = "_non_contradiction_auto"

    # export_results(evaluated_model_label=O_GEMMA_LABEL,
    #                evaluator_model_1=O_GEMMA3_27B_LABEL
    #                measure_name=MEASURE_NAME)
    # export_results(evaluated_model_label=DEEPSEEK_R1_LABEL,
    #                evaluator_model_1=O_GEMMA3_27B_LABEL
    #                measure_name=MEASURE_NAME)

    # with open(join(RESULTS_ANALYSIS_PATH, COMBINED_EVIDENCE_TRIPLETS_FILE_NAME % MEASURE_NAME), "w", encoding="utf-8") as write_file:
    #     json.dump(results, write_file, indent=4, separators=(",", ": "))


    # # additional_elements_error

    # MEASURE_NAME = "_additional_elements_error_auto"

    # export_results(evaluated_model_label=O_GEMMA_LABEL,
    #                evaluator_model_1=O_DEEPSEEK_R1_32B_LABEL,
    #                measure_name=MEASURE_NAME,
    #                max_items=10)
    # export_results(evaluated_model_label=DEEPSEEK_R1_LABEL,
    #                evaluator_model_1=O_DEEPSEEK_R1_32B_LABEL,
    #                measure_name=MEASURE_NAME,
    #                max_items=10)

    # with open(join(RESULTS_ANALYSIS_PATH, COMBINED_EVIDENCE_TRIPLETS_FILE_NAME % MEASURE_NAME), "w", encoding="utf-8") as write_file:
    #     json.dump(results, write_file, indent=4, separators=(",", ": "))


    # misuse_unreliable_evidence

    MEASURE_NAME = "_misuse_unreliable_evidence_auto"

    export_results(evaluated_model_label=O_GEMMA_LABEL,
                   evaluator_model_1=O_DEEPSEEK_R1_32B_LABEL,
                   measure_name=MEASURE_NAME,
                   max_items=10)
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL,
                   evaluator_model_1=O_DEEPSEEK_R1_32B_LABEL,
                   measure_name=MEASURE_NAME,
                   max_items=10)

    with open(join(RESULTS_ANALYSIS_PATH, COMBINED_EVIDENCE_TRIPLETS_FILE_NAME % MEASURE_NAME), "w", encoding="utf-8") as write_file:
        json.dump(results, write_file, indent=4, separators=(",", ": "))

