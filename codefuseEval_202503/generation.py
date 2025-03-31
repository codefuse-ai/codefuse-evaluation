
import gzip
import logging
import os
import importlib
import json
from tqdm.auto import tqdm
import transformers
from typing import *
from data_registry import EVAL_DATASET, DATASET_SUPPORT, DATASET_LANGUAGE
from util import write_jsonl, create_logger
import fire
import time
import copy

# 模型全部注册信息
CKPT_CONFIG = json.load(open(os.path.join(os.path.dirname(__file__), "ckpt_config.json"), "r"))
transformers.logging.set_verbosity_error()


def load_dataset(file_path):
    """
    check dataset and load dataset
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"{file_path} not found")

    if not (file_path.endswith(".jsonl.gz") or file_path.endswith(".jsonl")):
        raise ValueError(f"{file_path} is not a jsonl file or jsonl.gz file")

    dataset = []
    if file_path.endswith(".jsonl.gz"):
        with gzip.open(file_path, "rt") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    dataset.append(data)
                except json.JSONDecodeError:
                    print(f"{line} is not a valid json")
    else:
        with open(file_path, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    dataset.append(data)
                except json.JSONDecodeError:
                    print(f"{line} is not a valid json")
    return dataset


def load_modelprocess(model_name, model_version, **kwargs):
    """
    load model process to load model and tokenizer && load dataset generator
    """
    path = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("generator_class", None)
    if "/" in path:
        module_path, class_name = path.rsplit("/", 1)
        module_path = module_path.split("generator")[1:]
        module_path = "generator".join(module_path).replace("/", ".")
    elif "." in path:
        module_path, class_name = path.rsplit(".", 1)
        module_path = module_path.split("generator")[1:]
        module_path = "generator".join(module_path)
    else:
        raise ValueError(f"{path} is invalid,can not find module and class")
    try:
        module = importlib.import_module(module_path, package="generator")
        module_class = getattr(module, class_name)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"module {module_path} can not find in package generator")
    except AttributeError:
        raise AttributeError(f"{path} can not find current class")
    kwargs["model_name"] = model_name
    kwargs["model_version"] = model_version
    return module_class(**kwargs)


def load_preprocess(model_name, model_version, **kwargs):
    """
    load model process to load model and tokenizer && load dataset generator
    """
    path = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("pre_processor_class", None)
    if "/" in path:
        module_path, class_name = path.rsplit("/", 1)
        module_path = module_path.split("pre_processor")[1:]
        module_path = "pre_processor".join(module_path).replace("/", ".")
    elif "." in path:
        module_path, class_name = path.rsplit(".", 1)
        module_path = module_path.split("pre_processor")[1:]
        module_path = "pre_processor".join(module_path)
    else:
        raise ValueError(f"{path} is invalid,can not find module and class")
    try:
        module = importlib.import_module(module_path, package="pre_processor")
        module_class = getattr(module, class_name)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"module {module_path} can not find in package pre_processor")
    except AttributeError:
        raise AttributeError(f"{path} can not find current class")
    kwargs["model_name"] = model_name
    kwargs["model_version"] = model_version
    return module_class(**kwargs)


def load_postprocess(model_name, model_version, **kwargs):
    """
    load model process to load model and tokenizer && load dataset generator
    """
    path = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("post_processor_class", None)
    if "/" in path:
        module_path, class_name = path.rsplit("/", 1)
        module_path = module_path.split("post_processor")[1:]
        module_path = "post_processor".join(module_path).replace("/", ".")
    elif "." in path:
        module_path, class_name = path.rsplit(".", 1)
        module_path = module_path.split("post_processor")[1:]
        module_path = "post_processor".join(module_path)
    else:
        raise ValueError(f"{path} is invalid,can not find module and class")
    try:
        module = importlib.import_module(module_path, package="post_processor")
        module_class = getattr(module, class_name)
    except ModuleNotFoundError:
        raise ModuleNotFoundError(f"module {module_path} can not find in package post_processor")
    except AttributeError:
        raise AttributeError(f"{path} can not find current class")
    kwargs["model_name"] = model_name
    kwargs["model_version"] = model_version
    return module_class(**kwargs)


def inference(model_name: str = "CodeFuse-CodeLlama-34B",
              model_version: str = "v1",
              eval_dataset: Union[str, List] = "humaneval_python",
              output_file: str = "default",
              task_mode: Union[str, List] = None,
              start: int = 0,
              end: int = 2,
              logger=None):
    """
    The main process for model to inference eval dataset and generate the result
    """
    if output_file == "default":
        if not os.path.exists("/mnt/evaluate_all"):
            os.makedirs("/mnt/evaluate_all")
        if isinstance(eval_dataset, str):
            output_file = f"/mnt/evaluate_all/{model_name}/{model_version}/{eval_dataset}-generation.jsonl"
        else:
            output_file = f"/mnt/evaluate_all/{model_name}/{model_version}/generation.jsonl"

    if not logger:
        logger = create_logger("generation", console_level=logging.INFO, file_level=logging.INFO)
    if isinstance(eval_dataset, str):
        if eval_dataset not in EVAL_DATASET:
            logger.error(
                f"{os.path.basename(__file__)}============eval_dataset {eval_dataset} not in [EVAL_DATASET]. please registry in data_registry.py")
            raise ValueError(f"eval_dataset {eval_dataset} not in [EVAL_DATASET]. please registry in data_registry.py")
        if eval_dataset not in DATASET_SUPPORT:
            logger.error(
                f"{os.path.basename(__file__)}============eval_dataset {eval_dataset} is not [DATASET_SUPPORT]. please registry in data_registry.py")
            raise ValueError(
                f"eval_dataset {eval_dataset} is not [DATASET_SUPPORT]. please registry in data_registry.py")
        if eval_dataset not in DATASET_LANGUAGE:
            logger.error(
                f"{os.path.basename(__file__)}============eval_dataset {eval_dataset} is not [DATASET_LANGUAGE]. please registry in data_registry.py")
            raise ValueError(
                f"eval_dataset {eval_dataset} is not [DATASET_LANGUAGE]. please registry in data_registry.py")
    elif isinstance(eval_dataset, list):
        if not all([dataset in EVAL_DATASET for dataset in eval_dataset]):
            illegal_dataset = [dataset for dataset in eval_dataset if dataset not in EVAL_DATASET]
            logger.error(
                f"{os.path.basename(__file__)}============eval_datasets {illegal_dataset} not in [EVAL_DATASET]. please registry in data_registry.py")
            raise ValueError(
                f"eval_datasets {illegal_dataset} not in [EVAL_DATASET]. please registry in data_registry.py")
        if not all([dataset in DATASET_SUPPORT for dataset in eval_dataset]):
            illegal_dataset = [dataset for dataset in eval_dataset if dataset not in DATASET_SUPPORT]
            logger.error(
                f"{os.path.basename(__file__)}============eval_datasets {illegal_dataset} is not [DATASET_SUPPORT]. please registry in data_registry.py")
            raise ValueError(
                f"eval_datasets {illegal_dataset} is not [DATASET_SUPPORT]. please registry in data_registry.py")
        if not all([dataset in DATASET_LANGUAGE for dataset in eval_dataset]):
            illegal_dataset = [dataset for dataset in eval_dataset if dataset not in DATASET_LANGUAGE]
            logger.error(
                f"{os.path.basename(__file__)}============eval_datasets {illegal_dataset} is not [DATASET_LANGUAGE]. please registry in data_registry.py")
            raise ValueError(
                f"eval_datasets {illegal_dataset} is not [DATASET_LANGUAGE]. please registry in data_registry.py")
    else:
        logger.error(f"{os.path.basename(__file__)}============eval_dataset parameter must be string or list")
        raise ValueError("eval_dataset parameter must be string or list")

    if task_mode is None:
        logger.info(
            f"{os.path.basename(__file__)}============[task_mode] parameter is None. Loading default task mode for corresponding dataset")
        if isinstance(eval_dataset, list):
            task_mode = [DATASET_SUPPORT.get(dataset)[0] for dataset in eval_dataset]
        if isinstance(eval_dataset, str):
            task_mode = DATASET_SUPPORT.get(eval_dataset)[0]
    # load and check dataset
    if not ((isinstance(eval_dataset, list) and isinstance(task_mode, list) and len(eval_dataset) == len(task_mode)
             and all([mode in DATASET_SUPPORT.get(dataset, []) for dataset, mode in zip(eval_dataset, task_mode)])) or
            (isinstance(eval_dataset, str) and isinstance(task_mode, str) and task_mode in DATASET_SUPPORT.get(
                eval_dataset, []))):
        logger.error(
            f"{os.path.basename(__file__)}============eval_dataset and task_mode must both be string or list. When both are list, the list length must be the same, "
            "and the task_mode must be among the task_modes supported by eval_datasets.")
        raise ValueError(
            "eval_dataset and task_mode must both be string or list. When both are list, the list length must be the same, "
            "and the task_mode must be among the task_modes supported by eval_datasets.")

    if CKPT_CONFIG.get(model_name, None) is None:
        logger.error(
            f"{os.path.basename(__file__)}============{model_name} not find in ckpt_config.json, please config model first")
        raise ValueError(f"{model_name} not find in ckpt_config.json, please config model first")
    if CKPT_CONFIG.get(model_name, {}).get(model_version, None) is None:
        logger.error(
            f"{os.path.basename(__file__)}============{model_version} not find in {model_name} in ckpt_config.json, please config model first")
        raise ValueError(f"{model_version} not find in {model_name} in ckpt_config.json, please config model first")

    if not isinstance(eval_dataset, list):
        eval_datasets = [eval_dataset]
        task_modes = [task_mode]
    else:
        eval_datasets = eval_dataset
        task_modes = task_mode

    # 如果是在线推理，检查配置的path路径, 路径存在，则进行模型load
    path = CKPT_CONFIG.get(model_name, {}).get("path", None)

    pre_processor_path = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("pre_processor_class", None)
    if pre_processor_path:
        pre_processor = load_preprocess(model_name, model_version)
    else:
        pre_processor = None
    post_processor_path = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("post_processor_class", None)
    if post_processor_path:
        post_processor = load_postprocess(model_name, model_version)
    else:
        post_processor = None
    logger.info(f"{os.path.basename(__file__)}============loading model========")
    st = time.time()
    generator = load_modelprocess(model_name, model_version, path=path)
    logger.info(f"{os.path.basename(__file__)}============Model load spend: {time.time() - st:.4f}s===========")
    print('Model load spend: {:.4f}s'.format(time.time() - st))

    generation_datasets = {}
    for evaldataset, task_mode in zip(eval_datasets, task_modes):
        language = DATASET_LANGUAGE.get(evaldataset)
        data_path = EVAL_DATASET.get(evaldataset)
        if data_path.startswith("http:") and evaldataset:  # 如果是 http 开头的，说明是 oss 地址，需要先下载评测数据集
            import subprocess
            save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "tmp", str(evaldataset))
            os.makedirs(save_dir, exist_ok=True)
            cmd = "wget -P {} {}".format(save_dir, data_path)
            print("cmd: {}".format(cmd))
            subprocess.run(cmd, shell=True, check=True)
            time.sleep(10)
            all_items = os.listdir(save_dir)
            files = [os.path.join(save_dir, item) for item in all_items if
                     os.path.isfile(os.path.join(save_dir, item)) and os.path.join(save_dir, item).endswith(".jsonl")]
            # todo 增加对文件MD5 的校验
            print("files: {}".format(files))
            print(subprocess.run("md5sum {}".format(files[0]), shell=True, check=True, stdout=subprocess.PIPE).stdout)
            data_path = files[0]
        if data_path is None:
            logger.error(
                f"{os.path.basename(__file__)}============{evaldataset} is not support, can not find current dataset information")
            raise ValueError(f"{evaldataset} is not support, can not find current dataset information")
        if not os.path.exists(data_path):
            logger.error(
                f"{os.path.basename(__file__)}============{evaldataset} corresponding data_path is {data_path}, file not exist")
            raise ValueError(f"{evaldataset} corresponding data_path is {data_path}, file not exist")
        if not DATASET_SUPPORT.get(evaldataset):
            logger.error(
                f"{os.path.basename(__file__)}============current dataset {evaldataset} not set support tasks, please set in data_registry.py")
            raise ValueError(f"current dataset {evaldataset} not set support tasks, please set in data_registry.py")
        logger.info(
            f"{os.path.basename(__file__)}============current generation task task mode is {task_mode}======================")

        dataset_origin = load_dataset(data_path)
        dataset_origin = dataset_origin[start:end]
        batch_size = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("batch_size", 1)
        sample_num = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("sample_num", 1)

        if pre_processor:
            if "mbpp" in evaldataset:
                if not CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("mbpp_mode"):
                    logger.info(
                        f"{os.path.basename(__file__)}============Can not find mbpp_mode, use default value 「mbpp_mode」is 「en」======================")
                    mbpp_mode = "en"
                else:
                    mbpp_mode = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get("mbpp_mode")
                all_prompt_list = pre_processor.pre_process(dataset_origin, language, task_mode, evaldataset,
                                                            mbpp_mode=mbpp_mode)
            elif "text2sql" == model_version or "fim" == model_version:
                all_prompt_list = pre_processor.pre_process(dataset_origin, language, task_mode, evaldataset,
                                                            model_name=model_name)
            else:
                all_prompt_list = pre_processor.pre_process(dataset_origin, language, task_mode, evaldataset)
        else:
            all_prompt_list = [data.get("prompt", None) for data in dataset_origin]

        eval_data = []
        if all_prompt_list or all(all_prompt_list):
            if len(all_prompt_list) % batch_size == 0:
                batch_num = len(all_prompt_list) // batch_size
            else:
                batch_num = len(all_prompt_list) // batch_size + 1
            batch_prompt_list = [all_prompt_list[batch_index * batch_size: (batch_index + 1) * batch_size] for
                                 batch_index in range(batch_num)]
            batch_dataset = [dataset_origin[batch_index * batch_size: (batch_index + 1) * batch_size] for batch_index in
                             range(batch_num)]
            index = 0
            for prompt_list in tqdm(batch_prompt_list):
                for _ in range(sample_num):
                    # 一个batch的推理时间，时间按照batch大小进行平均分配。
                    start_time = time.time()
                    logger.info(f"{os.path.basename(__file__)}*****************prompt_list:\n {prompt_list}")
                    try:
                        outputs = generator.generate(prompt_list, language, task_mode, evaldataset,
                                                     ckpt_config=CKPT_CONFIG)
                    except Exception as e:
                        logger.error("model generate error: error msg:{}".format(str(e)))
                        outputs = "ERROR"
                    logger.info(f"{os.path.basename(__file__)}*****************outputs:\n {outputs}")
                    endtime = time.time()
                    for num, (data, out) in enumerate(zip(batch_dataset[index], outputs)):
                        # 因为chat 的 prompt_real 中不会体现角色标签，增加 data["pre_processor_path"]帮助排查模型加载方式
                        data["pre_processor_path"] = CKPT_CONFIG.get(model_name, {}).get(model_version, {}).get(
                            "generator_class", None)
                        data["generation"] = out
                        data["generation_ori"] = copy.deepcopy(out)
                        data["processing_time"] = (endtime - start_time) / len(prompt_list)
                        data["prompt_real"] = prompt_list[num]
                        if post_processor:
                            data = post_processor.post_process(data, language, task_mode, evaldataset)
                        eval_data.append(data)
                        tempfile = output_file.replace(".jsonl", ".jsonl.temp")
                        if os.path.dirname(tempfile) and not os.path.exists(os.path.dirname(tempfile)):
                            os.makedirs(os.path.dirname(tempfile), exist_ok=True)  # 创建结果文件夹，避免因为文件夹不存在导致写入失败
                        with open(tempfile, "a") as f:
                            f.write(json.dumps(data, ensure_ascii=False) + "\n")
                    logger.info(
                        f"{os.path.basename(__file__)}*****************current batch size is {batch_size},current batch generation cost time is {endtime - start_time}")
                index += 1
            total_time_cost = sum([item.get("processing_time", 0) for item in eval_data])
            logger.info(f"{os.path.basename(__file__)}*****************Total time cost: {total_time_cost}")
            logger.info(
                f"{os.path.basename(__file__)}*****************Average time cost: {total_time_cost / len(eval_data)}")
            task_key = "#".join([model_name, model_version, evaldataset, task_mode])
            logger.info(f"{os.path.basename(__file__)}===============task_key:{task_key}")
            if task_key not in generation_datasets:
                generation_datasets[task_key] = eval_data
        else:
            logger.error(
                f"{os.path.basename(__file__)}============current prompt list is empty or all prompts are empty, "
                f"please check your dataset prompt {all_prompt_list}")
            raise ValueError("current prompt list is empty or all prompts are empty, "
                             "please check your dataset prompt", all_prompt_list)

    # 写入总数据文件，如果当前数据集大于1,分别写文件。
    write_list = []
    for _, value in generation_datasets.items():
        write_list.extend(value)
    write_jsonl(write_list, output_file)
    print("aistudio_oss_tool put", output_file)
    for key, value in generation_datasets.items():
        gen_model_name, gen_model_version, gen_evaldataset, gen_task_mode = key.split("#")
        file_name = os.path.join("/mnt/pipeline", gen_model_name, gen_model_version, gen_evaldataset,
                                 f"{gen_evaldataset}_{gen_task_mode}_generation.jsonl")
        write_jsonl(value, file_name)


if __name__ == "__main__":
    fire.Fire(inference)
