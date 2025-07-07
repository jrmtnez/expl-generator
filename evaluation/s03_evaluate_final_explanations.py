import logging
import json
import gc
import torch
from tqdm import tqdm
from os import makedirs
from os.path import join
from readability import Readability
from readability.exceptions import ReadabilityException
import sys
sys.path.append('.')
from llm_mgmt.pipeline_mgmt import get_gpu_pipeline, query_model
from pipeline.json_helpers import extract_json
from pipeline.openai_loop import GPT_MODEL_LABEL

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL

from llm_mgmt.llm_ollama_mgmt import O_GEMMA3_27B_LABEL, O_GEMMA3_27B_MODEL_NAME
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL, O_DEEPSEEK_R1_32B_MODEL_NAME

from pipeline.config import RESULTS_PATH, RESULTS_FILE_NAME, ROOT_LOGGER_ID
from prompt_library.final_evaluation.m1_extract_arguments_on_item_explanation import PROMPT as EXTRACT_ARGUMENTS_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.final_evaluation.m1_extract_arguments_on_item_explanation import QUERY_TEXT as EXTRACT_ARGUMENTS_ON_ITEM_EXPLANATION_QUERY_TEXT
from prompt_library.final_evaluation.m2_extract_main_argument_on_item_explanation import PROMPT as EXTRACT_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.final_evaluation.m2_extract_main_argument_on_item_explanation import QUERY_TEXT as EXTRACT_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_QUERY_TEXT
from prompt_library.final_evaluation.n1_evaluate_coverage_on_item_explanation import PROMPT as EVALUATE_COVERAGE_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.final_evaluation.n1_evaluate_coverage_on_item_explanation import QUERY_TEXT as EVALUATE_COVERAGE_ON_ITEM_EXPLANATION_QUERY_TEXT
from prompt_library.final_evaluation.n1_evaluate_coverage_main_argument_on_item_explanation import PROMPT as EVALUATE_COVERAGE_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.final_evaluation.n1_evaluate_coverage_main_argument_on_item_explanation import QUERY_TEXT as EVALUATE_COVERAGE_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_QUERY_TEXT
from prompt_library.final_evaluation.n2_evaluate_non_contradiction_on_item_explanation import PROMPT as EVALUATE_NON_CONTRADICTION_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.final_evaluation.n2_evaluate_non_contradiction_on_item_explanation import QUERY_TEXT as EVALUATE_NON_CONTRADICTION_ON_ITEM_EXPLANATION_QUERY_TEXT
from prompt_library.final_evaluation.n3_evaluate_non_redundancy_on_item_explanation import PROMPT as EVALUATE_NON_REDUNDANCY_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.final_evaluation.n3_evaluate_non_redundancy_on_item_explanation import QUERY_TEXT as EVALUATE_NON_REDUNDANCY_ON_ITEM_EXPLANATION_QUERY_TEXT


LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


PROMPT_LOG_FILE = "temp/prompt_result_%s_%s_%s_%s.txt"
PROMPT_ANALYSIS = """
=======================
QUERY
=======================
%s
=======================
RESPONSE
=======================
%s
=======================
"""


def format_response_text(response_text):
    response_text = response_text.replace("\n", " ")
    return response_text


def check_response_value(response_value, use_na=False):
    if use_na:
        if response_value not in ["OK", "NOK", "NA"]:
            raise ValueError('Response is not among allowed values: "OK", "NOK", "NA".')
    else:
        if response_value not in ["OK", "NOK"]:
            raise ValueError('Response is not among allowed values: "OK", "NOK".')

def evaluate_results(evaluator_model_name=O_GEMMA3_27B_MODEL_NAME, evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL, no_of_attempts=3, alternative_evaluator_model_label=None):

    logging.info("")
    logging.info("Evaluating model %s with model %s", evaluated_items_model_label, evaluator_model_label)
    logging.info("")

    makedirs("temp", exist_ok=True)

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    if alternative_evaluator_model_label is not None:
        evaluator_model_name = alternative_evaluator_model_label

    pipeline, _ = get_gpu_pipeline(model_name=evaluator_model_name)

    data_file = join(RESULTS_PATH, RESULTS_FILE_NAME % (evaluated_items_model_label, evaluator_model_label))

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    logger.info("Extraction of arguments...")

    for attempt in range(no_of_attempts):

        number_of_queries = 0
        number_of_errors = 0

        for item in tqdm(items, desc=f"Model: {evaluator_model_label}, attempt: {attempt + 1}"):

            for text_to_breakdown in ["original_reasoning_text", "justification"]:

                if evaluator_model_label + "_" + text_to_breakdown + "_breakdown" not in item:
                    try:

                        query_dict = {}
                        query_dict["veracity_analysis_text"] = item[text_to_breakdown]

                        query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                        prompt = EXTRACT_ARGUMENTS_ON_ITEM_EXPLANATION_PROMPT
                        query_text = EXTRACT_ARGUMENTS_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                        full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                        logging.debug("Breakdown %s response: %s", text_to_breakdown, response_text)

                        file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], text_to_breakdown + "_breakdown")
                        file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                        with open(file_name, "w") as prompt_log:
                            prompt_log.write(file_content)

                        response_text = format_response_text(response_text)

                        response_json = extract_json(response_text)[-1]
                        logging.debug("Breakdown %s json: %s", text_to_breakdown, response_json)

                        item[evaluator_model_label + "_" + text_to_breakdown + "_breakdown"] = response_json["arguments"]

                        with open(data_file, "w", encoding="utf-8") as write_file:
                            json.dump(items, write_file, indent=4, separators=(",", ": "))

                    except TypeError:
                        logging.info("Error breakdown %s (TypeError)...", text_to_breakdown)
                        number_of_errors += 1
                    except KeyError:
                        logging.info("Error breakdown %s (KeyError)...", text_to_breakdown)
                        number_of_errors += 1
                    except ValueError as err:
                        logging.info(err.args)
                        number_of_errors += 1
                    except AttributeError as err:
                        logging.info(err.args)
                        number_of_errors += 1

        logger.info("Attempt: %s, queries: %s, errors %s", attempt, number_of_queries, number_of_errors)
    logger.info("Items evaluated: %s", len(items))

    if number_of_errors > 0:
        logger.info("there are errors in the extraction of arguments. Ending process.")
        return

    logger.info("Extraction of main argument...")

    for attempt in range(no_of_attempts):

        number_of_queries = 0
        number_of_errors = 0

        for item in tqdm(items, desc=f"Model: {evaluator_model_label}, attempt: {attempt + 1}"):

            for text_to_breakdown in ["original_reasoning_text", "justification"]:

                if evaluator_model_label + "_" + text_to_breakdown + "_main_argument" not in item:
                    try:

                        query_dict = {}
                        query_dict["veracity_analysis_text"] = item[text_to_breakdown]

                        query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                        prompt = EXTRACT_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_PROMPT
                        query_text = EXTRACT_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                        full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                        logging.debug("Breakdown %s response: %s", text_to_breakdown, response_text)

                        file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], text_to_breakdown + "_breakdown")
                        file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                        with open(file_name, "w") as prompt_log:
                            prompt_log.write(file_content)

                        response_text = format_response_text(response_text)

                        response_json = extract_json(response_text)[-1]
                        logging.debug("Main argument %s json: %s", text_to_breakdown, response_json)

                        item[evaluator_model_label + "_" + text_to_breakdown + "_main_argument"] = response_json["main_argument"]

                        with open(data_file, "w", encoding="utf-8") as write_file:
                            json.dump(items, write_file, indent=4, separators=(",", ": "))

                    except TypeError:
                        logging.info("Error main argument %s (TypeError)...", text_to_breakdown)
                        number_of_errors += 1
                    except KeyError:
                        logging.info("Error main argument %s (KeyError)...", text_to_breakdown)
                        number_of_errors += 1
                    except ValueError as err:
                        logging.info(err.args)
                        number_of_errors += 1
                    except AttributeError as err:
                        logging.info(err.args)
                        number_of_errors += 1

        logger.info("Attempt: %s, queries: %s, errors %s", attempt, number_of_queries, number_of_errors)
    logger.info("Items evaluated: %s", len(items))

    if number_of_errors > 0:
        logger.info("there are errors in the extraction of main argument. Ending process.")
        return

    # return

    logger.info("Checking item explanation coverage...")

    for attempt in range(no_of_attempts):

        number_of_queries = 0
        number_of_errors = 0

        for item in tqdm(items, desc=f"Model: {evaluator_model_label}, attempt: {attempt + 1}"):

            if evaluator_model_label + "_item_coverage_auto" not in item:
                try:

                    query_dict = {}
                    query_dict["reference_arguments"] = item[evaluator_model_label + "_original_reasoning_text_breakdown"]
                    query_dict["proposed_arguments"] = item[evaluator_model_label + "_justification_breakdown"]

                    query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                    prompt = EVALUATE_COVERAGE_ON_ITEM_EXPLANATION_PROMPT
                    query_text = EVALUATE_COVERAGE_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                    full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                    logging.debug("Evaluate item coverage response: %s", response_text)

                    file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], "item_coverage")
                    file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                    with open(file_name, "w") as prompt_log:
                        prompt_log.write(file_content)

                    response_text = format_response_text(response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Evaluate item coverage json: %s", response_json)

                    item[evaluator_model_label + "_item_coverage_auto"] = response_json["coverage"]
                    item[evaluator_model_label + "_item_coverage_analysis_auto"] = response_json["equivalence_list"]

                    with open(data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error evaluating item coverage (TypeError)...")
                    number_of_errors += 1
                except KeyError:
                    logging.info("Error evaluating item coverage (KeyError)...")
                    number_of_errors += 1
                except ValueError as err:
                    logging.info(err.args)
                    number_of_errors += 1
                except AttributeError as err:
                    logging.info(err.args)
                    number_of_errors += 1

        logger.info("Attempt: %s, queries: %s, errors %s", attempt, number_of_queries, number_of_errors)
    logger.info("Items evaluated: %s", len(items))


    logger.info("Checking item explanation coverage main argument...")

    for attempt in range(no_of_attempts):

        number_of_queries = 0
        number_of_errors = 0

        for item in tqdm(items, desc=f"Model: {evaluator_model_label}, attempt: {attempt + 1}"):

            if evaluator_model_label + "_item_coverage_main_argument_auto" not in item:
                try:

                    query_dict = {}
                    query_dict["reference_main_argument"] = item[evaluator_model_label + "_original_reasoning_text_main_argument"]
                    query_dict["proposed_main_argument"] = item[evaluator_model_label + "_justification_main_argument"]

                    query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                    prompt = EVALUATE_COVERAGE_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_PROMPT
                    query_text = EVALUATE_COVERAGE_MAIN_ARGUMENT_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                    full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                    logging.debug("Evaluate item coverage main argument response: %s", response_text)

                    file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], "item_coverage_main_argument")
                    file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                    with open(file_name, "w") as prompt_log:
                        prompt_log.write(file_content)

                    response_text = format_response_text(response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Evaluate item coverage main argument json: %s", response_json)

                    item[evaluator_model_label + "_item_coverage_main_argument_auto"] = response_json["coverage"]
                    if "analysis" in response_json:
                        item[evaluator_model_label + "_item_coverage_main_argument_analysis_auto"] = response_json["analysis"]

                    with open(data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error evaluating item coverage main argument (TypeError)...")
                    number_of_errors += 1
                except KeyError:
                    logging.info("Error evaluating item coverage main argument (KeyError)...")
                    number_of_errors += 1
                except ValueError as err:
                    logging.info(err.args)
                    number_of_errors += 1
                except AttributeError as err:
                    logging.info(err.args)
                    number_of_errors += 1

        logger.info("Attempt: %s, queries: %s, errors %s", attempt, number_of_queries, number_of_errors)
    logger.info("Items evaluated: %s", len(items))


    # return

    logger.info("Checking item explanation non contradiction...")

    for attempt in range(no_of_attempts):

        number_of_queries = 0
        number_of_errors = 0

        for item in tqdm(items, desc=f"Model: {evaluator_model_label}, attempt: {attempt + 1}"):

            if evaluator_model_label + "_item_non_contradiction_auto" not in item:
                try:

                    query_dict = {}
                    query_dict["claim"] = item["claim"]
                    query_dict["explanatory text"] = item["justification"]

                    query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                    prompt = EVALUATE_NON_CONTRADICTION_ON_ITEM_EXPLANATION_PROMPT
                    query_text = EVALUATE_NON_CONTRADICTION_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                    full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                    logging.debug("Evaluate item non contradiction response: %s", response_text)

                    file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], "item_non_contradiction")
                    file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                    with open(file_name, "w") as prompt_log:
                        prompt_log.write(file_content)

                    response_text = format_response_text(response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Evaluate item non contradiction json: %s", response_json)

                    item[evaluator_model_label + "_item_non_contradiction_auto"] = response_json["non_contradiction"]
                    if response_json.get("analysis"):
                        item[evaluator_model_label + "_item_non_contradiction_analysis_auto"] = response_json["analysis"]

                    with open(data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error evaluating item non contradiction (TypeError)...")
                    number_of_errors += 1
                except KeyError:
                    logging.info("Error evaluating item non contradiction (KeyError)...")
                    number_of_errors += 1
                except ValueError as err:
                    logging.info(err.args)
                    number_of_errors += 1
                except AttributeError as err:
                    logging.info(err.args)
                    number_of_errors += 1

        logger.info("Attempt: %s, queries: %s, errors %s", attempt, number_of_queries, number_of_errors)
    logger.info("Items evaluated: %s", len(items))


    logger.info("Checking item explanation non redundancy...")

    for attempt in range(no_of_attempts):

        number_of_queries = 0
        number_of_errors = 0

        for item in tqdm(items, desc=f"Model: {evaluator_model_label}, attempt: {attempt + 1}"):

            if evaluator_model_label + "_item_non_redundancy_auto" not in item:
                try:

                    query_dict = {}
                    query_dict["claim"] = item["claim"]
                    query_dict["explanatory text"] = item["justification"]

                    query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                    prompt = EVALUATE_NON_REDUNDANCY_ON_ITEM_EXPLANATION_PROMPT
                    query_text = EVALUATE_NON_REDUNDANCY_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                    full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                    logging.debug("Evaluate item non redundancy response: %s", response_text)

                    file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], "item_non_redundancy")
                    file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                    with open(file_name, "w") as prompt_log:
                        prompt_log.write(file_content)

                    response_text = format_response_text(response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Evaluate item non redundancy json: %s", response_json)

                    item[evaluator_model_label + "_item_non_redundancy_auto"] = response_json["non_redundancy"]
                    if response_json.get("analysis"):
                        item[evaluator_model_label + "_item_non_redundancy_analysis_auto"] = response_json["analysis"]

                    with open(data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error evaluating item non redundancy (TypeError)...")
                    number_of_errors += 1
                except KeyError:
                    logging.info("Error evaluating item non redundancy (KeyError)...")
                    number_of_errors += 1
                except ValueError as err:
                    logging.info(err.args)
                    number_of_errors += 1
                except AttributeError as err:
                    logging.info(err.args)
                    number_of_errors += 1

        logger.info("Attempt: %s, queries: %s, errors %s", attempt, number_of_queries, number_of_errors)
    logger.info("Items evaluated: %s", len(items))


if __name__ == '__main__':

    evaluate_results(evaluator_model_name=O_GEMMA3_27B_MODEL_NAME, evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    evaluate_results(evaluator_model_name=O_GEMMA3_27B_MODEL_NAME, evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)

    evaluate_results(evaluator_model_name=O_DEEPSEEK_R1_32B_MODEL_NAME, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    evaluate_results(evaluator_model_name=O_DEEPSEEK_R1_32B_MODEL_NAME, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)

    evaluate_results(evaluator_model_name=O_GEMMA3_27B_MODEL_NAME, evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=GPT_MODEL_LABEL)
    evaluate_results(evaluator_model_name=O_DEEPSEEK_R1_32B_MODEL_NAME, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=GPT_MODEL_LABEL)
