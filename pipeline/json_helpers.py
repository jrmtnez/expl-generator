# from https://github.com/vaseghisam/JEXON

import re
import json


def extract_json(text_response):
    json_objects = []

    start_pos = None
    braces_count = 0

    for i, char in enumerate(text_response):
        if char == '{':
            if start_pos is None:
                start_pos = i
            braces_count += 1
        elif char == '}':
            braces_count -= 1
            if braces_count == 0 and start_pos is not None:
                potential_json = text_response[start_pos:i+1]
                try:
                    json_object = json.loads(potential_json)
                    json_objects.append(json_object)
                except json.JSONDecodeError:
                    pass
                start_pos = None
    return json_objects if json_objects else None


def extract_json_old(text_response):
    pattern = r"\{.*?\}"
    matches = re.finditer(pattern, text_response, re.DOTALL)
    json_objects = []

    for match in matches:
        print(match)
        json_str = extend_search_new(text_response, match.span())
        try:
            json_obj = json.loads(json_str)
            json_objects.append(json_obj)
        except json.JSONDecodeError as e:
            print(e)
            print(json_str)
            continue

    return json_objects if json_objects else None


def extend_search_new(text, span):
    start, end = span
    nest_count = 1
    for i in range(end, len(text)):
        if text[i] == "{":
            nest_count += 1
        elif text[i] == "}":
            nest_count -= 1
            if nest_count == 0:
                return text[start:i + 1]
    return text[start:end]
