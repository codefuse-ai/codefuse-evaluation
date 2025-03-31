# -*- coding: utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re


class MbppDeepSeekBasePostProcessor(BasePostProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.IMPORT_HELPER = {
            "python": [
                "import math",
                "import unittest",
                "import re",
                "import sys",
                "import copy",
                "import datetime",
                "import itertools",
                "import collections",
                "import heapq",
                "import statistics",
                "import functools",
                "import hashlib",
                "import numpy",
                "import numpy as np",
                "import string",
                "from typing import *",
                "from collections import *",
            ],
            "cpp": [
                "#include<stdlib.h>",
                "#include<algorithm>",
                "#include<math.h>",
                "#include<stdio.h>",
                "#include<vector>",
                "#include<string>",
                "#include<climits>",
                "#include<cstring>",
                "#include<iostream>",
                "#include <stdexcept>",
            ],
            "java": [
                "import java.io.*;",
                "import java.lang.*;",
                "import java.util.*;",
                "import java.math.*;",
            ]
        }

    def post_process(self, data: Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        """
        后置处理
        @param data: 生成的结果 jsonl 文件里面的单个对象，{"task_id":"Rust/3","prompt":"****","generation":"xxx"...}
        @param language: 代码语言
        @param task_mode:
        @param dataset_name:
        @param kwargs:
        @return: 将处理完成后的 generation 替换之前的 generation，返回的仍是单个的 json 对象
        """
        generation = str(data["generation"])
        print("generation:{}".format(generation))
        print("=" * 200)
        print("generation_ori:{}".format(data.get("generation_ori", "")))
        if language.lower() == "python":
            code = self.__deal_humaneval_python(generation)
        else:
            code = self.__deal_humaneval_code(generation)
        data["generation"] = code if code is not None else generation

        return data

    @classmethod
    def __deal_humaneval_python(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 python 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 python 代码
        """
        generation = generation.split("\nUser:")[0] if "\nUser:" in generation else generation
        lines = generation.split("\n")
        lines = lines[1:] if "# language: python" in lines[0] else lines  # 去掉第一个注释，方便后面截断字符
        index = 0
        for index in range(len(lines)):  # 去掉模型回答代码前面可能存在的描述性信息
            if "import" in lines[index] or "def " in lines[index] or "```" in lines[index]:
                break
            else:
                index += 1
                continue
        generation = "\n".join(lines[index:])
        generation = generation.split("\n# language: python\n")[0] if "\n# language: python\n" in generation else generation
        generation = generation.split("\nThis function")[0] if "\nThis function" in generation else generation
        lines = generation.split("\n")
        new_lines = []
        for line in lines[::-1]:  # 从后往前，去掉 print，去掉 print 可能的结果，去掉 ```
            if line.strip().startswith("print"):
                continue
            elif line.strip().startswith("```"):
                continue
            elif not line:
                continue
            else:
                new_lines.append(line)
        generation = "\n".join(new_lines[::-1])
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            code = re.split(r'# Example ', code, maxsplit=1)[0]
            code = re.split(r'if __name__ == ', code, maxsplit=1)[0]
            code = re.split(r'# Test cases\nprint', code, maxsplit=1)[0]
            return code

        pattern = r'```\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            return code
        generation = generation.lstrip("\n")
        generation = generation.split("```python\n")[0] if "```python\n" in generation else generation
        generation = generation.split("\n```")[0] if "\n```" in generation else generation
        generation = generation.split("\n# Test the function\n")[0] if "\n# Test the function\n" in generation else generation
        generation = generation.split("\nExplanation:\n")[0] if "\nExplanation:\n" in generation else generation
        generation = generation.split("\n# Test cases")[0] if "\n# Test cases" in generation else generation
        generation = generation.split("\nThis code")[0] if "\nThis code" in generation else generation
        generation = generation.split("\nIn this code")[0] if "\nIn this code" in generation else generation
        generation = generation.split("\nI hope this")[0] if "\nI hope this" in generation else generation
        generation = generation.split("\nassert")[0] if "\nassert" in generation else generation
        generation = generation.split("\nOutput:")[0] if "\nOutput:" in generation else generation
        generation = generation if generation.startswith("\n") else "\n" + generation
        return generation.rstrip() if generation.startswith("\n") else "\n" + generation.rstrip()

    @classmethod
    def __deal_humaneval_code(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 java 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 java 代码
        """
        pattern = r'```\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            return code
        return None
