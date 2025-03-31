# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re

class BaseMarkdownPostProcessor(BasePostProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def post_process(self, data:Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        generation = data["generation"]
        data["real_generation"]=generation
        generation=self.extract_code_from_markdown(generation)

        data["generation"] = generation
        print("======================generation======================")
        print(generation)
        
        return data

    def remove_comments(self,js_code):
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
    def extract_code_from_markdown(self,markdown_text):
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

    