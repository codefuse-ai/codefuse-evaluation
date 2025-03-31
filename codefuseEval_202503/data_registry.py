# Copyright (c) 2022-2025 Ant Group
import os

EVAL_DATASET = {
    "humaneval_python": os.path.join(os.path.dirname(__file__), "data", "code_completion", "humaneval_python.jsonl"),
    "mbpp_x": os.path.join(os.path.dirname(__file__), "data", "nl2code", "mbpp_x.jsonl"),

    "evalPlus_mbpp": os.path.join(os.path.dirname(__file__), "data", "nl2code", "EvalPlus_MBPP_Python.jsonl"),
    "evalPlus_humaneval": os.path.join(os.path.dirname(__file__), "data", "code_completion", "EvalPlus_HumanEval_Python.jsonl"),

    "mbxp_cpp": os.path.join(os.path.dirname(__file__), "data", "mbxp", "mbcpp_text_code_result100_new.jsonl"),
    "mbxp_java": os.path.join(os.path.dirname(__file__), "data", "mbxp", "mbjava_text_code_result100_new.jsonl"),
    "mbxp_js": os.path.join(os.path.dirname(__file__), "data", "mbxp", "mbjsp_text_code_result100_new.jsonl"),
    "mbxp_ts": os.path.join(os.path.dirname(__file__), "data", "mbxp", "mbtsp_text_code_result100_new.jsonl"),
    "mbxp_go": os.path.join(os.path.dirname(__file__), "data", "mbxp", "mbgo_text_code_result100_new.jsonl"),
    "mbxp_php": os.path.join(os.path.dirname(__file__), "data", "mbxp", "mbphp_text_code_result100_new.jsonl"),

    "humanevalfix_python": os.path.join(os.path.dirname(__file__), "data", "code_fix", "humanevalfix_python.jsonl"),
    "humanevalfix_js": os.path.join(os.path.dirname(__file__), "data", "code_fix", "humanevalfix_js.jsonl"),
    "humanevalfix_java": os.path.join(os.path.dirname(__file__), "data", "code_fix", "humanevalfix_java.jsonl"),
    "humanevalfix_go": os.path.join(os.path.dirname(__file__), "data", "code_fix", "humanevalfix_go.jsonl"),
    "humanevalfix_rust": os.path.join(os.path.dirname(__file__), "data", "code_fix", "humanevalfix_rust.jsonl"),
    "humanevalfix_cpp": os.path.join(os.path.dirname(__file__), "data", "code_fix", "humanevalfix_cpp.jsonl"),

    "spider_test": os.path.join(os.path.dirname(__file__), "data", "text2sql", "spider", "spider-test.jsonl"),

    "MultiPL-E-Humaneval-cpp": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_cpp.jsonl"),
    "MultiPL-E-Humaneval-cs": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_cs.jsonl"),
    "MultiPL-E-Humaneval-java": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_java.jsonl"),
    "MultiPL-E-Humaneval-js": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_js.jsonl"),
    "MultiPL-E-Humaneval-php": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_php.jsonl"),
    "MultiPL-E-Humaneval-python": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_python.jsonl"),
    "MultiPL-E-Humaneval-sh": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_sh.jsonl"),
    "MultiPL-E-Humaneval-ts": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_ts.jsonl"),
    "MultiPL-E-Humaneval-rs": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_rs.jsonl"),
    "MultiPL-E-Humaneval-go": os.path.join(os.path.dirname(__file__), "data", "multie_humaneval", "qwen_multiple_humaneval_go.jsonl"),

    "MultiPL-E-MBPP-cpp": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_cpp.jsonl"),
    "MultiPL-E-MBPP-cs": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_cs.jsonl"),
    "MultiPL-E-MBPP-java": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_java.jsonl"),
    "MultiPL-E-MBPP-js": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_js.jsonl"),
    "MultiPL-E-MBPP-php": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_php.jsonl"),
    "MultiPL-E-MBPP-python": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_python.jsonl"),
    "MultiPL-E-MBPP-sh": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_sh.jsonl"),
    "MultiPL-E-MBPP-ts": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_ts.jsonl"),
    "MultiPL-E-MBPP-go": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_go.jsonl"),
    "MultiPL-E-MBPP-rust": os.path.join(os.path.dirname(__file__), "data", "multie_mbpp", "mbpp_rust.jsonl"),

    "bigcodebench_full": os.path.join(os.path.dirname(__file__), "data", "bigcodebench", "bigcodebench-full.jsonl"),
    "bigcodebench_hard": os.path.join(os.path.dirname(__file__), "data", "bigcodebench", "bigcodebench-hard.jsonl"),

    "livecodebench_easy_add": os.path.join(os.path.dirname(__file__), "data", "LiveCodeBench", "easy_add.jsonl"),
    "livecodebench_medium_add": os.path.join(os.path.dirname(__file__), "data", "LiveCodeBench", "medium_add.jsonl"),
    "livecodebench_hard_add": os.path.join(os.path.dirname(__file__), "data", "LiveCodeBench", "hard_add.jsonl"),

    "crux-O-input": os.path.join(os.path.dirname(__file__), "data", "CRUX-O", "CRUX-O.jsonl"),
    "crux-O-output": os.path.join(os.path.dirname(__file__), "data", "CRUX-O", "CRUX-O.jsonl"),
}

DATASET_SUPPORT = {
    "humaneval_python": ["code_completion"],
    "mbpp_x": ["text-to-code"],

    "evalPlus_humaneval": ["code_completion"],
    "evalPlus_mbpp": ["text-to-code"],

    "mbxp_cpp": ["text_code"],
    "mbxp_java": ["text_code"],
    "mbxp_js": ["text_code"],
    "mbxp_ts": ["text_code"],
    "mbxp_go": ["text_code"],
    "mbxp_php": ["text_code"],

    "humanevalfix_python": ["code_fix"],
    "humanevalfix_js": ["code_fix"],
    "humanevalfix_java": ["code_fix"],
    "humanevalfix_go": ["code_fix"],
    "humanevalfix_rust": ["code_fix"],
    "humanevalfix_cpp": ["code_fix"],

    "spider_test": ["text-to-sql"],

    "MultiPL-E-Humaneval-cpp": ["code-completion"],
    "MultiPL-E-Humaneval-cs": ["code-completion"],
    "MultiPL-E-Humaneval-java": ["code-completion"],
    "MultiPL-E-Humaneval-js": ["code-completion"],
    "MultiPL-E-Humaneval-php": ["code-completion"],
    "MultiPL-E-Humaneval-python": ["code-completion"],
    "MultiPL-E-Humaneval-sh": ["code-completion"],
    "MultiPL-E-Humaneval-ts": ["code-completion"],
    "MultiPL-E-Humaneval-rs": ["code-completion"],
    "MultiPL-E-Humaneval-go": ["code-completion"],

    "MultiPL-E-MBPP-cpp": ["code-completion"],
    "MultiPL-E-MBPP-cs": ["code-completion"],
    "MultiPL-E-MBPP-java": ["code-completion"],
    "MultiPL-E-MBPP-js": ["code-completion"],
    "MultiPL-E-MBPP-php": ["code-completion"],
    "MultiPL-E-MBPP-python": ["code-completion"],
    "MultiPL-E-MBPP-sh": ["code-completion"],
    "MultiPL-E-MBPP-go": ["code-completion"],
    "MultiPL-E-MBPP-rust": ["code-completion"],
    "MultiPL-E-MBPP-ts": ["code-completion"],

    "bigcodebench_full": ["text_code"],
    "bigcodebench_hard": ["text_code"],

    "livecodebench_easy_add": ["text_code"],
    "livecodebench_medium_add": ["text_code"],
    "livecodebench_hard_add": ["text_code"],

    "crux-O-input": ["code_infer"],
    "crux-O-output": ["code_infer"]
}

DATASET_LANGUAGE = {
    "humaneval_python": "python",
    "mbpp_x": "python",

    "evalPlus_humaneval": "python",
    "evalPlus_mbpp": "python",

    "mbxp_cpp": "cpp",
    "mbxp_java": "java",
    "mbxp_js": "js",
    "mbxp_ts": "ts",
    "mbxp_go": "go",
    "mbxp_php": "php",

    "humanevalfix_python": "python",
    "humanevalfix_js": "js",
    "humanevalfix_java": "java",
    "humanevalfix_go": "go",
    "humanevalfix_rust": "rust",
    "humanevalfix_cpp": "cpp",

    "spider_test": "sql",

    "MultiPL-E-Humaneval-cpp": "cpp",
    "MultiPL-E-Humaneval-cs": "cs",
    "MultiPL-E-Humaneval-java": "java",
    "MultiPL-E-Humaneval-js": "js",
    "MultiPL-E-Humaneval-php": "php",
    "MultiPL-E-Humaneval-python": "python",
    "MultiPL-E-Humaneval-sh": "shell",
    "MultiPL-E-Humaneval-ts": "ts",
    "MultiPL-E-Humaneval-rs": "rust",
    "MultiPL-E-Humaneval-go": "go",

    "MultiPL-E-MBPP-cpp": "cpp",
    "MultiPL-E-MBPP-cs": "cs",
    "MultiPL-E-MBPP-java": "java",
    "MultiPL-E-MBPP-js": "js",
    "MultiPL-E-MBPP-php": "php",
    "MultiPL-E-MBPP-python": "python",
    "MultiPL-E-MBPP-sh": "shell",
    "MultiPL-E-MBPP-ts": "ts",
    "MultiPL-E-MBPP-go": "go",
    "MultiPL-E-MBPP-rust": "rust",

    "bigcodebench_full": "python",
    "bigcodebench_hard": "python",

    "livecodebench_easy_add": "python",
    "livecodebench_medium_add": "python",
    "livecodebench_hard_add": "python",

    "crux-O-input": "python",
    "crux-O-output": "python"
}
