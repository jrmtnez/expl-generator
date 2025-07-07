import transformers
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

GEMMA_2_LABEL = "gemma2"
GEMMA_2_MODEL_NAME = "google/gemma-2-9b-it"

FULL_INSTRUCTION_PROMPT = """
<start_of_turn>user
%s

%s
<start_of_turn>model
"""


def get_gpu_pipeline(model_name=GEMMA_2_MODEL_NAME, device_map=None):

    if torch.cuda.get_device_capability(device_map)[0] >= 8:
        tokenizer = None
        pipeline = transformers.pipeline(
            "text-generation",
            model=model_name,
            model_kwargs={
                "torch_dtype": torch.bfloat16,
                "low_cpu_mem_usage": True,
                "quantization_config": {"load_in_4bit": True}
            },
            device_map=device_map,
        )
    else:
        quantization_config = BitsAndBytesConfig(
            # load_in_8bit=True,  # not working
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=True)

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

    sequences = pipeline(
        query_text_with_prompt,
        max_new_tokens=1024,
        do_sample=False,
    )

    for sequence in sequences:
        results.append(sequence["generated_text"])

    query_text = sequences[0]['generated_text'][:len(query_text_with_prompt)]
    response_text = sequences[0]['generated_text'][len(query_text_with_prompt):]

    return query_text, response_text


def build_instruction_query(prompt, query_text):
    query = FULL_INSTRUCTION_PROMPT % (prompt, query_text)
    return query
