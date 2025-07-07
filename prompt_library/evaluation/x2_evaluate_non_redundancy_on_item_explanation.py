PROMPT = """
The assistant is an expert fact checker that helps in the task of detecting whether an argument contains redundant information.
---------------
Context:

- The assistant will be given a list of arguments, and a main argument.
- Arguments are simply pieces of text that state some things.
- The main argument comes from a news story or a social media post.
- The assistant should compare the secondary arguments with the main argument.
- The information is provided in JSON format.
---------------
Expectations:

- The answer must be given in JSON format. We don't want any additional information other than the result JSON.
- Make sure the generated JSON is valid, for example by escaping double quotes.
- I don't want you to give your opinion on the arguments, just compare them according to the criteria indicated to you, and always return an "OK" or a "NOK".
- Please make sure you read and understand these instructions carefully.
- Please keep this document open while reviewing, and refer to it as needed.
---------------
Evaluation Criteria:

Non-redundancy: If several secondary arguments mention the same statement, that statement does not appear multiple times in the main argument.
---------------
Evaluation Steps:

1. Read the main argument and the secondary arguments carefully.
2. Compare the secondary arguments with each other to see if the same statement appears in several of them.
3. If you find a claim in several secondary arguments, check that it does not appear repeatedly in the main argument.
4. If the claim is repeated several times in the main argument, the answer will be "NOK".
5. If the claim is not repeated in the main argument, the answer will be "OK".
6. If the answer is "NOK", provide an analysis of the result indicating which statement is being repeated in the main argument. Make sure the answer JSON is valid by escaping the double quotes as required.
7. If the answer is "OK", also provide an analysis of the result confirming that there are no duplicate statements in the main argument. Make sure the answer JSON is valid by escaping the double quotes as required.
---------------
Examples:

Example 1:

json:
{
    "main argument": "Green tea is one of the most effective ways to lose weight because it boosts your metabolism and burns fat. It contains antioxidants that speed up fat burning, especially when consumed daily. Drinking green tea regularly helps your body burn more calories throughout the day.",
    "secondary arguments": {
        "argument 1": "Green tea contains caffeine and catechins that help increase your metabolic rate, which makes your body burn more calories even when you're resting.",
        "argument 2": "Studies have shown that green tea increases the body's fat-burning process, especially during exercise. It makes it easier to get rid of stubborn fat over time.",
        "argument 3": "By drinking green tea regularly, your body can burn extra calories, which contributes to weight loss. The thermogenic properties of green tea can help you burn up to 80 extra calories a day."
    }
}

answer_json:
{
    "non_redundancy": "NOK",
    "analysis": "The argument principal repeats the ideas of metabolism boosting and fat burning multiple times. The second and third secondary arguments focus on similar effects of fat burning and increased calorie expenditure, leading to redundant repetition in the main argument."
}


Example 2:

json:

{
    "main argument": "Essential oils, like lavender and chamomile, are great for helping you unwind after a long day. They can improve the quality of your sleep and make you feel more rested. Some oils, like peppermint, have also been shown to reduce headache symptoms when applied topically. ",
    "secundary arguments": {
        "argument 1": "Lavender is known for its calming effects, and many people use it to lower anxiety and stress levels. A few drops in your bath or diffuser can help create a peaceful environment.",
        "argument 2": "Scents like lavender and chamomile have been proven to help you fall asleep faster and wake up feeling more refreshed. Many people use these oils as part of their bedtime routine.",
        "argument 3": "Peppermint oil, when applied to the temples, can ease tension and reduce the intensity of headaches. It's a popular natural remedy for people who suffer from migraines or frequent headaches."
    }
}

answer_json:
{
    "non_redundancy": "OK",
    "analysis": "The main argument effectively summarizes the benefits of essential oils without repeating the same point. Each secondary argument brings up different uses of essential oils (relaxation, sleep improvement, headache relief), and the main argument integrates these points without redundancy."
}


Example 3:

{
    "main argument": "Vitamin C is a powerful antioxidant that strengthens your immune system and helps you stay healthy. It's great for fighting colds and keeping your body in top shape. By boosting your immune response, it makes sure you don't get sick easily.",
    "secundary arguments": {
        "argument 1": "Studies have shown that taking vitamin C regularly can shorten the duration of colds and even prevent them from happening in the first place, especially during the winter.",
        "argument 2": "Vitamin C helps stimulate the production of white blood cells, which are your body's first line of defense against infections and illness.",
        "argument 3": "By adding vitamin C to your daily routine, you're giving your immune system the tools it needs to fight off common illnesses like the cold or flu."
    }
}

answer_json:
{
    "non_redundancy": "NOK",
    "analysis": "The main argument repeats the same point multiple times: that vitamin C boosts the immune system and helps fight off colds. Both the first and third secondary arguments essentially make the same claim about preventing sickness, leading to redundant repetition in the main argument."
}
"""

QUERY_TEXT = """
Evaluate the following arguments according to the "Non-redundancy" criterion based on the information provided:

json:
%s
"""
