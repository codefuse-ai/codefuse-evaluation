# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re


class HumanevalFixPreProcessor(BasePostProcessor):
    def __init__(self,**kwargs):
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

    def post_process(self, data:Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        generation = data["generation"]
        if language.lower()=="cpp":
            generation = self.__deal_humanevalifx_cpp(generation,data)

        elif language.lower()=="java":
            generation = self.__deal_humanevalifx_java(generation,data)

        elif language.lower()=="go":
            generation = self.__deal_humanevalifx_go(generation,data)

        elif language.lower()=="python":
            generation = self.__deal_humanevalifx_python(generation,data)

        elif language.lower()=="rust":
            data["prompt"] = data["prompt"][data["prompt"].index("\n")+1:]
            generation = self.__deal_humanevalifx_rust(generation,data)

        elif language.lower()=="js" or language.lower()=="javascript":
            generation = self.__deal_humanevalifx_js(generation,data)
        else:
            generation = data["generation"]
        data["generation"] = generation
        return data

    def extract_code_from_text(self,text, prompt):
        function = prompt.strip().split("\n")[-1].split("(")[0]
        if "```" in text:
            if text.count("```") == 1:
                lines = text.split("```")
                if lines[1]:
                    code = lines[1]
                else:
                    code = lines[0]
            else:
                pattern = r"```(.*?)```"
                matches = re.findall(pattern, text, re.S)
                if matches:
                    if len(matches) > 1:
                        find_match = [match for match in matches if function in match]
                        if find_match:
                            code = find_match[0]
                        else:
                            code = matches[0]
                    else:
                        code = matches[0]
        else:
            code = text

        return code

    def __deal_humanevalifx_cpp(self,generation,data):
        code = self.extract_code_from_text(generation, data["prompt"])
        function = data["prompt"].strip().split("\n")[-1].split("(")[0].replace(" ","")+"("
        if code.startswith(("cpp", "c++")):
            code = code[4:]
        elif code.startswith("c"):
            code = code[2:]
        code_lines = code.split("\n")
        new_lines = []
        start_append = False
        for line in code_lines:
            if "issame" in line:
                break
            if "main(" in line:
                break
            if function in line.replace(" ",""):
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

    def __deal_humanevalifx_go(self,generation,data):
        code = self.extract_code_from_text(generation, data["prompt"])
        function = data["prompt"].strip().split("\n")[-1].split("(")[0]
        if code.startswith("go"):
            code = code[3:]
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

    def __deal_humanevalifx_python(self,generation,data):
        code = self.extract_code_from_text(generation, data["prompt"])
        function = [line for line in data["prompt"].split("\n") if line.startswith("def")][-1].split("(")[0].split(" ")[
            1]
        if code.startswith("python"):
            code = code[7:]
        new_code_lines = []
        code_lines = code.split("\n")
        for line in code_lines:
            if f"check({function})" in line:
                break
            if line.startswith(("from", "import")):
                continue
            if line.startswith(f"def {function}"):
                continue
            if not line:
                continue
            new_code_lines.append(line)
        new_code = "\n".join(new_code_lines)
        print(new_code)
        return new_code

    def __deal_humanevalifx_rust(self,generation,data):
        code = self.extract_code_from_text(generation, data["prompt"])
        function = data["prompt"].strip().split("\n")[-1].split("(")[0]
        if code.startswith("rust"):
            code = code[5:]
        code = code.split("#[cfg(test)]")[0]
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

    def __deal_humanevalifx_js(self,generation,data):
        code = self.extract_code_from_text(generation, data["prompt"])
        function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip()
        if "=" in function:
            function = function.split("=")[0].strip()
        function_name = function.split(" ")[1]
        if code.startswith("javascript"):
            code = code[11:]
        if code.startswith("js"):
            code = code[3:]
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

    def __deal_humanevalifx_java(self,generation,data):
        code = self.extract_code_from_text(generation, data["prompt"])
        function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip()
        if code.startswith("java"):
            code = code[5:]
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
        print(new_code)
        return new_code