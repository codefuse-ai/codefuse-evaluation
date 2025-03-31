# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re


class MbxpOpenCoderChatPostProcessor(BasePostProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.IMPORT_HELPER = {
            "go": [
                "math",
                "strings",
                "fmt",
                "strconv",
                "time",
                "bytes",
                "regexp",
                "sort",
                "math/rand",
                "crypto/md5",
                "math/big",
                "unicode",
                "bufio",
                "testing",
            ]
        }

    def post_process(self, data: Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        lang = data["task_id"].split("/")[0]
        lang = "typescript" if lang == "ts" else lang
        real_generation = self.extract_code_from_markdown(data["generation"])
        print("===============real_generation")
        print(real_generation)
        data["real_generation"] = real_generation
        generation = self.process_generation_mbxp(real_generation, lang, data)
        data["generation"] = generation
        print("======================generation======================")
        print(generation)
        return data

    def remove_comments(self, js_code):
        import re
        # 单行注释
        single_line_comment = re.compile(r'//.*')
        # 多行注释
        multi_line_comment = re.compile(r'/\*.*?\*/', re.DOTALL)

        # 删除多行注释
        js_code = multi_line_comment.sub('', js_code)
        # 删除单行注释
        js_code = single_line_comment.sub('', js_code)

        return js_code.strip('\n')

    def extract_code_from_markdown(self, markdown_text):
        import re
        # 使用正则表达式提取代码块
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            code = re.split(r'# Example ', code, maxsplit=1)[0]
            code = re.split(r'if __name__ == ', code, maxsplit=1)[0]
            return code
        pattern = r'```java\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return code
        pattern = r'```go\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return code
        pattern = r'```javascript\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return self.remove_comments(code)
        pattern = r'```cpp\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return code
        pattern = r'```rust\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return self.remove_comments(code)
        pattern = r'```typescript\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return self.remove_comments(code)
        pattern = r'```Python\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            code = re.split(r'# Example ', code, maxsplit=1)[0]
            code = re.split(r'if __name__ == ', code, maxsplit=1)[0]
            return code
        pattern = r'```(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            code = re.split(r'# Example ', code, maxsplit=1)[0]
            code = re.split(r'if __name__ == ', code, maxsplit=1)[0]
            return code

        return markdown_text

    def process_generation_mbxp(self, real_generation, language, data):
        if language.lower() == "java":
            print("java")
            return self.process_generation_java(real_generation, data)
        elif language.lower() == "cpp":
            print("cpp")
            return self.process_generation_cpp(real_generation)
        elif language.lower() == "go":
            print("go")
            return self.process_generation_go(real_generation)
        elif language.lower() == "javascript":
            print("javascript")
            return self.process_generation_js(real_generation)
        elif language.lower() == "typescript":
            print("typescript")
            generation = self.dealts(real_generation, data)
            data["test_code"] = generation + "\n" + data["test"]
            return generation
        else:
            print("php")
            return self.process_generation_php(real_generation)

    def dealts(self, text, data):
        if text.startswith(("javascript", "typescript")):
            text = text[11:]
        if text.startswith(("js", "ts")):
            text = text[3:]
        lines = text.split("\n")
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
            if not line.startswith((" ", "\t", "}", "function", "const", "import")):
                continue
            if "import * as assert from 'assert'" in line:
                if any([data["entry_point"] in line for line in new_lines]):
                    break
                else:
                    continue
            new_lines.append(line)
            temp_code = "\n".join(new_lines).strip()
            if temp_code.count("}") - temp_code.count("{") == 1:
                break
        new_code = "\n".join(new_lines).strip()
        if new_code.startswith("}"):
            new_code = new_code[1:]
        return new_code

    def process_generation_java(self, real_generation, data: dict):
        def drop_comments_and_import(code: str, function_name: str):
            """
            去掉 code 里面的注释跟 import 内容
            :param code: 原始代码
            :param code: 预期的函数名称
            """
            lines = code.split("\n")
            new_lines, common = [], False
            main_index = code.index("main(String[] args)")
            func_index = code.index(function_name) if function_name in code else -1
            if main_index > func_index != -1:  # 说明当前代码中，先出现目标函数，然后再出现 main 函数，可以直接走截断方式
                for line in lines:
                    if "main(String[] args)" in line:
                        break
                    if not line.strip() or line.strip().startswith("//") or line.strip().startswith("import"):
                        continue
                    if line.strip().startswith("/*"):
                        common = True
                        continue
                    if line.strip().startswith("*/"):
                        common = False
                        continue
                    if not common:
                        new_lines.append(line)
                return "\n".join(new_lines)
            else:
                return ""

        def re_function(code: str, function_name: str):
            """
            通过正则表达式来提取 java 代码，适用于先出现 main 函数的场景再出现目标函数
            :param: 原始代码
            :param: 目标函数
            """
            import re
            function_pattern = re.compile(r'public\sstatic\s.*?\s{\s(?:\s[^{}]*{\s[^{}]*\s})*[^{}]*\s}', re.DOTALL)
            functions = function_pattern.findall(code)
            test = []
            for function in functions:
                if function_name in function:
                    if "main(String[] args)" not in function:
                        return "    " + function
                    else:
                        continue
                test.append("    " + function)
            return "\n".join(test)

        code_list = real_generation.split("\n")
        new_code_list = ["import java.io.*;", "import java.lang.*;", "import java.util.*;", "import java.math.*;"]
        flag = False
        flag_main = False
        for code in code_list:
            if code.strip("") == "":
                continue
            if code.startswith("//"):
                continue
            if "class Main" in code:
                flag = True
                continue
            if "public class" in code:
                new_code_list.append(code.replace("public class", "class"))
                continue
            if "static void main" in code:
                flag_main = True
                continue
            if flag_main:
                if code.startswith("    }"):
                    flag_main = False
                    continue
                else:
                    continue
            if flag:
                if code.startswith("}"):
                    flag = False
                    continue
                else:
                    continue
            new_code_list.append(code)
        new_code_list.append("}") if new_code_list[-1] != "}" else new_code_list
        new_code = "\n".join(new_code_list)
        new_code = new_code.replace("public class Main", "class Main")
        prompt_lines = data.get("prompt").split("\n")
        func_define = ["public", "void", "protected", "private"]
        function_name = ""
        new_prompt_lines = []
        for line in prompt_lines[::-1]:  # 查找预期的函数名称，同时去掉 prompt 中关于函数名的定义
            if any(func_define in line for func_define in func_define) and "(" in line:
                function_name = (line.split("(")[0] + "(").split(" ")[-1]
                continue
            new_prompt_lines.append(line)
        if function_name not in new_code:   # 如果按照前面步骤提取的代码不包含被测试的函数，则进行后面的处理
            real_generation_code = drop_comments_and_import(real_generation, function_name)
            tests_code_code = drop_comments_and_import(data.get("test"), function_name)
            tests_code_code = tests_code_code if tests_code_code else re_function(data.get("test"), function_name)
            if real_generation_code:
                new_code = real_generation_code.replace(tests_code_code, "")
            else:
                new_code = re_function(real_generation, function_name)
            prompt_code = "\n".join(new_prompt_lines[::-1]).rstrip("")
            new_code = new_code.replace("public class Main", "class Main")
            new_code = new_code.replace("class Main {", "")
            new_code = prompt_code + "\n" + new_code.lstrip("\n")
            new_code = new_code if new_code.count("{") == new_code.count("}") else new_code + "\n}"

        return new_code

    def delete_template(self, code):
        code_list = code.split("\n")
        new_code_list = []
        # # include <bits/stdc++.h>
        # using
        # namespace
        # std;

        for code in code_list:

            if code.startswith("template"):
                continue

            new_code_list.append(code)
        return "\n".join(new_code_list)

    def process_generation_cpp(self, real_generation):
        flag = 0
        templateNum = 0

        code_list = real_generation.split("\n")
        new_code_list = []
        # # include <bits/stdc++.h>
        # using
        # namespace
        # std;
        new_code_list.append("#include <bits/stdc++.h>")
        new_code_list.append("using namespace std;")
        templatestring = ""
        for code in code_list:
            if flag == 0 and code.lstrip() == code and "int main" in code:
                flag = 1
                continue
            if flag == 1:
                if code.lstrip() == code and "}" in code:
                    flag = 0
                    continue
                else:
                    continue
            if code.startswith("template") and code.rstrip().endswith("T>"):
                templatestring = code
                templateNum = 1
                continue
            if "T " in code or "<T>" in code or ", T>" in code or "T&" in code:
                new_code_list.append(templatestring)
                templatestring = ""
                new_code_list.append(code)
            else:
                new_code_list.append(code)
        # for i in range(len(new_code_list)):
        #     if new_code_list[i].lstrip() == new_code_list[i] and "}" in new_code_list[i]:
        #         new_code_list=new_code_list[:i+1]
        #         break
        new_code = "\n".join(new_code_list)
        if "T " not in new_code and "<T>" not in new_code and ", T>" not in new_code and "T&" not in new_code:
            new_code = self.delete_template(new_code)

        return new_code

    def delete_import(self, code):
        if code.startswith("package"):
            code_list = code.split("\n")
            new_code_list = []
            # # include <bits/stdc++.h>
            # using
            # namespace
            # std;

            for code in code_list:
                # if "fmt" in code:
                #     continue

                new_code_list.append(code)
            return "\n".join(new_code_list)
        elif code.startswith("import"):
            code_list = code.split("\n")
            new_code_list = []
            new_code_list.append("package main")
            # # include <bits/stdc++.h>
            # using
            # namespace
            # std;

            for code in code_list:
                # if "fmt" in code:
                #     continue

                new_code_list.append(code)
            return "\n".join(new_code_list)

    def process_generation_go(self, real_generation):
        flag = 0
        templateNum = 0

        #code_list=data["generation"].strip().split("\n")
        new_code_list = []
        # # include <bits/stdc++.h>
        # using
        # namespace
        # std;
        real_prompt = "func " + real_generation.split("func ", 1)[-1]
        code_list = real_prompt.strip().split("\n")

        for code in code_list:
            if code.startswith("//"):
                continue
            if code.startswith("golang"):
                continue
            if code.startswith("Golang"):
                continue
            if flag == 0 and code.lstrip() == code and ("deepCompare" in code or "func main()" in code):
                flag = 1
                continue
            if flag == 1:
                if code.lstrip() == code and "}" in code:
                    flag = 0
                    continue
                else:
                    continue

            new_code_list.append(code)
        # for i in range(len(new_code_list)):
        #     if new_code_list[i].lstrip() == new_code_list[i] and "}" in new_code_list[i]:
        #         new_code_list=new_code_list[:i+1]
        #         break
        new_code = "\n".join(new_code_list)
        if True:
            import_prompt = real_generation.split("func")[0]
            real_prompt = real_generation.split("func ", 1)[-1]
            pkg_list = []
            for pkg in self.IMPORT_HELPER["go"]:

                p = pkg.split("/")[-1]
                if p + "." in new_code:
                    pkg_list.append(f"\"{pkg}\"")
            import_other_pkgs = ""
            if pkg_list:
                import_other_pkgs = "import (\n" + "    ".join([p + "\n" for p in pkg_list]) + ")"
                new_code_list.insert(0, import_other_pkgs)
            if "encoding/json" not in import_other_pkgs:
                new_code_list.insert(0, "import \"encoding/json\"\n")
            if "reflect" not in import_other_pkgs:
                new_code_list.insert(0, "import \"reflect\"\n")

        new_code = "\n".join(new_code_list)

        new_code = self.delete_import(new_code)
        new_code = new_code.replace("&quot;", '"')
        new_code = new_code.replace("&amp;", "&")
        new_code = new_code.replace("&lt;", "<")
        new_code = new_code.replace("&gt;", ">")
        return new_code

    def process_generation_js(self, real_generation):

        code_list = real_generation.split("\n")
        function_flag = 0
        new_code_list = []
        for code in code_list:
            if code.startswith("function") and "compare(" not in code:
                function_flag = 1
                new_code_list.append(code)
                continue
            if function_flag == 1:
                if code.lstrip() == code and code == "}":
                    function_flag = 0
                    new_code_list.append(code)
                    continue
                else:
                    new_code_list.append(code)
                    continue
            if function_flag == 0:
                continue

        new_code = "\n".join(new_code_list)
        return new_code

    def process_generation_php(self, real_generation):

        code_list = real_generation.split("\n")
        function_flag = 0
        new_code_list = []
        new_code_list.append("<?php")
        for code in code_list:
            if code.startswith("function"):
                function_flag = 1
                new_code_list.append(code)
                continue
            if function_flag == 1:
                if code.lstrip() == code and code == "}":
                    function_flag = 0
                    new_code_list.append(code)
                    continue
                else:
                    new_code_list.append(code)
                    continue
            if function_flag == 0:
                continue

        new_code = "\n".join(new_code_list)
        return new_code
