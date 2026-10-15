#!/usr/bin/env python3
import json
import os
import time

from huggingface_hub import HfApi
from vllm import LLM, SamplingParams

MODEL_ID = "swiss-ai/Apertus-v1.5-8B"
QUESTION = "Wie heisst die Hauptstadt der Schweiz?"

def main():
    started = time.time()
    revision = HfApi().model_info(MODEL_ID, token=os.environ.get("HF_TOKEN")).sha

    llm = LLM(
        model=MODEL_ID,
        gpu_memory_utilization=0.6,
        max_model_len=4096,
    )

    sampling = SamplingParams(
        temperature=0.0,
        max_tokens=64,
        seed=0,
    )

    outputs = llm.chat(
        [{"role": "user", "content": QUESTION}],
        sampling_params=sampling,
        use_tqdm=False,
        chat_template_content_format="string",
        chat_template_kwargs={"enable_thinking": False},
    )

    candidate = outputs[0].outputs[0]
    result = {
        "job_id": os.environ.get("JOB_ID"),
        "accelerator": os.environ.get("ACCELERATOR"),
        "model": MODEL_ID,
        "model_revision": revision,
        "thinking": False,
        "temperature": 0.0,
        "max_tokens": 64,
        "seed": 0,
        "question": QUESTION,
        "response": candidate.text,
        "finish_reason": getattr(candidate, "finish_reason", None),
        "elapsed_seconds": round(time.time() - started, 2),
    }

    print("\n=== APERTUS_SMOKE_RESULT ===")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("=== END_APERTUS_SMOKE_RESULT ===")

if __name__ == "__main__":
    main()
