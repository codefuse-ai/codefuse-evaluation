# -*- coding:utf-8 -*-
from typing import List, Union
from .base import BaseProcessor
import os
import torch
# modeling_rodimus and tokenization_rodimus_fast file see https://github.com/codefuse-ai/rodimus/
from .developer_provide_rodimus.modeling_rodimus import RodimusForCausalLM
from .developer_provide_rodimus.tokenization_rodimus_fast import RodimusTokenizer

os.environ['TOKENIZERS_PARALLELISM'] = 'false'


class Rodimus_Processor(BaseProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tokenizer = RodimusTokenizer.from_pretrained(self.path)
        self.model = RodimusForCausalLM.from_pretrained(
            self.path,
            torch_dtype=torch.bfloat16,
            device_map="cuda"
        ).eval()

    def generate(self, prompt_list: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[List,str]:
        generation = []
        for prompt in prompt_list:
            messages = [
                {"role": "HUMAN", "content": prompt}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                # system='You are Rodimus+, created by AntGroup. You are a helpful assistant.',
                tokenize=False,
            )
            print("real prompt:{}".format(text))
            model_inputs = self.tokenizer(text, return_tensors="pt").to(self.model.device)
            generated_ids = self.model.generate(**model_inputs, max_new_tokens=2048)
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
            generation.append(response)
        print("generation success")
        return generation
