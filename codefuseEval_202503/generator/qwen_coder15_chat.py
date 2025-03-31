# Copyright (c) 2022-2025 Ant Group
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import *
from .base import BaseProcessor


class QwenCoder15InstructProcessor( BaseProcessor ):
    def __init__(self, **kwargs):
        super().__init__( **kwargs )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained( self.path )

    def generate(self, promptlist: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[List, str]:
        generation = []
        for prompt in promptlist:
            final_prompt = prepare_prompt(prompt)
            text = self.tokenizer.apply_chat_template(
                final_prompt,
                tokenize=False,
                add_generation_prompt=True
            )
            inputs = self.tokenizer([text], return_tensors="pt").to("cuda")
            outputs = self.model.generate( inputs.input_ids, max_new_tokens=4096, do_sample=False, eos_token_id=2 )[0]
            generated_text = self.tokenizer.decode( outputs[len( inputs.input_ids[0] ):], skip_special_tokens=True )
            generation.append( generated_text )
        return generation


def prepare_prompt(prompt):
    """
    准备prompt
    """
    prompt = [
        {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ]
    return prompt
