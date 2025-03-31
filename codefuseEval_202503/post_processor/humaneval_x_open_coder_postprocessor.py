# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re


class HumanevalXOpenCoderPostProcessor(BasePostProcessor):
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
        generation = generation if "user_0\n" not in generation else generation.split("user_0\n")[0]
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
            code = self.__deal_humaneval_python(generation, data)
        elif language.lower() == "rust":
            code = self.__deal_humaneval_rust(generation)
        elif language.lower() == "js" or language.lower() == "javascript":
            code = self.__deal_humaneval_js(generation)
        code = self.__deal_humaneval_code(generation) if code is None else code
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
    def __deal_humaneval_python(cls, generation: str, data: dict) -> str or bool:
        """
        后置化处理，得到 python 代码
        @param generation: 模型生成的答案，做后置处理
        @return: 可以直接运行的 python 代码
        """
        generation = generation.split("[DONE]")[0] if "[DONE]" in generation else generation
        generation = generation.split("[BEGIN]\n")[1] if "[BEGIN]\n" in generation else generation
        generation = generation.split("<|file_sep|>")[0] if "<|file_sep|>" in generation else generation
        generation = generation.split("<|fim_middle|>")[0] if "<|fim_middle|>" in generation else generation
        if (generation.startswith(' \'') and generation.endswith('\' \n')) or (
                generation.startswith(' \"') and generation.endswith('\" \n')):
            generation = "\n" + generation[2: -3] + "\n"
        generation = generation.split("\n:::\n")[0].rstrip("\n") if "\n:::\n" in generation else generation.rstrip("\n")
        generation = generation if "# Test cases" not in generation else generation.split("# Test cases")[0]
        generation = generation if "\nusername_0" not in generation else generation.split("\nusername_0")[0]
        generation = generation if "\nuser\n" not in generation else generation.split("\nuser\n")[0]
        generation = generation if "\n# test\n" not in generation else generation.split("\n# test\n")[0]
        generation = generation if "\n assistant\n" not in generation else generation.split("\n assistant\n")[0]
        generation = generation if "\ncode\ncode" not in generation else generation.split("\ncode\ncode")[0]
        generation = generation if "\n# test the function\n" not in generation else generation.split("\n# test the function\n")[0]
        generation = generation if "\n>>>" not in generation else generation.split("\n>>>")[0]
        generation = generation if "\nverifier\n" not in generation else generation.split("\nverifier\n")[0]
        generation = generation if "\n�" not in generation else generation.split("\n�")[0]
        generation = generation if "```\n```\n" not in generation else generation.split("```\n```\n")[0]
        generation = generation if "\n::" not in generation else generation.split("\n::")[0]
        generation = generation if "\n:" not in generation else generation.split("\n:")[0]
        generation = generation if "\n This code works by iterating through " not in generation else \
        generation.split("\n This code works by iterating through ")[0]
        generation = generation.split("\nAssistant: #")[0] if "\nAssistant: #" in generation else generation
        generation = generation.split("\nAssistant:\n")[0] if "\nAssistant:\n" in generation else generation
        generation = generation.split("\nStudent: #")[0] if "\nStudent: #" in generation else generation
        generation = generation.split('if __name__ ==')[0] if 'if __name__ ==' in generation else generation
        lines = generation.split("\n")
        lines = lines[1:] if "# language: python" in lines[0] else lines  # 去掉第一个注释，方便后面截断字符
        new_lines = []
        for line in lines[::-1]:    # 从后往前，去掉 print，去掉 print 可能的结果（局限于1跟-1开头的）去掉 ```
            if line.strip().startswith("print") or line.strip().startswith("1") or line.strip().startswith("-1"):
                continue
            elif line.strip().startswith("```"):
                continue
            elif not line:
                continue
            else:
                new_lines.append(line)
        generation = "\n".join(new_lines[::-1])
        generation = generation.split("\n# language: python\n")[0] if "\n# language: python\n" in generation else generation
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

        generation = data.get("prompt") + generation if "def" not in generation else generation
        generation = generation.lstrip("\n")
        return generation.rstrip() if generation.startswith("\n") else "\n" + generation.rstrip()

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
