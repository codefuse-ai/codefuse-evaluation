# Copyright (c) 2022-2025 Ant Group
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import *
from .base import BaseProcessor


class QwenCoderInstructProcessor(BaseProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.path,
            torch_dtype="auto",
            device_map="auto"
        )
        self.tokenizer = AutoTokenizer.from_pretrained( self.path )


    # def process_before(self, dataset, language, task_mode, dataset_name, **kwargs):
        # print("deal prompt for dataset "+ dataset_name)
        # return dataset

    def generate(self, promptlist: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[List,str]:
        generation = []
        for input_text in promptlist:

            messages = [
                {"role": "system", "content": "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."},
                {"role": "user", "content": input_text}
            ]
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True
            )
            model_inputs = self.tokenizer( [text], return_tensors="pt" ).to( self.model.device )

            generated_ids = self.model.generate(
                **model_inputs,
                max_new_tokens=512
            )
            generated_ids = [
                output_ids[len( input_ids ):] for input_ids, output_ids in zip( model_inputs.input_ids, generated_ids )
            ]

            response = self.tokenizer.batch_decode( generated_ids, skip_special_tokens=True )[0]
            generation.append(response)
        return generation

    # def process_after(self, dataset, language, task_mode, dataset_name, **kwargs):
        # print("deal dataset generations for " + dataset_name)