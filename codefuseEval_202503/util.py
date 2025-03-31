''' CodefuseEval utility functions '''

from typing import *
import gzip
import json
import os
import logging
import oss2

# import lib for current language
IMPORT_HELPER = {
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
        "using namespace std;",
        "#include<cassert>",
        "#include<stdlib.h>",
        "#include<algorithm>",
        "#include<cmath>",
        "#include<math.h>",
        "#include<numeric>",
        "#include<stdio.h>",
        "#include<vector>",
        "#include<set>",
        "#include<map>",
        "#include<queue>",
        "#include<stack>",
        "#include<list>",
        "#include<deque>",
        "#include<boost/any.hpp>",
        "#include<string>",
        "#include<climits>",
        "#include<cstring>",
        "#include<iostream>",
        "#include<sstream>",
        "#include<fstream>",
    ],
    "java": [
        "import java.io.*;",
        "import java.lang.*;",
        "import java.util.*;",
        "import java.math.*;",
    ],
    "java_mbpp": [
        "import java.util.*;",
        "import java.lang.reflect.*;",
        "import org.javatuples.*;",
        "import java.security.*;",
        "import java.math.*;",
        "import java.io.*;",
        "import java.util.stream.*;",
    ],
    "cs": [
        "using System;",
        "using System.Numerics;",
        "using System.Diagnostics;",
        "using System.Collections.Generic;",
        "using System.Linq;",
        "using System.Text;",
        "using System.Security.Cryptography;",
        "using System.Collections.Generic;",
    ]
}


#eval dataset registry, support jsonlfile or jsonl.gz file

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


def get_gopackages(code):
    """
    The main purpose is to extract go package information and then diagnose the usage of the package.
    If the current package is not used, delete it directly to improve the compilation pass rate.
    Args:
    code: The golang code.
    Returns:
    The golang code import libs list.
    """
    code_line = code.split("\n")
    packages = []
    start_import = False
    for line in code_line:
        if "import" in line:
            if "(" in line:
                start_import = True
                continue
            else:
                packages.append(line.split(" ")[1][1:-1])
        if start_import:
            if ")" in line:
                start_import = False
                continue
            temp_line = line.split(",")[0].strip()
            if temp_line == "":
                continue
            if temp_line.startswith("\"") or temp_line.startswith("\'"):
                if temp_line.endswith("\"") or temp_line.endswith("\'"):
                    packages.append(temp_line[1:-1])
                else:
                    packages.append(temp_line[1:])
            else:
                packages.append(line.split(",")[0].strip())
    return packages


def write_jsonl(data, output_path):
    """
    write data in a jsonl file
    """
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    write_data = []
    for item in data:
        try:
            data = json.dumps(item, ensure_ascii=False)
            write_data.append(data)
        except Exception as e:
            print(f"fail to dumps lines,the line is {item}")
    with open(output_path, "w", encoding='utf-8') as f:
        f.write("\n".join(write_data))


def create_logger(name, console_level=logging.INFO, file_level=logging.INFO):
    os.makedirs("logs", exist_ok=True)
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # 创建处理器 - 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)

    # 创建处理器 - 文件处理器
    file_handler = logging.FileHandler(f'logs/{name}.log')
    file_handler.setLevel(file_level)

    # 创建并设置格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将处理器添加到 Logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
