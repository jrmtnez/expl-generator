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

from llm_mgmt.llm_ollama_mgmt import O_GEMMA_LABEL
from  llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_LABEL

from llm_mgmt.llm_ollama_mgmt import O_GEMMA3_27B_LABEL, O_GEMMA3_27B_MODEL_NAME
from llm_mgmt.llm_ollama_mgmt import O_QWEN_MOE_30B_LABEL, O_QWEN_MOE_30B_MODEL_NAME
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_32B_LABEL, O_DEEPSEEK_R1_32B_MODEL_NAME
from llm_mgmt.llm_ollama_mgmt import O_COGITO_32B_LABEL, O_COGITO_32B_MODEL_NAME
from llm_mgmt.llm_ollama_mgmt import O_MISTRAL_24B_LABEL, O_MISTRAL_24B_MODEL_NAME
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_70B_LABEL, O_DEEPSEEK_R1_70B_MODEL_NAME

from pipeline.config import RESULTS_PATH, RESULTS_FILE_NAME, ROOT_LOGGER_ID
from prompt_library.evaluation.y1_evaluate_non_contradiction_on_claim_explanation import PROMPT as EVAL_NON_CONTRADICTION_ON_CLAIM_EXPLANATION_PROMPT
from prompt_library.evaluation.y1_evaluate_non_contradiction_on_claim_explanation import QUERY_TEXT as EVAL_NON_CONTRADICTION_ON_CLAIM_EXPLANATION_QUERY_TEXT
from prompt_library.evaluation.y2_evaluate_additional_elements_on_claim_explanation import PROMPT as EVAL_ADDITIONAL_ELEMENT_ON_CLAIM_EXPLANATION_PROMPT
from prompt_library.evaluation.y2_evaluate_additional_elements_on_claim_explanation import QUERY_TEXT as EVAL_ADDITIONAL_ELEMENT_ON_CLAIM_EXPLANATION_QUERY_TEXT
from prompt_library.evaluation.y3_evaluate_misuse_unreliable_evidence_on_claim_explanation import PROMPT as EVAL_MISUSE_UNRELIABLE_EVIDENCE_ON_CLAIM_EXPLANATION_PROMPT
from prompt_library.evaluation.y3_evaluate_misuse_unreliable_evidence_on_claim_explanation import QUERY_TEXT as EVAL_MISUSE_UNRELIABLE_EVIDENCE_ON_CLAIM_EXPLANATION_QUERY_TEXT
from prompt_library.evaluation.x1_evaluate_non_contradiction_on_item_explanation import PROMPT as EVAL_NON_CONTRADICTION_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.evaluation.x1_evaluate_non_contradiction_on_item_explanation import QUERY_TEXT as EVAL_NON_CONTRADICTION_ON_ITEM_EXPLANATION_QUERY_TEXT
from prompt_library.evaluation.x2_evaluate_non_redundancy_on_item_explanation import PROMPT as EVAL_NON_REDUNDANCY_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.evaluation.x2_evaluate_non_redundancy_on_item_explanation import QUERY_TEXT as EVAL_NON_REDUNDANCY_ON_ITEM_EXPLANATION_QUERY_TEXT
from prompt_library.evaluation.x3_evaluate_coverage_on_item_explanation import PROMPT as EVAL_COVERAGE_ON_ITEM_EXPLANATION_PROMPT
from prompt_library.evaluation.x3_evaluate_coverage_on_item_explanation import QUERY_TEXT as EVAL_COVERAGE_ON_ITEM_EXPLANATION_QUERY_TEXT


LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


PROMPT_LOG_FILE = "temp/prompt_result_%s_%s_%s_%s_%s.txt"
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

    makedirs("temp", exist_ok = True)

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

    for attempt in range(no_of_attempts):

        number_of_queries = 0
        number_of_errors = 0

        for item in tqdm(items, desc=f"Model: {evaluator_model_label}, attempt: {attempt + 1}"):

            item_query_dict = {}
            item_query_dict["main argument"] = item["justification"]

            item_claims_query_dict = {}
            claim_counter = 0

            sentences = item["fr_sentences"]
            for sentence in sentences:

                triplets = sentence["triplets"]
                for triplet in triplets:

                    claim_counter += 1
                    item_claims_query_dict["argument " + str(claim_counter)] = triplet["explanation"]

                    number_of_queries += 1

                    if evaluator_model_label + "_non_contradiction_auto" not in triplet:
                        try:
                            query_dict = {}
                            query_dict["claim"] = triplet["claim"]
                            query_dict["evidence"] = triplet["evidence"]
                            query_dict["explanation"] = triplet["explanation"]

                            query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                            prompt = EVAL_NON_CONTRADICTION_ON_CLAIM_EXPLANATION_PROMPT
                            query_text = EVAL_NON_CONTRADICTION_ON_CLAIM_EXPLANATION_QUERY_TEXT % (query_json)

                            full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                            logging.debug("Evaluating non-contradiction response: %s", response_text)

                            file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], claim_counter, "triplet_non_contradiction")
                            file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                            with open(file_name, "w") as prompt_log:
                                prompt_log.write(file_content)

                            response_text = format_response_text(response_text)

                            response_json = extract_json(response_text)[-1]
                            logging.debug("Evaluating non-contradiction json: %s", response_json)

                            check_response_value(response_json["non_contradiction"], use_na=True)

                            triplet[evaluator_model_label + "_non_contradiction_auto"] = response_json["non_contradiction"]

                            if response_json["non_contradiction"] == "NOK" and "analysis" not in response_json:
                                raise ValueError("Missing non contradiction analisys in result for claim %s", triplet["claim"])

                            if "analysis" in response_json:
                                triplet[evaluator_model_label + "_non_contradiction_analysis_auto"] = response_json["analysis"]

                            with open(data_file, "w", encoding="utf-8") as write_file:
                                json.dump(items, write_file, indent=4, separators=(",", ": "))

                        except TypeError:
                            logging.info("Error evaluating non-contradiction (TypeError)...")
                            number_of_errors += 1
                        except KeyError:
                            logging.info("Error evaluating non-contradiction (KeyError)...")
                            number_of_errors += 1
                        except ValueError as err:
                            logging.info(err.args)
                            number_of_errors += 1
                        except AttributeError as err:
                            logging.info(err.args)
                            number_of_errors += 1

                    number_of_queries += 1

                    if evaluator_model_label + "_additional_elements_error_auto" not in triplet:
                        try:
                            query_dict = {}
                            query_dict["claim"] = triplet["claim"]
                            query_dict["evidence"] = triplet["evidence"]
                            query_dict["explanation"] = triplet["explanation"]

                            query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                            prompt = EVAL_ADDITIONAL_ELEMENT_ON_CLAIM_EXPLANATION_PROMPT
                            query_text = EVAL_ADDITIONAL_ELEMENT_ON_CLAIM_EXPLANATION_QUERY_TEXT % (query_json)

                            full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                            logging.debug("Evaluating additional elements response: %s", response_text)

                            file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], claim_counter, "additional_elements_error")
                            file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                            with open(file_name, "w") as prompt_log:
                                prompt_log.write(file_content)

                            response_text = format_response_text(response_text)

                            response_json = extract_json(response_text)[-1]
                            logging.debug("Evaluating additional elements json: %s", response_json)

                            check_response_value(response_json["additional_elements_error"])

                            triplet[evaluator_model_label + "_additional_elements_error_auto"] = response_json["additional_elements_error"]

                            if response_json["additional_elements_error"] == "NOK" and "analysis" not in response_json:
                                raise ValueError("Missing additional elements error analisys in result for claim %s", triplet["claim"])

                            if "analysis" in response_json:
                                triplet[evaluator_model_label + "_additional_elements_error_analysis_auto"] = response_json["analysis"]

                            with open(data_file, "w", encoding="utf-8") as write_file:
                                json.dump(items, write_file, indent=4, separators=(",", ": "))

                        except TypeError:
                            logging.info("Error evaluating additional elements (TypeError)...")
                            number_of_errors += 1
                        except KeyError:
                            logging.info("Error evaluating additional elements (KeyError)...")
                            number_of_errors += 1
                        except ValueError as err:
                            logging.info(err.args)
                            number_of_errors += 1
                        except AttributeError as err:
                            logging.info(err.args)
                            number_of_errors += 1

                    number_of_queries += 1

                    if evaluator_model_label + "_misuse_unreliable_evidence_auto" not in triplet:
                        try:
                            query_dict = {}
                            query_dict["claim"] = triplet["claim"]
                            query_dict["evidence"] = triplet["evidence"]
                            query_dict["explanation"] = triplet["explanation"]

                            query_json = json.dumps(query_dict, indent=4, separators=(",", ": "))

                            prompt = EVAL_MISUSE_UNRELIABLE_EVIDENCE_ON_CLAIM_EXPLANATION_PROMPT
                            query_text = EVAL_MISUSE_UNRELIABLE_EVIDENCE_ON_CLAIM_EXPLANATION_QUERY_TEXT % (query_json)

                            full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                            logging.debug("Evaluating misuse unreliable evidence response: %s", response_text)

                            file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], claim_counter, "misuse_unreliable_evidence")
                            file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                            with open(file_name, "w") as prompt_log:
                                prompt_log.write(file_content)

                            response_text = format_response_text(response_text)

                            response_json = extract_json(response_text)[-1]
                            logging.debug("Evaluating misuse unreliable evidence json: %s", response_json)

                            check_response_value(response_json["misuse_unreliable_evidence"])

                            triplet[evaluator_model_label + "_misuse_unreliable_evidence_auto"] = response_json["misuse_unreliable_evidence"]

                            if response_json["misuse_unreliable_evidence"] == "NOK" and "analysis" not in response_json:
                                raise ValueError("Missing misuse unreliable evidence analisys in result for claim %s", triplet["claim"])

                            if "analysis" in response_json:
                                triplet[evaluator_model_label + "_misuse_unreliable_evidence_analysis_auto"] = response_json["analysis"]

                            with open(data_file, "w", encoding="utf-8") as write_file:
                                json.dump(items, write_file, indent=4, separators=(",", ": "))

                        except TypeError:
                            logging.info("Error evaluating misuse unreliable evidence (TypeError)...")
                            number_of_errors += 1
                        except KeyError:
                            logging.info("Error evaluating misuse unreliable evidence (KeyError)...")
                            number_of_errors += 1
                        except ValueError as err:
                            logging.info(err.args)
                            number_of_errors += 1
                        except AttributeError as err:
                            logging.info(err.args)
                            number_of_errors += 1

            item_query_dict["secondary arguments"] = item_claims_query_dict

            number_of_queries += 1

            if evaluator_model_label + "_non_contradiction_auto" not in item:
                try:
                    query_json = json.dumps(item_query_dict, indent=4, separators=(",", ": "))

                    prompt = EVAL_NON_CONTRADICTION_ON_ITEM_EXPLANATION_PROMPT
                    query_text = EVAL_NON_CONTRADICTION_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                    full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                    logging.debug("Evaluating item non-contradiction response: %s", response_text)

                    file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], 0, "non_contradiction")
                    file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                    with open(file_name, "w") as prompt_log:
                        prompt_log.write(file_content)

                    response_text = format_response_text(response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Evaluating item non-contradiction json: %s", response_json)

                    check_response_value(response_json["non_contradiction"])

                    item[evaluator_model_label + "_non_contradiction_auto"] = response_json["non_contradiction"]
                    item[evaluator_model_label + "_non_contradiction_analysis_auto"] = response_json["analysis"]

                    with open(data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error evaluating item non-contradiction (TypeError)...")
                    number_of_errors += 1
                except KeyError:
                    logging.info("Error evaluating item non-contradiction (KeyError)...")
                    number_of_errors += 1
                except ValueError as err:
                    logging.info(err.args)
                    number_of_errors += 1
                except AttributeError as err:
                    logging.info(err.args)
                    number_of_errors += 1

            # ----------------------------------------------------------------
            # no aporta nada respecto a la evaluación manual de no redundancia
            # ----------------------------------------------------------------

            # number_of_queries += 1

            # if evaluator_model_label + "_non_redundancy_auto" not in item:
            #     try:

            #         query_json = json.dumps(item_query_dict, indent=4, separators=(",", ": "))

            #         prompt = EVAL_NON_REDUNDANCY_ON_ITEM_EXPLANATION_PROMPT
            #         query_text = EVAL_NON_REDUNDANCY_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

            #         _, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
            #         logging.debug("Evaluating item non-redundancy response: %s", response_text)

            #         response_text = format_response_text(response_text)

            #         response_json = extract_json(response_text)[-1]
            #         logging.debug("Evaluating item non-redundancy json: %s", response_json)

            #         check_response_value(response_json["non_redundancy"])

            #         item[evaluator_model_label + "_non_redundancy_auto"] = response_json["non_redundancy"]
            #         item[evaluator_model_label + "_non_redundancy_analysis_auto"] = response_json["analysis"]

            #         with open(data_file, "w", encoding="utf-8") as write_file:
            #             json.dump(items, write_file, indent=4, separators=(",", ": "))

            #     except TypeError:
            #         logging.info("Error evaluating item non-redundancy (TypeError)...")
            #         number_of_errors += 1
            #     except KeyError:
            #         logging.info("Error evaluating item non-redundancy (KeyError)...")
            #         number_of_errors += 1
            #     except ValueError as err:
            #         logging.info(err.args)
            #         number_of_errors += 1
            #     except AttributeError as err:
            #         logging.info(err.args)
            #         number_of_errors += 1

            number_of_queries += 1

            if evaluator_model_label + "_coverage_auto" not in item:
                try:
                    query_json = json.dumps(item_query_dict, indent=4, separators=(",", ": "))

                    prompt = EVAL_COVERAGE_ON_ITEM_EXPLANATION_PROMPT
                    query_text = EVAL_COVERAGE_ON_ITEM_EXPLANATION_QUERY_TEXT % (query_json)

                    full_query_text, response_text = query_model(prompt, query_text, pipeline, model_name=evaluator_model_name)
                    logging.debug("Evaluating item coverage response: %s", response_text)

                    file_name = PROMPT_LOG_FILE % (evaluated_items_model_label, evaluator_model_label, item["item_id"], 0, "coverage")
                    file_content = PROMPT_ANALYSIS % (full_query_text, response_text)

                    with open(file_name, "w") as prompt_log:
                        prompt_log.write(file_content)

                    response_text = format_response_text(response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Evaluating item coverage json: %s", response_json)

                    check_response_value(response_json["coverage"])

                    item[evaluator_model_label + "_coverage_auto"] = response_json["coverage"]
                    item[evaluator_model_label + "_coverage_analysis_auto"] = response_json["analysis"]

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

            r = Readability(item["justification"])

            if "readability flesch-kincaid score" not in item:
                # https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
                # 50.0–30.0: College
                # 30.0–10.0: College graduate
                # 10.0– 0.0: Professional
                try:
                    fk = r.flesch_kincaid()
                    item["readability flesch-kincaid score"] = fk.score
                except ReadabilityException as err:
                    logging.info(err.args)
                    item["readability flesch-kincaid score"] = err.args

            if "readability gunning fog score" not in item:
                # https://readabilityformulas.com/the-gunnings-fog-index-or-fog-readability-formula/
                # 12: High School
                # 17-: University Graduate
                try:
                    gf = r.gunning_fog()
                    item["readability gunning fog score"] = gf.score
                except ReadabilityException as err:
                    logging.info(err.args)
                    item["readability gunning fog score"] = err.args

            if "readability ari score" not in item:
                # https://readabilityformulas.com/the-automated-readability-index-ari/
                # 28 and above: College
                try:
                    a = r.ari()
                    item["readability ari score"] = a.score
                except ReadabilityException as err:
                    logging.info(err.args)
                    item["readability ari score"] = err.args
        logger.info("Attempt: %s, queries: %s, errors %s", attempt, number_of_queries, number_of_errors)
    logger.info("Items evaluated: %s", len(items))


if __name__ == '__main__':

    evaluate_results(evaluator_model_name=O_GEMMA3_27B_MODEL_NAME, evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    evaluate_results(evaluator_model_name=O_GEMMA3_27B_MODEL_NAME, evaluator_model_label=O_GEMMA3_27B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)
    evaluate_results(evaluator_model_name=O_DEEPSEEK_R1_32B_MODEL_NAME, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=O_GEMMA_LABEL)
    evaluate_results(evaluator_model_name=O_DEEPSEEK_R1_32B_MODEL_NAME, evaluator_model_label=O_DEEPSEEK_R1_32B_LABEL, evaluated_items_model_label=DEEPSEEK_R1_LABEL)

