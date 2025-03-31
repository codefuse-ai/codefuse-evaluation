# Copyright (c) 2022-2025 Ant Group
import json
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


func = [
    {
        "question": "You are given a 0-indexed array of positive integers nums. Find the number of triplets (i, j, k) that meet the following conditions:\n\n0 <= i < j < k < nums.length\nnums[i], nums[j], and nums[k] are pairwise distinct.\n\t\nIn other words, nums[i] != nums[j], nums[i] != nums[k], and nums[j] != nums[k].\n\n\n\nReturn the number of triplets that meet the conditions.\n \nExample 1:\n\nInput: nums = [4,4,2,4,3]\nOutput: 3\nExplanation: The following triplets meet the conditions:\n- (0, 2, 4) because 4 != 2 != 3\n- (1, 2, 4) because 4 != 2 != 3\n- (2, 3, 4) because 2 != 4 != 3\nSince there are 3 triplets, we return 3.\nNote that (2, 0, 4) is not a valid triplet because 2 > 0.\n\nExample 2:\n\nInput: nums = [1,1,1,1,1]\nOutput: 0\nExplanation: No triplets meet the conditions so we return 0.\n\n \nConstraints:\n\n3 <= nums.length <= 100\n1 <= nums[i] <= 1000\n\n",
        "sample_code": "class Solution:\n    def unequalTriplets(self, nums: List[int]) -> int:\n        ",
        "answer": "class Solution:\n    def unequalTriplets(self, a: List[int]) -> int:\n        ans = 0\n        n = len(a)\n        for i in range(n):\n            for j in range(i + 1, n):\n                for k in range(j + 1, n):\n                    ans += len({a[i], a[j], a[k]}) == 3\n        return ans"
    },
    {
        "question": "You are given two strings s and t consisting of only lowercase English letters.\nReturn the minimum number of characters that need to be appended to the end of s so that t becomes a subsequence of s.\nA subsequence is a string that can be derived from another string by deleting some or no characters without changing the order of the remaining characters.\n \nExample 1:\n\nInput: s = \"coaching\", t = \"coding\"\nOutput: 4\nExplanation: Append the characters \"ding\" to the end of s so that s = \"coachingding\".\nNow, t is a subsequence of s (\"coachingding\").\nIt can be shown that appending any 3 characters to the end of s will never make t a subsequence.\n\nExample 2:\n\nInput: s = \"abcde\", t = \"a\"\nOutput: 0\nExplanation: t is already a subsequence of s (\"abcde\").\n\nExample 3:\n\nInput: s = \"z\", t = \"abcde\"\nOutput: 5\nExplanation: Append the characters \"abcde\" to the end of s so that s = \"zabcde\".\nNow, t is a subsequence of s (\"zabcde\").\nIt can be shown that appending any 4 characters to the end of s will never make t a subsequence.\n\n \nConstraints:\n\n1 <= s.length, t.length <= 10^5\ns and t consist only of lowercase English letters.\n\n",
        "sample_code": "class Solution:\n    def appendCharacters(self, s: str, t: str) -> int:\n        ",
        "answer": "class Solution:\n    def appendCharacters(self, s: str, t: str) -> int:\n        i = 0\n        for char in s:\n            if i < len(t) and char == t[i]:\n                i += 1\n        return len(t) - i"
    }
]

stdin = [
    {
        "question": "You have $n$ gifts and you want to give all of them to children. Of course, you don't want to offend anyone, so all gifts should be equal between each other. The $i$-th gift consists of $a_i$ candies and $b_i$ oranges.\n\nDuring one move, you can choose some gift $1 \\le i \\le n$ and do one of the following operations:\n\n  eat exactly one candy from this gift (decrease $a_i$ by one);  eat exactly one orange from this gift (decrease $b_i$ by one);  eat exactly one candy and exactly one orange from this gift (decrease both $a_i$ and $b_i$ by one). \n\nOf course, you can not eat a candy or orange if it's not present in the gift (so neither $a_i$ nor $b_i$ can become less than zero).\n\nAs said above, all gifts should be equal. This means that after some sequence of moves the following two conditions should be satisfied: $a_1 = a_2 = \\dots = a_n$ and $b_1 = b_2 = \\dots = b_n$ (and $a_i$ equals $b_i$ is not necessary).\n\nYour task is to find the minimum number of moves required to equalize all the given gifts.\n\nYou have to answer $t$ independent test cases.\n\n\n-----Input-----\n\nThe first line of the input contains one integer $t$ ($1 \\le t \\le 1000$) \u2014 the number of test cases. Then $t$ test cases follow.\n\nThe first line of the test case contains one integer $n$ ($1 \\le n \\le 50$) \u2014 the number of gifts. The second line of the test case contains $n$ integers $a_1, a_2, \\dots, a_n$ ($1 \\le a_i \\le 10^9$), where $a_i$ is the number of candies in the $i$-th gift. The third line of the test case contains $n$ integers $b_1, b_2, \\dots, b_n$ ($1 \\le b_i \\le 10^9$), where $b_i$ is the number of oranges in the $i$-th gift.\n\n\n-----Output-----\n\nFor each test case, print one integer: the minimum number of moves required to equalize all the given gifts.\n\n\n-----Example-----\nInput\n5\n3\n3 5 6\n3 2 3\n5\n1 2 3 4 5\n5 4 3 2 1\n3\n1 1 1\n2 2 2\n6\n1 1000000000 1000000000 1000000000 1000000000 1000000000\n1 1 1 1 1 1\n3\n10 12 8\n7 5 4\n\nOutput\n6\n16\n0\n4999999995\n7\n\n\n\n-----Note-----\n\nIn the first test case of the example, we can perform the following sequence of moves:\n\n  choose the first gift and eat one orange from it, so $a = [3, 5, 6]$ and $b = [2, 2, 3]$;  choose the second gift and eat one candy from it, so $a = [3, 4, 6]$ and $b = [2, 2, 3]$;  choose the second gift and eat one candy from it, so $a = [3, 3, 6]$ and $b = [2, 2, 3]$;  choose the third gift and eat one candy and one orange from it, so $a = [3, 3, 5]$ and $b = [2, 2, 2]$;  choose the third gift and eat one candy from it, so $a = [3, 3, 4]$ and $b = [2, 2, 2]$;  choose the third gift and eat one candy from it, so $a = [3, 3, 3]$ and $b = [2, 2, 2]$.",
        "answer": "def minimum_moves(t, test_cases):\n    for _ in range(t):\n        n = test_cases[_][0]\n        candies = test_cases[_][1]\n        oranges = test_cases[_][2]\n        min_candies = min(candies)\n        min_oranges = min(oranges)\n        ans = 0\n        for i in range(n):\n            ans += max(candies[i] - min_candies, oranges[i] - min_oranges)\n        print(ans)\n\n\ndef main():\n    t = int(input())\n    test_cases = []\n    for _ in range(t):\n        n = int(input())\n        candies = list(map(int, input().split()))\n        oranges = list(map(int, input().split()))\n        test_cases.append((n, candies, oranges))\n    minimum_moves(t, test_cases)\n\n\nmain()\n"
    },
    {
        "question": "Let's call a string a phone number if it has length 11 and fits the pattern \"8xxxxxxxxxx\", where each \"x\" is replaced by a digit.\n\nFor example, \"80123456789\" and \"80000000000\" are phone numbers, while \"8012345678\" and \"79000000000\" are not.\n\nYou have n cards with digits, and you want to use them to make as many phone numbers as possible. Each card must be used in at most one phone number, and you don't have to use all cards. The phone numbers do not necessarily have to be distinct.\n\nInput\n\nThe first line contains an integer n \u2014 the number of cards with digits that you have (1 \u2264 n \u2264 100).\n\nThe second line contains a string of n digits (characters \"0\", \"1\", ..., \"9\") s_1, s_2, \u2026, s_n. The string will not contain any other characters, such as leading or trailing spaces.\n\nOutput\n\nIf at least one phone number can be made from these cards, output the maximum number of phone numbers that can be made. Otherwise, output 0.\n\nExamples\n\nInput\n\n11\n00000000008\n\n\nOutput\n\n1\n\n\nInput\n\n22\n0011223344556677889988\n\n\nOutput\n\n2\n\n\nInput\n\n11\n31415926535\n\n\nOutput\n\n0\n\nNote\n\nIn the first example, one phone number, \"8000000000\", can be made from these cards.\n\nIn the second example, you can make two phone numbers from the cards, for example, \"80123456789\" and \"80123456789\".\n\nIn the third example you can't make any phone number from the given cards.",
        "answer": "def count_phone_numbers(num_cards, card_digits):\n    count_eights = card_digits.count(\"8\")\n    max_phone_numbers = num_cards // 11\n    max_possible = min(count_eights, max_phone_numbers)\n    return max_possible\n\ndef main():\n    num_cards = int(input())\n    card_digits = input().strip()\n    max_possible = count_phone_numbers(num_cards, card_digits)\n    print(max_possible)\n\nmain()"
    }
]


class LiveCodeBenchPreProcessor(BasePreProcessor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_deepseek_code_question_template_answer(self, question):
        prompt = f"### Instruction: You will be given a question (problem specification) and will generate a correct Python program that matches the specification and passes all tests. You will NOT return anything except for the program.\n\n"
        prompt += f"Question:\n{question['question_content']}\n\n"
        if question["starter_code"]:
            prompt += f"### Instruction: {PromptConstants.FORMATTING_MESSAGE_WITH_STARTER_CODE}\n"
            prompt += f"```python\n{question['starter_code']}\n```\n\n"
        else:
            prompt += f"### Instruction: {PromptConstants.FORMATTING_WITHOUT_STARTER_CODE}\n"
            prompt += f"```python\n# YOUR CODE HERE\n```\n\n"
        prompt += f"### Response:\n\n"
        return prompt

    def get_deepseek_prompt(self, question):
        prompt = f"{PromptConstants.SYSTEM_MESSAGE_DEEPSEEK}\n\n"
        prompt += f"{self.get_deepseek_code_question_template_answer(question)}"
        return prompt

    def get_base_model_question_template_answer(self, question):
        if question["starter_code"]:
            examples_json = func
        else:
            examples_json = stdin

        def get_example_prompt(example):
            prompt = ""
            prompt += "### Question\n"
            prompt += example["question"]
            prompt += "\n\n"
            if question["starter_code"]:
                prompt += "### Starter Code\n"
                prompt += example["sample_code"]
                prompt += "\n\n"
            prompt += "### Answer\n\n"
            prompt += example["answer"]
            if example["answer"]:
                prompt += "\n\n"
            return prompt

        prompt = ""
        prompt += get_example_prompt(examples_json[0])
        prompt += get_example_prompt(
            {
                "question": question["question_content"],
                "sample_code": question["starter_code"],
                "answer": "",
            }
        )
        return prompt

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        prompt_list = []
        for data in dataset:
            prompt_list.append(self.get_base_model_question_template_answer(data))
        print("prompt_real:", prompt_list[0])
        return prompt_list
