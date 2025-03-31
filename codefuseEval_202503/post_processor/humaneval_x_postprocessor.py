# -*- coding: utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re


class HumanevalXPostProcessor(BasePostProcessor):
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
        generation = generation if "</s>" not in generation else generation.split("</s>")[0]
        generation = generation if "votes\n" not in generation else generation.split("votes\n")[0]
        print("generation:{}".format(generation))
        print("=" * 200)
        print("generation_ori:{}".format(data.get("generation_ori", "")))
        code = None
        if language.lower() == "cpp":
            code = self.__deal_humaneval_cpp(generation)
        elif language.lower() == "java":
            code = self.__deal_humaneval_java(generation)
        elif language.lower() == "go":
            code = self.__deal_humaneval_go(generation)
        elif language.lower() == "python":
            code = self.__deal_humaneval_python(generation)
        elif language.lower() == "rust":
            code = self.__deal_humaneval_rust(generation)
        elif language.lower() == "js" or language.lower() == "javascript":
            code = self.__deal_humaneval_js(generation)
        elif code is None:
            code = self.__deal_humaneval_code(generation)
        data["generation"] = code if code is not None else generation
        return data

    @classmethod
    def __deal_humaneval_cpp(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 cpp 的 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 返回可以直接运行的 cpp 代码
        """
        pattern = r'```cpp\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            return code
        return None

    @classmethod
    def __deal_humaneval_go(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 go 的代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 go 代码
        """
        pattern = r'```go\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            return code
        return None

    @classmethod
    def __deal_humaneval_python(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 python 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 python 代码
        """
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            code = re.split(r'# Example ', code, maxsplit=1)[0]
            code = re.split(r'if __name__ == ', code, maxsplit=1)[0]
            code = re.split(r'# Test cases\nprint', code, maxsplit=1)[0]
            return code
        return None

    @classmethod
    def __deal_humaneval_rust(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 rust 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 rust 代码
        """
        pattern = r'```rust\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            single_line_comment = re.compile(r'//.*')
            multi_line_comment = re.compile(r'/\*.*?\*/', re.DOTALL)
            code = multi_line_comment.sub('', code)
            code = single_line_comment.sub('', code)
            code = code.strip('\n')
            return code
        return None

    @classmethod
    def __deal_humaneval_js(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 js 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 js 代码
        """
        pattern = r'```js\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        code = None
        if len(matches) > 0:
            code = matches[0]
            single_line_comment = re.compile(r'//.*')
            multi_line_comment = re.compile(r'/\*.*?\*/', re.DOTALL)
            code = multi_line_comment.sub('', code)
            code = single_line_comment.sub('', code)
            code = code.strip('\n')
        if code is None:
            pattern = r'```javascript\n(.*?)```'
            matches = re.findall(pattern, generation, re.DOTALL)
            if len(matches) > 0:
                code = matches[0]
                single_line_comment = re.compile(r'//.*')
                multi_line_comment = re.compile(r'/\*.*?\*/', re.DOTALL)
                code = multi_line_comment.sub('', code)
                code = single_line_comment.sub('', code)
                code = code.strip('\n')
        return code

    @classmethod
    def __deal_humaneval_javascript(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 js 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 js 代码
        """
        pattern = r'```javascript\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            single_line_comment = re.compile(r'//.*')
            multi_line_comment = re.compile(r'/\*.*?\*/', re.DOTALL)
            code = multi_line_comment.sub('', code)
            code = single_line_comment.sub('', code)
            code = code.strip('\n')
            return code
        return None

    @classmethod
    def __deal_humaneval_java(cls, generation: str) -> str or bool:
        """
        后置化处理，得到 java 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 java 代码
        """
        pattern = r'```java\n(.*?)```'
        matches = re.findall(pattern, generation, re.DOTALL)
        if len(matches) > 0:
            code = matches[0]
            return code
        return None

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
