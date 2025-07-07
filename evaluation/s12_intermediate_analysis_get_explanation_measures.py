import logging
import json
import sys
from os.path import join
sys.path.append('.')

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL
from llm_mgmt.llm_ollama_mgmt import O_GEMMA3_27B_LABEL
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL

from pipeline.config import RESULTS_PATH, RESULTS_FILE_NAME, ROOT_LOGGER_ID
from pipeline.pipeline_loop import get_class

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL):

    logger.info("")
    logger.info("Results for model %s evaluated with %s", evaluated_model_label, evaluator_model_label)

    data_file = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_model_label, evaluator_model_label))

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    triplets_to_evaluate = 0

    item_non_contradiction_auto = 0
    item_coverage_auto = 0
    sentence_count = 0

    triplet_non_contradiction_auto = 0
    triplet_additional_elements_error_auto = 0
    triplet_misuse_unreliable_evidence_auto = 0

    for item in items:

        if item[evaluator_model_label + "_non_contradiction_auto"] == "OK":
            item_non_contradiction_auto += 1
        if item[evaluator_model_label + "_coverage_auto"] == "OK":
            item_coverage_auto += 1

        sentences = item["fr_sentences"]
        for sentence in sentences:
            sentence_count += 1

            triplets = sentence["triplets"]
            for triplet in triplets:
                triplets_to_evaluate += 1

                if triplet[evaluator_model_label + "_non_contradiction_auto"] == "OK":
                    triplet_non_contradiction_auto += 1
                if triplet[evaluator_model_label + "_additional_elements_error_auto"] == "OK":
                    triplet_additional_elements_error_auto += 1
                if triplet[evaluator_model_label + "_misuse_unreliable_evidence_auto"] == "OK":
                    triplet_misuse_unreliable_evidence_auto += 1

    items_to_evaluate = len(items)

    item_non_contradiction_auto_perc = 100 * item_non_contradiction_auto / items_to_evaluate
    item_coverage_auto_perc = 100 * item_coverage_auto / items_to_evaluate
    triplet_non_contradiction_auto_perc = 100 * triplet_non_contradiction_auto / triplets_to_evaluate
    triplet_additional_elements_error_auto_perc = 100 * triplet_additional_elements_error_auto / triplets_to_evaluate
    triplet_misuse_unreliable_evidence_auto_perc = 100 * triplet_misuse_unreliable_evidence_auto / triplets_to_evaluate

    avg = (item_non_contradiction_auto_perc + item_coverage_auto_perc + triplet_non_contradiction_auto_perc + triplet_additional_elements_error_auto_perc + triplet_misuse_unreliable_evidence_auto_perc) / 5

    logger.info("")
    logger.info(f"Items to evaluate:               {items_to_evaluate:{' '}{'>'}{4}}")
    logger.info(f"Sentence count:                  {sentence_count:{' '}{'>'}{4}}")
    logger.info(f"non_contradiction_auto:          {item_non_contradiction_auto:{' '}{'>'}{4}} : {item_non_contradiction_auto_perc:{' '}{'>'}{6}.2f}%" )
    logger.info(f"coverage_auto:                   {item_coverage_auto:{' '}{'>'}{4}} : {item_coverage_auto_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"Triplets to evaluate:            {triplets_to_evaluate:{' '}{'>'}{4}}")
    logger.info(f"non_contradiction_auto:          {triplet_non_contradiction_auto:{' '}{'>'}{4}} : {triplet_non_contradiction_auto_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"additional_elements_error_auto:  {triplet_additional_elements_error_auto:{' '}{'>'}{4}} : {triplet_additional_elements_error_auto_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"misuse_unreliable_evidence_auto: {triplet_misuse_unreliable_evidence_auto:{' '}{'>'}{4}} : {triplet_misuse_unreliable_evidence_auto_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"Average:                         {items_to_evaluate + triplets_to_evaluate:{' '}{'>'}{4}} : {avg:{' '}{'>'}{6}.2f}%")
    logger.info("")


if __name__ == '__main__':

    export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL)
    export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL)
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL)
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL)
