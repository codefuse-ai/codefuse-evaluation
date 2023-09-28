''' inference scripts '''
import os
import torch
import sys
import time
from tqdm import tqdm
import re
import json
import gzip
import fire
from copy import deepcopy
import transformers

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoConfig,
    LlamaTokenizer,
    LlamaForCausalLM,
    GenerationConfig
)

transformers.logging.set_verbosity_error()

HUMAN_ROLE_START_TAG = "<|role_start|>human<|role_end|>"
BOT_ROLE_START_TAG = "<|role_start|>bot<|role_end|>"

LANGUAGE_TAG = {
    "c++": "// language: C++",
    "numpy": "# language: Python",
    "Pandas": "# language: Python",
    "Pytorch": "# language: Python",
    "Scipy": "# language: Python",
    "Sklearn": "# language: Python",
    "Tensorflow": "# language: Python",
    "matplotlib": "# language: Python",
    "cpp": "// language: C++",
    "c": "// language: C",
    "csharp": "// language: C#",
    "cs": "// language: C#",
    "c#": "// language: C#",
    "cuda": "// language: Cuda",
    "objective-c": "// language: Objective-C",
    "objective-c++": "// language: Objective-C++",
    "python": "# language: Python",
    "perl": "# language: Perl",
    "java": "// language: Java",
    "scala": "// language: Scala",
    "tex": f"% language: TeX",
    "html": "<!--language: HTML-->",
    "php": "// language: PHP",
    "js": "// language: JavaScript",
    "javascript": "// language: JavaScript",
    "typescript": "// language: TypeScript",
    "go": "// language: Go",
    "shell": "# language: Shell",
    "rust": "// language: Rust",
    "css": "/* language: CSS */",
    "sql": "-- language: SQL",
    "kotlin": "// language: Kotlin",
    "pascal": "// language: Pascal",
    "r": "# language: R",
    "fortran": "!language: Fortran",
    "lean": "-- language: Lean",
}

EVAL_DATASET = {
    "humaneval_python": os.path.join(os.path.dirname(__file__), "data", "code_completion", "humaneval_python.jsonl"),
    "humaneval_js": os.path.join(os.path.dirname(__file__), "data", "code_completion", "humaneval_js.jsonl"),
    "humaneval_java": os.path.join(os.path.dirname(__file__), "data", "code_completion", "humaneval_java.jsonl"),
    "humaneval_go": os.path.join(os.path.dirname(__file__), "data", "code_completion", "humaneval_go.jsonl"),
    "humaneval_rust": os.path.join(os.path.dirname(__file__), "data", "code_completion", "humaneval_rust.jsonl"),
    "humaneval_cpp": os.path.join(os.path.dirname(__file__), "data", "code_completion", "humaneval_cpp.jsonl")
}


def get_tc_prompt(mbpp_mode, item):
    if mbpp_mode == "en":  # 英文原版
        prompt = item["prompt"] + "Your code should satisfy these tests:\n" + "\n".join(item["test"])
    elif mbpp_mode == "cn":  # 中文原版
        prompt = item["prompt_text_chinese"] + "你的代码必须能够通过这些测试用例:\n" + "\n".join(item["test"])
    else:
        raise ValueError("unknown mbpp_mode, en or cn expected.")
    return prompt


def load_model_tokenizer(path, model_name):
    print("********* path *********")
    print("path========: ", path)
    print("model_name========: ", model_name)
    st = time.time()
    if model_name == "CodeFuse-CodeLlama-34B":
        tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True, use_fast=False, legacy=False)
        tokenizer.eos_token = "</s>"
        tokenizer.pad_token = "<unk>"
        tokenizer.eos_id = tokenizer._convert_token_to_id(tokenizer.eos_token)
        tokenizer.pad_id = tokenizer._convert_token_to_id(tokenizer.pad_token)
        tokenizer.padding_side = "left"
        print(tokenizer)
        print(f"eos_token_id: {tokenizer.eos_token_id}, pad_token_id: {tokenizer.pad_token_id}")
        config, unused_kwargs = AutoConfig.from_pretrained(path, trust_remote_code=True, return_unused_kwargs=True)
        config_dict = config.to_dict()
        config_dict["use_flash_attn"] = 1
        config_dict["use_xformers"] = 1

        model = AutoModelForCausalLM.from_pretrained(path, config=config, device_map="auto", torch_dtype=torch.bfloat16,
                                                     trust_remote_code=True, use_safetensors=False)

        print("ids========: ")
        print(tokenizer.eos_id, tokenizer.pad_id)

    elif model_name == "CodeFuse-13B":
        tokenizer = AutoTokenizer.from_pretrained(path)
        model = AutoModelForCausalLM.from_pretrained(path, load_in_8bit=False, torch_dtype=torch.float16,
                                                     device_map="auto")
        model.config.pad_token_id = tokenizer.pad_token_id
        model.half()
        model.eval()
        if torch.__version__ >= "2" and sys.platform != "win32":
            model = torch.compile(model)
    else:
        raise ValueError("unknown model_name, CodeFuse-CodeLlama-34B and CodeFuse-13B supported.")

    print("loading model========  ")
    print('Model load spend: {:.4f}s'.format(time.time() - st))
    print(tokenizer)

    return model, tokenizer


def generate_outputs(model, tokenizer, prompt_list, decode_mode, temperature, model_name):
    if model_name == "CodeFuse-13B":
        print(tokenizer.pad_token_id)
        generation_config = GenerationConfig(
            pad_token_id=tokenizer.pad_token_id,
            temperature=temperature,
            max_new_tokens=600,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            num_beams=3,
            top_p=0.95
        )
        inputs = tokenizer(prompt_list, return_tensors="pt", truncation=True, padding=True, max_length=600).to("cuda")
    else:
        generation_config = GenerationConfig(
            pad_token_id=tokenizer.pad_token_id,
            temperature=temperature,
            max_new_tokens=512,
            num_return_sequences=1,
            eos_token_id=tokenizer.eos_token_id,
            num_beams=1,
            top_p=0.9
        )
        inputs = tokenizer(prompt_list, return_tensors="pt", padding=True, add_special_tokens=False).to("cuda")

    if decode_mode == "greedy":
        generation_config.do_sample = False
        generation_config.num_beams = 1
        generation_config.max_new_tokens = 512
    elif decode_mode == "beams":
        generation_config.do_sample = False
        generation_config.num_beams = 5
        generation_config.max_new_tokens = 600
        generation_config.num_return_sequences = 1
    else:
        raise ValueError("unknown decode_mode, only support greedy and beams.")

    generate_ids = model.generate(
        inputs=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        **generation_config.to_dict()
    )

    outputs = tokenizer.batch_decode(generate_ids[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return outputs


def stop_word_post_process(stop_words, trg_prediction):
    for stop_word in stop_words:
        if stop_word in trg_prediction:
            trg_prediction = trg_prediction.split(stop_word)[0]

    return trg_prediction


def post_process_mkcode(language, data):
    print("********* post_process_mkcode *********")
    print(data)
    re_result = re.findall(f"```{language}(.*?)```", data, re.DOTALL | re.IGNORECASE)
    if len(re_result) > 0:
        data = re.sub(f'```{language}|```', '', re_result[0], flags=re.IGNORECASE)
    if "import" in data:
        end_id = 0
        if '"""' in data:
            first_id = data.find('"""') + 3
            end_id = data.find('"""', first_id) + 3
            data = data[end_id:]
        elif "'''" in data:
            first_id = data.find("'''") + 3
            end_id = data.find("'''", first_id) + 3
            data = data[end_id:]
        else:
            new_line = "\n".join([word for word in data.strip().split("\n") if
                                  not word.startswith("def") and not word.startswith("from")])
            data = new_line
    data = data.replace('<|endoftext|>', '')

    return data


def generate_prompt(language, input):
    INSTRUCTION = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Create a {language} script for this problem:
{input}

### Response:"""
    return INSTRUCTION


def load_data(eval_dataset):
    data = []
    data_path = EVAL_DATASET.get(eval_dataset)
    if not data_path:
        raise ValueError("unknown eval_dataset")
    try:
        with gzip.open(data_path, "r") as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error processing line: {line}")
                    print(e)
    except gzip.BadGzipFile:
        with open(data_path, "r") as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Error processing line: {line}")
                    print(e)
    return data


def process_generation(generated_code, language):
    code = generated_code
    if language == "python" or language == "matplotlib" or language == "numpy" or language == "Pandas":
        generation = ""
        for line in code.split("\n"):
            if line and line[0] != ' ':
                break
            generation += line + "\n"

    elif language == "cpp":
        generation = ""
        for line in code.split("\n"):
            if line and line.startswith("int main"):
                break
            generation += line + "\n"

    elif language == "js" or language == "java" or language == "go" or language == "rust":
        generation = ""
        for line in code.split("\n"):
            generation += line + "\n"
            if line == "}" or line == "};":
                break
    else:
        generation = code
    return generation


def extract_code_from_response(output_ori):
    response_start = "### Response:"
    print(output_ori)
    response_index = output_ori.find(response_start)
    if response_index == -1:
        return output_ori
    code = output_ori[response_index + len(response_start):]
    return code


def write_jsonl(data, output_path):
    output_dir = os.sep.join(output_path.split(os.sep)[:-1])
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_path, "w", encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return


def inference(model, tokenizer, eval_dataset, model_name, decode_mode, sample_num, batch_size, temperature, task_mode,
              mbpp_mode, language):
    data = load_data(eval_dataset)
    eval_data = []
    prompt_list = []
    item_list = []
    count = 0
    for item in tqdm(data):
        # modify prompt
        if model_name == "CodeFuse-13B":
            # 代码续写
            if task_mode == "code_completion":
                prompt_origin = item["prompt"].replace('    ', '\t')
                prompt = generate_prompt(language, prompt_origin)
            else:  # 自然语言到代码、其他
                prompt = item["prompt"]
        else:  # model_name = "CodeFuse-CodeLlama-34B":
            # 代码续写
            if task_mode == "code_completion":
                language_tag = LANGUAGE_TAG[language]
                prompt_origin = language_tag + "\n" + item["prompt"]
                prompt = HUMAN_ROLE_START_TAG + prompt_origin + BOT_ROLE_START_TAG
            # 自然语言到代码
            elif task_mode == "text_to_code":
                prompt_origin = get_tc_prompt(mbpp_mode, item)
                prompt = HUMAN_ROLE_START_TAG + prompt_origin + BOT_ROLE_START_TAG
            else:
                prompt = item["prompt"]
        print(item["task_id"] + "\n" + prompt)

        # generate outputs
        item_list.append(item)
        prompt_list.append(prompt)
        count += 1
        if prompt_list and len(prompt_list) % batch_size == 0 or count == len(prompt_list):
            # sample_num: 对同一prompt生成几个不同的答案
            for _ in range(sample_num):
                outputs = generate_outputs(model, tokenizer, prompt_list, decode_mode, temperature, model_name)
                print(f"outputs*******:\n {outputs}")
                for idx, a_prompt in enumerate(prompt_list):
                    print(f"********* prompt *********:\n{a_prompt}")
                    output_ori = outputs[idx]
                    print(f"********* before data *********:\n{output_ori}")
                    # 代码补全场景
                    if task_mode == "code_completion":
                        if model_name == "CodeFuse-13B":
                            generation = extract_code_from_response(output_ori).replace('\t', '    ')
                            generation = post_process_mkcode(language, generation)
                        else:
                            generation = output_ori
                            generation = post_process_mkcode(language, generation)
                            generation = process_generation(generation, language)

                    else:
                        generation = post_process_mkcode(language, output_ori)
                    print(f"********* generation *********:\n{generation}")
                    new_item = deepcopy(item_list[idx])
                    new_item["generation"] = generation

                    eval_data.append(new_item)

            prompt_list = []
            item_list = []
    return eval_data


def main(
        ## 必填参数
        # 数据集相关
        eval_dataset: str = "mbpp",
        # 模型相关
        model_name: str = 'CodeFuse-CodeLlama-34B',
        # 推理结果存储位置
        output_file: str = "result.jsonl",

        ## 非必填
        # 运行相关
        batch_size: int = 1,
        # 模型相关
        temperature: float = 0.2,
        decode_mode: str = 'beams',
        sample_num: int = 1,
        # 推理场景相关
        # 推理场景，代码续写：code_completion, 自然语言到代码：text_to_code
        task_mode: str = "code_completion",
        # 自然语言语种，支持en和cn
        mbpp_mode: str = "en",
        # 编程语言类型
        language: str = "python"
):
    print("********* params *********")
    print(
        f"eval_dataset={eval_dataset}, model_name={model_name}, decode_mode={decode_mode}, sample_num={sample_num}, "
        f"batch_size={batch_size}, temperature={temperature}, language={language}, output_file={output_file},"
        f" task_mode={task_mode}, mbpp_mode={mbpp_mode}")

    ckpt_dict = json.load(open("codefuseEval/ckpt_config.json"))
    ckpt_path = ckpt_dict[model_name]
    if not ckpt_path:
        raise ValueError("unknown ckpt_version")
    if not output_file.endswith(".jsonl"):
        raise ValueError("output file should be jsonl")

    print("Using {} ckpt version, is chat: {}, output file: {}".format(model_name, decode_mode, output_file))

    # load tokenizer
    model, tokenizer = load_model_tokenizer(ckpt_path, model_name)

    # generation outputs
    eval_data = inference(
        model, tokenizer, eval_dataset, model_name, decode_mode, sample_num, batch_size, temperature, task_mode,
        mbpp_mode, language
    )

    # persist result
    _ = write_jsonl(eval_data, output_file)


if __name__ == "__main__":
    fire.Fire(main)
