import transformers
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

QWEN_25_LABEL = "qwen25"
QWEN_25_MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
# QWEN_25_MODEL_NAME = "Qwen/QwQ-32B-Preview"


FULL_INSTRUCTION_PROMPT = """
<|im_start|>system
%s<|im_end|>
<|im_start|>user
%s<|im_end|>
<|im_start|>assistant
<|im_end|>
"""


def get_gpu_pipeline(model_name=QWEN_25_MODEL_NAME, device_map=None, mode="4bits"):

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
        do_sample=False,
        temperature=None,
        top_k=None,
        top_p=None,
    )

    for sequence in sequences:
        results.append(sequence["generated_text"])
    initial_offset = 3
    final_offset = 1
    query_text = sequences[0]['generated_text'][:len(query_text_with_prompt) - initial_offset]
    response_text = sequences[0]['generated_text'][len(query_text_with_prompt) + initial_offset: -final_offset]

    return query_text, response_text


def build_instruction_query(prompt, query_text):
    query = FULL_INSTRUCTION_PROMPT % (prompt, query_text)
    return query
