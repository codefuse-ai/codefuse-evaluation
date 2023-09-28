''' CodefuseEval utility functions '''

import os
from typing import *
import gzip
import json

IMPORT_HELPER = {
    "python": [
        "from math import *",
        "import math",
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
        "from itertools import combinations_with_replacement",
        "import cmath",
        "import collections as ct",
        "import heapq as hq",
        "from collections import Counter",
        "from itertools import chain",
        "from heapq import heappop, heappush",
        "from operator import itemgetter",
        "from itertools import groupby",
        "from copy import deepcopy"

    ],
    "go": [
        "math",
        "strings",
        "fmt",
        "strconv",
        "time",
        "bytes",
        "regexp",
        "sort",
        "math/rand",
        "crypto/md5",
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
    ],
}

LANGUAGE_TAG = {
    "c": "// language: C",
    "c++": "// language: C++",
    "cpp": "// language: C++",
    "c#": "// language: C#",
    "csharp": "// language: C#",
    "css": "/* language: CSS */",
    "cuda": "// language: Cuda",
    "dart": "// language: Dart",
    "lua": "// language: Lua",
    "objectivec": "// language: Objective-C",
    "objective-c": "// language: Objective-C",
    "objective-c++": "// language: Objective-C++",
    "python": "# language: Python",
    "perl": "# language: Perl",
    "prolog": f"% language: Prolog",
    "swift": "// language: swift",
    "lisp": "; language: Lisp",
    "java": "// language: Java",
    "scala": "// language: Scala",
    "tex": f"% language: TeX",
    "vue": "<!--language: Vue-->",
    "markdown": "<!--language: Markdown-->",
    "html": "<!--language: HTML-->",
    "php": "// language: PHP",
    "js": "// language: JavaScript",
    "javascript": "// language: JavaScript",
    "typescript": "// language: TypeScript",
    "go": "// language: Go",
    "shell": "# language: Shell",
    "rust": "// language: Rust",
    "sql": "-- language: SQL",
    "kotlin": "// language: Kotlin",
    "vb": "' language: Visual Basic",
    "ruby": "# language: Ruby",
    "pascal": "// language: Pascal",
    "r": "# language: R",
    "fortran": "!language: Fortran",
    "lean": "-- language: Lean",
    "matlab": f"% language: Matlab",
    "delphi": "{language: Delphi}",
    "scheme": "; language: Scheme",
    "basic": "' language: Basic",
    "assembly": "; language: Assembly",
    "groovy": "// language: Groovy",
    "abap": "* language: Abap",
    "gdscript": "# language: GDScript",
    "haskell": "-- language: Haskell",
    "julia": "# language: Julia",
    "elixir": "# language: Elixir",
    "excel": "' language: Excel",
    "clojure": "; language: Clojure",
    "actionscript": "// language: ActionScript",
    "solidity": "// language: Solidity",
    "powershell": "# language: PowerShell",
    "erlang": f"% language: Erlang",
    "cobol": "// language: Cobol",
}


def read_dataset(
        data_file: str = None,
        dataset_type: str = "humaneval",
        num_shot=None,
) -> Dict:
    """
    read dataset file and return as a dictionary
    """
    if num_shot is not None:
        print(f"{num_shot}-shot setting...")
    if "humaneval" in dataset_type.lower():
        if data_file is None:
            current_path = os.path.dirname(os.path.abspath(__file__))
            # 补充一个默认数据集
            data_file = os.path.join(current_path, "data", "code_completion", "humaneval_python.jsonl")
        dataset = {task["task_id"]: task for task in stream_jsonl(data_file)}
    else:
        raise f"Dataset: {dataset_type} not supported."

    return dataset


def stream_jsonl(filename: str) -> Iterable[Dict]:
    """
    Parses each jsonl line and yields it as a dictionary
    """
    if filename.endswith(".gz"):
        with open(filename, "rb") as gzfp:
            with gzip.open(gzfp, "rt") as fp:
                for line in fp:
                    if any(not x.isspace() for x in line):
                        yield json.loads(line)
    else:
        with open(filename, "r") as fp:
            for line in fp:
                if any(not x.isspace() for x in line):
                    yield json.loads(line)


def is_contain_chinese(check_str):
    """
    Determine whether the string contains Chinese characters
    """
    for ch in check_str:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False
