import logging
import json
import sys
from datetime import datetime
from os import makedirs
from os.path import join, exists
from openai import OpenAI
sys.path.append('.')
from prompt_library.baseline_explanations.a1_generate_baseline_explanation import PROMPT as BASELINE_EXPLANATION_PROMPT
from prompt_library.baseline_explanations.a1_generate_baseline_explanation import QUERY_TEXT as BASELINE_EXPLANATION_QUERY_TEXT
from pipeline.config import ROOT_LOGGER_ID, DATA_PATH, NEWS_ITEMS_FILE_NAME, EVALUATED_NEWS_ITEMS_FILE_NAME, RESULTS_PATH
from pipeline.keys import OPENAI_API_KEY


LOGGING_LEVEL = logging.INFO
logging.basicConfig(format='%(levelname)s : %(message)s', level=LOGGING_LEVEL)
logger = logging.getLogger(ROOT_LOGGER_ID)
logger.setLevel(LOGGING_LEVEL)

GPT_MODEL_LABEL = "gpt-4.1-2025-04-14"


FULL_QUERY_TEXT = """
%s
%s
"""


def generate_baseline_explanations(items, model_name, evaluated_data_file):

    client = OpenAI(api_key=OPENAI_API_KEY)

    item_no = 0
    for item in items:
        item_no += 1
        logging.info("Item %s of %s", item_no, len(items))

        if "justification" not in item:
            logging.info("Generating baseline explanation from item %s with model '%s'...", item["item_id"], model_name)

            item_text = item["text"]
            item_class = item["item_class"]

            prompt = BASELINE_EXPLANATION_PROMPT
            query_text = BASELINE_EXPLANATION_QUERY_TEXT % (item_class, item_text)

            content_text = FULL_QUERY_TEXT % (prompt, query_text)

            completion = client.chat.completions.create(
                model=model_name,
                store=False,
                messages=[
                    {"role": "user", "content": content_text}
                ]
            )

            response_text = completion.choices[0].message.content

            item["justification"] = response_text

            with open(evaluated_data_file, "w", encoding="utf-8") as write_file:
                json.dump(items, write_file, indent=4, separators=(",", ": "))


def main_loop(preferred_model_label=GPT_MODEL_LABEL):

    initial_data_file = join(DATA_PATH, NEWS_ITEMS_FILE_NAME)
    evaluated_data_file = join(RESULTS_PATH, EVALUATED_NEWS_ITEMS_FILE_NAME % preferred_model_label)

    makedirs(RESULTS_PATH, exist_ok=True)

    data_file = initial_data_file
    if exists(evaluated_data_file):
        data_file = evaluated_data_file

    logging.info("Loading data from %s ...", data_file)

    with open(data_file, encoding="utf-8") as json_file:
        items = json.load(json_file)

    generate_baseline_explanations(items, preferred_model_label, evaluated_data_file)


if __name__ == '__main__':

    logging.info("Launching main loop...")

    starting_time = datetime.now()

    main_loop()

    ending_time = datetime.now()

    logging.info("Total time: %s.", ending_time - starting_time)
