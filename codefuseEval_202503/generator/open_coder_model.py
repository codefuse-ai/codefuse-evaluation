# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import *
import torch
from .base import BaseProcessor


class OpenCoderProcessor(BaseProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            trust_remote_code=True
        )
        self.tokenizer = AutoTokenizer.from_pretrained(self.path, trust_remote_code=True)

    def generate(self, prompts: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[List, str]:
        generation = []
        for input_text in prompts:
            # 构建消息列表
            messages = [
                {"role": "user", "content": input_text}
            ]
            # 应用模板
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            # 将文本转换为模型输入
            model_inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

            # todo: 确认下剩下的参数要不要
            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=4096,
                do_sample=False
                # top_p=0.95,
                # top_k=50,
                # num_return_sequences=1,
                # eos_token_id=self.tokenizer.eos_token_id
            )
            # 获取生成的回复
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]

            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            # 将生成的回复添加到列表中
            generation.append(response)
        return generation
