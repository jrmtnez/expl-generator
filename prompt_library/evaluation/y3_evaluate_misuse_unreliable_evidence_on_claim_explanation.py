PROMPT = """
The assistant is an expert fact checker who assists in the task of evaluating an explanation based on a metric.
---------------
Context:

- The assistant will be given a fact-checking explanation along with the verified claim and the evidence used for fact-checking.
- Each piece of evidence has an associated credibility: reliable, neutral or unreliable. Neutral means that we do not have enough information to evaluate the source.
- The information is provided in JSON format.
---------------
Expectations:

- The answer must be given in JSON format.
- We don't want any additional information other than the result JSON.
- Please make sure you read and understand these instructions carefully.
- Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

Misuse of unreliable evidence: The explanation relies on data from unreliable sources, presenting them as reliable.

Evaluation Steps:

1. Read the fact-checking explanation, the claim, and every piece of evidence provided carefully.
2. Compare the explanation with the claim and with each piece of unreliable evidence analyze whether the explanation relies on data from these unreliable sources, presenting them as reliable.
3. If data from unreliable sources is used as reliable in the explanation, the answer will be "NOK".
4. If the explanation only uses reliable sources, or if it uses unreliable sources but clearly identifies them as unreliable, the answer will be "OK."
5. If the answer is "NOK", identify which unreliable evidence data is being used in the explanation. Make sure the answer JSON is valid by escaping the double quotes as required.
---------------
Examples:

Example 1:

json:
{
    "claim": "drinking coffee can cure cancer.",
    "evidence": {
        "Source 1 (unreliable)": "Coffee has been shown to eliminate cancer cells completely in laboratory studies, and many alternative health practitioners endorse it as a cure.",
        "Source 2 (reliable)": "There is currently no scientific evidence to support the claim that coffee cures cancer. Some studies suggest potential cancer prevention benefits, but more research is needed."
        "Source 3 (reliable)": "Researchers have found a potential link between regular coffee consumption and a reduced risk of certain types of cancer, but this is not the same as a cure."
    },
    "explanation": "The claim that coffee cures cancer is backed by several sources that highlight its ability to eliminate cancer cells, as seen in the research by alternative health experts. While mainstream medical institutions have been slow to adopt this view, the evidence is clear."
}

answer_json:
{
    "misuse_unreliable_evidence": "NOK",
    "analysis": "The explanation relies on data from an unreliable source (Source 1) and presents it as reliable. The claim that coffee cures cancer is not supported by the reliable sources (Source 2 and Source 3), both of which state there is no evidence that coffee cures cancer. Instead, the explanation elevates the unreliable source's claim to suggest a cure, misrepresenting the scientific consensus."
}


Example 2:

json:
{
"claim": "organic food is healthier than non-organic food.",
    "evidence": {
        "Source 1 (reliable)": "Research indicates that organic foods may have higher antioxidant levels, but the health benefits can be variable.",
        "Source 2 (unreliable)": "Organic foods are guaranteed to be healthier and free from all chemicals and pesticides."
        "Source 3 (reliable)": "While organic foods can reduce exposure to pesticide residues, the overall health benefits compared to non-organic foods are still a topic of debate.",
    },
    "explanation": "According to research from the National Institutes of Health and Harvard T.H. Chan School of Public Health, organic foods may offer certain advantages, such as reduced pesticide exposure and higher antioxidant levels. However, the health benefits compared to non-organic foods can vary, and further research is needed to draw definitive conclusions."
}

answer_json:
{
    "misuse_unreliable_evidence": "OK"
}
"""

QUERY_TEXT = """
Evaluate the following explanation according to the "Misuse of unreliable evidence" metric based on the information provided:

json:
%s
"""
