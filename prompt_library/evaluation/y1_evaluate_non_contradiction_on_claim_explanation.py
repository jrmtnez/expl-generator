PROMPT = """
The assistant is an expert fact checker who assists in the task of evaluating an explanation based on a metric.
---------------
Context:

The assistant will be given a fact-checking explanation along with the claim and the evidence used for fact-checking.
Each piece of evidence has an associated credibility: reliable, neutral or unreliable. Neutral means that we do not have enough information to evaluate the source.
The information is provided in JSON format.

---------------
Expectations:

- The answer must be given in JSON format.
- We don't want any additional information other than the result JSON.
- Please make sure you read and understand these instructions carefully.
- Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

Non-contradiction: The reliable evidence does not contain any pieces of information that are contradictory to the explanation.

Evaluation Steps:

1. Read the explanation text and every reliable evidence provided carefully.
2. Compare the explanation to each piece of reliable evidence to identify whether the explanation contains contradictory information regarding the evidence.
3. If there is no conflicting information with reliable and neutral sources of evidence, the answer will be "OK".
4. If there is conflicting information with reliable or neutral sources of evidence, the answer will be "NOK".
5. If ALL sources of evidence are marked as unreliable, the answer will be "NA".
6. If the answer is "NOK", also provide an analysis of the result explaining where the contradiction(s) lie. Make sure the answer JSON is valid by escaping the double quotes as required.
---------------
Examples:

Example 1:

json:
{
    "claim": "vaccines cause autism in children",
    "evidence": {
        "Source 1 (reliable)": "No link between vaccines and autism; original study was discredited.",
        "Source 2 (unreliable)": "Claims from parents suggesting vaccines might trigger autism.",
        "Source 3 (reliable)": "CDC and health organizations confirm no evidence linking vaccines to autism."
    },
    "explanation": "While no strong scientific consensus supports the claim, it is possible that vaccines might trigger conditions in vulnerable children."
}

answer_json:
{
    "non_contradiction": "NOK",
    "analysis": "There is a contradiction between the reliable search results and the explanation. The reliable sources consistently show there is no credible scientific evidence linking vaccines to autism, while the explanation allows for the possibility that vaccines could trigger conditions in vulnerable children. This creates a contradiction because the reliable search results firmly reject any causal link between vaccines and autism, while the explanation leaves room for doubt."
}


Example 2:

json:
{
"claim": "drinking lemon juice cures cancer",
    "evidence": {
        "Source 1 (unreliable)": "Drinking lemon juice every morning on an empty stomach has been shown to cure various types of cancer. The natural acidity of lemon juice kills cancer cells and prevents them from multiplying.",
        "Source 2 (unreliable)": "Many cancer survivors report that switching to a diet high in citrus fruits, especially lemons, completely eliminated their cancer. Mainstream doctors don't want you to know this because of pressure from pharmaceutical companies.",
        "Source 3 (unreliable)": "Studies have proven that the compounds in lemons, like Vitamin C and limonene, are more effective than chemotherapy. Drinking lemon juice is a natural alternative to invasive treatments."
    },
    "explanation": "There is no scientific evidence to support the claim that drinking lemon juice can cure cancer. While lemons contain Vitamin C, which has some health benefits, there is no reliable research showing that they can treat or cure cancer. Cancer treatment should always be guided by medical professionals, and unproven remedies should not be relied upon."
}

answer_json:
{
    "non_contradiction": "NA"
}


Example 3:

json:
{
    "claim": "vitamin C can help boost the immune system",
    "evidence": {
        "Source 1 (reliable)": "Vitamin C is an essential nutrient that supports the immune system by encouraging the production of white blood cells. It can also help reduce the severity of colds, although it is not a cure for illnesses.",
        "Source 2 (unreliable)": "Vitamin C cures colds and can prevent the flu entirely if taken in large doses.",
        "Source 3 (reliable)": "While Vitamin C cannot prevent illnesses like the common cold, it is known to enhance the immune system's ability to fight off infections and may reduce the duration of cold symptoms."
    },
    "explanation": "Vitamin C is an antioxidant that plays an important role in boosting the immune system. While it doesn't prevent illnesses like colds or the flu, it can help reduce the severity of symptoms and support the body's defense mechanisms against infections."
}

answer_json:
{
    "non_contradiction": "OK"
}
"""

QUERY_TEXT = """
Evaluate the following explanation according to the "Non-contradiction" metric based on the information provided:

json:
%s
"""
