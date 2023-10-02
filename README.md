# CodeFuseEval: Multi-tasking Evaluation Benchmark for Code Large Language Model

<div align="center">

<p>
    <a href="https://github.com/codefuse-ai/codefuse-evaluation">
        <img alt="stars" src="https://img.shields.io/github/stars/codefuse-ai/codefuse-evaluation?style=social" />
    </a>
    <a href="https://github.com/codefuse-ai/codefuse-evaluation">
        <img alt="forks" src="https://img.shields.io/github/forks/codefuse-ai/codefuse-evaluation?style=social" />
    </a>
    <a href="https://github.com/codefuse-ai/codefuse-evaluation/issues">
      <img alt="Open Issues" src="https://img.shields.io/github/issues-raw/codefuse-ai/codefuse-evaluation" />
    </a>
</p>

[中文](README_CN.md) **｜** **English**

</div>

CodeFuseEval is a Code Generation benchmark that combines the multi-tasking scenarios of CodeFuse Model with the benchmarks of HumanEval-x and MBPP. This benchmark is designed to evaluate the performance of models in various multi-tasking tasks, including code completion, code generation from natural language, test case generation, cross-language code translation, and code generation from Chinese commands, among others.


## Generation environment：
CodeFuse-13B: Python 3.8 or above,PyTorch 1.12 or above, with a recommendation for 2.0 or above, Transformers 4.24.0 or above ,CUDA 11.4 or above (for GPU users and flash-attention users, this option should be considered).

CodeFuse-CodeLlama-34B:python>=3.8,pytorch>=2.0.0,transformers==4.32.0,Sentencepiece,CUDA 11.

## Generation Comand：

```
bash codefuseEval/script/generation.sh MODELNAME EVALDATASET OUTFILE LANGUAGE

eg:
bash codefuseEval/script/generation.sh CodeFuse-13B humaneval_python result/test.jsonl python
```

## How to use codefuseEval

### Evaluation Data
Data are stored in ``codefuseEval/data``, using JSON list format. We first integrated humaneval-X dataset.

*   ``task_id``: indicates the target language and ID of the problem. Language is one of ["Python", "Java", "JavaScript", "CPP", "Go"].
*   ``prompt``: the function declaration and docstring, used for code generation.
*   ``declaration``: only the function declaration, used for code translation. 
*   ``canonical_solution``: human-crafted example solutions.
*   ``test``: hidden test samples, used for evaluation
*   ``example_test``: public test samples (appeared in prompt), used for evaluation. 
*   ``prompt_text``: prompt text
*   ``prompt_explain``: prompt explanation
*   ``func_title``: code function title 
*   ``prompt_text_chinese``: Chinese prompt

### Evaluation Environment

The evaluation of the generated codes involves compiling and running in multiple programming languages. The versions of the programming language environments and packages we use are as follows:

| Dependency | Version  |
| ---------- | -------- |
| Python     | 3.8.12   |
| JDK        | 18.0.2.1 |
| Node.js    | 16.14.0  |
| js-md5     | 0.7.3    |
| C++        | 11       |
| g++        | 7.5.0    |
| Boost      | 1.71.0   |
| OpenSSL    | 3.0.0    |
| go         | 1.18.4   |

In order to save everyone the trouble of setting up the environments for these languages, we create a Docker image with the required environments and codefuseEval.
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/codefuse/codefuseeval:latest
```

If you are familiar with docker, you can build the image from `codefuseEval/docker/Dockerfile` or configure the Dockerfile as you like it:

```bash
cd codefuseEval/docker
docker build [OPTIONS] .
```

After obtaining the image, you can build a container using the following command:

```bash
docker run -it --gpus all --mount type=bind,source=<LOCAL PATH>,target=<PATH IN CONTAINER> [OPTIONS] <IMAGE NAME:TAG>
```

### Evaluation Metrics
In addition to the unbiased pass@k indicators currently provided in [Codex](https://arxiv.org/abs/2107.03374), we will also integrate the relevant indicators of huggingface open source with [CodeBLEU](https://arxiv.org/abs/2009.10297) for integration.
The main indicators currently recommended for users are as follows:
*   ``codebleu``
*   ``pass@k``
*   ``bleu``
*   ``bleurt``

For other related metrics, you can check the code of the metric or the evaluation code to meet your requirements.

### Evaluation

We recommend evaluating in [the provided image](#evaluation-environment). To evaluate the generated samples, save generated codes in the following JSON list format:

```
{"task_id": "../..", "generation: "..."}
{"task_id": "../..", "generation: "..."}
...
```

and evaluate them using the following script under the root directory of the repository (<font color='red'>please execute with caution, the generated codes might have unexpected behaviours though with very low possibility. See the warnings in [execution.py](execution.py) and uncomment the execution lines at your own risk</font>):

```
bash codefuseEval/script/evaluation.sh <RESULT_FILE> <METRIC> <PROBLEM_FILE> <TEST_GROUDTRUTH>
eg: 
bash codefuseEval/script/evaluation.sh codefuseEval/result/test.jsonl pass@k humaneval_python
```

At the same time, we currently provide the following flags, which can directly bring the sample answers in the test data set as generated answers for testing.

* ``TEST_GROUDTRUTH`` default False

When TEST_GROUDTRUTH is True, the self-test mode is turned on, PROBLEM_FILE will be read, and the sample answer will be substituted as the generated answer for testing.

When TEST_GROUDTRUTH is False, open the evaluation mode, read RESULT_FILE and PROBLEM_FILE, and substitute the generated answer for testing.

# Check result Command：
We provide the script to check the result for provided code LLMs. Please use following scripts to check corresponding results and the environment .

```bash
bash codefuseEval/script/check_reference.sh codefuseEval/result/CodeFuse-CodeLlama-34B/humaneval_result_python.jsonl humaneval_python
bash codefuseEval/script/check_reference.sh codefuseEval/result/CodeFuse-13B/humaneval_result_python.jsonl humaneval_python 

```

# Check dataset Command：
```bash
bash codefuseEval/script/check_dataset.sh humaneval_python

bash codefuseEval/script/check_dataset.sh humaneval_java

bash codefuseEval/script/check_dataset.sh humaneval_js

bash codefuseEval/script/check_dataset.sh humaneval_rust

bash codefuseEval/script/check_dataset.sh humaneval_go

bash codefuseEval/script/check_dataset.sh humaneval_cpp
```


