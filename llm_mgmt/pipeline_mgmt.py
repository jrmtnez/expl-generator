import logging
import torch
from datetime import datetime
# from pynvml import nvmlInit, nvmlDeviceGetHandleByIndex, nvmlDeviceGetMemoryInfo
from pipeline.config import ROOT_LOGGER_ID

from llm_mgmt.llm_llama3_mgmt import get_gpu_pipeline as get_llama3_gpu_pipeline
from llm_mgmt.llm_llama3_mgmt import query_model as query_llama3_model
from llm_mgmt.llm_llama3_mgmt import LLAMA_3_MODEL_NAME

from llm_mgmt.llm_gemma2_mgmt import get_gpu_pipeline as get_gemma2_gpu_pipeline
from llm_mgmt.llm_gemma2_mgmt import query_model as query_gemma2_model
from llm_mgmt.llm_gemma2_mgmt import GEMMA_2_MODEL_NAME

from llm_mgmt.llm_phi3_mgmt import get_gpu_pipeline as get_phi3_gpu_pipeline
from llm_mgmt.llm_phi3_mgmt import query_model as query_phi3_model
from llm_mgmt.llm_phi3_mgmt import PHI_3_MODEL_NAME

from llm_mgmt.llm_yi15_mgmt import get_gpu_pipeline as get_yi15_gpu_pipeline
from llm_mgmt.llm_yi15_mgmt import query_model as query_yi15_model
from llm_mgmt.llm_yi15_mgmt import YI_15_MODEL_NAME

from llm_mgmt.llm_qwen25_mgmt import get_gpu_pipeline as get_qwen25_gpu_pipeline
from llm_mgmt.llm_qwen25_mgmt import query_model as query_qwen25_model
from llm_mgmt.llm_qwen25_mgmt import QWEN_25_MODEL_NAME

from llm_mgmt.llm_deepseek_r1_mgmt import get_gpu_pipeline as get_deepseek_r1_gpu_pipeline
from llm_mgmt.llm_deepseek_r1_mgmt import query_model as query_deepseek_r1_model
from llm_mgmt.llm_deepseek_r1_mgmt import DEEPSEEK_R1_MODEL_NAME, DEEPSEEK_R1_14B_MODEL_NAME

from llm_mgmt.llm_ollama_mgmt import query_model as query_ollama_model
from llm_mgmt.llm_ollama_mgmt import OLLAMA_MODELS
from llm_mgmt.llm_ollama_mgmt import O_DEEPSEEK_R1_MODEL_NAME, O_DEEPSEEK_R1_32B_MODEL_NAME, O_DEEPSEEK_R1_70B_MODEL_NAME
from llm_mgmt.llm_ollama_mgmt import O_COGITO_32B_MODEL_NAME

logger = logging.getLogger(ROOT_LOGGER_ID)



def get_gpu_pipeline(model_name=LLAMA_3_MODEL_NAME, low_memory_gpu=True):

    logging.info("Loading %s model on gpu...", model_name)

    starting_time = datetime.now()

    # gpu_total_memory = get_gpu_total_memory()
    # if not low_memory_gpu:
    #     low_memory_gpu = (gpu_total_memory < 12000)

    # device_map = f"cuda:{torch.cuda.current_device()}"
    # logging.info("Device id used: %s", device_map)
    # logging.info("Compute capability: %s", torch.cuda.get_device_capability(device_map))

    if torch.backends.mps.is_available():
        device_map = "mps"
    else:
        device_map = f"cuda:{torch.cuda.current_device()}"
        logging.info("Compute capability: %s", torch.cuda.get_device_capability(device_map))

    logging.info("Device id used: %s", device_map)

    if model_name == LLAMA_3_MODEL_NAME:
        pipeline, tokenizer = get_llama3_gpu_pipeline(device_map=device_map, low_memory_gpu=low_memory_gpu)
    if model_name == GEMMA_2_MODEL_NAME:
        pipeline, tokenizer = get_gemma2_gpu_pipeline(device_map=device_map)
    if model_name == PHI_3_MODEL_NAME:
        pipeline, tokenizer = get_phi3_gpu_pipeline(device_map=device_map)
    if model_name == YI_15_MODEL_NAME:
        pipeline, tokenizer = get_yi15_gpu_pipeline(device_map=device_map)
    if model_name == QWEN_25_MODEL_NAME:
        pipeline, tokenizer = get_qwen25_gpu_pipeline(device_map=device_map)
    if model_name == QWEN_25_MODEL_NAME:
        pipeline, tokenizer = get_qwen25_gpu_pipeline(device_map=device_map)
    if model_name == DEEPSEEK_R1_MODEL_NAME:
        pipeline, tokenizer = get_deepseek_r1_gpu_pipeline(device_map=device_map)
    if model_name == DEEPSEEK_R1_14B_MODEL_NAME:
        pipeline, tokenizer = get_deepseek_r1_gpu_pipeline(model_name=DEEPSEEK_R1_14B_MODEL_NAME, device_map=device_map)
    if model_name in OLLAMA_MODELS:
        pipeline, tokenizer = None, None

    ending_time = datetime.now()

    logging.info("%s model ready!", model_name)
    logging.info("Total time: %s.", ending_time - starting_time)

    return pipeline, tokenizer


def query_model(prompt, query_text, pipeline, model_name="meta-llama/Meta-Llama-3.1-8B-Instruct"):
    starting_time = datetime.now()

    if model_name == LLAMA_3_MODEL_NAME:
        query_text, response_text = query_llama3_model(prompt, query_text, pipeline)
    if model_name == GEMMA_2_MODEL_NAME:
        query_text, response_text = query_gemma2_model(prompt, query_text, pipeline)
    if model_name == PHI_3_MODEL_NAME:
        query_text, response_text = query_phi3_model(prompt, query_text, pipeline)
    if model_name == PHI_3_MODEL_NAME:
        query_text, response_text = query_phi3_model(prompt, query_text, pipeline)
    if model_name == YI_15_MODEL_NAME:
        query_text, response_text = query_yi15_model(prompt, query_text, pipeline)
    if model_name == QWEN_25_MODEL_NAME:
        query_text, response_text = query_qwen25_model(prompt, query_text, pipeline)
    if model_name == DEEPSEEK_R1_MODEL_NAME or model_name == DEEPSEEK_R1_14B_MODEL_NAME:
        query_text, response_text = query_deepseek_r1_model(prompt, query_text, pipeline, )
    if model_name in OLLAMA_MODELS:
        if model_name in [O_DEEPSEEK_R1_MODEL_NAME, O_DEEPSEEK_R1_32B_MODEL_NAME, O_DEEPSEEK_R1_70B_MODEL_NAME]:
            query_text, response_text = query_ollama_model(prompt, query_text, None, model_name=model_name, system_prompt=None)
        elif model_name in [O_COGITO_32B_MODEL_NAME]:
            query_text, response_text = query_ollama_model(prompt, query_text, None, model_name=model_name, system_prompt="Enable deep thinking subroutine.")
        else:
            query_text, response_text = query_ollama_model(prompt, query_text, None, model_name=model_name)

    ending_time = datetime.now()
    logging.debug("Query processed. Total time: %s.", ending_time - starting_time)

    return query_text, response_text


# def get_gpu_total_memory():
#     nvmlInit()
#     handle = nvmlDeviceGetHandleByIndex(0)
#     info = nvmlDeviceGetMemoryInfo(handle)
#     available_memory = info.total // 1024 ** 2
#     logging.info("GPU memory: %s", available_memory)
#     return available_memory
