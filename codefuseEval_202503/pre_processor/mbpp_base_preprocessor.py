# -*- coding: utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List, Dict, Union


class MbppBasePreProcessor(BasePreProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        """
        mbpp base 模型的前置处理
        @param dataset: 修改的数据集 [{"task_id":"go/1", "prompt":"xxx"....}, {"task_id":"go/1", "prompt":"xxx"....}]
        @param language: 当前数据集的语言情况，语言 data_registry.py 中 DATASET_LANGUAGE 对应的语言
        @param task_mode: 当前数据集的任务情况，任务模式为注册的任务模式中的其中一个，如果启动时没有传入，则默认为任务模式列表的第一个任务
        @param dataset_name: data_registry.py 中 DATASET_SUPPORT 的 key
        @param kwargs:
        @return: 返回处理之后的提示词的列表。
        """
        HUMAN_ROLE_START_TAG = "<role>HUMAN</role>\n"
        BOT_TAG = "<role>ASSISTANT</role>\n"
        prompt_list = []
        for data in dataset:
            lang = data["task_id"].split("/")[0]
            if lang == "cs":
                lang = "csharp"
            if lang == "js":
                lang = "javascript"
            if lang == "ts":
                lang = "typescript"
            tests = data.get("test")
            prompt_prefix = data.get("prompt", "")
            test_str = "\n".join(tests)
            prompt = f'''\
You are an expert Python programmer, and here is your task: Write a function to find the similar elements from the given two tuple lists. Your code should pass these tests:
 assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4) 
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14) 
[BEGIN]
 'def similar_elements(test_tup1, test_tup2):
  res = tuple(set(test_tup1) & set(test_tup2))
  return (res)' 
[DONE] 
You are an expert Python programmer, and here is your task: Write a python function to identify non-prime numbers. Your code should pass these tests:
 assert is_not_prime(2) == False 
assert is_not_prime(10) == True 
assert is_not_prime(35) == True 
[BEGIN]
 'import math
def is_not_prime(n):
    result = False
    for i in range(2,int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
    return result' 
[DONE] 
You are an expert Python programmer, and here is your task: Write a function to find the largest integers from a given list of numbers using heap queue algorithm. Your code should pass these tests:
 assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],3)==[85, 75, 65] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],2)==[85, 75] 
assert heap_queue_largest( [25, 35, 22, 85, 14, 65, 75, 22, 58],5)==[85, 75, 65, 58, 35] 
[BEGIN]
 'import heapq as hq
def heap_queue_largest(nums,n):
  largest_nums = hq.nlargest(n, nums)
  return largest_nums' 
[DONE] 
You are an expert Python programmer, and here is your task: {prompt_prefix} Your code should pass these tests:
{test_str}
[BEGIN]
'''
            # base 模型不需要添加 HUMAN_ROLE_START_TAG 跟 BOT_TAG
            prompt_list.append(f"Complete the following {lang.lower()} code:\n{prompt}")
        return prompt_list
