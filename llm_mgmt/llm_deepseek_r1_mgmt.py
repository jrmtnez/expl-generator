import transformers
import torch
import re
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

DEEPSEEK_R1_LABEL = "deepseekr1"
DEEPSEEK_R1_MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
# DEEPSEEK_R1_MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"

DEEPSEEK_R1_14B_LABEL = "deepseekr1_14b"
DEEPSEEK_R1_14B_MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"



FULL_INSTRUCTION_PROMPT = """
%s

%s

Please start your answer with "<think>\n" at the beginning of the output.
"""


def get_gpu_pipeline(model_name=DEEPSEEK_R1_MODEL_NAME, device_map=None, mode="4bits"):

    if mode == "4bits":
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

    if mode == "8bits":
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True,
        )

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)

    model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map, quantization_config=quantization_config).eval()

    pipeline = transformers.pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device_map=device_map
    )

    return pipeline, tokenizer


def query_model(prompt, query_text, pipeline):

    query_text_with_prompt = build_instruction_query(prompt, query_text)

    results = []

    sequences = pipeline(
        query_text_with_prompt,
        max_new_tokens=1024,
        temperature=0.6,
        top_p=0.95,
    )

    for sequence in sequences:
        results.append(sequence["generated_text"])

    query_text = sequences[0]['generated_text'][:len(query_text_with_prompt)]
    response_text = sequences[0]['generated_text'][len(query_text_with_prompt):]

    response_text = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL).strip()

    return query_text, response_text


def build_instruction_query(prompt, query_text):
    query = FULL_INSTRUCTION_PROMPT % (prompt, query_text)
    return query
