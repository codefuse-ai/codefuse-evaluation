# Copyright (c) 2022-2025 Ant Group
from abc import ABC, abstractmethod
from typing import List,Union,Dict

class BasePostProcessor( ABC ):
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

    @abstractmethod
    def post_process(self, data:Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        """
        processor generate data for given dataset
        param:dataset: {'task_id':'xxx','prompt':'xxx'}
        language:code language like python,java,cpp,js,go,rust
        task_mode:task mode for evaluation,define in DATASET_SUPPORT Variable in api_utils.py
        dataset_name:evaluate dataset name,define in EVALUATE_DATASET Variable in api_utils.py, the key is evaluation dataset name
        return post_processed_data: Dict
        """
        pass