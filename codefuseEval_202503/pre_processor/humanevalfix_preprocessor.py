# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List,Dict

class HumanevalFixPreProcessor(BasePreProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        for data in dataset:
            prompt_list.append(data['prompt'] + data['buggy_solution'] + '\n' + data['test'] + "\n" + "Fix bugs in " + data['entry_point'])
        return prompt_list
