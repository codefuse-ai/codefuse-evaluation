# -*- coding: utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
import re
from .base import BasePostProcessor
from typing import Dict


class MultieOpenCoderBasePostProcessor(BasePostProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.IMPORT_HELPER = {
            "python": [
                "import math",
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
            "go": [
                "math",
                "strings",
                "fmt",
                "strconv",
                "time",
                "bytes",
                "regexp",
                "sort",
                "unicode",
                "math/rand",
                "crypto/md5",
                "testing"
            ],
            "cpp": [
                "using namespace std;",
                "#include<cassert>",
                "#include<stdlib.h>",
                "#include<algorithm>",
                "#include<cmath>",
                "#include<math.h>",
                "#include<numeric>",
                "#include<stdio.h>",
                "#include<vector>",
                "#include<set>",
                "#include<map>",
                "#include<queue>",
                "#include<stack>",
                "#include<list>",
                "#include<deque>",
                "#include<boost/any.hpp>",
                "#include<string>",
                "#include<climits>",
                "#include<cstring>",
                "#include<iostream>",
                "#include<sstream>",
                "#include<fstream>",
            ],
            "java": [
                "import java.util.*;",
                "import java.lang.reflect.*;",
                "import org.javatuples.*;",
                "import java.security.*;",
                "import java.math.*;",
                "import java.io.*;",
                "import java.util.stream.*;",
            ],
            "cs": [
                "using System;",
                "using System.Numerics;",
                "using System.Diagnostics;",
                "using System.Collections.Generic;",
                "using System.Linq;",
                "using System.Text;",
                "using System.Security.Cryptography;",
                "using System.Collections.Generic;",
            ],
        }

    def post_process(self, data: Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        """
        此时的data要求对prompt不能存在任何处理，此时提取数据集的最后一行,提取函数指令
        """
        text = data["generation"]
        text = text if "</s>" not in text else text.split("</s>")[0]
        text = text if "votes\n" not in text else text.split("votes\n")[0]
        text = text if "user_0\n" not in text else text.split("user_0\n")[0]
        text = text if "\nuser\n" not in text else text.split("\nuser\n")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text if "user\n// Test cases\n" not in text else text.split("user\n// Test cases\n")[0]
        text = text if "// Test cases\n" not in text else text.split("// Test cases\n")[0]
        text = text if "\nbin/bash\n" not in text else text.split("\nbin/bash\n")[0]
        text = text if "\nphp\n" not in text else text.split("\nphp\n")[0]
        text = text if "\ncode\ncode\n" not in text else text.split("\ncode\ncode\n")[0]
        text = text if "}\n// Write a" not in text else text.split("}\n// Write a")[0] + "}\n"
        text = text if "}\n# Write a" not in text else text.split("}\n# Write a")[0] + "}\n"
        text = text if "}\n//Write" not in text else text.split("}\n//Write")[0] + "}\n"
        if language.lower() == "cpp":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "python":
            function = [line for line in data["prompt"].strip().split("\n") if line.startswith("def ")][0].split("(")[
                           0].strip().split(" ")[-1] + "("
        if language.lower() == "java":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "php":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "js" or language.lower() == "javascript":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "ts" or language.lower() == "typescript":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "cs" or language.lower() == "csharp":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "sh" or language.lower() == "shell":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "go":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("
        if language.lower() == "rust":
            function = data["prompt"].strip().split("\n")[-1].split("(")[0].strip().split(" ")[-1] + "("

        if text:
            if "```" in text:
                # 兼容逻辑，主要是完成多个markdown的提取情况
                if text.count("```") >= 2:
                    if text.count("```") % 2 != 0:
                        text_blocks = [block for block in text.split("```")]
                        if text_blocks:
                            choose_blocks_list = [block for block in text_blocks if function in block]
                            if choose_blocks_list:
                                text = choose_blocks_list[0]
                            else:
                                text = text_blocks[0]
                        else:
                            text = text
                    else:
                        pattern = r"```(.*?)```"
                        matches = re.findall(pattern, text, re.S)
                        if matches:
                            if len(matches) > 1:
                                find_match = [match for match in matches if function in match]
                                if find_match:
                                    text = find_match[0]
                                else:
                                    text = matches[0]
                            else:
                                text = matches[0]
                else:
                    text_split = text.split("```")
                    text_block = [block for block in text_split if function in block]
                    if text_block:
                        text = text_block[0]
                    else:
                        text = text_split[0]
        else:
            text = ""
        if language.lower() == "cpp":
            new_code, testcode = self.dealcpp(text, data)
        elif language.lower() == "python":
            new_code, testcode = self.dealpython(text, data)
        elif language.lower() == "java":
            new_code, testcode = self.dealjava(text, data)
        elif language.lower() == "php":
            new_code, testcode = self.dealphp(text, data)
        elif language.lower() == "sh" or language.lower() == "shell":
            new_code, testcode = self.dealshell(text, data)
        elif language.lower() == "js" or language.lower() == "javascript":
            new_code, testcode = self.dealjs(text, data)
        elif language.lower() == "ts" or language.lower() == "typescript":
            new_code, testcode = self.dealts(text, data)
        elif language.lower() == "cs" or language.lower() == "csharp":
            new_code, testcode = self.dealcsharp(text, data)
        elif language.lower() == "go":
            new_code, testcode = self.dealgo(text, data)
        elif language.lower() == "rust":
            new_code, testcode = self.dealrust(text, data)
        else:
            new_code, testcode = text, text
        data["code"] = new_code
        data["test_code"] = testcode
        return data

    def dealcpp(self, generation, data):
        text = generation
        if text.startswith("cpp"):
            text = text[4:]
        if text.startswith("c\n"):
            text = text[2:]
            # 设置当前环境需要的包
        prompt = data["prompt"]
        function = prompt.strip().split("\n")[-1].split("(")[0] + "("
        exists_packages = "\n".join(self.IMPORT_HELPER["cpp"])
        generation_packages = []
        lines = text.split("\n")
        new_lines = []
        # 去除测试用例
        change_prompt = data["prompt"]
        for line in lines:
            if not line:
                continue
            if line.startswith(("#include", "using")):
                generation_packages.append(line)
            if line.strip().startswith("//"):
                continue
            if "main()" in line:
                break
            if "issame(" in line:
                break
            new_lines.append(line)
            temp_code = "\n".join(new_lines)
            if temp_code.count("}") - temp_code.count("{") == 1:
                break
        new_code = "\n".join(new_lines)
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        test_code = new_code + "\n" + test

        if test_code.startswith(" "):
            test_code = change_prompt + "\n" + test_code
            new_code = change_prompt + "\n" + new_code
        test_code = "\n".join(generation_packages) + "\n" + exists_packages + "\n" + test_code
        new_code = "\n".join(generation_packages) + "\n" + exists_packages + "\n" + new_code
        return new_code, test_code

    def dealpython(self, generation, data):
        text = generation
        if text.startswith("python"):
            text = text[7:]
        lines = text.split("\n")
        prompt = data["prompt"]
        function = [line for line in prompt.split("\n") if line.startswith("def")][-1].split("(")[0]
        function_declare = [line for line in prompt.split("\n") if line.startswith("def")][-1] + "\n"
        code_packages = []
        new_lines = []
        for line in lines:
            if not line:
                continue
            if "_main_" in line:
                break
            if not line.startswith(("def", "class", "from", "import", " ", "\t")):
                continue
            if "bug_type" in data:
                if f"check({data['entry_point']})" in line:
                    break
            if line.startswith(("from", "import")):
                code_packages.append(line)
                continue
            if line.startswith("def "):
                catch_function_name = line.split("(")[0]
                if catch_function_name in prompt:
                    # 可能是prompt的函数，有可能是预先的函数，如果是预先函数
                    if catch_function_name != function:
                        new_lines.append(line)
                        continue
                    else:
                        new_lines.append("\n" + function_declare)
                        continue
                else:
                    new_lines.append(line)
                    continue
            new_lines.append(line)
        # if new_lines[0].startswith("def"):
        new_code = "\n".join(new_lines).strip()
        if not new_code.startswith("def"):
            new_code = data["prompt"] + "\n" + new_code
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        testcode = new_code + "\n\n" + test
        code_setup = ""
        if code_packages:
            code_setup = "\n".join(code_packages)
        new_code = "\n".join(self.IMPORT_HELPER["python"]) + f"\n{code_setup}\n" + new_code
        testcode = "\n".join(self.IMPORT_HELPER["python"]) + f"\n{code_setup}\n" + testcode
        return new_code, testcode

    def dealjava(self, generation, data):
        text = generation
        if text.startswith("java"):
            text = text[5:]
            # 读取import数据
        prompt = data['prompt'].strip()
        prompt_setpackages = "\n".join([line for line in prompt.split("\n") if line.startswith("import")])
        generation_packages = []
        function = prompt.strip().split("\n")[-1].split("(")[0].strip()
        function_name = function.split(" ")[-1] + "("
        lines = text.split("\n")
        new_lines = []
        # ToDo 需要补充关于提示词是不是存在类声明
        area_block = False
        # 去除单测用例情况
        for line in lines:
            if not line:
                continue
            # 删除注释
            if line.strip().startswith("//"):
                continue
            if area_block:
                if line.strip().startswith("*/"):
                    area_block = False
                    continue
            if line.strip().startswith("/*"):
                area_block = True
                continue
            if line.startswith(("class ", "public class")):
                continue
            if line.startswith("import"):
                generation_packages.append(line)
                continue
            if "main(" in line:
                break
            if line.strip().startswith(
                    ("private static", "public static", "protected static")) and function_name not in line:
                if not any([function_name in exist_line for exist_line in new_lines]):
                    prompt = "\n".join(prompt.split("\n")[:-1])
                    new_lines.append(line)
                    continue
            new_lines.append(line)

        prompt = "\n".join(prompt.strip().split("\n")[:-1])
        if new_lines:
            new_code = "\n".join(new_lines)
            if new_code.count("}") - new_code.count("{") == 1:
                new_code = new_code[:new_code.rfind("}")]
            new_code = prompt.strip() + "\n" + new_code
        else:
            new_code = prompt.strip() + "\n" + ""
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").strip()
        test = test[test.index("\n") + 1:] if test.startswith("}") else test
        if new_code.startswith(" "):
            new_code = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(generation_packages) + "\n" + prompt + new_code
            testcode = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(
                generation_packages) + "\n" + prompt + new_code + "\n" + test
        else:
            new_code = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(
                generation_packages) + "\n" + prompt_setpackages + "\n" + new_code
            testcode = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(
                generation_packages) + "\n" + prompt_setpackages + "\n" + new_code + "\n" + test
        new_code = new_code if new_code.count("{") == new_code.count("}") else new_code + "}\n"
        return new_code, testcode

    def dealphp(self, generation, data):
        def find_last_index(lst, element):
            # Reverse the list and find the first occurrence
            try:
                reverse_index = next(i for i, x in enumerate(reversed(lst)) if x == element)
                # Calculate the actual index from the end of the list
                return len(lst) - 1 - reverse_index
            except StopIteration:
                return 0

        text = generation
        function = data["prompt"].strip().split("\n")[-1].split("(")[0]
        if text.startswith("php"):
            text = text[4:]
        lines = text.split("\n")
        if lines.count("<?php") >= 2:
            index = find_last_index(lines, "<?php")
            lines = lines[index:]
        new_lines = []
        for line in lines:
            temp_code = "\n".join(new_lines)
            if line.startswith("}") and function in temp_code:
                new_lines.append(line)
                break
            new_lines.append(line)
        new_code = "\n".join(new_lines)
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        testcode = new_code + "\n" + test + "\n" + "?>"
        if testcode.startswith(" "):
            testcode = data["prompt"] + testcode
            new_code = data["prompt"] + new_code
        if not testcode.strip().startswith("<?php"):
            testcode = "<?php\n" + testcode
            new_code = "<?php\n" + new_code
        return new_code, testcode

    def dealshell(self, generation, data):
        text = generation
        if text.startswith("bash"):
            text = text[5:]
        if text.startswith("sh"):
            text = text[3:]
        lines = text.split("\n")
        if any(["}" == line for line in lines]):
            index = len(lines) - 1 - lines[::-1].index('}')
            new_lines = lines[:index + 1]
            new_code = "\n".join(new_lines)
        else:
            new_code = text
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        testcode = new_code + "\n" + test
        if testcode.startswith(" "):
            testcode = data['prompt'] + testcode
            new_code = data['prompt'] + new_code
        return new_code, testcode

    def dealjs(self, generation, data):
        text = generation
        if text.startswith(("javascript", "typescript")):
            text = text[11:]
        if text.startswith(("js", "ts")):
            text = text[3:]
        lines = text.split("\n")
        prompt = data["prompt"]
        function_declare = prompt.strip().split("\n")[-1] + "\n"
        function_name = function_declare.split("(")[0].split(" ")[-1]
        new_lines = []
        area_continue = False
        for line in lines:
            if area_continue:
                if line.strip().startswith("*/"):
                    area_continue = False
                    continue
                else:
                    continue
            if "console.log" in line:
                continue
            if line.strip().startswith("/*"):
                area_continue = True
                continue
            if line.startswith(("user", "assistant")):
                break
            if line.strip().startswith("//"):
                continue
            if line.startswith("function"):
                catch_function_name = line.split("(")[0].split(" ")[-1]
                if catch_function_name in prompt:
                    # 可能是prompt的函数，有可能是预先的函数，如果是预先函数
                    if catch_function_name != function_name:
                        new_lines.append(line)
                        continue
                    else:
                        new_lines.append("\n" + function_declare)
                        continue
                else:
                    catch_function_name = catch_function_name.replace("_", "").lower()
                    function_name = function_name.replace("_", "").lower()
                    if catch_function_name == function_name:
                        continue
                    else:
                        new_lines.append(line)
                        continue

            new_lines.append(line)
        new_code = "\n".join(new_lines).strip()

        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        if not new_code.startswith("function"):
            new_code = data["prompt"] + new_code
        testcode = new_code + "\n" + test
        return new_code, testcode

    def dealts(self, generation, data):
        text = generation
        if text.startswith(("javascript", "typescript")):
            text = text[11:]
        if text.startswith(("js", "ts")):
            text = text[3:]
        lines = text.split("\n")
        prompt = data["prompt"]
        function_declare = prompt.strip().split("\n")[-1] + "\n"
        function_name = function_declare.split("(")[0].split(" ")[-1]
        new_lines = []
        area_continue = False
        for line in lines:
            if area_continue:
                if line.strip().startswith("*/"):
                    area_continue = False
                    continue
                else:
                    continue
            if "console.log" in line:
                continue
            if line.strip().startswith("/*"):
                area_continue = True
                continue
            if line.strip().startswith("//"):
                continue
            if line.startswith(("user", "assistant")):
                break
            if "import * as assert from 'assert'" in line:
                break
            if line.startswith("function"):
                catch_function_name = line.split("(")[0].split(" ")[-1]
                if catch_function_name in prompt:
                    # 可能是prompt的函数，有可能是预先的函数，如果是预先函数
                    if catch_function_name != function_name:
                        new_lines.append(line)
                        continue
                    else:
                        new_lines.append("\n" + function_declare)
                        continue
                else:
                    catch_function_name = catch_function_name.replace("_", "").lower()
                    function_name = function_name.replace("_", "").lower()
                    if catch_function_name == function_name:
                        continue
                    else:
                        new_lines.append(line)
                        continue

            new_lines.append(line)
        new_code = "\n".join(new_lines).strip()
        if new_code.startswith("}"):
            new_code = new_code[1:]
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        if not new_code.startswith("function"):
            new_code = data["prompt"] + new_code
        testcode = new_code + "\n" + test
        testcode = testcode.replace("declare var require: any;", '')
        return new_code, testcode

    def dealcsharp(self, generation, data):
        text = generation
        if text.startswith("csharp"):
            text = text[6:]
        if text.startswith(("cs", "C#", "c#", "CS")):
            text = text[3:]
        lines = text.split("\n")
        new_lines = []
        prompt = data["prompt"]
        package_setup = "\n".join([line for line in prompt.split("\n") if line.startswith("using")])
        for line in lines:
            if "Main(" in line:
                break
            if line.startswith("}"):
                break
            if line in new_lines and line.lstrip().startswith("public static"):
                break
            new_lines.append(line)
            temp_code = "\n".join(new_lines)
            if temp_code.count("}") - temp_code.count("{") == 1:
                break
        new_code = "\n".join(new_lines)
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        testcode = new_code + "\n" + test
        if testcode.startswith(" "):
            testcode = data["prompt"] + testcode
        testcode = package_setup + "\n" + testcode
        new_code = package_setup + "\n" + new_code
        return new_code, testcode

    def dealgo(self, generation, data):
        generation = data.get("generation_ori")
        generation = generation if generation else data.get("generation")
        generation = generation.split("```go\n")[1] if "```go\n" in generation else generation
        generation = generation.split("```\n")[0] if "```\n" in generation else generation
        generation = generation.split("Solution:\n")[1] if "Solution:\n" in generation else generation
        generation = generation.split("**Solution:**\n")[1] if "**Solution:**\n" in generation else generation
        generation = generation.split("Here is the complete implementation in Go:\n")[
            1] if "Here is the complete implementation in Go:\n" in generation else generation
        lines = generation.split("\n")
        new_code = []
        flag = False
        import_list = []
        for line in lines:
            if "import" in line and "(" in line and ")" not in line:
                flag = True
                continue
            if "import" in line and "(" in line and ")" in line:
                import_list.append(line.split("(")[1].split(")")[0])
                continue
            if ")" in line and flag:
                flag = False
                continue
            if flag:
                import_list.append(line.strip())
            elif "package" in line:
                continue
            elif "*testing.T" in line or "main() {" in line:
                break
            else:
                new_code.append(line)
        if new_code:
            new_code = new_code if not str(new_code[-1]).startswith("//") else new_code[:-1]
        new_code = "\n".join(new_code).replace("```go", "").split("```")[0]
        test = data.get("tests", "") if data.get("tests") else data.get("test", "")
        for pkg in self.IMPORT_HELPER["go"]:
            if f"\"{pkg}\"" not in import_list:
                p = pkg.split("/")[-1]
                if p + "." in new_code or p + "." in test:
                    import_list.append(f"\"{pkg}\"")
        import_str = "".join("\t{}\n".format(imp) for imp in import_list)
        code = """
package main

import (
{}
)     

{}   
""".format(import_str.rstrip(), new_code.strip())
        test_code = code + "\n" + test
        return code, test_code

    def dealrust(self, generation, data):
        text = generation
        if text.startswith("rust"):
            text = text[5:]
        function_name = data['prompt'].strip().split("\n")[-1].split("(")[0]
        new_lines = []
        code_lines = text.split("\n")
        test = data.get("test", "") if data.get("test") else data.get("tests", "")
        area_block = False
        for index, line in enumerate(code_lines):
            if area_block:
                if line.strip().startswith("*/"):
                    area_block = False
                    continue
                else:
                    continue
            if line.strip().startswith("//"):
                continue
            if line.strip().startswith("/*"):
                area_block = True
                continue
            if function_name in line:
                continue
            if "fn main(" in line:
                break
            new_lines.append(line)
            new_code = "\n".join(new_lines)
            if new_code.count("}") - new_code.count("{") == 1:
                # 判断剩余函数
                exists_line_list = code_lines[index + 1:]
                # 除单测用例外函数外没有其它函数
                if not any(["fn " in line and "main(" not in line for line in exists_line_list]):
                    break
                else:
                    # 找到其它调用函数，如果
                    exists_code_function_line = [line for line in code_lines[index + 1:] if line.startswith("fn ")]
                    if not exists_code_function_line:
                        break
                    else:
                        if any([exist_function.split("(")[0].split(" ")[-1] + "(" in new_code for exist_function in
                                exists_code_function_line]):
                            continue
                        else:
                            break
        new_code = "\n".join(new_lines)
        code = data["prompt"] + new_code
        if test.strip().startswith("}"):
            test = test[test.index("\n"):]
        test_code = code + "\n" + test
        return code, test_code
