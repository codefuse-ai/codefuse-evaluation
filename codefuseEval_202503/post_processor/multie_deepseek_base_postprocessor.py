# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
import re
from .base import BasePostProcessor
from typing import Dict


class MultieDeepSeekBasePostProcessor(BasePostProcessor):
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
        text = data["generation"].lstrip("\n")
        if language.lower() == "cpp":
            new_code, testcode = self.deal_cpp(data.get("prompt_real") + text, data)
        elif language.lower() == "python":
            new_code, testcode = self.deal_python(data.get("prompt_real") + text, data)
        elif language.lower() == "java":
            new_code, testcode = self.deal_java(data.get("prompt_real") + text, data)
        elif language.lower() == "php":
            new_code, testcode = self.deal_php(data.get("prompt_real") + text, data)
        elif language.lower() == "sh" or language.lower() == "shell":
            new_code, testcode = self.deal_shell(data.get("prompt_real") + text, data)
        elif language.lower() == "js" or language.lower() == "javascript":
            new_code, testcode = self.deal_js(data.get("prompt_real") + text, data)
        elif language.lower() == "ts" or language.lower() == "typescript":
            new_code, testcode = self.deal_ts(data.get("prompt_real") + text, data)
        elif language.lower() == "cs" or language.lower() == "csharp":
            new_code, testcode = self.deal_csharp(data.get("prompt_real") + text, data)
        elif language.lower() == "go":
            new_code, testcode = self.deal_go(data.get("prompt_real") + text, data)
        elif language.lower() == "rust":
            new_code, testcode = self.deal_rust(text, data)
        else:
            new_code, testcode = data.get("prompt_real") + text, data.get("prompt_real") + text
        data["code"] = new_code
        data["test_code"] = testcode
        return data

    def deal_cpp(self, generation, data):
        text = generation.rstrip("\n")
        text = text if "\nAssistant:" not in text else text.split("\nAssistant:")[0]
        text = text if "\nUser:" not in text else text.split("\nUser:")[0]
        text = text if "```cpp" not in text else text.split("```cpp")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text[4:] if text.startswith("cpp") else text
        text = text[2:] if text.startswith("c\n") else text
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

    def deal_python(self, generation, data):
        text = generation
        text = text if "User:" not in text else text.split("User:")[0]
        text = text if "Assistant:" not in text else text.split("Assistant:")[0]
        text = text if "```python" not in text else text.split("```python")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        if text.count(data.get("prompt")) > 1:
            index = text.find(data.get("prompt"))
            text = text[:index] + text[index + len(data.get("prompt")):]
        text = text[7:] if text.startswith("python") else text
        lines = text.split("\n")
        prompt = data["prompt"]
        function = [line for line in prompt.split("\n") if line.startswith("def")][-1].split("(")[0]
        function_declare = [line for line in prompt.split("\n") if line.startswith("def")][-1] + "\n"
        code_packages = []
        new_lines = []
        flag = False
        for index in range(len(lines)):
            if function_declare[: -5] in lines[index]:
                flag = True
                if new_lines:
                    new_lines.append(lines[index])
                else:
                    new_lines = [lines[index]]
                continue
            if flag:
                new_lines.append(lines[index])
            if lines[index].lstrip().startswith("return") and "if" not in lines[index - 1]:
                flag = False
                continue
            if "import" in lines[index]:
                new_lines.append(lines[index])
                continue
        if len(new_lines) > 1:
            new_lines = new_lines[1:] if new_lines[0] == new_lines[1] else new_lines
        new_code = "\n".join(new_lines).strip()
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        testcode = new_code + "\n\n" + test
        code_setup = ""
        if code_packages:
            code_setup = "\n".join(code_packages)
        new_code = "\n".join(self.IMPORT_HELPER["python"]) + f"\n{code_setup}\n" + new_code
        testcode = "\n".join(self.IMPORT_HELPER["python"]) + f"\n{code_setup}\n" + testcode
        return new_code, testcode

    def deal_java(self, generation, data):
        text = generation
        text = text if "User:" not in text else text.split("User:")[0]
        text = text if "Assistant:" not in text else text.split("Assistant:")[0]
        text = text if "```java" not in text else text.split("```java")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text[5:] if text.startswith("java") else text
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
        if len(new_lines) > 1:
            new_lines = new_lines[1:] if new_lines[0].replace(" ", "") == new_lines[1].replace(" ", "") else new_lines
        prompt = "\n".join(prompt.strip().split("\n")[:-1])
        if new_lines:
            new_code = "\n".join(new_lines)
            if new_code.count("}") - new_code.count("{") == 1:
                new_code = new_code[:new_code.rfind("}")]
            new_code = prompt.strip() + "\n" + new_code
        else:
            new_code = prompt.strip() + "\n" + ""
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").strip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        if new_code.startswith(" "):
            new_code = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(generation_packages) + "\n" + prompt + new_code
            testcode = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(
                generation_packages) + "\n" + prompt + new_code + "\n" + test
        else:
            new_code = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(
                generation_packages) + "\n" + prompt_setpackages + "\n" + new_code
            testcode = "\n".join(self.IMPORT_HELPER["java"]) + "\n".join(
                generation_packages) + "\n" + prompt_setpackages + "\n" + new_code + "\n" + test
        return new_code, testcode

    def deal_php(self, generation, data):
        def find_last_index(lst, element):
            # Reverse the list and find the first occurrence
            try:
                reverse_index = next(i for i, x in enumerate(reversed(lst)) if x == element)
                # Calculate the actual index from the end of the list
                return len(lst) - 1 - reverse_index
            except StopIteration:
                return 0

        text = generation
        text = text if "User:" not in text else text.split("User:")[0]
        text = text if "Assistant:" not in text else text.split("Assistant:")[0]
        text = text if "```php" not in text else text.split("```php")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text if "// Test cases\n" not in text else text.split("// Test cases\n")[0]
        function = data["prompt"].strip().split("\n")[-1].split("(")[0]
        if text.count(function) > 1:
            text = "function" + text.split("function")[-1]
        text = text[4:] if text.startswith("php") else text
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

    def deal_shell(self, generation, data):
        text = generation
        text = text if "User: #!/bin/bash" not in text else text.split("User: #!/bin/bash")[0]
        text = text if "Assistant:" not in text else text.split("Assistant:")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text.split("#!/bin/bash")[-1] if text.count("#!/bin/bash") > 1 else text
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            if line.startswith("#"):
                continue
            else:
                new_lines.append(line)
        if len(new_lines) > 1:
            new_lines = new_lines[1:] if new_lines[0] == new_lines[1] else new_lines
        text = "\n".join(new_lines)
        text = text[5:] if text.startswith("bash") else text
        text = text[3:] if text.startswith("sh") else text
        lines = text.split("\n")
        if any(["}" == line for line in lines]):
            index = len(lines) - 1 - lines[::-1].index('}')
            new_lines = lines[:index + 1]
            new_code = "\n".join(new_lines)
        else:
            new_code = text
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        new_code = new_code if new_code.startswith("\n") else "\n" + new_code
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        testcode = new_code + "\n" + test
        if testcode.startswith(" "):
            testcode = data['prompt'] + testcode
            new_code = data['prompt'] + new_code
        return new_code, testcode

    def deal_js(self, generation, data):
        text = generation
        text = text if "Assistant:" not in text else text.split("Assistant:")[0]
        text = text if "User:" not in text else text.split("User:")[0]
        text = text if "```JavaScript" not in text else text.split("```JavaScript")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text if "// Test cases\n" not in text else text.split("// Test cases\n")[0]
        text = text[11:] if text.startswith(("javascript", "typescript")) else text
        text = text[3:] if text.startswith(("js", "ts")) else text
        lines = text.split("\n")
        prompt = data["prompt"]
        function_declare = prompt.strip().split("\n")[-1] + "\n"
        new_lines = []
        flag = False
        for index in range(len(lines)):
            if function_declare[: -5] in lines[index] and "//" not in lines[index]:
                flag = True
                if new_lines:
                    new_lines.append(lines[index])
                else:
                    new_lines = [lines[index]]
                continue
            if flag and lines[index]:
                if lines[index].lstrip().startswith("//"):
                    continue
                else:
                    new_lines.append(lines[index])
            if lines[index].lstrip().startswith("return") and "if" not in lines[index - 1]:
                flag = False
                continue
            if "import" in lines[index]:
                new_lines.append(lines[index])
                continue
        if len(new_lines) > 1:
            new_lines = new_lines[1:] if new_lines[0].replace(" ", "") == new_lines[1].replace(" ", "") else new_lines
        new_code = "\n".join(new_lines).strip()
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        if test.startswith("}"):
            test = test[test.index("\n") + 1:]
        if not new_code.startswith("function"):
            new_code = data["prompt"] + new_code
        new_code = new_code if new_code.startswith("\n") else "\n" + new_code
        new_code = new_code + "\n}" if new_code.count("}") + 1 == new_code.count("{") else new_code
        testcode = new_code + "\n" + test
        return new_code, testcode

    def deal_ts(self, generation, data):
        text = generation
        text = text if "User:" not in text else text.split("User:")[0]
        text = text if "\nAssistant:" not in text else text.split("\nAssistant:")[0]
        text = text if "```ts" not in text else text.split("```ts")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text if "// Test cases\n" not in text else text.split("// Test cases\n")[0]
        text = "function" + text.split("function")[-1] if text.count("function") > 1 else text
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
        new_code = new_code[1:] if new_code.startswith("}") else new_code
        test = data["tests"].lstrip() if "tests" in data else data.get("test", "").lstrip()
        test = test[test.index("\n") + 1:] if test.startswith("}") else test
        new_code = data["prompt"] + new_code if not new_code.startswith("function") else new_code
        new_code = "\n" + new_code if not new_code.startswith("\n") else new_code
        testcode = new_code + "\n" + test
        testcode = testcode.replace("declare var require: any;", '')
        return new_code, testcode

    def deal_csharp(self, generation, data):
        text = generation.rstrip("\n")
        text = text if "\nAssistant:" not in text else text.split("\nAssistant:")[0]
        text = text if "\nuser:" not in text else text.split("\nuser:")[0]
        text = text if "\nUser:" not in text else text.split("\nUser:")[0]
        text = text if "// Return the prime" not in text else text.split("// Return the prime")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text if "// Test cases\n" not in text else text.split("// Test cases\n")[0]
        text = text[6:] if text.startswith("csharp") else text
        text = text[3:] if text.startswith(("cs", "C#", "c#", "CS")) else text
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

    def deal_go(self, generation, data):
        text = generation.rstrip("\n")
        text = text if "User:" not in text else text.split("User:")[0]
        text = text if "Assistant:" not in text else text.split("Assistant:")[0]
        text = text if "\nTest:" not in text else text.split("\nTest:")[0]
        text = text if "```go" not in text else text.split("```go")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text if "// Test cases\n" not in text else text.split("// Test cases\n")[0]
        text = text[3:] if text.startswith("go") else text
        package_setup = """
package main

import (
    "testing"
)
        """
        import_area_continue = False
        function_package = []
        function_name = data['prompt'].strip().split("\n")[-1].split("(")[0]
        new_lines = []
        code_lines = text.split("\n")
        test = data.get("tests", "") if data.get("tests") else data.get("test", "")
        other_pkgs = []

        for index, line in enumerate(code_lines):
            if line.strip().startswith("//"):
                continue
            if line.startswith("package"):
                continue
            if import_area_continue:
                if line.startswith(")") or ")" in line:
                    import_area_continue = False
                function_package.append(line.strip())
                continue
            if line.startswith("import"):
                if "(" in line:
                    import_area_continue = True
                    continue
                else:
                    function_package.append(line)
            if function_name in line:
                continue
            new_lines.append(line)
            new_code = "\n".join(new_lines)
            if new_code.count("}") - new_code.count("{") == 1:
                # 判断剩余函数是否是单测用例，是否需要保留
                exists_line_list = code_lines[index + 1:]
                # 除单测用例外函数外没有其它函数
                if not any(["func " in line and "*testing.T" not in line for line in exists_line_list]):
                    break
                else:
                    # 找到其它调用函数，如果
                    exists_code_function_line = [line for line in code_lines[index + 1:] if line.startswith("func ")]
                    if not exists_code_function_line:
                        break
                    else:
                        if any([exist_function.split("(")[0].split(" ")[-1] + "(" in new_code for exist_function in
                                exists_code_function_line]):
                            continue
                        else:
                            break

        new_code = "\n".join(new_lines)

        for pkg in self.IMPORT_HELPER["go"]:
            if pkg not in package_setup:
                p = pkg.split("/")[-1]
                if p + "." in new_code or p + "." in test:
                    other_pkgs.append(f"\"{pkg}\"")

        if other_pkgs:
            import_other_pkgs = "import (\n" + "    ".join([p + "\n" for p in other_pkgs]) + ")"
        else:
            import_other_pkgs = ""
        prompt_function = data["prompt"].strip().split("\n")[-1]
        code = package_setup + "\n" + import_other_pkgs + "\n" + prompt_function + "\n" + new_code
        test_code = code + "\n" + test
        return code, test_code

    def deal_rust(self, generation, data):
        text = generation
        text = text if "\nAssistant: ///" not in text else text.split("\nAssistant: ///")[0]
        text = text if "```rust\n" not in text else text.split("```rust\n")[1].split("```")[0]
        text = text if "Here is the code for the function:\n" not in text else text.split("Here is the code for the function:\n")[1]
        text = text if "User:" not in text else text.split("User:")[0]
        text = text if "```rust:" not in text else text.split("```rust:")[1].split("```")[0]
        text = text if "```" not in text else text.split("```")[1].split("```")[0]
        text = text if "# Test cases\n" not in text else text.split("# Test cases\n")[0]
        text = text if "// Test cases\n" not in text else text.split("// Test cases\n")[0]
        text = text[5:] if text.startswith("rust") else text
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
        test = test[test.index("\n"):] if test.strip().startswith("}") else test
        test_code = code + "\n" + test
        return code.rstrip("\n"), test_code
