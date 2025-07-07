import requests

URL = "http://localhost:11434/api/chat"

# test
# curl localhost:11434/api/generate -d '{"model": "gemma3:27b-it-qat","prompt": "Why is the sky blue?","stream": false,"options": {"num_ctx": 8192}}' | jq .

# --- paper v1 ---
O_LLAMA33_70B_LABEL = "o_llama33_70b"
O_LLAMA33_70B_MODEL_NAME = "llama3.3:70b-instruct-q2_K"

O_GEMMA2_27B_LABEL = "o_gemma2_27b"
O_GEMMA2_27B_MODEL_NAME = "gemma2:27b"
# +++ paper v1 +++

O_DEEPSEEK_R1_32B_LABEL = "o_deepseek_r1_32b"
O_DEEPSEEK_R1_32B_MODEL_NAME = "deepseek-r1:32b"

O_DEEPSEEK_R1_70B_LABEL = "o_deepseek_r1_70b"
O_DEEPSEEK_R1_70B_MODEL_NAME = "deepseek-r1:70b"

O_MISTRAL_24B_LABEL = "o_mistral_small"
# ¡desapareció de ollama!
# O_MISTRAL_24B_MODEL_NAME = "mistral-small3.1:24b-instruct-2503-q4_K_M"
O_MISTRAL_24B_MODEL_NAME = "hf.co/unsloth/Mistral-Small-3.1-24B-Instruct-2503-GGUF:latest"

O_GEMMA3_27B_LABEL = "o_gemma3_27b"
O_GEMMA3_27B_MODEL_NAME = "gemma3:27b-it-qat"

O_QWQ_32B_LABEL = "o_qwq"
O_QWQ_32B_MODEL_NAME = "qwq:32b"

O_YI_34B_LABEL = "o_yi15_34b"
O_YI_34B_MODEL_NAME = "yi:34b"

O_QWEN_32B_LABEL = "o_qwen3_32b"
O_QWEN_32B_MODEL_NAME = "qwen3:32b"

O_QWEN_MOE_30B_LABEL = "o_qwen3_30b_a3b"
O_QWEN_MOE_30B_MODEL_NAME = "qwen3:30b-a3b"

O_COGITO_32B_LABEL = "o_cogito_32b"
O_COGITO_32B_MODEL_NAME = "cogito:32b"

# --- for 12GB GPU ---
# (algunos por problemas de compatibilidad de librería Transformers)

O_DEEPSEEK_R1_LABEL = "o_deepseekr1"
O_DEEPSEEK_R1_MODEL_NAME = "deepseek-r1:8b"

O_GEMMA_LABEL = "o_gemma3"
O_GEMMA_MODEL_NAME = "gemma3:12b-it-qat"

O_QWEN_LABEL = "o_qwen3"
O_QWEN_MODEL_NAME = "qwen3:8b"
# +++ for 12GB GPU +++

OLLAMA_MODELS = [O_GEMMA2_27B_MODEL_NAME, O_LLAMA33_70B_MODEL_NAME, O_COGITO_32B_MODEL_NAME,
                 O_QWQ_32B_MODEL_NAME, O_QWEN_32B_MODEL_NAME, O_YI_34B_MODEL_NAME, O_QWEN_MOE_30B_MODEL_NAME,
                 O_DEEPSEEK_R1_32B_MODEL_NAME, O_GEMMA3_27B_MODEL_NAME, O_MISTRAL_24B_MODEL_NAME,
                 O_GEMMA_MODEL_NAME, O_QWEN_MODEL_NAME, O_DEEPSEEK_R1_MODEL_NAME, O_DEEPSEEK_R1_70B_MODEL_NAME]


FULL_QUERY_TEXT = """
%s
%s
"""


def query_model(prompt, query_text, pipeline, system_prompt="prompt", model_name=O_LLAMA33_70B_MODEL_NAME):

    headers = {"Content-Type": "application/json"}

    match system_prompt:
        case "prompt":
            data = {
                "model": model_name,
                "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": query_text}],
                "stream": False,
                "options": {
                    "num_ctx": 8192
                }
            }
        case None:
            content_text = FULL_QUERY_TEXT % (prompt, query_text)
            data = {
                "model": model_name,
                "messages": [{"role": "user", "content": content_text}],
                "stream": False,
                "options": {
                    "num_ctx": 8192
                }
            }
        case _:
            content_text = FULL_QUERY_TEXT % (prompt, query_text)
            data = {
                "model": model_name,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": content_text}],
                "stream": False,
                "options": {
                    "num_ctx": 8192
                }
            }

    response = requests.post(URL, headers=headers, json=data)



    return FULL_QUERY_TEXT % (prompt, query_text), str(response.json().get("message").get("content"))
