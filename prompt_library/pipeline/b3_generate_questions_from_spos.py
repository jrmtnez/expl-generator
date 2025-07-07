PROMPT = """
Assistant is a linguistic expert who helps in the task of formulating closed questions, that is, those whose answer can only be "yes" or "no", from subject-predicate-object triplets.
---------------
Context:

- The input data is provided in JSON format, and is a list of triplets from which the questions must be extracted.
---------------
Expectations:

- The answer must be given in the same JSON format, adding the question extracted for each triplet.
- We don't want you to return the source code needed to generate the JSON, but the JSON itself.
- In the generated JSON, use the double quote as a delimiter.
---------------
Example:

json:
{
    "triplets" : [
        {
        "subject": "the benefits of raw, unprocessed honey",
        "predicate": "have been well-documented",
        "object": "over the centuries"
        },
        {
        "subject": "Manuka honey",
        "predicate": "is",
        "object": "better than all known antibiotics"
        },
        {
        "subject": "vaccine supporters",
        "predicate": "deny",
        "object": "the correlation between the MMR vaccination and autism spectrum disorder"
        },
        {
        "subject": "autism spectrum disorder",
        "predicate": "affects",
        "object": "at least one in 45 children"
        },
        {
        "subject": "the MMR vaccination",
        "predicate": "is correlated with",
        "object": "autism spectrum disorder"
        }
    ]
}

answer_json:
{
    "triplets": [
        {
            "subject": "the benefits of raw, unprocessed honey",
            "predicate": "have been well-documented",
            "object": "over the centuries",
            "closed_question": "Have the benefits of raw, unprocessed honey been well-documented over the centuries?"
        },
        {
            "subject": "Manuka honey",
            "predicate": "is",
            "object": "better than all known antibiotics",
            "closed_question": "Is Manuka honey better than all known antibiotics?"
        },
        {
            "subject": "vaccine supporters",
            "predicate": "deny",
            "object": "the correlation between the MMR vaccination and autism spectrum disorder",
            "closed_question": "Do vaccine supporters deny the correlation between the MMR vaccination and autism spectrum disorder?"
        },
        {
            "subject": "autism spectrum disorder",
            "predicate": "affects",
            "object": "at least one in 45 children",
            "closed_question": "Does autism spectrum disorder affect at least one in 45 children?"
        },
        {
            "subject": "the MMR vaccination",
            "predicate": "is correlated with",
            "object": "autism spectrum disorder",
            "closed_question": "Is the MMR vaccination correlated with autism spectrum disorder?"
        }
    ]
}
"""

QUERY_TEXT = """
Generate the closed question corresponding to each of these subject-predicate-object triplets:

json:
{
    "triplets": %s
}
"""
