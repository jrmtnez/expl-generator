import logging
import json
import sys
from os.path import join
sys.path.append('.')

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL
from llm_mgmt.llm_ollama_mgmt import O_GEMMA3_27B_LABEL
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL

from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH, ROOT_LOGGER_ID
from pipeline.config import RESULTS_FILE_NAME
from pipeline.openai_loop import GPT_MODEL_LABEL

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def deleteBadKey(badKey, json):
    if type(json) == list:
        for child_json in json:
            deleteBadKey(badKey, child_json)
    else:
        if type(json) == dict:
            for k, v in list(json.items()):
                if k == badKey:
                    del json[k]
                elif isinstance(v, dict):
                    deleteBadKey(badKey, v)
                elif isinstance(v, list):
                    for d in v:
                        deleteBadKey(badKey, d)
        # else:
        #     print(type(json))


def delete_from_results(evaluated_model_label=O_GEMMA_LABEL):

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % evaluated_model_label)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    for key in ["fact_checking_w_triplets_answer", "fact_checking_w_triplets_reasoning", "fact_checking_w_triplets_class",
                "reasoning_for_the_answer_given", "triplet_fact_checked_and_justified_with"]:
        deleteBadKey(key, items)

    with open(join(RESULTS_PATH, "new_" + EVALUATED_NEWS_ITEMS_FILE_NAME % evaluated_model_label), "w", encoding="utf-8") as write_file:
        json.dump(items, write_file, indent=4, separators=(",", ": "))


def delete_from_evaluations(evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL):

    data_file = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_items_model_label, evaluator_model_label))

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    # for key in ["original_reasoning_text"]:
    #     deleteBadKey(key, items)
    # for key in [f"{evaluator_model_label}_item_coverage_auto", f"{evaluator_model_label}_item_coverage_analysis_auto"]:
    #     deleteBadKey(key, items)
    # for key in [f"{evaluator_model_label}_original_reasoning_text_breakdown", f"{evaluator_model_label}_justification_breakdown"]:
    #     deleteBadKey(key, items)
    # for key in [f"{evaluator_model_label}_item_non_contradiction_auto", f"{evaluator_model_label}_item_non_redundancy_auto"]:
    #     deleteBadKey(key, items)
    # for key in [f"{evaluator_model_label}_item_coverage_auto", f"{evaluator_model_label}_item_coverage_analysis_auto"]:
    #     deleteBadKey(key, items)
    # for key in ["readability flesch-kincaid score", "readability gunning fog score", "readability ari score"]:
    #     deleteBadKey(key, items)
    # for key in [f"{evaluator_model_label}_non_contradiction_auto", f"{evaluator_model_label}_non_contradiction_analysis_auto"]:
    #     deleteBadKey(key, items)
    for key in [f"{evaluator_model_label}_item_coverage_main_argument_auto", f"{evaluator_model_label}_item_coverage_main_argument_analysis_auto"]:
        deleteBadKey(key, items)


    with open(join(RESULTS_PATH, "new_" + RESULTS_FILE_NAME % (evaluated_items_model_label, evaluator_model_label)), "w", encoding="utf-8") as write_file:
        json.dump(items, write_file, indent=4, separators=(",", ": "))



if __name__ == '__main__':

    # delete_from_evaluations(evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_COGITO_32B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_COGITO_32B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)


    # delete_from_evaluations(evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=GPT_MODEL_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)
    # delete_from_evaluations(evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=GPT_MODEL_LABEL)
