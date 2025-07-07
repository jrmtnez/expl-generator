import logging
import json
import sys
from os.path import join
sys.path.append('.')

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL, O_GEMMA3_27B_LABEL

from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH, COMBINED_ITEM_REASONING_FILE_NAME
from pipeline.config import RESULTS_FILE_NAME, RESULTS_ANALYSIS_PATH
from pipeline.config import ROOT_LOGGER_ID
from pipeline.pipeline_loop import get_class

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)

results = []


def export_results(evaluated_model_label=O_GEMMA_LABEL,
                   evaluator_model_1=None,
                   measure_name=None):

    results_items_dict_1 = {}

    if evaluator_model_1 is not None:
        data_file_1 = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_model_label, evaluator_model_1))

        with open(data_file_1, encoding="utf-8") as json_file:
            items = json.load(json_file)

            for item in items:
                item_evaluations = {}
                if item.get(evaluator_model_1 + measure_name):
                    item_evaluations[evaluator_model_1 + measure_name] = item.get(evaluator_model_1 + measure_name)
                results_items_dict_1[item["item_id"]] = item_evaluations

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % evaluated_model_label)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    for item in items:
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
                # reasoning_id = f"reasoning (argument {reasoning_no})"
                reasoning_id = f"argument {reasoning_no}"
                fact_checking_question_and_reasoning_dict = {}
                # fact_checking_question_and_reasoning_dict["question"] = triplet["closed_question"]
                # fact_checking_question_and_reasoning_dict["veracity"] = get_class(sentence["sentence_class"])
                fact_checking_question_and_reasoning_dict[reasoning_id] = triplet["reasoning_for_the_answer_given"]
                fact_checking_questions_and_reasoning.append(fact_checking_question_and_reasoning_dict)

        # item_dict["class_explained_from_evidence"] = fact_checking_questions_and_reasoning
        item_dict["justification arguments"] = fact_checking_questions_and_reasoning
        item_dict["justification"] = item["justification"]

        item_dict["generating model"] = evaluated_model_label

        if results_items_dict_1.get(item["item_id"]):
            if results_items_dict_1.get(item["item_id"]).get(evaluator_model_1 + measure_name):
                non_contradiction_evaluation_1 = results_items_dict_1.get(item["item_id"]).get(evaluator_model_1 + measure_name)

                if non_contradiction_evaluation_1 == "NOK":
                    results.append(item_dict)

    logger.info("Items to evaluate: %s", len(items))


if __name__ == '__main__':
    export_results(evaluated_model_label=O_GEMMA_LABEL,
                   evaluator_model_1=O_GEMMA3_27B_LABEL,
                   measure_name="_item_non_contradiction_auto")
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL,
                   evaluator_model_1=O_GEMMA3_27B_LABEL,
                   measure_name="_item_non_contradiction_auto")

    with open(join(RESULTS_ANALYSIS_PATH, COMBINED_ITEM_REASONING_FILE_NAME), "w", encoding="utf-8") as write_file:
        json.dump(results, write_file, indent=4, separators=(",", ": "))
