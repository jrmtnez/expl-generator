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

Non-redundancy: The arguments presented in the provided text are non-redundant and non-repetitive.

Evaluation Steps:

1. Carefully read the explanatory text and identify the different arguments it contains. The claim being evaluated can provide context.
2. Compare the identified arguments against each other to identify any instances of unnecessary repetition or redundancy.
3. If the presented arguments are non-redundant, the response will be "OK". Conversely, if redundancies or unnecessary repetitions are detected within the arguments, the response will be "NOK".
4. If the answer is "NOK", also provide an analysis of the result explaining where the redundancy(s) lie. Make sure the answer JSON is valid by escaping the double quotes as required.
---------------
Examples:

Example 1:

json:
{
    "claim": "Manuka honey, as a topical treatment, is better than all known antibiotics.",
    "explanatory text": "While it is true that Manuka honey has antibacterial properties and has been shown to be effective in treating certain types of wounds, the statement that it is "better than all known antibiotics" is an exaggeration. Manuka honey is not a replacement for traditional antibiotics, and its effectiveness is limited to specific types of bacteria and wounds. In fact, while it does have antibacterial properties, that does not make it a superior alternative to antibiotics. Furthermore, the idea that none of the bugs killed by Manuka honey have been able to build up immunity is also an exaggeration. Even though Manuka honey has been shown to kill bacteria, it is improbable that resistance can never develop. The statement that it can be used to kill all MSSA and MRSA biofilms in chronic wounds is another exaggeration. Though it has shown effectiveness in wound treatment, that does not mean it can treat all biofilms. Ultimately, Manuka honey has some benefits as a natural antibacterial, but many of the claims made about it are overstated and go beyond the scope of scientific evidence."
}

answer_json:
{
    "non_redundancy": "NOK",
    "analysis": "Repeating -antibacterial properties- and -effectiveness in wounds- multiple times; reiterating that it's not a replacement for antibiotics in slightly varied language; restating overstatement/exaggeration claims without adding specificity."
}


Example 2:

json:
{
    "claim": "Manuka honey, as a topical treatment, is better than all known antibiotics.",
    "explanatory text": "Manuka honey has antibacterial properties and has been shown to be effective in treating certain types of wounds. However, claims that it is superior to all known antibiotics are exaggerated. Its effects are limited to specific bacteria and wound types, and it is not a substitute for traditional antibiotics. Additionally, while it has shown the ability to kill certain bacteria, it is unlikely to completely prevent the development of resistance. Assertions that it eliminates all MSSA and MRSA biofilms in chronic wounds are similarly overstated. Overall, although Manuka honey is a useful natural treatment, some claims about its effectiveness exceed what current evidence supports."
}

answer_json:
{
    "non_redundancy": "OK"
}
"""

QUERY_TEXT = """
Evaluate the following explanation according to the "Non-redundancy" metric based on the information provided:

json:
%s
"""
