# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List, Dict


class PromptConstants:
    SYSTEM_MESSAGE_GENERIC = f"You are an expert Python programmer. You will be given a question (problem specification) and will generate a correct Python program that matches the specification and passes all tests. You will NOT return anything except for the program."

    SYSTEM_MESSAGE_DEEPSEEK = f"You are an AI programming assistant, you answer questions related to computer science."

    SYSTEM_MESSAGE_MAGIC = f"You are an exceptionally intelligent coding assistant that consistently delivers accurate and reliable responses to user instructions.\n\n@@ Instruction\n"

    SYSTEM_MESSAGE_WIZARD = "Below is an instruction that describes a task. Write a response that appropriately completes the request."

    SYSTEM_MESSAGE_PHIND = f"""You are an expert Python programmer. You will be given a question (problem specification) and will generate a correct Python program that matches the specification and passes all tests. You will NOT return anything except for the program. Put your fixed program within code delimiters, for example: 
```python 
# YOUR CODE HERE
```"""

    SYSTEM_MESSAGE_CODEQWEN = f"<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n<|im_start|>user"

    FORMATTING_MESSAGE_WITH_STARTER_CODE = "You will use the following starter code to write the solution to the problem and enclose your code within delimiters."

    FORMATTING_WITHOUT_STARTER_CODE = "Read the inputs from stdin solve the problem and write the answer to stdout (do not directly test on the sample inputs). Enclose your code within delimiters as follows."


class LiveCodeBenchPreProcessor(BasePreProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_deepseekcode_question_template_answer(self, question):
        prompt = f"### Instruction: You will be given a question (problem specification) and will generate a correct Python program that matches the specification and passes all tests. You will NOT return anything except for the program.\n\n"
        prompt += f"Question:\n{question['question_content']}\n\n"
        if question["starter_code"]:
            prompt += (
                f"### Instruction: {PromptConstants.FORMATTING_MESSAGE_WITH_STARTER_CODE}\n"
            )
            prompt += f"```python\n{question['starter_code']}\n```\n\n"
        else:
            prompt += (
                f"### Instruction: {PromptConstants.FORMATTING_WITHOUT_STARTER_CODE}\n"
            )
            prompt += f"```python\n# YOUR CODE HERE\n```\n\n"
        prompt += f"### Response:\n\n"
        return prompt

    def get_deepseek_prompt(self, question):
        prompt = f"{PromptConstants.SYSTEM_MESSAGE_DEEPSEEK}\n\n"
        prompt += f"{self.get_deepseekcode_question_template_answer(question)}"
        return prompt

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        for data in dataset:
            prompt_list.append(self.get_deepseek_prompt(data))
        print("prompt_real:", prompt_list[0])
        return prompt_list
