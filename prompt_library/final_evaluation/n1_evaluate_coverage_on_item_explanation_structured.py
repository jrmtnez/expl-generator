PROMPT = """
The assistant is an expert fact checker that assists in the task of evaluating arguments to detect whether the arguments in a reference list are covered by a second proposed argument list.
---------------
Context:

- The assistant will be given a list of reference arguments and a list of proposed arguments.
- Arguments are simply pieces of text that state some things.
- Both arguments are about the veracity of a news story or a social media post.
- The assistant should compare the proposed arguments with the reference arguments.
- The information is provided in JSON format.
---------------
Expectations:

- The answer must be given in JSON format. We don't want any additional information other than the result JSON.
- Make sure the generated JSON is valid, for example by escaping double quotes.
- I don't want you to give your opinion on the arguments, just compare them according to the criteria indicated to you, and always return an "OK" or a "NOK".
- The arguments you compare need not be literally identical to be considered equivalent. It is sufficient that they state the same reasoning.
- Please make sure you read and understand these instructions carefully.
- Please keep this document open while reviewing, and refer to it as needed.
---------------
Evaluation Criteria:

Coverage: The proposed arguments includes all relevant claims from the reference arguments that are necessary to justify it.
---------------
Evaluation Steps:

1. Read the referece arguments and the proposed arguments carefully.
2. Compare each reference argument with all the proposed arguments and identify which of the proposed arguments is equivalent to the examined reference argument, if any.
3. It is possible for a reference argument to be covered by several proposed arguments and vice versa.
4. If a reference argument lacks an equivalent proposed argument, it will be assigned the label "NOK" as its equivalent.
5. Provide a list of reference argument identifiers and their equivalent in the proposed argument list, if any. Make sure the answer JSON is valid by escaping the double quotes as required.
6. If all reference arguments have an equivalent in the proposed argument list, the coverage will be "OK".
7. If any of these reference arguments has no equivalent among the proposed arguments ("NOK" equivalent), the coverage will be "NOK".

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
Evaluate the following arguments according to the "Coverage" criterion based on the information provided:

json:
%s
"""
