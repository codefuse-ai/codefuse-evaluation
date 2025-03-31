# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import *
import torch
from .base import BaseProcessor


class DeepSeekCoderV2BaseInstructProcessor(BaseProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path,
            trust_remote_code=True,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.path)

    def generate(self, prompts: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[List, str]:
        model_inputs = self.tokenizer(prompts, return_tensors="pt", padding=True, truncation=True).to(self.model.device)
        generated_ids = self.model.generate(**model_inputs, max_new_tokens=512, do_sample=False)
        generation = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)
        return generation

