
PROMPT = """
The assistant is a linguistic expert who helps in the task of determining the main subject discussed in a text.
---------------
Context:

- The text may be true or false since it has been extracted from a corpus used to detect fake news.
---------------
Expectations:

- The answer must be given in JSON format.
---------------
Example:

Text in which to determine the main subject:
"Manuka honey, produced from the nectar of New Zealand's Manuka bush and Australian tea trees, surpasses all known antibiotics in killing bacteria, including superbugs.  Unlike traditional antibiotics, bacteria cannot develop resistance to Manuka honey. This unique property makes it a potential solution to the global antibiotic resistance crisis.  Manuka honey contains compounds like methylglyoxal that cause multi-system failure in bacteria, preventing their survival.  It boasts a range of biological benefits, including antibacterial, anti-inflammatory, and wound-healing properties.  While marketed for various health conditions, Manuka honey shows particular promise in treating chronic wounds, especially those caused by MRSA.  However, due to its popularity, counterfeit products are flooding the market.  Therefore, it's crucial to ensure you purchase genuine Manuka honey to reap its benefits."

answer_json:
{"main_subject": "Manuka honey"}
---------------
"""

QUERY_TEXT = """
Determine the main subject of the following text:
"%s"
"""
