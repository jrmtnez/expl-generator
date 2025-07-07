
PROMPT = """
Assistant is an expert linguist who helps in the task of summarizing texts by extracting the most relevant ideas.
---------------
Context:

- The text may be true or false since it has been extracted from a corpus used to detect fake news.
- Make the summary even if you consider it misleading.
---------------
Expectations:

- The answer must be given in JSON format.
- In the generated JSON, use the double quote as a delimiter, but if there are double quotes in the generated summary, use an escape sequence to make a valid JSON.
---------------
Example:

News item to summarize:
"Study: Manuka honey kills more bacteria than all available antibiotics. Not all honey is created equal. While the benefits of raw, unprocessed honey have been well-documented over the centuries, Australian researchers have found one type of honey, called Manuka honey, to be better than all known antibiotics. Manuka honey is produced by bees that forage on the nectar of Leptospermum Scoparium, or New Zealand’s Manuka bush, as well as tea trees, native to Australia and New Zealand only. This remarkable type of honey not only effectively kills bacteria, but none of the bugs killed by it have been able to build up immunity. In a world where many of the last resort antibiotics are failing against antibiotic-resistant superbugs, Manuka honey may hold the key to fighting resistance issues, saving thousands of lives worldwide. Manuka honey fights superbugs. Dr. Dee Carter from the University of Sydney’s School of Molecular and Microbial Biosciences noted that antibiotics not only have short shelf lives, but the bacteria they attack quickly become resistant as well, making them useless over time. The report, published in the European Journal of Clinical Microbiology and Infectious Diseases, claimed that Manuka honey killed almost every bacteria and pathogen it was tested on. Unlike all antibiotics available on today’s market, none of the bugs tested were able to survive the honey treatment. According to Dr. Carter, there are particular compounds, like methylglyoxal, in the Manuka honey that cause multi-system failure in the bacteria, killing them before they are able to adapt and build up immunity. What Manuka honey can do for you. Manuka’s biological properties range from antioxidant, anti-inflammatory, antibacterial, antiviral, antibiotic and wound healing, to immune-stimulatory. However, what separates Manuka honey from the rest is that its antibacterial powers challenge even the toughest superbugs, such as the life-threatening methicillin-resistant Staphylococcus aureus (MRSA). Mother Nature’s micronutrient secret: Organic Broccoli Sprout Capsules now available, delivering 280mg of high-density nutrition, including the extraordinary “sulforaphane” and “glucosinolate” nutrients found only in cruciferous healing foods. Every lot laboratory tested. See availability here. Manuka honey is marketed for cancer treatment and prevention, high cholesterol, chronic inflammation, diabetes, the treatment of gastrointestinal problems, and eye, ear and sinus infections. However, it might be most useful in treating skin wounds and leg ulcers. According to one study, published in the scientific journal Peer J, chronic wounds are becoming a major global health problem, due to antibiotic resistance issues. They are costly and difficult to treat, and bacterial biofilms are important contributors to the delay in healing. There is an urgent need for new, effective agents in topical wound care, and honey has shown some great potential in this regard. For their study, researchers reviewed Manuka honey in particular as an alternative treatment for wounds because of its broad-spectrum antibacterial activity and the inability of bacteria to develop resistance to it. Their study indicated that honey might prevent bacterial biofilms and eliminate established biofilms. Furthermore, they reported that Manuka honey could successfully be used to kill all MSSA and MRSA biofilms in a chronic wound, supporting the use of this type of honey as an effective topical treatment for chronic wound infections. In recent years, word of the biological benefits of Manuka honey has spread to every corner of the world, turning it into one of the most popular superfoods out there. Its fame and the over-demand, however, have caused shortages, resulting in fake, usually cheaper, products to enter the market. So, if you are going to spend your money on honey to reap its benefits, make sure you are buying the real thing."

answer_json:
{"extracted_summary": "The study highlights that Manuka honey, produced by bees that forage on New Zealand's Manuka bush and Australian tea trees, is more effective than all known antibiotics in killing bacteria, including antibiotic-resistant superbugs. Unlike traditional antibiotics, Manuka honey prevents bacteria from building up immunity, making it a potential solution to the global issue of antibiotic resistance. Manuka honey contains compounds like methylglyoxal that cause multi-system failure in bacteria, preventing them from adapting and surviving. It is noted for its wide range of biological properties, including antibacterial, anti-inflammatory, antiviral, and wound-healing abilities. Particularly, it shows promise in treating chronic wounds, such as those caused by MRSA, where antibiotics have failed. The honey is also marketed for various health benefits, including cancer prevention, high cholesterol, and gastrointestinal issues. However, due to its popularity, there are many counterfeit products on the market, so consumers are advised to ensure they purchase genuine Manuka honey."}
---------------
"""

QUERY_TEXT = """
Summarize the following text:
"%s"
"""

MAX_TEXT_SIZE = 15000