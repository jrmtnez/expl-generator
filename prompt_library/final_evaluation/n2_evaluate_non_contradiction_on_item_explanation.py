PROMPT = """
The assistant is an expert fact checker who assists in the task of evaluating an explanation based on a metric.
---------------
Context:

The assistant will be provided with a text containing reasoning regarding the truthfulness of a claim. The claim itself will also be provided as contextual information.
The information is provided in JSON format.

---------------
Expectations:

- The answer must be given in JSON format.
- We don't want any additional information other than the result JSON.
- Please make sure you read and understand these instructions carefully.
- Please keep this document open while reviewing, and refer to it as needed.

Evaluation Criteria:

Non-contradiction: The provided text exhibits no internal contradictions among its lines of reasoning.

Evaluation Steps:

1. Carefully read the explanatory text and identify the different arguments it contains. The claim being evaluated can provide context.
2. Compare the identified arguments against each other to identify any contradictions or inconsistencies.
3. If the presented arguments are consistent and free of contradictions, the response will be "OK". Conversely, if inconsistencies or contradictions are detected within the arguments, the response will be "NOK".
4. If the answer is "NOK", also provide an analysis of the result explaining where the contradiction(s) lie. Make sure the answer JSON is valid by escaping the double quotes as required.
---------------
Examples:

Example 1:

json:
{
    "claim": "Manuka honey, as a topical treatment, is better than all known antibiotics.",
    "explanatory text": "Manuka honey is known for its antibacterial properties and is more effective than all existing antibiotics. It has completely replaced antibiotics in treating bacterial infections and is guaranteed to work against all bacteria, including those that are resistant to antibiotics. None of the bacteria killed by Manuka honey have ever developed resistance to it, making it the ultimate solution for bacterial infections. At the same time, it is acknowledged that Manuka honey is only somewhat effective and works for a limited range of wounds and bacteria. Moreover, while it is said to eliminate all MSSA and MRSA biofilms in chronic wounds, some studies suggest it may not work on all biofilm types. Therefore, while Manuka honey is the best option available, its benefits are likely overstated."
}

answer_json:
{
    "non_contradiction": "NOK",
    "analysis": "Claims it -replaced antibiotics- yet also says it's -only somewhat effective-; calls it a -guaranteed solution- while admitting studies show limitations; describes it as -the best option- but says benefits are -likely overstated-."
}


Example 2:

json:
{
    "claim": "Manuka honey, as a topical treatment, is better than all known antibiotics.",
    "explanatory text": "Manuka honey possesses antibacterial properties and has demonstrated effectiveness in treating certain types of wounds. However, it should not be considered superior to all known antibiotics. Its benefits are limited to specific bacteria and wound types. Although studies show it can combat some bacteria, it is not immune to the broader challenge of bacterial resistance. Claims that Manuka honey can kill all MSSA and MRSA biofilms in chronic wounds are overly broad and not supported by conclusive evidence. While Manuka honey is a promising natural product, its effectiveness should be viewed within the scope of current scientific understanding and not as a universal cure or antibiotic replacement."
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
