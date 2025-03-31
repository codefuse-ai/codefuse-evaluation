# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re


class MbppOpenCoderBasePostProcessor(BasePostProcessor):
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
        generation = data["generation"]
        print("generation:{}".format(generation))
        print("=" * 200)
        print("generation_ori:{}".format(data.get("generation_ori", "")))
        code = self.__deal_humaneval_python(generation, data)
        data["generation"] = code if code is not None else generation
        return data

    @classmethod
    def __deal_humaneval_python(cls, generation: str, data: dict) -> str or bool:
        """
        后置化处理，得到 python 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 python 代码
        """
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        code = ""
        if len(matches) > 0:
            code = matches[0]
            code = re.split(r'# Example ', code, maxsplit=1)[0]
            code = re.split(r'if __name__ == ', code, maxsplit=1)[0]
            code = re.split(r'# Test cases\nprint', code, maxsplit=1)[0]

        if not code:
            pattern = r'```\n(.*?)```'
            matches = re.findall(pattern, generation, re.DOTALL)
            if len(matches) > 0:
                code = matches[0]
        if code:
            code = data.get("prompt") + code if "def" not in code else code
        else:
            code = generation
        code = code if "Your code should pass these tests:" not in code else code.split("Your code should pass these tests:")[0]
        code = code.lstrip("\n")
        assert_str = data.get("test")[0]
        target_func = ""
        pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        matches = re.findall(pattern, assert_str)
        for match in matches:
            if match not in ["set", "list", "assert"]:  # 排除内置方法
                # print("提取的函数名称:", match)
                target_func = match
                break
        code = code.rstrip() if code.startswith("\n") else "\n" + code.rstrip()
        if target_func in code:
            return code
        else:
            lines = code.split("\n")
            generation_func = ""
            for line in lines:
                if "def" in line:
                    generation_func = str(line).split("(")[0].replace("def", "").strip()
                    break
            return code.replace(generation_func, target_func) if generation_func else code
