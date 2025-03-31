# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import List,Union,Dict
import copy
import re


class Text2SqlPostProcessor( BasePostProcessor ):
    """
    模型后处理方式基类
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr( self, key, value )

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __str__(self):
        return f"{self.__class__.__name__}"


    def post_process(self, data:Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
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
        data["generation"] = extract_sql(generation)
            
        return data

def extract_sql(text):
    if text is None:
        return ""
    match = re.search(r'```\w*\n(.*?)```', text, re.DOTALL)
    if match:
        sql = match.group(1).strip()
    else:
        sql = text
    # 兼容输出不规范的情况
    sql = re.sub(r'```sql\n', '', sql)
    sql = re.sub(r'```', '', sql)
    sql = sql.split(";")[0]
    # print("generation after post_model_common:", sql)
    return sql
        