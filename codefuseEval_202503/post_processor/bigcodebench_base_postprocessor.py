# Copyright (c) 2022-2025 Ant Group
from .base import BasePostProcessor
from typing import Dict
import re

class BigCodeBenchPostProcessor(BasePostProcessor):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.IMPORT_HELPER = {
            "python": [
                "import math",
                "import unittest",
                "import re",
                "import sys",
                "import copy",
                "import datetime",
                "import itertools",
                "import collections",
                "import heapq",
                "import statistics",
                "import functools",
                "import hashlib",
                "import numpy",
                "import numpy as np",
                "import string",
                "from typing import *",
                "from collections import *",
            ],
            "cpp": [
                "#include<stdlib.h>",
                "#include<algorithm>",
                "#include<math.h>",
                "#include<stdio.h>",
                "#include<vector>",
                "#include<string>",
                "#include<climits>",
                "#include<cstring>",
                "#include<iostream>",
                "#include <stdexcept>",
            ],
            "java": [
                "import java.io.*;",
                "import java.lang.*;",
                "import java.util.*;",
                "import java.math.*;",

            ]
        }

    def post_process(self, data:Dict, language: str, task_mode: str, dataset_name: str, **kwargs) -> Dict:
        generation = data["generation"]
        generation = generation if "</s>" not in generation else generation.split("</s>")[0]
        data["generation"] = data["complete_prompt"] + generation.replace("\t", "    ")
        return data

    

    