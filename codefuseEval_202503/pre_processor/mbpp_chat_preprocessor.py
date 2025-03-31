# -*- coding: utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List,Dict,Union


class MbppChatPreProcessor(BasePreProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        """
        mbpp chat 模型的前置处理
        @param dataset: 修改的数据集 [{"task_id":"go/1", "prompt":"xxx"....}, {"task_id":"go/1", "prompt":"xxx"....}]
        @param language: 当前数据集的语言情况，语言 data_registry.py 中 DATASET_LANGUAGE 对应的语言
        @param task_mode: 当前数据集的任务情况，任务模式为注册的任务模式中的其中一个，如果启动时没有传入，则默认为任务模式列表的第一个任务
        @param dataset_name: data_registry.py 中 DATASET_SUPPORT 的 key
        @param kwargs:
        @return: 返回处理之后的提示词的列表。
        """
        prompt_list = []
        for data in dataset:
            lang = data["task_id"].split( "/" )[0]
            if lang == "cs":
                lang = "csharp"
            if lang == "js":
                lang = "javascript"
            if lang == "ts":
                lang = "typescript"
            tests = data.get("test")
            if not isinstance(tests, list):
                tests = [tests] if tests is not None else []
            prompt_prefix = data.get("prompt", "")  # 防止KeyError，使用get方法获取prompt
            test_str = "\n".join(tests)
            prompt = f"{prompt_prefix}\nYour code should satisfy these tests:\n{test_str}"  # 默认使用英文
            print("=" * 200 + "prompt")
            print(prompt)
            prompt_list.append(prompt)
        return prompt_list
