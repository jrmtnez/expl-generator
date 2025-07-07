import logging
import json
import sys
from os.path import join
sys.path.append('.')

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL
from llm_mgmt.llm_ollama_mgmt import O_GEMMA3_27B_LABEL
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL
from pipeline.openai_loop import GPT_MODEL_LABEL

from pipeline.config import ROOT_LOGGER_ID
from pipeline.config import RESULTS_FILE_NAME, RESULTS_PATH
from pipeline.config import RESULTS_ANALYSIS_PATH, FINAL_EXPLANATIONS_COMPARE_FILE_NAME
from pipeline.pipeline_loop import get_class

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL, show_items_with_zero_coverage=False):

    data_file = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_model_label, evaluator_model_label))

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    item_coverage_main_argument = 0
    item_coverage = 0
    item_coverage_some = 0
    item_coverage_perc_sum = 0
    generated_target_statemenet_ratio_sum = 0
    item_coverage_compensated = 0

    item_non_contradiction = 0
    item_non_redundancy = 0

    results = []
    for item in items:
        item_id = item["item_id"]

        item_fields = "id, review_entity"
        db_items = select_fields_where(connection, "annotate_item", item_fields, f"id = {item_id}")

        review_entity = db_items[0][1]

        item_dict = {}
        item_dict["item_id"] = item["item_id"]
        item_dict["claim"] = item["claim"]
        item_dict["item_class"] = item["item_class"]
        item_dict["original_reasoning_text"] = item["original_reasoning_text"]
        item_dict["justification"] = item["justification"]
        item_dict[evaluator_model_label + "_original_reasoning_text_breakdown"] = item[evaluator_model_label + "_original_reasoning_text_breakdown"]
        item_dict[evaluator_model_label + "_justification_breakdown"] = item[evaluator_model_label + "_justification_breakdown"]
        item_dict[evaluator_model_label + "_item_coverage_auto"] = item[evaluator_model_label + "_item_coverage_auto"]
        item_dict[evaluator_model_label + "_item_coverage_analysis_auto"] = item[evaluator_model_label + "_item_coverage_analysis_auto"]
        item_dict[evaluator_model_label + "_item_non_contradiction_auto"] = item[evaluator_model_label + "_item_non_contradiction_auto"]
        if item.get(evaluator_model_label + "_item_non_contradiction_analysis_auto"):
            item_dict[evaluator_model_label + "_item_non_contradiction_analysis_auto"] = item[evaluator_model_label + "_item_non_contradiction_analysis_auto"]
        item_dict[evaluator_model_label + "_item_non_redundancy_auto"] = item[evaluator_model_label + "_item_non_redundancy_auto"]
        if item.get(evaluator_model_label + "_item_non_redundancy_analysis_auto"):
            item_dict[evaluator_model_label + "_item_non_redundancy_analysis_auto"] = item[evaluator_model_label + "_item_non_redundancy_analysis_auto"]

        item_dict[evaluator_model_label + "_item_coverage_main_argument_auto"] = item[evaluator_model_label + "_item_coverage_main_argument_auto"]
        if item.get(evaluator_model_label + "_item_coverage_main_argument_analysis_auto"):
            item_dict[evaluator_model_label + "_item_coverage_main_argument_analysis_auto"] = item[evaluator_model_label + "_item_coverage_main_argument_analysis_auto"]
        results.append(item_dict)

        generated_justification_statements = item[evaluator_model_label + "_justification_breakdown"]
        generated_justification_statements_count = len(generated_justification_statements)

        # -----------------------
        # coverage main argument
        # -----------------------

        if item[evaluator_model_label + "_item_coverage_main_argument_auto"] == "OK":
            item_coverage_main_argument += 1


        # -----------------------
        # % statement covered sum
        # -----------------------

        total_statements_to_cover = 0
        statements_covered = 0

        item_coverage_analysis = item[evaluator_model_label + "_item_coverage_analysis_auto"]
        total_statements_to_cover = len(item_coverage_analysis)
        for statement in item_coverage_analysis:
            for value in statement.values():
                if value != "NOK":
                    statements_covered += 1

        if show_items_with_zero_coverage:
            if statements_covered == 0:
                logger.info(f'item_id {item["item_id"]} with zero coverage!')

        item_coverage_perc = statements_covered / total_statements_to_cover
        item_coverage_perc_sum += item_coverage_perc

        if item_coverage_perc > 0:
            item_coverage_some += 1

        # ------------------------------------------
        # coverage compensates with other statements
        # ------------------------------------------

        generated_target_statemenet_ratio = generated_justification_statements_count / total_statements_to_cover
        if generated_target_statemenet_ratio > 1:
            generated_target_statemenet_ratio = 1

        generated_target_statemenet_ratio_sum += generated_target_statemenet_ratio

        if generated_target_statemenet_ratio == 1:
            item_coverage_compensated += 1

        if item[evaluator_model_label + "_item_coverage_auto"] == "OK":
            item_coverage += 1
        if item[evaluator_model_label + "_item_non_contradiction_auto"] == "OK":
            item_non_contradiction += 1
        if item[evaluator_model_label + "_item_non_redundancy_auto"] == "OK":
            item_non_redundancy += 1

    with open(join(RESULTS_ANALYSIS_PATH, FINAL_EXPLANATIONS_COMPARE_FILE_NAME % (evaluated_model_label, evaluator_model_label)), "w", encoding="utf-8") as write_file:
        json.dump(results, write_file, indent=4, separators=(",", ": "))

    items_to_evaluate = len(items)
    item_coverage_main_argument_perc = 100 * item_coverage_main_argument / items_to_evaluate
    item_coverage_perc = 100 * item_coverage / items_to_evaluate
    item_non_contradiction_perc = 100 * item_non_contradiction / items_to_evaluate
    item_non_redundancy_perc = 100 * item_non_redundancy / items_to_evaluate

    item_coverage_sum_perc = 100 * item_coverage_perc_sum / items_to_evaluate

    item_coverage_compensated_perc = 100 * item_coverage_compensated / items_to_evaluate

    generated_target_statemenet_ratio_sum_perc = 100 * generated_target_statemenet_ratio_sum / items_to_evaluate

    logger.info("")
    logger.info("-----------------------------------------------")
    logger.info(f"{evaluated_model_label} evaluated with {evaluator_model_label}")
    logger.info("-----------------------------------------------")
    logger.info(f"items_to_evaluate:                  {items_to_evaluate:{' '}{'>'}{3}}")
    logger.info(f"item_non_contradiction:             {item_non_contradiction:{' '}{'>'}{3}} : {item_non_contradiction_perc:{' '}{'>'}{6}.2f}%" )
    logger.info(f"item_non_redundancy:                {item_non_redundancy:{' '}{'>'}{3}} : {item_non_redundancy_perc:{' '}{'>'}{6}.2f}%" )
    logger.info(f"item_coverage:                      {item_coverage:{' '}{'>'}{3}} : {item_coverage_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"item_coverage_main_argument:        {item_coverage_main_argument:{' '}{'>'}{3}} : {item_coverage_main_argument_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"item_coverage_sum_perc:             {item_coverage_some:{' '}{'>'}{3}} : {item_coverage_sum_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"item_coverage_compensated:          {item_coverage_compensated:{' '}{'>'}{3}} : {item_coverage_compensated_perc:{' '}{'>'}{6}.2f}%")
    logger.info(f"item_coverage_compensated_sum_perc: {item_coverage_compensated:{' '}{'>'}{3}} : {generated_target_statemenet_ratio_sum_perc:{' '}{'>'}{6}.2f}%")


if __name__ == '__main__':
    export_results(evaluated_model_label=GPT_MODEL_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL)
    export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL)
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL, evaluator_model_label=O_GEMMA3_27B_LABEL)

    export_results(evaluated_model_label=GPT_MODEL_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL)
    export_results(evaluated_model_label=O_GEMMA_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL)
    export_results(evaluated_model_label=DEEPSEEK_R1_LABEL, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL)
