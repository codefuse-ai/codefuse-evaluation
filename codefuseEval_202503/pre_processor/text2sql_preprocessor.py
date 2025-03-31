# Copyright (c) 2022-2025 Ant Group
from .base import BasePreProcessor
from typing import List,Dict


class Text2SqlPreProcessor(BasePreProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        model_name = kwargs.get("model_name")
        prompt_list = []
        for data in dataset:
            if "spider" in dataset_name:
                # ---------- spider -------------
                if "qwen-coder25" in model_name:
                    final_prompt = gen_spider_prompt_qwen25(data)
                else:
                    final_prompt = gen_spider_prompt_bailing(data)

            elif "bird" in dataset_name:
                # ------------  bird  -----------
                if "qwen" in model_name:
                    final_prompt = gen_bird_prompt_qwen25(data)
                else:
                    final_prompt = gen_bird_prompt_bailing(data)

            else:
                # ----------- default ------------
                final_prompt = data['prompt']

            prompt_list.append(final_prompt)
        
        return prompt_list


def gen_spider_prompt_bailing(data):
    schema_prompt = data['tables']
    pattern_prompt = "-- Using valid SQLite, answer the following questions for the tables provided above."
    question_prompt = f"Question: {data['prompt']}"
    demand_prompt = "Please output only the final SQL query, starts with keyword `SELECT`. "

    final_prompt = schema_prompt + "\n\n\n" + pattern_prompt + "\n" + question_prompt + "\n" + demand_prompt
    return final_prompt


def gen_spider_prompt_qwen25(data):
    schema_prompt = data['tables']
    pattern_prompt = "-- Using valid SQLite, answer the following questions for the tables provided above."
    question_prompt = f"Question: {data['prompt']}"

    final_prompt = schema_prompt + "\n\n" + pattern_prompt + "\n" + question_prompt + "\n"
    return final_prompt


def gen_bird_prompt_bailing(data,use_knowledge=True):
    schema_prompt = data['tables']
    knowledge_prompt = "-- External Knowledge: {}".format(data['evidence'])
    pattern_prompt_no_kg = "-- Using valid SQLite, answer the following questions for the tables provided above."
    pattern_prompt_kg = "-- Using valid SQLite and understading External Knowledge, answer the following questions for the tables provided above."
    question_prompt = "Question: {}".format(data['prompt'])
    demand_prompt = "Please output only the final SQL query, starts with keyword `SELECT`. "

    final_prompt = schema_prompt + '\n\n\n'
    if not use_knowledge:
        final_prompt += pattern_prompt_no_kg + '\n' + question_prompt + '\n'
    else:
        final_prompt += knowledge_prompt + '\n' + pattern_prompt_kg + '\n' + question_prompt + '\n'
    final_prompt += demand_prompt
    return final_prompt


def gen_bird_prompt_qwen25(data, use_knowledge=True):
    schema_prompt = data['tables']
    knowledge_prompt = "-- External Knowledge: {}".format(data['evidence'])
    pattern_prompt_no_kg = "-- Using valid SQLite, answer the following questions for the tables provided above."
    pattern_prompt_kg = "-- Using valid SQLite and understading External Knowledge, answer the following questions for the tables provided above."
    question_prompt = "Question: {}".format(data['prompt'])

    final_prompt = schema_prompt + '\n\n'
    if not use_knowledge:
        final_prompt += pattern_prompt_no_kg + '\n\n' + question_prompt + '\n'
    else:
        final_prompt += knowledge_prompt + '\n\n' + pattern_prompt_kg + '\n\n' + question_prompt + '\n'
    return final_prompt
    
