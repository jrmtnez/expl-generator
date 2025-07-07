import logging
import json
import sys
from os.path import join
sys.path.append('.')
from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL
from pipeline.config import RESULTS_FILE_NAME, RESULTS_ANALYSIS_PATH
from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH
from pipeline.config import ITEM_NON_CONTRADICTION_FILE_NAME
from pipeline.config import ROOT_LOGGER_ID
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL, O_GEMMA3_27B_LABEL


LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def export_results(evaluated_model_label=O_GEMMA_LABEL,
                   evaluator_model_1=None, evaluator_model_2=None,
                   measure_name=None,
                   measure_reasoning=None,
                   max_items=200, offset=0):

    results_items_dict_1 = {}
    results_items_dict_2 = {}

    if evaluator_model_1 is not None:
        data_file_1 = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_model_label, evaluator_model_1))

        with open(data_file_1, encoding="utf-8") as json_file:
            items = json.load(json_file)

            for item in items:
                item_evaluations = {}
                if item.get(evaluator_model_1 + measure_name):
                    item_evaluations[evaluator_model_1 + measure_name] = item.get(evaluator_model_1 + measure_name)
                if item.get(evaluator_model_1 + measure_reasoning):
                    item_evaluations[evaluator_model_1 + measure_reasoning] = item.get(evaluator_model_1 + measure_reasoning)
                results_items_dict_1[item["item_id"]] = item_evaluations

    if evaluator_model_2 is not None:
        data_file_2 = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_model_label, evaluator_model_2))

        with open(data_file_2, encoding="utf-8") as json_file:
            items = json.load(json_file)

            for item in items:
                item_evaluations = {}
                if item.get(evaluator_model_2 + measure_name):
                    item_evaluations[evaluator_model_2 + measure_name] = item.get(evaluator_model_2 + measure_name)
                if item.get(evaluator_model_2 + measure_reasoning):
                    item_evaluations[evaluator_model_2 + measure_reasoning] = item.get(evaluator_model_2 + measure_reasoning)
                results_items_dict_2[item["item_id"]] = item_evaluations

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % evaluated_model_label)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)


    results = []
    for item in items[offset: max_items + offset]:
        item_dict = {}
        item_dict["item_id"] = item["item_id"]
        item_dict["claim"] = item["claim"]

        if item["item_class"] == "T":
            item_dict["item_class"] = "true"
        if item["item_class"] == "PF":
            item_dict["item_class"] = "partially false"
        if item["item_class"] == "F":
            item_dict["item_class"] = "false"

        fact_checking_questions_and_reasoning = []
        reasoning_no = 0

        sentences = item["fr_sentences"]
        for sentence in sentences:
            triplets = sentence["triplets"]
            for triplet in triplets:
                reasoning_no += 1
                reasoning_id = f"argument {reasoning_no}"
                fact_checking_question_and_reasoning_dict = {}
                fact_checking_question_and_reasoning_dict[reasoning_id] = triplet["reasoning_for_the_answer_given"]
                fact_checking_questions_and_reasoning.append(fact_checking_question_and_reasoning_dict)

        item_dict["arguments"] = fact_checking_questions_and_reasoning
        item_dict["justification"] = item["justification"]

        non_contradiction_evaluation_1 = ""
        non_contradiction_evaluation_2 = ""

        if results_items_dict_1.get(item["item_id"]):
            if results_items_dict_1.get(item["item_id"]).get(evaluator_model_1 + measure_name):
                non_contradiction_evaluation_1 = results_items_dict_1.get(item["item_id"]).get(evaluator_model_1 + measure_name)

                item_dict[evaluator_model_1 + measure_name] = non_contradiction_evaluation_1

                if results_items_dict_1.get(item["item_id"]).get(evaluator_model_1 + measure_reasoning):
                    item_dict[evaluator_model_1 + measure_reasoning] = results_items_dict_1.get(item["item_id"]).get(evaluator_model_1 + measure_reasoning)

        if results_items_dict_2.get(item["item_id"]):
            if results_items_dict_2.get(item["item_id"]).get(evaluator_model_2 + measure_name):
                non_contradiction_evaluation_2 = results_items_dict_2.get(item["item_id"]).get(evaluator_model_2 + measure_name)

                item_dict[evaluator_model_2 + measure_name] = non_contradiction_evaluation_2

                if results_items_dict_2.get(item["item_id"]).get(evaluator_model_2 + measure_reasoning):
                    item_dict[evaluator_model_2 + measure_reasoning] = results_items_dict_2.get(item["item_id"]).get(evaluator_model_2 + measure_reasoning)

        if non_contradiction_evaluation_1 == "NOK" or non_contradiction_evaluation_2 == "NOK":
            results.append(item_dict)


    with open(join(RESULTS_ANALYSIS_PATH, ITEM_NON_CONTRADICTION_FILE_NAME % (evaluated_model_label, measure_name)), "w", encoding="utf-8") as write_file:
        json.dump(results, write_file, indent=4, separators=(",", ": "))

    logger.info("Items to evaluate: %s", len(items))


if __name__ == '__main__':

    # item_non_contradiction

    export_results(evaluated_model_label=O_GEMMA_LABEL,
                   evaluator_model_1=O_GEMMA3_27B_LABEL, evaluator_model_2=O_DEEPSEEK_R1_32B_LABEL,
                   max_items=200,
                   measure_name="_item_non_contradiction_auto", measure_reasoning="_item_non_contradiction_analysis_auto")
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL,
                   evaluator_model_1=O_GEMMA3_27B_LABEL, evaluator_model_2=O_DEEPSEEK_R1_32B_LABEL,
                   max_items=200,
                   measure_name="_item_non_contradiction_auto", measure_reasoning="_item_non_contradiction_analysis_auto")
