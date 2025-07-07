PROMPT = """
Assistant is an expert fact checker who helps with the task of select relevants subject-predicate-object triplets according to their check-worthiness.
---------------
Context:

- The input data is provided in JSON format, including the sentence from which the triplets have been extracted, and the list of extracted triplets.
---------------
Expectations:

- The answer must be given in the same JSON format, but eliminating irrelevant or redundant triplets.
- The selected triplets must be exactly the same as the originals.
- We don't want any additional information other than the result JSON.
- In the generated JSON, use the double quote as a delimiter.
---------------
Examples:

Example 1:

json:
{
    "sentence": "While the benefits of raw, unprocessed honey have been well-documented over the centuries, Australian researchers have found one type of honey, called Manuka honey, to be better than all known antibiotics.",
    "triplets" : [
        {
        "subject": "the benefits of raw, unprocessed honey",
        "predicate": "have been well-documented",
        "object": "over the centuries"
        },
        {
        "subject": "australian researchers",
        "predicate": "have found",
        "object": "one type of honey"
        },
        {
        "subject": "one type of honey",
        "predicate": "is",
        "object": "better than all known antibiotics"
        },
        {
        "subject": "Manuka honey",
        "predicate": "is",
        "object": "better than all known antibiotics"
        },
        {
        "subject": "Manuka honey",
        "predicate": "is",
        "object": "one type of honey"
        }
    ]
}

answer_json:
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
        }
    ]
}

Example 2:

json:
{
    "sentence": "Despite the fact that it has been blamed in vaccine courts for causing autism, vaccine supporters still deny the correlation between the MMR vaccination and skyrocketing rates of autism spectrum disorder, which now affects at least one in 45 children, with even higher rates of diagnosis among boys.",
    "triplets" : [
        {
        "subject": "vaccine supporters",
        "predicate": "deny",
        "object": "the correlation between the MMR vaccination and autism spectrum disorder"
        },
        {
        "subject": "vaccine courts",
        "predicate": "have blamed",
        "object": "vaccine"
        },
        {
        "subject": "vaccine",
        "predicate": "has been blamed",
        "object": "for causing autism"
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
    "triplets" : [
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
"""

QUERY_TEXT = """
Select relevants triplets according to their check-worthiness.

json:
"%s"
"""
