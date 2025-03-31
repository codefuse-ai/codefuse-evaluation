# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List,Dict


class BigcodebenchPreProcessor(BasePreProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        for data in dataset:
            instruct_prompt=data["instruct_prompt"]
            prompt=f'Please provide a self-contained Python script that solves the following problem in a markdown code block:\n```\n{instruct_prompt}```\n Below is a Python script with a self-contained function that solves the problem and passes corresponding tests:\n```python\n'
            prompt_list.append(prompt) 
        print("prompt_real:",prompt_list[0])           
        return prompt_list
