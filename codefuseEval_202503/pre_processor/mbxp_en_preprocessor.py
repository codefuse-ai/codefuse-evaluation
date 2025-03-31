# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List,Dict


class MbxpEnPreProcessor(BasePreProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def get_mbxp_prompt(self, mbpp_mode, item):
        # 从item中获取测试用例，并确保其为列表形式
        tests = item.get("test")
        lang = item["task_id"].split("/")[0].lower()
        if lang == "ts":
            lang = "typescript"
        if not isinstance(tests, list):
            tests = [tests] if tests is not None else []
        
        # 根据模式(mbpp_mode)构建和返回提示信息
        if mbpp_mode == "en":  # 英文原版
            prompt_prefix = item.get("description", "")  # 防止KeyError，使用get方法获取prompt
            test_str = "\n".join(tests)
            prompt = f"Please complete the following requirement using {lang}:\n"
            prompt = prompt + f"{prompt_prefix}\nYour code should satisfy these tests:\n{test_str}"
        elif mbpp_mode == "cn":  # 中文原版
            prompt_prefix = item.get("description_cn", "")  # 类似地，防止KeyError
            test_str = "\n".join(tests)
            prompt = f"请用{lang}完成下述需求:\n"
            prompt = prompt + f"{prompt_prefix}你的代码必须能够通过这些测试用例:\n{test_str}"
        else:
            prompt = "Unsupported mbpp mode."
        
        return prompt
    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        for data in dataset:
            prompt=self.get_mbxp_prompt("en", data)
            prompt_list.append(prompt) 
        print("prompt_real:",prompt_list[0])            
        return prompt_list
