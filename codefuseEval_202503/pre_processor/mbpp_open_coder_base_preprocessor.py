# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List, Dict, Union


class MbppOpenCoderBasePreProcessor(BasePreProcessor):
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
        prompt_list = []
        for data in dataset:
            lang = data["task_id"].split("/")[0]

            lang = "csharp" if lang == "cs" else lang
            lang = "javascript" if lang == "js" else lang
            lang = "typescript" if lang == "ts" else lang
            tests = data.get("test")
            prompt_prefix = data.get("prompt", "")
            test_str = "\n".join(tests)
            prompt = f'''\
You are an expert Python programmer, and here is your task:
Write a function to find the minimum cost path to reach (m, n) from (0, 0) for the given cost matrix cost[][] and a position (m, n) in cost[][].
Your code should pass these tests:
assert min_cost([[1, 2, 3], [4, 8, 2], [1, 5, 3]], 2, 2) == 8
assert min_cost([[2, 3, 4], [5, 9, 3], [2, 6, 4]], 2, 2) == 12
assert min_cost([[3, 4, 5], [6, 10, 4], [3, 7, 5]], 2, 2) == 16

```python
R = 3
C = 3
def min_cost(cost, m, n): 
    tc = [[0 for x in range(C)] for x in range(R)] 
    tc[0][0] = cost[0][0] 
    for i in range(1, m+1): 
        tc[i][0] = tc[i-1][0] + cost[i][0] 
    for j in range(1, n+1): 
        tc[0][j] = tc[0][j-1] + cost[0][j] 
    for i in range(1, m+1): 
        for j in range(1, n+1): 
            tc[i][j] = min(tc[i-1][j-1], tc[i-1][j], tc[i][j-1]) + cost[i][j] 
    return tc[m][n]
```

You are an expert Python programmer, and here is your task:
Write a function to find the similar elements from the given two tuple lists.
Your code should pass these tests:
assert similar_elements((3, 4, 5, 6),(5, 7, 4, 10)) == (4, 5)
assert similar_elements((1, 2, 3, 4),(5, 4, 3, 7)) == (3, 4)
assert similar_elements((11, 12, 14, 13),(17, 15, 14, 13)) == (13, 14)

```python
def similar_elements(test_tup1, test_tup2):
    res = tuple(set(test_tup1) & set(test_tup2))
    return (res)
```

You are an expert Python programmer, and here is your task:
Write a python function to identify non-prime numbers.
Your code should pass these tests:
assert is_not_prime(2) == False
assert is_not_prime(10) == True
assert is_not_prime(35) == True

```python
import math
def is_not_prime(n):
    result = False
    for i in range(2,int(math.sqrt(n)) + 1):
        if n % i == 0:
            result = True
    return result
```
You are an expert Python programmer, and here is your task:
{prompt_prefix}
Your code should pass these tests:
{test_str}
'''
            # base 模型不需要添加 HUMAN_ROLE_START_TAG 跟 BOT_TAG
            prompt_list.append(f"Complete the following {lang.lower()} code:\n{prompt}")
        return prompt_list
