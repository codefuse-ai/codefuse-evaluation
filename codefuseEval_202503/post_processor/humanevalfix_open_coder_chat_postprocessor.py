# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re


class HumanevalFixOpenCoderChatPostProcessor(BasePostProcessor):
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
        if language.lower() == "cpp":
            generation = self.__deal_humanevalifx_cpp(data)

        elif language.lower() == "java":
            generation = self.__deal_humanevalifx_java(data)

        elif language.lower() == "go":
            generation = self.__deal_humanevalifx_go(data)

        elif language.lower() == "python":
            generation = self.__deal_humanevalifx_python(data)

        elif language.lower() == "rust":
            data["prompt"] = data["prompt"][data["prompt"].index("\n") + 1:]
            generation = self.__deal_humanevalifx_rust(data)

        elif language.lower() == "js" or language.lower() == "javascript":
            generation = self.__deal_humanevalifx_js(data)
        else:
            generation = data["generation"]
        data["generation"] = generation
        return data

    def __deal_humanevalifx_cpp(self, data):
        code = data.get("generation", "")
        code = code if "\nvotes\n" not in code else code.split("\nvotes\n")[0]
        code = code if "\nvote\n" not in code else code.split("\nvote\n")[0]
        code = code if "\na\n" not in code else code.split("\na\n")[0]
        code = code if "\n:)\n" not in code else code.split("\n:)\n")[0]
        code = code if "\ned\n" not in code else code.split("\ned\n")[0]
        code = code if "\ns\n" not in code else code.split("\ns\n")[0]
        code = code if "\ncode\n" not in code else code.split("\ncode\n")[0]
        code = code if "\n:fix\n" not in code else code.split("\n:fix\n")[0]
        code = code if "\n��\n" not in code else code.split("\n��\n")[0]
        code = code if "\n�\n" not in code else code.split("\n�\n")[0]
        code = code if "\n:wq\n" not in code else code.split("\n:wq\n")[0]
        code = code if "The correct sum for the fourth vector is 12, not 12.\n't\nuser" not in code else code.split("The correct sum for the fourth vector is 12, not 12.\n't\nuser")[1]
        code = code if "\nuser\n" not in code else code.split("\nuser\n")[0]
        code = code if "\nusername_0\n" not in code else code.split("\nusername_0\n")[0]
        code = code if "\n't need to fix anything." not in code else code.split("\n't need to fix anything.")[0]
        code = code if "\n't need to fix anything here." not in code else code.split("\n't need to fix anything here.")[0]
        code = code if "\n: Fix bugs" not in code else code.split("\n: Fix bugs")[0]
        code = code if "\n: No bugs to fix." not in code else code.split("\n: No bugs to fix.")[0]
        code = code if "\n```cpp" not in code else code.split("\n```cpp")[1].split("```\n")[0]
        code = code if "\n```c++" not in code else code.split("\n```c++")[1].split("```\n")[0]
        code = code if "\n```c" not in code else code.split("\n```c")[1].split("```\n")[0]
        code = code if "\n:::cpp" not in code else code.split("\n:::cpp")[1].split(":::\n")[0]
        code = code if "\n::cpp" not in code else code.split("\n::cpp")[1].split("\n:")[0]
        code = code if "\n:::\n" not in code else code.split("\n:::\n")[1].split("\n:")[0]
        code = code if "\n```\n" not in code else code.split("\n```\n")[1].split("\n:")[0]
        function, common = "", False
        for item in data.get("prompt", "").strip().split("\n")[::-1]:
            if item.strip().startswith("*/"):
                common = True
                continue
            if item.strip().startswith("/*"):
                common = False
                continue
            if "/*" in item and "*/" in item or item.strip().startswith("//"):
                continue
            if not common and "(" in item and " " in item:
                function = item.replace("long long", "long").strip().split("(")[0].split(" ")[1] + "("
                break
        code = code[4:] if code.startswith(tuple(["cpp", "c++"])) else code
        code = code[2:] if code.startswith("c") else code
        code_lines = code.split("\n")
        new_lines = []
        start_append = False
        for line in code_lines:
            if "issame" in line:
                break
            if "main(" in line:
                break
            if function in line.replace(" ", ""):
                start_append = True
                continue
            if line.startswith(("#include", "using", "#undef")):
                continue
            if start_append:
                new_lines.append(line)
            new_code = "\n".join(new_lines)
            if new_code.count("}") - new_code.count("{") == 1:
                break
        new_code = "\n".join(new_lines)
        print(new_code)
        return new_code

    def __deal_humanevalifx_go(self, data):
        code = data.get("generation", "")
        code = code if "\nvotes\n" not in code else code.split("\nvotes\n")[0]
        code = code if "\nvote\n" not in code else code.split("\nvote\n")[0]
        code = code if "\na\n" not in code else code.split("\na\n")[0]
        code = code if "\n:)\n" not in code else code.split("\n:)\n")[0]
        code = code if "\ned\n" not in code else code.split("\ned\n")[0]
        code = code if "\ns\n" not in code else code.split("\ns\n")[0]
        code = code if "\ncode\n" not in code else code.split("\ncode\n")[0]
        code = code if "\n:fix\n" not in code else code.split("\n:fix\n")[0]
        code = code if "\n��\n" not in code else code.split("\n��\n")[0]
        code = code if "\n�\n" not in code else code.split("\n�\n")[0]
        code = code if "\n:wq\n" not in code else code.split("\n:wq\n")[0]
        code = code if "\nuser\n" not in code else code.split("\nuser\n")[0]
        code = code if "\nusername_0\n" not in code else code.split("\nusername_0\n")[0]
        code = code if "\n't need to fix anything." not in code else code.split("\n't need to fix anything.")[0]
        code = code if "\n't need to fix anything here." not in code else code.split("\n't need to fix anything here.")[0]
        code = code if "\n: Fix bugs" not in code else code.split("\n: Fix bugs")[0]
        code = code if "\n: No bugs to fix." not in code else code.split("\n: No bugs to fix.")[0]
        code = code if "\n```go" not in code else code.split("\n```go")[1].split("```\n")[0]
        code = code if "\n:::go" not in code else code.split("\n:::go")[1].split(":::\n")[0]
        code = code if "\n::go" not in code else code.split("\n::go")[1].split("\n:")[0]
        code = code if "\n:::\n" not in code else code.split("\n:::\n")[1].split("\n:")[0]
        code = code if "\n```\n" not in code else code.split("\n```\n")[1].split("\n:")[0]
        function = data["prompt"].strip().split("\n")[-1].split("(")[0]
        code = code[3:] if code.startswith("go") else code
        new_code_lines = []
        code_lines = code.split("\n")
        area_continue = False
        for line in code_lines:
            if area_continue:
                if line.count(")") - line.count("(") == 1:
                    area_continue = False
                    continue
                else:
                    continue
            if function in line:
                continue
            if line.startswith("package"):
                continue
            if line.startswith("import"):
                if "(" in line and ")" not in line:
                    area_continue = True
                    continue
                else:
                    continue
            if line.startswith("//"):
                continue
            if not line.strip():
                continue
            if "func main(" in line:
                break
            if "*testing.T)" in line:
                break
            new_code_lines.append(line)
        new_code = "\n".join(new_code_lines)
        print(new_code)
        return new_code

    def __deal_humanevalifx_python(self, data):
        code = data.get("generation", "")
        code = code if "\nvotes\n" not in code else code.split("\nvotes\n")[0]
        code = code if "\nvote\n" not in code else code.split("\nvote\n")[0]
        code = code if "\na\n" not in code else code.split("\na\n")[0]
        code = code if "\n:)\n" not in code else code.split("\n:)\n")[0]
        code = code if "\ned\n" not in code else code.split("\ned\n")[0]
        code = code if "\ncode\n" not in code else code.split("\ncode\n")[0]
        code = code if "\n```python" not in code else code.split("\n```python")[1].split("```\n")[0]
        code = code if "\n:::python" not in code else code.split("\n:::python")[1].split(":::\n")[0]
        code = code if "\n::python" not in code else code.split("\n::python")[1].split("\n:")[0]
        code = code if "\n```\n" not in code else code.split("\n```\n")[1].split("\n:")[0]
        code = code if "\n'test cases passed'\n" not in code else code.split("\n'test cases passed'\n")[1].split("\n:")[0]
        function = [line for line in data["prompt"].split("\n") if line.startswith("def")][-1].split("(")[0].split(" ")[1]
        code = code[7:] if code.startswith("python") else code
        new_code_lines = []
        code_lines = code.split("\n")
        for line in code_lines:
            if f"check({function})" in line:
                break
            if line.startswith(("from", "import")) or not line:
                continue
            if line.startswith(f"def {function}"):
                continue
            if not line:
                continue
            new_code_lines.append(line)
        new_code = "\n".join(new_code_lines)
        print(new_code)
        return new_code

    def __deal_humanevalifx_rust(self, data):
        code = data.get("generation", "")
        code = code if "\nvotes\n" not in code else code.split("\nvotes\n")[0]
        code = code if "\nvote\n" not in code else code.split("\nvote\n")[0]
        code = code if "\na\n" not in code else code.split("\na\n")[0]
        code = code if "\n:)\n" not in code else code.split("\n:)\n")[0]
        code = code if "\ned\n" not in code else code.split("\ned\n")[0]
        code = code if "\ns\n" not in code else code.split("\ns\n")[0]
        code = code if "\ncode\n" not in code else code.split("\ncode\n")[0]
        code = code if "\n:fix\n" not in code else code.split("\n:fix\n")[0]
        code = code if "\n��\n" not in code else code.split("\n��\n")[0]
        code = code if "\n�\n" not in code else code.split("\n�\n")[0]
        code = code if "\n:wq\n" not in code else code.split("\n:wq\n")[0]
        code = code if "The correct sum for the fourth vector is 12, not 12.\n't\nuser" not in code else code.split("The correct sum for the fourth vector is 12, not 12.\n't\nuser")[1]
        code = code if "\nuser\n" not in code else code.split("\nuser\n")[0]
        code = code if "\n'test\n" not in code else code.split("\n'test\n")[0]
        code = code if "\nusername_0\n" not in code else code.split("\nusername_0\n")[0]
        code = code if "\n't need to fix anything." not in code else code.split("\n't need to fix anything.")[0]
        code = code if "\n't need to fix anything here." not in code else code.split("\n't need to fix anything here.")[0]
        code = code if "\n: Fix bugs" not in code else code.split("\n: Fix bugs")[0]
        code = code if "\n: No bugs to fix." not in code else code.split("\n: No bugs to fix.")[0]
        code = code if "\n```rust" not in code else code.split("\n```rust")[1].split("```\n")[0]
        code = code if "\n```rust" not in code else code.split("\n```rust")[1].split("```\n")[0]
        code = code if "\n:::rust" not in code else code.split("\n:::rust")[1].split(":::\n")[0]
        code = code if "\n::rust" not in code else code.split("\n::rust")[1].split("\n:")[0]
        code = code if "\n:::\n" not in code else code.split("\n:::\n")[1].split("\n:")[0]
        code = code if "\n```\n" not in code else code.split("\n```\n")[1].split("\n:")[0]
        function = data["prompt"].strip().split("\n")[-1].split("(")[0]
        code = code[5:] if code.startswith("rust") else code
        code = code if "\n#[cfg(test)]" not in code else code.split("\n#[cfg(test)]")[0]
        code_lines = code.split("\n")
        new_codelines = []
        area_continue = False
        for line in code_lines:
            if area_continue:
                if line.count("{") == line.count("}"):
                    continue
                elif line.count("}") - line.count("{") == 1:
                    area_continue = False
                    continue
                else:
                    continue
            if function in line:
                continue
            if line.startswith("use "):
                continue
            if "fn main()" in line:
                if "{" in line and "}" in line:
                    continue
                if "{" in line:
                    area_continue = True
                    continue
            new_codelines.append(line)
        new_code = "\n".join(new_codelines)
        print(new_code)
        return new_code

    def __deal_humanevalifx_js(self, data):
        code = data.get("generation", "")
        code = code if "\nvotes\n" not in code else code.split("\nvotes\n")[0]
        code = code if "\nvote\n" not in code else code.split("\nvote\n")[0]
        code = code if "\na\n" not in code else code.split("\na\n")[0]
        code = code if "\n:)\n" not in code else code.split("\n:)\n")[0]
        code = code if "\ned\n" not in code else code.split("\ned\n")[0]
        code = code if "\ns\n" not in code else code.split("\ns\n")[0]
        code = code if "\ncode\n" not in code else code.split("\ncode\n")[0]
        code = code if "\n```javascript" not in code else code.split("\n```javascript")[1].split("```\n")[0]
        code = code if "\n:::javascript" not in code else code.split("\n:::javascript")[1].split(":::\n")[0]
        code = code if "\n::javascript" not in code else code.split("\n::javascript")[1].split("\n:")[0]
        code = code if "\n```\n" not in code else code.split("\n```\n")[1].split("\n:")[0]
        function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip()
        function = function.split("=")[0].strip() if "=" in function else function
        function_name = function.split(" ")[1]
        code = code[11:] if code.startswith("javascript") else code
        code = code[3:] if code.startswith("js") else code
        new_lines = []
        code_lines = code.split("\n")
        for line in code_lines:
            if f"test{function_name.lower()}" in line.lower():
                break
            if function in line:
                continue
            if "console.log" in line:
                continue
            new_lines.append(line)
        new_code = "\n".join(new_lines)
        print(new_code)
        return new_code

    def __deal_humanevalifx_java(self, data):
        code = data.get("generation", "")
        code = code if "\nvotes\n" not in code else code.split("\nvotes\n")[0]
        code = code if "\nvote\n" not in code else code.split("\nvote\n")[0]
        code = code if "\na\n" not in code else code.split("\na\n")[0]
        code = code if "\n:)\n" not in code else code.split("\n:)\n")[0]
        code = code if "\ned\n" not in code else code.split("\ned\n")[0]
        code = code if "\ns\n" not in code else code.split("\ns\n")[0]
        code = code if "\ncode\n" not in code else code.split("\ncode\n")[0]
        code = code if "\n't need to fix anything." not in code else code.split("\n't need to fix anything.")[0]
        code = code if "\n't need to fix anything here." not in code else code.split("\n't need to fix anything here.")[0]
        code = code if "\n```java" not in code else code.split("\n```java")[1].split("```\n")[0]
        code = code if "\n:::java" not in code else code.split("\n:::java")[1].split(":::\n")[0]
        code = code if "\n::java" not in code else code.split("\n::java")[1].split("\n:")[0]
        code = code if "\n:::\n" not in code else code.split("\n:::\n")[1].split("\n:")[0]
        code = code if "\n```\n" not in code else code.split("\n```\n")[1].split("\n:")[0]
        function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip()
        code = code[5:] if code.startswith("java") else code
        new_code_lines = []
        code_lines = code.split("\n")
        for line in code_lines:
            if "main(" in line:
                break
            if line.startswith(("import", "class", "public class")):
                continue
            if line.lstrip().startswith(function):
                continue
            new_code_lines.append(line)
        new_code = "\n".join(new_code_lines)
        if new_code.count("}") - new_code.count("{") < 2:
            new_code += "\n".join(["}"] * (new_code.count("}") - new_code.count("{")))
        print(data.get("task_id") + ": " + new_code)
        return new_code
