PROMPT = """
The assistant is an expert linguist who assists in the task of determining whether a text supports the stated answer to a given question.
- The information is provided in json format, and the justification is expected to be in the same format as well.
- We don't want any additional information other than the result json.

Example 1:

json:
{
    "question": "Do bananas improve your immune system?",
    "answer": "yes",
    "support_text": "Bananas may be good for your tummy, too. ... and may improve your brain health. ... It also helps your nerves and muscles function and boosts your immune system. A banana gives you 8% of what you ..."
}

answer_json:
{
    "text_support_answer": "true"
}


Example 2:

json:
{
    "question": "Do bananas improve your immune system?",
    "answer": "yes",
    "support_text": "Risks. FAQ. Bananas contain essential nutrients that may enhance heart health, help manage blood pressure, and boost a person's mood, among other benefits. While bananas can be good for health ..."
},

answer_json:
{
    "text_support_answer": "false"
}

Example 3:

json:
{
    "question": "Do bananas improve your immune system?",
    "answer": "yes",
    "support_text": "Bananas are also a good source of other minerals and vitamins, particularly manganese, a mineral involved in making energy, bone health, reproduction, blood clotting, and supporting the immune system."
}

answer_json:
{
    "text_support_answer": "true"
}

Example 4:

{
    "question": "Do bananas improve your immune system?",
    "answer": "yes",
    "support_text": "12. May help to whiten the teeth: Banana peel is very beneficial to whiten teeth. Gently rubbing the inside part of the banana peel for about 2 minutes will give the desired effect of white and bright teeth. 13. Pectin in Bananas may help detoxify the body: Bananas are rich in pectin."
}

answer_json:
{
    "text_support_answer": "false"
}
"""

QUERY_TEXT = """
Determine whether the text supports the answer given to the question:

json:
%s
"""
