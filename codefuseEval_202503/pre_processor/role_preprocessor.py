# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List,Dict,Union


class RolePreProcessor(BasePreProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        HUMAN_ROLE_START_TAG = "<role>HUMAN</role>"
        BOT_TAG = "<role>ASSISTANT</role>"
        prompt_list = []
        for data in dataset:
            prompt_list.append(f"{HUMAN_ROLE_START_TAG}{data['prompt']}{BOT_TAG}")
        return prompt_list
