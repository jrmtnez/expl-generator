import transformers
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import warnings
warnings.filterwarnings('ignore', '.*Sparse CSR tensor support is in beta state.*')

PHI_3_LABEL = "phi3"

PHI_3_MINI_MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
PHI_3_MINI_MODEL_NAME = "microsoft/Phi-3.5-mini-instruct"

PHI_3_MINI_FULL_INSTRUCTION_PROMPT = """
<|system|>
%s<|end|>
<|user|>
%s<|end|>
<|assistant|>
"""

PHI_3_SMALL_MODEL_NAME = "microsoft/Phi-3-small-8k-instruct"

PHI_3_SMALL_FULL_INSTRUCTION_PROMPT = """
<|endoftext|><|user|>
%s

%s<|end|>
<|assistant|>
"""

# device_map = f"cuda:{torch.cuda.current_device()}"

# print(device_map)

SELECTED_MODEL = "mini"

if SELECTED_MODEL == "mini":
    PHI_3_MODEL_NAME = PHI_3_MINI_MODEL_NAME
    FULL_INSTRUCTION_PROMPT = PHI_3_MINI_FULL_INSTRUCTION_PROMPT

if SELECTED_MODEL == "small":
    PHI_3_MODEL_NAME = PHI_3_SMALL_MODEL_NAME
    FULL_INSTRUCTION_PROMPT = PHI_3_SMALL_FULL_INSTRUCTION_PROMPT


def get_gpu_pipeline(model_name=PHI_3_MODEL_NAME, device_map=None, flash_attention_2=True):

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    if flash_attention_2:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device_map,
            quantization_config=quantization_config,
            trust_remote_code=True,
            attn_implementation="flash_attention_2",
        )
    else:
        # Tesla M40 requires "mini" + "eager"
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device_map,
            quantization_config=quantization_config,
            trust_remote_code=True,
            attn_implementation="eager",
        )

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
        return_full_text=False,
        do_sample=False,
    )

    for sequence in sequences:
        results.append(sequence["generated_text"])

    response_text = sequences[0]['generated_text']

    return query_text_with_prompt, response_text


def build_instruction_query(prompt, query_text):
    query = FULL_INSTRUCTION_PROMPT % (prompt, query_text)
    return query
