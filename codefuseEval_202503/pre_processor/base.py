# Copyright (c) 2022-2025 Ant Group
from abc import ABC, abstractmethod
from typing import List,Dict

class BasePreProcessor( ABC ):
    """
    模型前处理方式，主要是处理prompt
    """
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr( self, key, value )

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __str__(self):
        return f"{self.__class__.__name__}"

    @abstractmethod
    def pre_process(self, dataset: List[Dict], language: str, task_mode: str, dataset_name: str, **kwargs) -> List[str]:
        """
        processor generate data for given dataset
        param:dataset: [{'task_id':'xxx','prompt':'xxx'}
        language:code language like python,java,cpp,js,go,rust
        task_mode:task mode for evaluation,define in DATASET_SUPPORT Variable in data_registry.py
        dataset_name:evaluate dataset name,define in EVALUATE_DATASET Variable in data_registry.py, the key is evaluation dataset name
        return dataset
        """
        pass
