# codefuseEval: 代码大语言模型的多任务评估基准

codefuseEval在HumanEval-x、MBPP的基准上，结合CodeFuse大模型多任务场景，开发的编程领域多任务的评测基准， 可用于评估模型在代码补全，自然语言生成代码，测试用例生成、跨语言代码翻译，中文指令生成代码等多类任务的性能。

## 推理环境：
CodeFuse-13B: python 3.8及以上版本，pytorch 2.0及以上版本，transformers 4.24.0及以上版本，CUDA 11.4及以上；

CodeFuse-CodeLlama-34B: python 3.8及以上版本，pytorch2.0及以上版本，transformers==4.32.0 ，Sentencepiece，CUDA 11.4及以上。
## 推理命令：

```
bash codefuseEval/script/generation.sh MODELNAME EVALDATASET OUTFILE LANGUAGE
eg:
bash codefuseEval/script/generation.sh CodeFuse-13B humaneval_python result/test.jsonl python
```

🌐 <a href="README.md" target="_blank">English</a>

## 如何使用codefuseEval

### 评测数据集
样本使用JSON列表格式存储在``codefuseEval/data``中,根据用户所需的下游任务情况，每条样本包含

*   ``task_id``: 题目的目标语言与ID。语言为["Python", "Java", "JavaScript", "CPP", "Go"]中之一。
*   ``prompt``: 函数声明与描述，用于代码生成。
*   ``declaration``: 仅有函数声明，用于代码翻译。
*   ``canonical_solution``: 手写的示例解答。
*   ``test``: 隐藏测例，用于评测。
*   ``example_test``: 公共测试样本，用于评估生成代码。
*   ``prompt_text``: prompt文本情况。
*   ``prompt_explain``: prompt信息说明。
*   ``func_title``: 生成函数头信息。
*   ``prompt_text_chinese``: 中文prompt信息。

### 评测执行环境

评测生成的代码需要使用多种语言编译、运行。我们使用的各编程语言依赖及所用包的版本如下：

| 依赖    | 版本     |
| ------- | -------- |
| Python  | 3.8.12   |
| JDK     | 18.0.2.1 |
| Node.js | 16.14.0  |
| js-md5  | 0.7.3    |
| C++     | 11       |
| g++     | 7.5.0    |
| Boost   | 1.71.0   |
| OpenSSL | 3.0.0    |
| go      | 1.18.4   |

为了省去使用者配置这些语言环境的麻烦，我们构建了一个Docker镜像，并在其中配置了所需要的环境，你可以按照下面的指令拉取使用
```bash
docker pull registry.cn-hangzhou.aliyuncs.com/codefuse/codefuseeval:latest
```

如果您熟悉Dockerfile，也可以从`codefuseEval/docker/Dockerfile`构建镜像，或者修改之以定制自己的配置：

```bash
cd codefuseEval/docker
docker build [OPTIONS] .
```

获取镜像后，使用如下命令创建容器：

```bash
docker run -it --gpus all --mount type=bind,source=<LOCAL PATH>,target=<PATH IN CONTAINER> [OPTIONS] <IMAGE NAME:TAG>
```

### 评测指标
除了目前提供的[Codex](https://arxiv.org/abs/2107.03374) 中提出的无偏 pass@k 指标之外，我们还将huggingface开源的相关指标与[CodeBLEU](https://arxiv.org/abs/2009.10297)提出的相似性指标进行集成。
目前建议用户主要使用的指标如下：
*   ``codebleu``: codebleu相似性评测指标。
*   ``pass@k``: 无偏pass@k的评测指标。
*   ``bleu``: 文本相似性指标bleu
*   ``bleurt``: 文本语义相似性指标bleurt

其它的相关指标情况用户可以查看metric的使用情况与代码情况进行调整使用。

### 评测

我们推荐使用给定的[评测环境](#评测环境)进行评测。在评测前，将生成的代码以如下JSON列表形式存储：

```
{"task_id": "../..", "generation: "..."}
{"task_id": "../..", "generation: "..."}
...
```

### 评测命令：
```
bash codefuseEval/script/evaluation.sh <RESULT_FILE> <METRIC> <PROBLEM_FILE> <TEST_GROUDTRUTH>
eg: 
bash codefuseEval/script/evaluation.sh codefuseEval/result/test.jsonl pass@k humaneval_python 
```

并在本仓库的根目录下使用如下指令（<font color='red'>请谨慎执行，生成的代码可能有极低概率产生意外行为。在[execution.py](execution.py)中查看警告并取消执行代码的注释，风险自负</font>）：

同时我们当前提供如下的标志位，可以直接将测试数据集中的示例解答作为生成答案带入进行测试。
* ``TEST_GROUDTRUTH`` 取值为True或False

当TEST_GROUDTRUTH为True时，开启self-test模式，将读取PROBLEM_FILE，将示例解答作为生成答案代入进行测试。
TEST_GROUDTRUTH为False时，开启评测模式，读取RESULT_FILE和将读取PROBLEM_FILE，将生成答案代入进行测试

# 检查推理结果指令
我们提供脚本来检查所提供代码 LLM 的结果。请使用以下脚本检查相应的推理结果。
```
bash codefuseEval/script/check_reference.sh codefuseEval/result/CodeFuse-CodeLlama-34B/humaneval_result_python.jsonl humaneval_python
bash codefuseEval/script/check_reference.sh codefuseEval/result/CodeFuse-13B/humaneval_result_python.jsonl humaneval_python 
```

# 检查数据集及环境：
```bash
bash codefuseEval/script/check_dataset.sh humaneval_python

bash codefuseEval/script/check_dataset.sh humaneval_java

bash codefuseEval/script/check_dataset.sh humaneval_js

bash codefuseEval/script/check_dataset.sh humaneval_rust

bash codefuseEval/script/check_dataset.sh humaneval_go

bash codefuseEval/script/check_dataset.sh humaneval_cpp
```