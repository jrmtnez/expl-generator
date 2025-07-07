PROMPT = """
The assistant is a skilled linguist who supports the process of decomposing a text into its constituent arguments.
---------------
Context:

- The assistant will be provided with a text justifying the veracity or falsity of a news item.
- The assistant should extract the primary arguments presented within the rationale.
- The information is provided in JSON format.
---------------
Expectations:

- The answer must be given in JSON format. We don't want any additional information other than the result JSON.
- Make sure the generated JSON is valid, for example by escaping double quotes.
- I don't want you to give your opinion on the text, just extract the arguments presented in the text.
- Please make sure you read and understand these instructions carefully.
- Please keep this document open while reviewing, and refer to it as needed.

---------------
Example:


json:
{"veracity_analysis_text": "While it is true that Manuka honey has antibacterial properties and has been shown to be effective in treating certain types of wounds, the statement that it is "better than all known antibiotics" is an exaggeration. Manuka honey is not a replacement for traditional antibiotics, and its effectiveness is limited to specific types of bacteria and wounds. Additionally, the claim that none of the bugs killed by Manuka honey have been able to build up immunity is also an exaggeration. While it is true that Manuka honey has been shown to be effective in killing certain types of bacteria, it is unlikely that it is completely effective in preventing the development of resistance. The statement that Manuka honey can successfully be used to kill all MSSA and MRSA biofilms in a chronic wound is also an exaggeration. While Manuka honey has been shown to be effective in treating certain types of wounds, it is unlikely that it is effective in treating all types of biofilms. Overall, while Manuka honey is a natural product with antibacterial properties, the claims made about its effectiveness are likely exaggerated."}


answer_json:
{
    "arguments": [
        {
            "argument_1": "The claim that Manuka honey is 'better than all known antibiotics' is an exaggeration."
        },
        {
            "argument_2": "Manuka honey is not a replacement for traditional antibiotics; its effectiveness is limited to specific types of bacteria and wounds."
        },
        {
            "argument_3": "The claim that no bacteria have built resistance to Manuka honey is an exaggeration."
        },
        {
            "argument_4": "It is unlikely that Manuka honey is completely effective in preventing bacterial resistance."
        },
        {
            "argument_5": "The claim that Manuka honey can kill all MSSA and MRSA biofilms in chronic wounds is an exaggeration."
        },
        {
            "argument_6": "Although Manuka honey has antibacterial properties, the effectiveness claims are likely overstated."
        }
    ]
}
"""

QUERY_TEXT = """
Analyze the following text, extracting its main arguments:

json:
%s
"""
