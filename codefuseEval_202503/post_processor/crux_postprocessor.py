# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re

class CRUXPostProcessor(BasePostProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
    def extract_code_from_markdown(self,markdown_text):
        import re
        # 使用正则表达式提取代码块
        pattern = r'```python\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
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
            return code
        pattern = r'```cpp\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return code
        pattern = r'```rust\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return code
        pattern = r'```Python\n(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return code
        pattern = r'```(.*?)```'
        matches = re.findall(pattern, markdown_text, re.DOTALL)

        if len(matches) > 0:
            code = matches[0]
            return code

        return markdown_text
    def post_process(self, data:Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        generation = data["generation"]
        data["real_generation"]=generation
        generation=self.humaneval_postprocess_v2(generation)

        data["generation"] = generation
        print("======================generation======================")
        print(generation)
        return data

    def humaneval_postprocess_v2(self,text):
        raw_result1 = text.replace('&lt;', '<')
        raw_result2 = raw_result1.replace('&gt;', '>')
        generation=raw_result2.split("[/ANSWER]")[0]
        if "[ANSWER]" in generation:
            generation = generation.split("[ANSWER]")[1].strip()
        
        return self.extract_code_from_markdown(generation)

    