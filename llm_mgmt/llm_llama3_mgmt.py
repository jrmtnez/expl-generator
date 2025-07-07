import transformers
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

LLAMA_3_LABEL = "llama3"
LLAMA_3_MODEL_NAME = "meta-llama/Meta-Llama-3.1-8B-Instruct"

FULL_INSTRUCTION_PROMPT = """
<|begin_of_text|><|start_header_id|>system<|end_header_id|>

%s<|eot_id|><|start_header_id|>user<|end_header_id|>

%s<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""


def get_gpu_pipeline(model_name=LLAMA_3_MODEL_NAME, device_map=None, low_memory_gpu=False):

    tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

    if low_memory_gpu:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )
    else:
        quantization_config = BitsAndBytesConfig(
            load_in_8bit=True
        )

    model = AutoModelForCausalLM.from_pretrained(model_name, device_map=device_map, quantization_config=quantization_config)

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

    terminators = [
        pipeline.tokenizer.eos_token_id,
        pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
    ]

    sequences = pipeline(
        query_text_with_prompt,
        max_new_tokens=1024,
        eos_token_id=terminators,
        pad_token_id=pipeline.tokenizer.eos_token_id,
        do_sample=True,
        temperature=0.6,
        top_p=0.9,
    )

    for sequence in sequences:
        results.append(sequence["generated_text"])

    query_text_with_prompt = sequences[0]['generated_text'][:len(query_text_with_prompt)]
    response_text = sequences[0]['generated_text'][len(query_text_with_prompt):]

    return query_text_with_prompt, response_text


def build_instruction_query(prompt, query_text):
    query = FULL_INSTRUCTION_PROMPT % (prompt, query_text)
    return query
