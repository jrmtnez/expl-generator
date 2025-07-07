import logging
import json
import sys
import torch
import gc
from tqdm import tqdm
from os.path import join, exists
sys.path.append('.')
from llm_mgmt.pipeline_mgmt import get_gpu_pipeline, query_model
from pipeline.json_helpers import extract_json
from rag_mgmt.search_engine_mgmt import get_base_url
from llm_mgmt.llm_llama3_mgmt import LLAMA_3_MODEL_NAME, LLAMA_3_LABEL
from llm_mgmt.llm_gemma2_mgmt import GEMMA_2_MODEL_NAME, GEMMA_2_LABEL
from llm_mgmt.llm_phi3_mgmt import PHI_3_MODEL_NAME, PHI_3_LABEL
from llm_mgmt.llm_yi15_mgmt import YI_15_MODEL_NAME, YI15_LABEL
from llm_mgmt.llm_qwen25_mgmt import QWEN_25_MODEL_NAME, QWEN_25_LABEL
from llm_mgmt.llm_ollama_mgmt import O_GEMMA_MODEL_NAME, O_GEMMA_LABEL
from prompt_library.rag_mgmt.z1_identify_unreliable_site import PROMPT as IDENTIFY_UNRELIABLE_SITE_PROMPT
from prompt_library.rag_mgmt.z1_identify_unreliable_site import QUERY_TEXT as IDENTIFY_UNRELIABLE_SITE_QUERY_TEXT
from prompt_library.rag_mgmt.z2_identify_trivial_questions import PROMPT as IDENTIFY_TRIVIAL_QUESTION_PROMPT
from prompt_library.rag_mgmt.z2_identify_trivial_questions import QUERY_TEXT as IDENTIFY_TRIVIAL_QUESTION_QUERY_TEXT
from prompt_library.rag_mgmt.z3_unreliable_sites_naive_fact_checking import PROMPT as UNRELIABLE_SITES_NAIVE_FACT_CHECKING_PROMPT
from prompt_library.rag_mgmt.z3_unreliable_sites_naive_fact_checking import QUERY_TEXT as UNRELIABLE_SITES_NAIVE_FACT_CHECKING_QUERY_TEXT
from pipeline.config import EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH, UNRELIABLE_SEARCH_SITES_FILE_NAME, ROOT_LOGGER_ID
from pipeline.config import CREDIBILITY_DATA_PATH, CRED_SCORE_NAIVE_FC_SITES_FILE_NAME

LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)

# MODEL_LIST = [[LLAMA_3_MODEL_NAME, LLAMA_3_LABEL], [GEMMA_2_MODEL_NAME, GEMMA_2_LABEL], [QWEN_25_MODEL_NAME, QWEN_25_LABEL]]
MODEL_LIST = [[O_GEMMA_MODEL_NAME, O_GEMMA_LABEL]]

def export_unreliable_sites(model_name=LLAMA_3_MODEL_NAME, model_label=LLAMA_3_LABEL, evaluated_items_model_label=LLAMA_3_LABEL):

    data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % evaluated_items_model_label)
    unreliable_sites_file = join(RESULTS_PATH, UNRELIABLE_SEARCH_SITES_FILE_NAME)

    if not exists(unreliable_sites_file):
        with open(data_file, encoding="utf-8") as json_file:
            items = json.load(json_file)

        questions_data = []
        for item in items:
            sentences = item["fr_sentences"]
            for sentence in sentences:
                if sentence["sentence_class"] != "T":
                    triplets = sentence["triplets"]
                    for triplet in triplets:
                        search_results = triplet["search_results"]
                        for search_result in search_results:
                            if search_result["url_credibility"] == 0:
                                question_dict = {}
                                question_dict["question"] = triplet["closed_question"]
                                question_dict["answer"] = "yes"
                                question_dict["support_text"] = search_result["body"]
                                question_dict["url"] = search_result["url"]
                                questions_data.append(question_dict)

        with open(unreliable_sites_file, "w", encoding="utf-8") as write_file:
            json.dump(questions_data, write_file, indent=4, separators=(",", ": "))

    with open(unreliable_sites_file, encoding="utf-8") as json_file:
        questions_data = json.load(json_file)

    pipeline = None
    gc.collect()
    with torch.no_grad():
        torch.cuda.empty_cache()

    pipeline, _ = get_gpu_pipeline(model_name=model_name)

    last_question = ""
    for question_data in tqdm(questions_data):
        if question_data["question"] != last_question:
            last_question = question_data["question"]

            if model_label + "_classified_as" not in question_data:
                try:
                    query_dict = {}
                    query_dict["question"] = question_data["question"]

                    prompt = IDENTIFY_TRIVIAL_QUESTION_PROMPT
                    query_text = IDENTIFY_TRIVIAL_QUESTION_QUERY_TEXT % (query_dict)

                    _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)
                    logging.debug("Identify trivial question response: %s", response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Identify trivial question json: %s", response_json)

                    question_data[model_label + "_classified_as"] = response_json["classified_as"]

                    with open(unreliable_sites_file, "w", encoding="utf-8") as write_file:
                        json.dump(questions_data, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error identifiying trivial question (TypeError)...")
                    continue
                except KeyError:
                    logging.info("Error identifiying trivial question (KeyError)...")
                    continue
            classified_as = question_data[model_label + "_classified_as"]

            if model_label + "_correct_answer" not in question_data:

                try:
                    query_dict = {}
                    query_dict["question"] = question_data["question"]
                    query_dict["answer"] = "yes"

                    prompt = UNRELIABLE_SITES_NAIVE_FACT_CHECKING_PROMPT
                    query_text = UNRELIABLE_SITES_NAIVE_FACT_CHECKING_QUERY_TEXT % (query_dict)

                    _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)
                    logging.debug("Naive fact-ckecking response: %s", response_text)

                    response_json = extract_json(response_text)[-1]
                    logging.debug("Naive fact-ckecking json: %s", response_json)

                    question_data[model_label + "_correct_answer"] = response_json["correct_answer"]

                    with open(unreliable_sites_file, "w", encoding="utf-8") as write_file:
                        json.dump(questions_data, write_file, indent=4, separators=(",", ": "))

                except TypeError:
                    logging.info("Error fact-checking (TypeError)...")
                    continue
                except KeyError:
                    logging.info("Error fact-checking sites (KeyError)...")
                    continue
            correct_answer = question_data[model_label + "_correct_answer"]

        else:
            if model_label + "_classified_as" not in question_data:
                question_data[model_label + "_classified_as"] = classified_as
            if model_label + "_correct_answer" not in question_data:
                question_data[model_label + "_correct_answer"] = correct_answer

        if model_label + "_supports" not in question_data:

            try:
                query_dict = {}
                query_dict["question"] = question_data["question"]
                query_dict["answer"] = "yes"
                query_dict["support_text"] = question_data["support_text"]

                prompt = IDENTIFY_UNRELIABLE_SITE_PROMPT
                query_text = IDENTIFY_UNRELIABLE_SITE_QUERY_TEXT % (query_dict)

                _, response_text = query_model(prompt, query_text, pipeline, model_name=model_name)
                logging.debug("Identify unreliable site response: %s", response_text)

                response_json = extract_json(response_text)[-1]
                logging.debug("Identify unreliable site json: %s", response_json)

                question_data[model_label + "_supports"] = response_json["text_support_answer"]

                with open(unreliable_sites_file, "w", encoding="utf-8") as write_file:
                    json.dump(questions_data, write_file, indent=4, separators=(",", ": "))

            except TypeError:
                logging.info("Error identifiying unreliable sites (TypeError)...")
                continue
            except KeyError:
                logging.info("Error identifiying unreliable sites (KeyError)...")
                continue

def check_urls():

    unreliable_sites_file = join(RESULTS_PATH, UNRELIABLE_SEARCH_SITES_FILE_NAME)

    with open(unreliable_sites_file, encoding="utf-8") as json_file:
        questions_data = json.load(json_file)

    sites_dict = {}

    for question_data in questions_data:

        classified_as_total_count = 0
        classified_as_interesting_count = 0
        correct_answer_total_count = 0
        correct_answer_count = 0
        supports_total_count = 0
        supports_count = 0

        for [_, model_label] in MODEL_LIST:

            if model_label + "_classified_as" in question_data:
                classified_as_total_count += 1
                if question_data[model_label + "_classified_as"] == "interesting":
                    classified_as_interesting_count += 1

            if model_label + "_correct_answer" in question_data:
                correct_answer_total_count += 1
                if question_data[model_label + "_correct_answer"] == "true":
                    correct_answer_count += 1

            if model_label + "_supports" in question_data:
                supports_total_count += 1
                if question_data[model_label + "_supports"] == "true":
                    supports_count += 1


        select_url = classified_as_interesting_count / classified_as_total_count > 0.50 and correct_answer_count / correct_answer_total_count < 0.50 and supports_count / supports_total_count > 0.5

        logging.info("Question: %s", question_data["question"])
        logging.info("-> selected: %s interesting: %s/%s, correct answer: %s/%s, supports: %s/%s", select_url, classified_as_interesting_count, classified_as_total_count, correct_answer_count, correct_answer_total_count, supports_count, supports_total_count)
        base_url = get_base_url(question_data["url"])
        if select_url:
            logging.info("Site selected: %s", base_url)
            if not sites_dict.get(base_url):
                sites_dict[base_url] = -1

    with open(join(CREDIBILITY_DATA_PATH, CRED_SCORE_NAIVE_FC_SITES_FILE_NAME), "w", encoding="utf-8") as write_file:
        json.dump(sites_dict, write_file, indent=4, separators=(",", ": "))


if __name__ == '__main__':

    for [model_name, model_label] in MODEL_LIST:
        # export_unreliable_sites(model_name=model_name, model_label=model_label, evaluated_items_model_label=LLAMA_3_LABEL)
        export_unreliable_sites(model_name=model_name, model_label=model_label, evaluated_items_model_label=O_GEMMA_LABEL)

    check_urls()
