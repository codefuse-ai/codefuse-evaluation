# -*- coding:utf-8 -*-
# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import List, Union, Dict
import copy
import re


class Text2SqlOpenCoderPostProcessor(BasePostProcessor):
    """
    模型后处理方式基类
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __str__(self):
        return f"{self.__class__.__name__}"

    def post_process(self, data: Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        """
        processor generate data for given dataset
        param:
        dataset: [{'task_id':'xxx','prompt':'xxx'}
        language: code language like python,java,cpp,js,go,rust
        task_mode: task mode for evaluation,define in DATASET_SUPPORT Variable in util.py
        dataset_name: evaluate dataset name,define in EVALUATE_DATASET Variable in util.py, the key is evaluation dataset name
        return post_processed_data: Dict
        """
        generation = data["generation"]
        data['generation_ori'] = copy.deepcopy(generation)
        new_line = []
        lines = generation.split("\n")
        for line in lines:  # 去掉空换行符
            if line:
                new_line.append(line)
            else:
                continue
        generation = "\n".join(new_line)
        generation = generation if "\nuser\n" not in generation else generation.split("\nuser\n")[0]
        generation = generation if "\ntable" not in generation else generation.split("\ntable")[0]
        generation = generation if "\n user\n" not in generation else generation.split("\n user\n")[0]
        generation = generation if "\nusername_1\n" not in generation else generation.split("\nusername_1\n")[0]
        generation = generation if "\nouser\n" not in generation else generation.split("\nouser\n")[0]
        generation = generation if "\nousername_0" not in generation else generation.split("\nousername_0")[0]
        generation = generation if "\nvotes for solutions\n" not in generation else generation.split("\nvotes for solutions\n")[0]
        generation = generation if "\nassistant:" not in generation else generation.split("\nassistant:")[0]
        generation = generation if "\n�" not in generation else generation.split("\n�")[0]
        generation = generation if "\nassistant\n" not in generation else generation.split("\nassistant\n")[0]
        generation = generation if "\nassault" not in generation else generation.split("\nassault")[0]
        generation = generation if "\n-LAST-QUERY" not in generation else generation.split("\n-LAST-QUERY")[0]
        generation = generation if "\n```\n" not in generation else generation.split("\n```\n")[0]
        generation = generation if "\n-->" not in generation else generation.split("\n-->")[0]
        generation = generation if "\nemphasize" not in generation else generation.split("\nemphasize")[0]
        generation = generation if "\n>>>" not in generation else generation.split("\n>>>")[0]
        generation = generation if "\ndiv\n" not in generation else generation.split("\ndiv\n")[0]
        generation = generation if "\ntruncated for brevity\n" not in generation else generation.split("\ntruncated for brevity\n")[0]
        generation = generation if "\nQuestion:" not in generation else generation.split("\nQuestion:")[0]
        generation = generation if "\n_Note:" not in generation else generation.split("\n_Note:")[0]
        generation = generation if "\nation:" not in generation else generation.split("\nation:")[0]
        generation = generation if "\nassumption:" not in generation else generation.split("\nassumption:")[0]
        generation = generation if "\ntruncated" not in generation else generation.split("\ntruncated")[0]
        generation = generation if "\nQuestion:" not in generation else generation.split("\nQuestion:")[0]
        generation = generation if "\nvotes" not in generation else generation.split("\nvotes")[0]
        generation = generation if "\nanswer:" not in generation else generation.split("\nanswer:")[0]
        generation = generation if "\ncode" not in generation else generation.split("\ncode")[0]
        generation = generation if "\nThe provided SQL" not in generation else generation.split("\nThe provided SQL")[0]
        generation = generation if "\nThe above" not in generation else generation.split("\nThe above")[0]
        generation = generation if "\nThe query " not in generation else generation.split("\nThe query ")[0]
        generation = generation if "\nThe description " not in generation else generation.split("\nThe description ")[0]
        generation = generation if "\nexplanation:" not in generation else generation.split("\nexplanation:")[0]
        generation = generation if "\n -- The output" not in generation else generation.split("\n -- The output")[0]
        generation = generation if "\n-- Using" not in generation else generation.split("\n-- Using")[0]
        generation = generation if ";\ns" not in generation else generation.split(";\ns")[0]
        generation = generation if ";\nb" not in generation else generation.split(";\nb")[0]
        generation = generation if ";\n 1." not in generation else generation.split(";\n 1.")[0]
        generation = generation if ";\n{" not in generation else generation.split(";\n{")[0]
        generation = generation if "\n:~" not in generation else generation.split("\n:~")[0]
        generation = generation if ";\n:" not in generation else generation.split(";\n:")[0]
        generation = generation if ";\n://" not in generation else generation.split(";\n://")[0]
        generation = generation if "\nemote:" not in generation else generation.split("\nemote:")[0]
        generation = generation if "\nrows:\n" not in generation else generation.split("\nrows:\n")[0]
        generation = generation if "\nect" not in generation else generation.split("\nect")[0]
        generation = generation if "\n:END" not in generation else generation.split("\n:END")[0]
        generation = generation if "\n::" not in generation else generation.split("\n::")[0]
        generation = generation.strip()
        generation = generation if str(generation).endswith(";") else generation + ";"
        data["generation"] = generation
        return data
