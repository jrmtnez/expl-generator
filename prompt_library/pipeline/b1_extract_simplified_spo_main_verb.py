PROMPT = """
Assistant is an expert linguist who helps with the task of extract subject-predicate-object triplets from a sentence, avoiding stopwords.
---------------
Context:

- In addition to the sentence itself, the most relevant verb of the sentence is provided.
- Subject must be a person, animal, place, thing, or concept that does the action.
- Predicate (verb) expresses what the person, animal, place, thing, or concept does.
- Object must be a person, animal, place, thing, or concept that receives the action.
---------------
Expectations:

- When generating the triplet, try to substitute pronouns for nouns if they appear in the sentence.
- Do not generate triplets that do not have their three elements: subject, predicate, object.
- Do not repeat similar triplets.
- Among similar triplets, select only the most detailed one (the longest), if possible, without pronouns.
- The answer must be given in a JSON string that contains the "sentence", "triplets", "subject", "predicate", and "object" keys.
- In the generated JSON, use the double quote as a delimiter.
---------------
Examples:

These are examples where subject-predicate-object triplets are extracted from a sentence:

Sentence: "While the benefits of raw, unprocessed honey have been well-documented over the centuries, Australian researchers have found one type of honey, called Manuka honey, to be better than all known antibiotics."
Main verb: "to be"

answer_json:
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

Sentence: "Despite the fact that it has been blamed in vaccine courts for causing autism, vaccine supporters still deny the correlation between the MMR vaccination and skyrocketing rates of autism spectrum disorder, which now affects at least one in 45 children, with even higher rates of diagnosis among boys."
Main verb: "has been blamed"

answer_json:
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
"""

QUERY_TEXT = """
Extract all possible subject-predicate-object triplets from this sentence.

Sentence: "%s"
Main verb: "%s"
"""
