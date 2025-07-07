# ---------------------------------------------------------------------------------
# generates *_item_evidence_reasoning.json files containing item explanation and
# triplet/closed question explanations, useful to check manually the criterion
# "item-triplets non-contradiction" and "item-triplets coverage"
# ---------------------------------------------------------------------------------

import logging
import json
import sys
from os.path import join
sys.path.append('.')

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL

from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH, EVIDENCE_REASONING_FILE_NAME, RESULTS_ANALYSIS_PATH, ROOT_LOGGER_ID
from pipeline.pipeline_loop import get_class

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def export_results(preferred_model_label=O_GEMMA_LABEL):

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % preferred_model_label)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    results = []
    for item in items:
        item_dict = {}
        item_dict["item_id"] = item["item_id"]
        item_dict["claim"] = item["claim"]
        item_dict["item_class"] = item["item_class"]

        fact_checking_questions_and_reasoning = []
        reasoning_no = 0

        sentences = item["fr_sentences"]
        for sentence in sentences:
            triplets = sentence["triplets"]
            for triplet in triplets:
                reasoning_no += 1
                reasoning_id = f"reasoning (argument {reasoning_no})"
                fact_checking_question_and_reasoning_dict = {}
                fact_checking_question_and_reasoning_dict["question"] = triplet["closed_question"]
                fact_checking_question_and_reasoning_dict["veracity"] = get_class(sentence["sentence_class"])
                fact_checking_question_and_reasoning_dict[reasoning_id] = triplet["reasoning_for_the_answer_given"]
                fact_checking_questions_and_reasoning.append(fact_checking_question_and_reasoning_dict)

        item_dict["class_explained_from_evidence"] = fact_checking_questions_and_reasoning
        item_dict["justification"] = item["justification"]
        results.append(item_dict)

    with open(join(RESULTS_ANALYSIS_PATH, EVIDENCE_REASONING_FILE_NAME % preferred_model_label), "w", encoding="utf-8") as write_file:
        json.dump(results, write_file, indent=4, separators=(",", ": "))

    logger.info("Items to evaluate: %s", len(items))


if __name__ == '__main__':
    export_results(preferred_model_label=O_GEMMA_LABEL)
    export_results(preferred_model_label=DEEPSEEK_R1_LABEL)
