# -*- coding: utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List, Dict, Union


class HumanevalXPreprocessor(BasePreProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        print("*language: {}".format(language))
        for data in dataset:
            prompt = data["prompt"].strip()
            prompt = prompt + "\n" if not str(prompt).endswith("\n") else prompt
            language = "javascript" if language == "js" else language
            prompt_list.append("Complete the following {} code:\n{}".format(language, prompt))
        print("#" * 100)
        print(prompt_list)
        return prompt_list
