PROMPT = """
- I will give you a list of reference arguments and a list of proposed arguments.
- Arguments are simply pieces of text that state some things.
- Both lists of arguments come from a news story or a social media post.
- You must compare the list of reference arguments and the list of proposed arguments and detect for each reference argument, which proposed argument is equivalent, if any.
- When a reference argument has an equivalent in a proposed argument we say that it is covered.
- The arguments you compare need not be literally identical to be considered equivalent. It is sufficient that they state the same reasoning.
- Provide a list of reference argument identifiers and their equivalent in the proposed argument list, if any. Make sure the answer JSON is valid by escaping the double quotes as required.
- If all reference arguments have an equivalent in the proposed argument list, the coverage will be "OK".
- If any of these reference arguments has no equivalent among the proposed arguments, the coverage will be "NOK".
- The information is provided in JSON format, and the response must also be in Json format.
- Here are some examples to help you understand the task and the format of the data.

---------------
Examples:

...............
Example 1:

json:
{
    "reference_arguments": [
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
    ],
    "proposed_arguments": [
        {
            "argument_1": "Manuka honey should be seen as a complementary treatment rather than a substitute for conventional antibiotics, as its benefits are limited in scope."
        },
        {
            "argument_2": "The idea that Manuka honey can eradicate every biofilm of MSSA and MRSA in chronic wounds seems overly optimistic."
        },
        {
            "argument_3": "Saying that Manuka honey surpasses all antibiotics is likely a dramatic overstatement."
        },
        {
            "argument_4": "While Manuka honey does exhibit antibacterial effects, the widespread claims about its potency appear exaggerated."
        },
        {
            "argument_5": "Most studies on Manuka honey’s antibacterial effects have been conducted in laboratory settings, which may not reflect real-world medical outcomes."
        },
        {
            "argument_6": "The concentration of active compounds in Manuka honey can vary widely between batches, making its effects inconsistent and hard to standardize."
        },
        {
            "argument_7": "It's unrealistic to assume Manuka honey can fully eliminate the risk of bacterial resistance development."
        },
        {
            "argument_8": "Relying heavily on Manuka honey without sufficient clinical oversight could delay necessary antibiotic treatment for serious infections."
        },
        {
            "argument_9": "The notion that bacteria have not developed any resistance to Manuka honey may be an inflated claim."
        },
        {
            "argument_10": "The antibacterial action of Manuka honey is specific and narrow, so it should not be used as a broad-spectrum substitute for antibiotics."
        }
    ]
}

answer_json:
{
    "equivalence_list": [
        {
            "reference_argument_1": "proposed_argument_3"
        },
        {
            "reference_argument_2": "proposed_argument_1"
        },
        {
            "reference_argument_2": "proposed_argument_10"
        },
        {
            "reference_argument_3": "proposed_argument_9"
        },
        {
            "reference_argument_4": "proposed_argument_7"
        },
        {
            "reference_argument_5": "proposed_argument_2"
        },
        {
            "reference_argument_6": "proposed_argument_4"
        }
    ],
    "coverage": "OK"
}

...............
Example 2:

json:
{
    "reference_arguments": [
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
    ],
    "proposed_arguments": [
        {
            "argument_1": "Manuka honey should be seen as a complementary treatment rather than a substitute for conventional antibiotics, as its benefits are limited in scope."
        },
        {
            "argument_3": "Saying that Manuka honey surpasses all antibiotics is likely a dramatic overstatement."
        },
        {
            "argument_4": "While Manuka honey does exhibit antibacterial effects, the widespread claims about its potency appear exaggerated."
        },
        {
            "argument_5": "Most studies on Manuka honey’s antibacterial effects have been conducted in laboratory settings, which may not reflect real-world medical outcomes."
        },
        {
            "argument_6": "The concentration of active compounds in Manuka honey can vary widely between batches, making its effects inconsistent and hard to standardize."
        },
        {
            "argument_7": "It's unrealistic to assume Manuka honey can fully eliminate the risk of bacterial resistance development."
        },
        {
            "argument_8": "Relying heavily on Manuka honey without sufficient clinical oversight could delay necessary antibiotic treatment for serious infections."
        }
    ]
}

answer_json:
{
    "equivalence_list": [
        {
            "reference_argument_1": "proposed_argument_3"
        },
        {
            "reference_argument_2": "proposed_argument_1"
        },
        {
            "reference_argument_3": "NOK"
        },
        {
            "reference_argument_4": "proposed_argument_7"
        },
        {
            "reference_argument_5": "NOK"
        },
        {
            "reference_argument_6": "proposed_argument_4"
        }
    ],
    "coverage": "NOK"
}

"""

QUERY_TEXT = """
Evaluate the coverage of the following reference arguments taking into account the proposed arguments I provide.

json:
%s
"""
