PROMPT = """
Assistant is an expert fact checker who helps with the task of select relevants subject-predicate-object triplets according to their check-worthiness.
---------------
Context:

- The input data is provided in JSON format.
- The input data contains the list of triplets to be evaluated, the question that these triplets are intended to answer, and a summary of the topic to which the question is related.
- The question is a closed question, that is, its answer can only be yes or no.
- Each triplet is associated with the reliability of the website from which it was extracted. Positive values indicate more reliable websites than negative values. Values close to zero are considered neutral.
---------------
Expectations:

- First, carefully examine all subject-predicate-object triplets from the list of candidate triplets provided.
- Next, discard repetitive triplets, those that are not related to the topic being discussed, or are trivial.
- Try to have at least three triplets selected.
- Build a new list with the selected triplets (those not discarded).
- The selected triplets must be exactly the same as the originals. Please do not rewrite them in any other way.
- The response must be given in JSON format. I don't want any additional information other than JSON.
- In the generated JSON, use the double quote as a delimiter.
---------------
Example:

json:
{
    "closed_question": "Does Manuka honey kill more bacteria?",
    "context": "Australian researchers have found that Manuka honey, produced by bees that forage on New Zealand's Manuka bush and Australian tea trees, is more effective than all known antibiotics in killing bacteria, including antibiotic-resistant superbugs. Manuka honey contains compounds like methylglyoxal that cause multi-system failure in bacteria, preventing them from adapting and surviving. It has a wide range of biological properties, including antibacterial, anti-inflammatory, and wound-healing abilities, making it a potential solution to the global issue of antibiotic resistance and a promising treatment for chronic wounds, such as those caused by MRSA.",
    "candidate_triplet_list": [
        {
            "id": 1,
            "subject": "Manuka honey",
            "predicate": "has",
            "object": "antibacterial, anti-inflammatory and antioxidant properties",
            "url_credibility": 1
        },
        {
            "id": 2,
            "subject": "honey",
            "predicate": "has",
            "object": "natural antibacterial properties",
            "url_credibility": -1.4227272727272728
        },
        {
            "id": 3,
            "subject": "Manuka honey benefits",
            "predicate": "extend to",
            "object": "sore throats",
            "url_credibility": -0.16818181818181815
        },
        {
            "id": 4,
            "subject": "Manuka honey",
            "predicate": "can kill",
            "object": "more bacteria than antibiotics",
            "url_credibility": -0.9545454545454519
        },
        {
            "id": 5,
            "subject": "Manuka honey",
            "predicate": "promotes",
            "object": "good bacteria",
            "url_credibility": -0.004545454545454519
        },
        {
            "id": 6,
            "subject": "Manuka honey",
            "predicate": "can be used for",
            "object": "digestive problems",
            "url_credibility": -0.004545454545454519
        },
        {
            "id": 7,
            "subject": "Lin et al. (2011)",
            "predicate": "showed",
            "object": "that Manuka honey is significantly more effective against most gastrointestinal bacteria than artificial honey",
            "url_credibility": 1
        },
        {
            "id": 8,
            "subject": "Manuka honey",
            "predicate": "is highly effective in",
            "object": "preventing biofilm formation",
            "url_credibility": -1.477272727272727
        },
        {
            "id": 9,
            "subject": "Manuka honey",
            "predicate": "may improve",
            "object": "treatment of gastro\u2010esophageal reflux disease",
            "url_credibility": 1
        },
        {
            "id": 10,
            "subject": "Manuka honey",
            "predicate": "can help",
            "object": "promote tissue regeneration",
            "url_credibility": 0.14090909090909093
        },
        {
            "id": 11,
            "subject": "Manuka honey",
            "predicate": "has",
            "object": "prebiotic components",
            "url_credibility": 0.14090909090909093
        },
        {
            "id": 12,
            "subject": "manuka honey",
            "predicate": "offers",
            "object": "an exciting natural alternative to traditional medications",
            "url_credibility": -1.6227272727272726
        },
        {
            "id": 13,
            "subject": "manuka honey",
            "predicate": "performs well against",
            "object": "COVID-19",
            "url_credibility": -1.6227272727272726
        },
        {
            "id": 14,
            "subject": "honey",
            "predicate": "have",
            "object": "antibacterial properties",
            "url_credibility": -0.9136363636363636
        },
        {
            "id": 15,
            "subject": "honey",
            "predicate": "does not kill",
            "object": "the good bacteria in kefir",
            "url_credibility": -0.9136363636363636
        }
    ]
}

answer_json:
{
    "selected_triplet_list": [
        {
            "id": 4,
            "subject": "Manuka honey",
            "predicate": "can kill",
            "object": "more bacteria than antibiotics",
            "url_credibility": -0.9545454545454519
        },
        {
            "id": 7,
            "subject": "Lin et al. (2011)",
            "predicate": "showed",
            "object": "that Manuka honey is significantly more effective against most gastrointestinal bacteria than artificial honey",
            "url_credibility": 1
        },
        {
            "subject": "manuka honey",
            "predicate": "offers",
            "object": "an exciting natural alternative to traditional medications",
            "url_credibility": -1.6227272727272726
        }
    ]
}
"""

QUERY_TEXT = """
Select the most relevant subject-predicate-object triplets for this closed question given the context provided.

json:
"%s"
"""
