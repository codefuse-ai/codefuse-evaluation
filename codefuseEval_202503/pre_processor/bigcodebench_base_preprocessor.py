# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List,Dict


class BigcodebenchBasePreProcessor(BasePreProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    
    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        for data in dataset:
            complete_prompt=data["complete_prompt"]
            prompt_list.append(complete_prompt)
        print("prompt_real:",prompt_list[0])           
        return prompt_list
