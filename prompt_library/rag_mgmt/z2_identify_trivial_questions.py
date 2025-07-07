PROMPT = """
The assistant is an expert fact checker who helps determine whether a question is trivial, uninteresting, or too vague to be considered.
- The information is provided in json format, and the justification is expected to be in the same format as well.
- We don't want any additional information other than the result json.

Example 1:

json:
{
    "question": "Do bananas improve your immune system?"
}

answer_json:
{
    "classified_as": "interesting"
}

Example 2:

json:
{
    "question": "Is an effective approach to treating depression?"
}

answer_json:
{
    "classified_as": "vague"
}


Example 3:

json:
{
    "question": "Is magnesium a mineral?"
}

answer_json:
{
    "classified_as": "trivial"
}


Example 4:

json:
{
    "question": "Can depression medications cure these imbalances?"
}

answer_json:
{
    "classified_as": "vague"
}


Example 5:

json:
{
    "question": "Did Sour Honey kill 13% of the cancer?"
}

answer_json:
{
    "classified_as": "interesting"
}


Example 6:

json:
{
    "question": Are people suffering from some form of depression?"
}

answer_json:
{
    "classified_as": "uninteresting"
}
"
"""

QUERY_TEXT = """
Determine whether the question is interesting enough to be verified:

json:
%s
"""
