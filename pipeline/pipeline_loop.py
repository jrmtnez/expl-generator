import logging
import torch
import gc
import json
import sys
import time
from datetime import datetime
from os import makedirs
from os.path import join, exists
sys.path.append('.')
from llm_mgmt.pipeline_mgmt import get_gpu_pipeline, query_model

from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_MODEL_NAME, DEEPSEEK_R1_LABEL
from llm_mgmt.llm_ollama_mgmt import O_GEMMA_MODEL_NAME, O_GEMMA_LABEL
from prompt_library.pipeline.a1_summarize_news_item import PROMPT as SUMMARIZE_NEWS_ITEM_PROMPT
from prompt_library.pipeline.a1_summarize_news_item import QUERY_TEXT as SUMMARIZE_NEWS_ITEM_QUERY_TEXT
from prompt_library.pipeline.a1_summarize_news_item import MAX_TEXT_SIZE as SUMMARIZE_NEWS_ITEM_MAX_TEXT_SIZE
from prompt_library.pipeline.a2_extract_news_item_main_topic import PROMPT as EXTRACT_ITEM_MAIN_SUBJECT_PROMPT
from prompt_library.pipeline.a2_extract_news_item_main_topic import QUERY_TEXT as EXTRACT_ITEM_MAIN_SUBJECT_QUERY_TEXT
from prompt_library.pipeline.b1_extract_simplified_spo_main_verb import PROMPT as EXTRACT_SIMPLIFIED_SPO_PROMPT
from prompt_library.pipeline.b1_extract_simplified_spo_main_verb import QUERY_TEXT as EXTRACT_SIMPLIFIED_SPO_QUERY_TEXT
from prompt_library.pipeline.b2_select_relevant_spos import PROMPT as SELECT_RELEVANT_SPOS_PROMPT
from prompt_library.pipeline.b2_select_relevant_spos import QUERY_TEXT as SELECT_RELEVANT_SPOS_QUERY_TEXT
from prompt_library.pipeline.b3_generate_questions_from_spos import PROMPT as GENERATE_QUESTIONS_FROM_SPOS_PROMPT
from prompt_library.pipeline.b3_generate_questions_from_spos import QUERY_TEXT as GENERATE_QUESTIONS_FROM_SPOS_QUERY_TEXT
from prompt_library.pipeline.c_select_relevant_search_results import PROMPT as SELECT_RELEVANT_SEARCH_RESULTS_PROMPT
from prompt_library.pipeline.c_select_relevant_search_results import QUERY_TEXT as SELECT_RELEVANT_SEARCH_RESULTS_QUERY_TEXT
from prompt_library.pipeline.d1_extract_spo_from_search_result import PROMPT as EXTRACT_SEARCH_SPO_PROMPT
from prompt_library.pipeline.d1_extract_spo_from_search_result import QUERY_TEXT as EXTRACT_SEARCH_SPO_QUERY_TEXT
from prompt_library.pipeline.d2_complete_spos import PROMPT as COMPLETE_SPOS_PROMPT
from prompt_library.pipeline.d2_complete_spos import QUERY_TEXT as COMPLETE_SPOS_QUERY_TEXT
from prompt_library.pipeline.e_select_relevant_search_spos import PROMPT as SELECT_RELEVANT_SEARCH_SPOS_PROMPT
from prompt_library.pipeline.e_select_relevant_search_spos import QUERY_TEXT as SELECT_RELEVANT_SEARCH_SPOS_QUERY_TEXT
from prompt_library.pipeline.f1_fact_check_question_with_context import PROMPT as FACT_CHECK_QUESTION_WITH_CONTEXT_PROMPT
from prompt_library.pipeline.f1_fact_check_question_with_context import QUERY_TEXT as FACT_CHECK_QUESTION_WITH_CONTEXT_QUERY_TEXT
from prompt_library.pipeline.f2_fact_check_extract_class import PROMPT as FACT_CHECK_EXTRACT_CLASS_PROMPT
from prompt_library.pipeline.f2_fact_check_extract_class import QUERY_TEXT as FACT_CHECK_EXTRACT_CLASS_QUERY_TEXT
from prompt_library.pipeline.i1_fact_check_question_with_spos_and_context import PROMPT as FACT_CHECK_QUESTION_W_SPO_PROMPT
from prompt_library.pipeline.i1_fact_check_question_with_spos_and_context import QUERY_TEXT as FACT_CHECK_QUESTION_W_SPO_QUERY_TEXT
from prompt_library.pipeline.i2_explain_fact_checked_question_with_spos_and_context import PROMPT as JUSTIFY_ANSWER_TO_QUESTION_W_SPO_PROMPT
from prompt_library.pipeline.i2_explain_fact_checked_question_with_spos_and_context import QUERY_TEXT as JUSTIFY_ANSWER_TO_QUESTION_W_SPO_QUERY_TEXT
from prompt_library.pipeline.j_explain_fact_checked_item import PROMPT as EXPLAIN_FACT_CHECKED_ITEM_PROMPT
from prompt_library.pipeline.j_explain_fact_checked_item import QUERY_TEXT as EXPLAIN_FACT_CHECKED_ITEM_QUERY_TEXT
from pipeline.config import ROOT_LOGGER_ID, DATA_PATH, NEWS_ITEMS_FILE_NAME, EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH
from pipeline.json_helpers import extract_json
from rag_mgmt.search_results_mgmt import get_base_url_and_body_results_list
from rag_mgmt.search_engine_mgmt import get_rate_limit_exception, get_timeout_exception

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)


def count_sentences_without_triplets(items):
    items_count = 0
    senteces_count = 0
    for item in items:
        exist_triplets = True
        sentences = item["fr_sentences"]
        for sentence in sentences:
            if "triplets" not in sentence:
                senteces_count += 1
                exist_triplets = False
        if not exist_triplets:
            items_count += 1
    return items_count, senteces_count


def all_items_summarized(items):
    for item in items:
        if "summary" not in item or "main_subject" not in item:
            return False
    return True


def all_sentences_have_triplets(items):
    for item in items:
        sentences = item["fr_sentences"]
        for sentence in sentences:
            if "triplets" not in sentence:
                return False
    return True


def all_triplets_have_selected_search_results(items):
    for item in items:
        sentences = item["fr_sentences"]
        for sentence in sentences:
            triplets = sentence["triplets"]
            for triplet in triplets:
                if "selected_search_results" not in triplet:
                    return False
    return True


def all_search_results_have_triplets(items):
    for item in items:
        sentences = item["fr_sentences"]
        for sentence in sentences:
            triplets = sentence["triplets"]
            for triplet in triplets:
                if "selected_search_results" not in triplet:
                    return False
                for search_result in triplet["selected_search_results"]:
                    if "search_result_triplets" not in search_result:
                        return False
    return True


def all_triplets_have_relevant_search_triplets(items):
    for item in items:
        sentences = item["fr_sentences"]
        for sentence in sentences:
            triplets = sentence["triplets"]
            for triplet in triplets:
                if "selected_search_triplets" not in triplet:
                    return False
    return True


def all_triplets_have_been_checked(items, fact_checking_mode="text"):
    for item in items:
        sentences = item["fr_sentences"]
        for sentence in sentences:
            if "triplets" not in sentence:
                return False

            triplets = sentence["triplets"]
            for triplet in triplets:
                if fact_checking_mode == "text":
                    if "class" not in triplet:
                        return False
                if fact_checking_mode == "triplets":
                    if "fact_checking_w_triplets_class" not in triplet:
                        return False
                    if "reasoning_for_the_answer_given" not in triplet:
                        return False
    return True


def all_items_justified(items):
    for item in items:
        if "justification" not in item:
            return False
    return True


def is_a_null_value(value):
    if value == None:
        return True
    if value == "null":
        return True
    return False


def summarize_items(items, model_name, attempt, evaluated_data_file):
    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s, attempt %s", item_no, len(items), attempt + 1)

        if "summary" not in item or "main_subject" not in item:
            try:
                if "summary" not in item:

                    logging.info("Extracting summary from item %s with model '%s'...", item["item_id"], model_name)

                    item_text = item["text"]
                    if len(item_text) > SUMMARIZE_NEWS_ITEM_MAX_TEXT_SIZE:
                        logging.info("Item %s too long (%s), cutting to %s characters...", item["item_id"], len(item_text), SUMMARIZE_NEWS_ITEM_MAX_TEXT_SIZE)
                        item_text = item_text[:SUMMARIZE_NEWS_ITEM_MAX_TEXT_SIZE]

                    prompt = SUMMARIZE_NEWS_ITEM_PROMPT
                    query_text = SUMMARIZE_NEWS_ITEM_QUERY_TEXT % (item_text)

                    _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)
                    logging.debug("Summarize response: %s", response_text)

                    response_json = extract_json(response_text)

                    response_json = response_json[-1]
                    logging.debug("Summarize json: %s", response_json)

                    main_subject = response_json["extracted_summary"]

                    item["summary"] = main_subject
                    item["summarized_with"] = model_name

                    with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                if "summary" in item and "main_subject" not in item:

                    logging.info("Extracting main subject from item %s with model '%s'...", item["item_id"], model_name)

                    prompt = EXTRACT_ITEM_MAIN_SUBJECT_PROMPT
                    query_text = EXTRACT_ITEM_MAIN_SUBJECT_QUERY_TEXT % (item["summary"])

                    _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)
                    logging.debug("Extract main subject response: %s", response_text)

                    response_json = extract_json(response_text)

                    response_json = response_json[-1]
                    logging.debug("Extract main subject json: %s", response_json)

                    main_subject = response_json["main_subject"]

                    item["main_subject"] = main_subject
                    item["main_subject_extracted_with"] = model_name

                    with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

            except TypeError:
                logging.info("Error summarizing text (TypeError)...")
                continue
            except KeyError:
                logging.info("Error summarizing text (KeyError)...")
                continue


def extract_triplets_and_questions(items, model_name, attempt, evaluated_data_file):

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s, attempt %s", item_no, len(items), attempt + 1)

        sentences = item["fr_sentences"]
        for sentence in sentences:

            null_triplet = False

            if "triplets" not in sentence:

                logging.info("Extracting subtriplets from sentence: '%s...'", sentence["sentence_text"][:50])

                prompt = EXTRACT_SIMPLIFIED_SPO_PROMPT
                query_text = EXTRACT_SIMPLIFIED_SPO_QUERY_TEXT % (sentence["sentence_text"], sentence["predicate"])

                _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)
                logging.debug("Extract spo response: %s", response_text)

                try:
                    response_json = extract_json(response_text)[-1]
                    logging.debug("Extract spo json: %s", response_json)

                    triplets = response_json["triplets"]

                    for triplet in triplets:
                        if is_a_null_value(triplet["subject"]) or is_a_null_value(triplet["predicate"]) or is_a_null_value(triplet["object"]):
                            null_triplet = True

                    if null_triplet:
                        logging.info("Null triplet detected, skipping sentence...")
                    else:
                        logging.info("Selecting relevant subtriplets from sentence: '%s...'", sentence["sentence_text"][:50])

                        prompt = SELECT_RELEVANT_SPOS_PROMPT
                        query_text = SELECT_RELEVANT_SPOS_QUERY_TEXT % (triplets)

                        logging.debug("Select relevant query: %s", query_text)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        logging.debug("Select relevant response: %s", response_text)
                        response_json = extract_json(response_text)[-1]
                        logging.debug("Select relevant json: %s", response_json)
                        triplets = response_json["triplets"]

                        logging.debug("Select triplets: %s", triplets)

                        logging.info("Generating closed questions from triplets:'")
                        for triplet in triplets:
                            logging.info("  %s", triplet)

                        prompt = GENERATE_QUESTIONS_FROM_SPOS_PROMPT
                        query_text = GENERATE_QUESTIONS_FROM_SPOS_QUERY_TEXT % (triplets)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        logging.debug("Closed questions response: %s", response_text)
                        response_json = extract_json(response_text)[-1]
                        logging.debug("Closed questions json: %s", response_json)
                        triplets = response_json["triplets"]

                        logging.debug("Closed questions triplets: %s", triplets)

                        sentence["triplets"] = triplets
                        sentence["triplets_extracted_with"] = model_name

                    with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error extracting subtriplets and questions (TypeError)...")
                    continue
                except KeyError:
                    logging.info("Error extracting subtriplets and questions (KeyError)...")
                    continue


def extract_search_results(items, model_name, attempt, evaluated_data_file, max_results=10, init_search=False):

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s, attempt %s", item_no, len(items), attempt + 1)

        sentences = item["fr_sentences"]
        for sentence in sentences:

            triplets = sentence["triplets"]
            for triplet in triplets:

                if "search_results" not in triplet or init_search:
                    while True:
                        time.sleep(30)
                        try:
                            text_results_list, results_list = get_base_url_and_body_results_list(triplet["closed_question"], max_results=max_results)
                            triplet["text_results_list"] = text_results_list
                            triplet["search_results"] = results_list
                        except get_rate_limit_exception():
                            logging.info("%s Sleeping to avoid search engine quota limit...", datetime.now())
                            time.sleep(120)
                            continue
                        except get_timeout_exception():
                            logging.info("%s Sleeping due to timeout exception...", datetime.now())
                            time.sleep(120)
                            continue
                        break
                    with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                if "search_results" in triplet and "selected_search_results" not in triplet:
                    logging.info("Selecting search result for question: '%s...'", triplet["closed_question"][:50])

                    try:
                        search_results_query_json = {}
                        search_results_query_json["closed_question"] = triplet["closed_question"]

                        search_result_dict = {}
                        for search_result in triplet["search_results"]:
                            # id = search_result["id"]
                            search_result_content = {}
                            search_result_content["text"] = search_result["body"].replace('"', '')
                            search_result_content["credibility"] = search_result["url_credibility"]
                            search_result_dict[search_result["id"]] = search_result_content
                        search_results_query_json["search_results"] = search_result_dict

                        prompt = SELECT_RELEVANT_SEARCH_RESULTS_PROMPT
                        query_text = SELECT_RELEVANT_SEARCH_RESULTS_QUERY_TEXT % (search_results_query_json)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        response_text = clean_response(response_text)

                        logging.debug("Selecting search results response: %s", response_text)

                        response_json = extract_json(response_text)[-1]
                        logging.debug("Selecting search results json: %s", response_json)

                        selected_search_results_dict = response_json["selected_search_results"]

                        triplet["selected_search_results_dict"] = selected_search_results_dict

                        selected_search_results = []
                        for search_result in triplet["search_results"]:
                            if search_result["id"] in selected_search_results_dict:
                                selected_search_result_dict = {}
                                selected_search_result_dict["url"] = search_result["url"]
                                selected_search_result_dict["url_credibility"] = search_result["url_credibility"]
                                selected_search_result_dict["last_update"] = search_result["last_update"]
                                selected_search_result_dict["body"] = search_result["body"]
                                selected_search_results.append(selected_search_result_dict)

                        triplet["selected_search_results"] = selected_search_results
                        triplet["selected_search_results_with"] = model_name

                        with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                            json.dump(items, write_file, indent=4, separators=(",", ": "))

                    except TypeError:
                        logging.info("Error extracting search results (TypeError)...")
                        continue
                    except KeyError:
                        logging.info("Error extracting search results (KeyError)...")
                        continue

def clean_response(response_text):
    response_text = response_text.replace('\\xa0', ' ')
    response_text = response_text.replace("\'", "")
    return response_text


def assign_first_search_results(items, evaluated_data_file, max_results=3):
    # No results were selected using an LLM.
    # We assume that the first results returned by the search engine are those that are most similar to the question.

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s", item_no, len(items))

        sentences = item["fr_sentences"]
        for sentence in sentences:

            triplets = sentence["triplets"]
            for triplet in triplets:

                if "search_results" in triplet and "selected_search_results" not in triplet:
                    logging.info("Assigning first search results for question: '%s...'", triplet["closed_question"][:50])

                    assigned = 0
                    selected_search_results = []
                    for search_result in triplet["search_results"]:
                        selected_search_result_dict = {}
                        selected_search_result_dict["url"] = search_result["url"]
                        selected_search_result_dict["url_credibility"] = search_result["url_credibility"]
                        selected_search_result_dict["last_update"] = search_result["last_update"]
                        selected_search_result_dict["body"] = search_result["body"]
                        selected_search_results.append(selected_search_result_dict)
                        assigned += 1
                        if assigned >= max_results:
                            break

                    triplet["selected_search_results"] = selected_search_results
                    triplet["selected_search_results_with"] = "The first search results"

                    with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))


def extract_triplets_from_search_results(items, model_name, attempt, evaluated_data_file, complete_triplets=True):

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s, attempt %s", item_no, len(items), attempt + 1)

        sentences = item["fr_sentences"]
        for sentence in sentences:

            triplets = sentence["triplets"]
            for triplet in triplets:

                for search_result in triplet["selected_search_results"]:

                    if "search_result_triplets" not in search_result:
                        logging.info("Extracting triplets from search result: '%s...'", search_result["body"][:50])

                        try:
                            prompt = EXTRACT_SEARCH_SPO_PROMPT
                            query_text = EXTRACT_SEARCH_SPO_QUERY_TEXT % (search_result["body"])

                            _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                            logging.debug("Extract search result triplets response: %s", response_text)

                            response_json = extract_json(response_text)[-1]
                            logging.debug("Extract search result spo json: %s", response_json)

                            search_result_triplets = response_json["triplets"]

                            if complete_triplets:
                                logging.info("Completing the meaning of triplets...")

                                prompt = COMPLETE_SPOS_PROMPT
                                query_text = COMPLETE_SPOS_QUERY_TEXT % (search_result_triplets)

                                _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                                logging.debug("Completing search result triplets response: %s", response_text)

                                response_json = extract_json(response_text)[-1]
                                logging.debug("Completing search result spo json: %s", response_json)

                            search_result_triplets = response_json["triplets"]

                            null_triplet = False
                            selected_search_result_triplets = []
                            for triplet in search_result_triplets:
                                if triplet.get("subject") and triplet.get("predicate") and triplet.get("object"):
                                    if is_a_null_value(triplet["subject"]) or is_a_null_value(triplet["predicate"]) or is_a_null_value(triplet["object"]):
                                        null_triplet = True
                                    else:
                                        selected_search_result_triplets.append(triplet)
                                else:
                                    null_triplet = True

                                if null_triplet:
                                    logging.info("Null search triplet detected, skipping triplet...")

                            search_result["search_result_triplets"] = selected_search_result_triplets
                            search_result["search_result_triplets_extracted_with"] = model_name
                            with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                                json.dump(items, write_file, indent=4, separators=(",", ": "))
                        except TypeError:
                            logging.info("Error extracting search triplets (TypeError)...")
                            continue
                        except KeyError:
                            logging.info("Error extracting search triplets (KeyError)...")
                            continue


def extract_relevant_search_triplets(items, model_name, attempt, evaluated_data_file, use_alternative_match_method=False):

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s, attempt %s (item_id = %s)", item_no, len(items), attempt + 1, item["item_id"])

        sentences = item["fr_sentences"]
        for sentence in sentences:

            triplets = sentence["triplets"]
            for triplet in triplets:

                if "selected_search_triplets" not in triplet:

                    query_for_select_search_triplets_prompt = {}
                    query_for_select_search_triplets_prompt["context"] = item["summary"]
                    query_for_select_search_triplets_prompt["closed_question"] = triplet["closed_question"]

                    candidate_triplet_list = []

                    triplet_id = 0

                    for search_result in triplet["selected_search_results"]:

                        search_result_triplets = search_result["search_result_triplets"]
                        for search_result_triplet in search_result_triplets:
                            triplet_id += 1
                            candidate_triplet = {}
                            candidate_triplet["id"] = triplet_id
                            candidate_triplet["subject"] = search_result_triplet["subject"]
                            candidate_triplet["predicate"] = search_result_triplet["predicate"]
                            candidate_triplet["object"] = search_result_triplet["object"]
                            candidate_triplet["url_credibility"] = search_result["url_credibility"]
                            candidate_triplet_list.append(candidate_triplet)

                    query_for_select_search_triplets_prompt["candidate_triplet_list"] = candidate_triplet_list

                    triplet["query_for_select_search_triplets_prompt"] = query_for_select_search_triplets_prompt

                    try:
                        prompt = SELECT_RELEVANT_SEARCH_SPOS_PROMPT
                        query_text = SELECT_RELEVANT_SEARCH_SPOS_QUERY_TEXT % (query_for_select_search_triplets_prompt)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        logging.debug("Select search triplets response: %s", response_text)

                        response_text = clean_response(response_text)

                        response_json = extract_json(response_text)[-1]
                        logging.debug("Select search triplets json: %s", response_json)

                        selected_search_triplets = response_json["selected_triplet_list"]

                        triplet["original_selected_search_triplets"] = selected_search_triplets

                        # check selected search triplets integrity
                        found = False
                        for selected_search_triplet in selected_search_triplets:
                            found = False
                            for search_triplet in candidate_triplet_list:
                                if search_triplet["subject"] == selected_search_triplet["subject"] and search_triplet["predicate"] == selected_search_triplet["predicate"] and search_triplet["object"] == selected_search_triplet["object"]:
                                    selected_search_triplet["url_credibility"] = search_triplet["url_credibility"]
                                    found = True
                                    break
                            if not found and not use_alternative_match_method:
                                raise ValueError('Selected triplet not found in candidates triplet list.')

                        alternative_selected_search_triplets = []
                        if not found and use_alternative_match_method:
                            for selected_search_triplet in selected_search_triplets:
                                found = False
                                for search_triplet in candidate_triplet_list:
                                    if search_triplet["id"] == selected_search_triplet["id"]:
                                        alternative_selected_search_triplets.append(search_triplet)
                                        found = True
                                        break
                                if not found:
                                    raise ValueError('Selected triplet not found in candidates triplet list.')
                            selected_search_triplets = alternative_selected_search_triplets

                        triplet["selected_search_triplets"] = selected_search_triplets
                        triplet["selected_search_triplets_extracted_with"] = model_name

                        with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                            json.dump(items, write_file, indent=4, separators=(",", ": "))

                    except TypeError:
                        print(response_text)
                        logging.info("Error selecting search triplets (TypeError)...")
                    except KeyError:
                        print(response_text)
                        logging.info("Error selecting search triplets (KeyError)...")
                    except ValueError as err:
                        print(response_text)
                        logging.info(err.args)



def fact_check_triplets(items, model_name, evaluated_data_file):

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s (item_id = %s)", item_no, len(items), item["item_id"])

        sentences = item["fr_sentences"]
        for sentence in sentences:

            false_triplets = 0
            true_triplets = 0

            triplets = sentence["triplets"]
            for triplet in triplets:
                try:
                    if "fact_checking" not in triplet or "class" not in triplet:
                        logging.info("Fact checking subtriplets from sentence: '%s...'", sentence["sentence_text"][:50])

                    if "fact_checking" not in triplet:

                        triplet_text = triplet["subject"] + " " + triplet["predicate"] + " " + triplet["object"]
                        logging.info("Fact-checking triplet: %s...", triplet_text[:50])

                        question = triplet["closed_question"]
                        context = item["summary"]
                        text_results_list = triplet["text_results_list"]

                        prompt = FACT_CHECK_QUESTION_WITH_CONTEXT_PROMPT
                        query_text = FACT_CHECK_QUESTION_WITH_CONTEXT_QUERY_TEXT % (question, text_results_list, context)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        logging.debug("Fact check response: %s", response_text)

                        triplet["fact_checking"] = response_text


                    if "class" not in triplet:

                        triplet_text = triplet["subject"] + " " + triplet["predicate"] + " " + triplet["object"]
                        logging.info("Extracting triplet class: %s...", triplet_text[:50])

                        question = triplet["closed_question"]
                        fact_checking = triplet["fact_checking"]

                        prompt = FACT_CHECK_EXTRACT_CLASS_PROMPT
                        query_text = FACT_CHECK_EXTRACT_CLASS_QUERY_TEXT % (question, fact_checking)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        logging.debug("Extract class response: %s", response_text)
                        response_json = extract_json(response_text)[-1]
                        triplet["class"] = response_json["class"]

                    triplet["triplet_fact_checked_with"] = model_name

                    with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                    if triplet["class"] == "true":
                        true_triplets += 1
                    else:
                        false_triplets += 1

                except TypeError:
                    logging.info("Error fact checking triplet (TypeError)...")
                    continue
                except KeyError:
                    logging.info("Error fact checking triplet (KeyError)...")
                    continue

            if true_triplets > 0 and false_triplets == 0:
                item["estimated_item_class"] = "T"
            if true_triplets > 0 and false_triplets > 0:
                item["estimated_item_class"] = "PF"
            if true_triplets == 0 and false_triplets > 0:
                item["estimated_item_class"] = "F"
            if true_triplets == 0 and false_triplets == 0:
                item["estimated_item_class"] = "NA"

            with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                json.dump(items, write_file, indent=4, separators=(",", ": "))


def get_class(class_code):
    if class_code == "T":
        return "true"
    if class_code == "F":
        return "false"
    if class_code == "PF":
        return "partially false"
    return "not applicable"


def fact_check_triplets_w_triplets(items, model_name, evaluated_data_file):

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s", item_no, len(items))

        sentences = item["fr_sentences"]
        for sentence in sentences:

            false_triplets = 0
            true_triplets = 0

            triplets = sentence["triplets"]
            for triplet in triplets:
                try:
                    if "fact_checking_w_triplets_answer" not in triplet or "reasoning_for_the_answer_given" not in triplet:
                        logging.info("Fact checking subtriplets with subtriplets and justifying answer from sentence: '%s...'", sentence["sentence_text"][:50])

                    if "fact_checking_w_triplets_reasoning" not in triplet:

                        triplet_text = triplet["subject"] + " " + triplet["predicate"] + " " + triplet["object"]
                        logging.info("Fact-checking triplet: %s...", triplet_text[:50])

                        question_dict = {}
                        question_dict["closed_question"] = triplet["closed_question"]

                        question_dict["triplets_found"] = triplet["selected_search_triplets"]       # V0
                        # question_dict["evidence_triplets"] = triplet["selected_search_triplets"]  # V1
                        question_dict["summary"] = item["summary"]

                        prompt = FACT_CHECK_QUESTION_W_SPO_PROMPT
                        query_text = FACT_CHECK_QUESTION_W_SPO_QUERY_TEXT % (question_dict)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        logging.debug("Fact check response: %s", response_text)

                        response_json = extract_json(response_text)[-1]

                        triplet["fact_checking_w_triplets_answer"] = response_json["answer"]
                        triplet["fact_checking_w_triplets_reasoning"] = response_json["reasoning"]
                        if triplet["fact_checking_w_triplets_answer"] == "no":
                            triplet["fact_checking_w_triplets_class"] = "false"
                        else:
                            triplet["fact_checking_w_triplets_class"] = "true"

                    if "reasoning_for_the_answer_given" not in triplet:

                        triplet_text = triplet["subject"] + " " + triplet["predicate"] + " " + triplet["object"]
                        logging.info("Justifying answer for triplet: %s...", triplet_text[:50])

                        if sentence["sentence_class"] == "T":
                            verified_answer = "yes"
                        else:
                            verified_answer = "no"

                        question_dict = {}
                        question_dict["closed_question"] = triplet["closed_question"]
                        question_dict["verified_answer"] = verified_answer
                        question_dict["triplets_found"] = triplet["selected_search_triplets"]
                        question_dict["summary"] = item["summary"]

                        prompt = JUSTIFY_ANSWER_TO_QUESTION_W_SPO_PROMPT
                        query_text = JUSTIFY_ANSWER_TO_QUESTION_W_SPO_QUERY_TEXT % (question_dict)

                        _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)

                        logging.debug("Justifying answer response: %s", response_text)

                        response_json = extract_json(response_text)[-1]

                        triplet["reasoning_for_the_answer_given"] = response_json["reasoning_for_the_answer_given"]

                    triplet["triplet_fact_checked_and_justified_with"] = model_name

                    with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                        json.dump(items, write_file, indent=4, separators=(",", ": "))

                    if triplet["fact_checking_w_triplets_class"] == "true":
                        true_triplets += 1
                    else:
                        false_triplets += 1

                except TypeError:
                    logging.info("Error fact checking triplet with subtriplets (TypeError)...")
                    continue
                except KeyError:
                    logging.info("Error fact checking triplet with subtriplets (KeyError)...")
                    continue

            if true_triplets > 0 and false_triplets == 0:
                item["fact_checking_w_triplets_estimated_item_class"] = "T"
            if true_triplets > 0 and false_triplets > 0:
                item["fact_checking_w_triplets_estimated_item_class"] = "PF"
            if true_triplets == 0 and false_triplets > 0:
                item["fact_checking_w_triplets_estimated_item_class"] = "F"
            if true_triplets == 0 and false_triplets == 0:
                item["fact_checking_w_triplets_estimated_item_class"] = "NA"

            with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                json.dump(items, write_file, indent=4, separators=(",", ": "))


def explain_item_fact_checking(items, model_name, attempt, evaluated_data_file):
    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s, attempt %s", item_no, len(items), attempt + 1)

        if "justification" not in item:

            question_dict = {}
            question_dict["claim"] = item["claim"].replace('\"', "'")  # double quoute issue in generated claim inside response
            question_dict["veracity"] = get_class(item["item_class"])

            fact_checking_questions_and_reasoning = []

            sentences = item["fr_sentences"]
            for sentence in sentences:

                triplets = sentence["triplets"]
                for triplet in triplets:
                    fact_checking_question_and_reasoning_dict = {}
                    fact_checking_question_and_reasoning_dict["question"] = triplet["closed_question"]
                    fact_checking_question_and_reasoning_dict["veracity"] = get_class(sentence["sentence_class"])
                    fact_checking_question_and_reasoning_dict["resoning"] = triplet["reasoning_for_the_answer_given"]

                    fact_checking_questions_and_reasoning.append(fact_checking_question_and_reasoning_dict)

            question_dict["fact_checking_questions_and_reasoning"] = fact_checking_questions_and_reasoning

            try:
                logging.info("Justifying the veracity of item %s with model '%s'...", item["item_id"], model_name)

                prompt = EXPLAIN_FACT_CHECKED_ITEM_PROMPT
                query_text = EXPLAIN_FACT_CHECKED_ITEM_QUERY_TEXT % (question_dict)

                _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)
                logging.debug("Justifying response: %s", response_text)

                response_text = clean_response(response_text)
                response_json = extract_json(response_text)

                response_json = response_json[-1]
                logging.debug("Justifying json: %s", response_json)

                justification = response_json["justification"]

                item["justification_query"] = question_dict
                item["justification"] = justification
                item["justified_with"] = model_name

                with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                    json.dump(items, write_file, indent=4, separators=(",", ": "))

            except TypeError:
                logging.info("Error justifying item (TypeError)...")
                continue
            except KeyError:
                logging.info("Error justifying item (KeyError)...")
                continue


def main_loop(preferred_model_label=None,
              models_for_summarizing=None,
              models_for_other_tasks=None,
              no_of_attempts=3,
              require_all_items_summarized=True,
              require_all_sentences_have_triplets=True,
              require_all_triplets_have_search_results=False,
              require_all_search_results_have_triplets=True,
              require_all_triplets_have_relevant_search_triplets=True,
              require_all_triplets_fact_checked=True,
              fact_checking_mode="triplets"):

    initial_data_file = join(DATA_PATH, NEWS_ITEMS_FILE_NAME)
    evaluated_data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % preferred_model_label)

    makedirs(RESULTS_PATH, exist_ok = True)

    data_file = initial_data_file
    if exists(evaluated_data_file):
        data_file = evaluated_data_file

    logging.info("Loading data from %s ...", data_file)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)


    # ------------------
    # summary generation
    # ------------------

    items_summarized = False
    for model_name in models_for_summarizing:
        for attempt in range(no_of_attempts):
            items_summarized = all_items_summarized(items)
            if items_summarized:
                break
            summarize_items(items, model_name, attempt, evaluated_data_file)
        if items_summarized:
            break

    items_summarized = all_items_summarized(items)
    if not items_summarized and require_all_items_summarized:
        logging.info("Not all items summarized. Exiting the process...")
        return

    # -------------------------------
    # triplets & questions extraction
    # -------------------------------

    print("items/sentences without triplets", count_sentences_without_triplets(items))

    triplets_extracted = False
    for model_name in models_for_other_tasks:
        for attempt in range(no_of_attempts):
            triplets_extracted = all_sentences_have_triplets(items)
            if triplets_extracted:
                break
            extract_triplets_and_questions(items, model_name, attempt, evaluated_data_file)
        if triplets_extracted:
            break

    triplets_extracted = all_sentences_have_triplets(items)
    if not triplets_extracted and require_all_sentences_have_triplets:
        logging.info("Not all sentences have triplets. Exiting the process...")
        return

    # -------------------------------------
    # search results generation & selection
    # -------------------------------------

    search_results_selected = False
    for model_name in models_for_other_tasks:
        for attempt in range(no_of_attempts):
            search_results_selected = all_triplets_have_selected_search_results(items)
            if search_results_selected:
                break
            extract_search_results(items, model_name, attempt, evaluated_data_file)
        if search_results_selected:
            break

    search_results_selected = all_triplets_have_selected_search_results(items)
    if not search_results_selected and require_all_triplets_have_search_results:
        logging.info("Not all triplets have selected search results. Exiting the process...")
        return

    # ----------------------------------
    # search results triplets extraction
    # ----------------------------------

    triplets_extracted = False
    for model_name in models_for_other_tasks:
        for attempt in range(no_of_attempts):
            triplets_extracted = all_search_results_have_triplets(items)
            if triplets_extracted:
                break
            extract_triplets_from_search_results(items, model_name, attempt, evaluated_data_file)
        if triplets_extracted:
            break

    triplets_extracted = all_search_results_have_triplets(items)
    if not triplets_extracted and require_all_search_results_have_triplets:
        logging.info("Not all search results have triplets. Exiting the process...")
        return

    # ----------------------------------
    # relevant search triplets selection
    # ----------------------------------

    triplets_selected = False
    for model_name in models_for_other_tasks:
        for attempt in range(no_of_attempts + 3):
            triplets_selected = all_triplets_have_relevant_search_triplets(items)
            if triplets_selected:
                break
            extract_relevant_search_triplets(items, model_name, attempt, evaluated_data_file, use_alternative_match_method=False)
        if triplets_selected:
            break

    triplets_selected = all_triplets_have_relevant_search_triplets(items)
    if not triplets_selected and require_all_triplets_have_relevant_search_triplets:
        logging.info("Not all triplets have relevant search triplets. Exiting the process...")
        return

    # -------------------
    # fact check triplets
    # -------------------

    triplets_checked = False
    for model_name in models_for_other_tasks:
        for attempt in range(no_of_attempts):
            triplets_checked = all_triplets_have_been_checked(items, fact_checking_mode=fact_checking_mode)
            if triplets_checked:
                break
            if fact_checking_mode == "text":
                fact_check_triplets(items, model_name, evaluated_data_file)
            if fact_checking_mode == "triplets":
                fact_check_triplets_w_triplets(items, model_name, evaluated_data_file)
        if triplets_checked:
            break

    triplets_checked = all_triplets_have_been_checked(items, fact_checking_mode=fact_checking_mode)
    if not triplets_checked and require_all_triplets_fact_checked:
        logging.info("Not all triplets have been fact-checked. Exiting the process...")
        return

    # -------------------------------
    # explain given fact checked item
    # -------------------------------

    items_verified = False
    for model_name in models_for_other_tasks:
        for attempt in range(no_of_attempts):
            items_verified = all_items_justified(items)
            if items_verified:
                break
            explain_item_fact_checking(items, model_name, attempt, evaluated_data_file)
        if items_verified:
            break

    items_verified = all_items_justified(items)
    if items_verified :
        logging.info("All items justified.")
    else:
        logging.info("Not all items have been justified.")


if __name__ == '__main__':

    logging.info("Launching main loop...")

    starting_time = datetime.now()

    main_loop(preferred_model_label=DEEPSEEK_R1_LABEL,
              models_for_summarizing=[DEEPSEEK_R1_MODEL_NAME],
              models_for_other_tasks=[DEEPSEEK_R1_MODEL_NAME],
              no_of_attempts=3)

    main_loop(preferred_model_label=O_GEMMA_LABEL,
              models_for_summarizing=[O_GEMMA_MODEL_NAME],
              models_for_other_tasks=[O_GEMMA_MODEL_NAME],
              no_of_attempts=3)

    ending_time = datetime.now()

    logging.info("Total time: %s.", ending_time - starting_time)
