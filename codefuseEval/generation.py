import gzip
import os
import importlib
import json
from tqdm.auto import tqdm
import transformers
from transformers import GenerationConfig
from copy import deepcopy
from util import EVAL_DATASET, DATASET_SUPPORT, ALL_DECODE_MODE, DATASET_LANGUAGE, write_jsonl
import fire
import time
import numpy as np

# model information and evaluation configs
CKPT_CONFIG = json.load( open( os.path.join( os.path.dirname( __file__ ), "ckpt_config.json" ), "r" ) )
transformers.logging.set_verbosity_error()


def load_dataset(file_path):
    """
    check dataset and load dataset
    """
    if not os.path.exists( file_path ):
        raise FileNotFoundError( f"{file_path} not found" )

    if not (file_path.endswith( ".jsonl.gz" ) or file_path.endswith( ".jsonl" )):
        raise ValueError( f"{file_path} is not a jsonl file or jsonl.gz file" )

    dataset = []
    if file_path.endswith( ".jsonl.gz" ):
        with gzip.open( file_path, "rt" ) as f:
            for line in f:
                try:
                    data = json.loads( line )
                    dataset.append( data )
                except json.JSONDecodeError:
                    print( f"{line} is not a valid json" )
    else:
        with open( file_path, "r" ) as f:
            for line in f:
                try:
                    data = json.loads( line )
                    dataset.append( data )
                except json.JSONDecodeError:
                    print( f"{line} is not a valid json" )
    return dataset


def load_modelprocess(model_name, model_version, *args, **kwargs):
    """
    load model process to load model and tokenizer && load dataset processor
    """
    path = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "processor_class", None )
    if "/" in path:
        module_path, class_name = path.rsplit( "/", 1 )
        module_path = module_path.split( "processor" )[1:]
        module_path = "processor".join( module_path ).replace( "/", "." )
    elif "." in path:
        module_path, class_name = path.rsplit( ".", 1 )
        module_path = module_path.split( "processor" )[1:]
        module_path = "processor".join( module_path )
    else:
        raise ValueError( f"{path} is invalid,can not find module and class" )
    try:
        module = importlib.import_module( module_path, package="processor" )
        module_class = getattr( module, class_name )
    except ModuleNotFoundError:
        raise ModuleNotFoundError( f"module {module_path} can not find in package processor" )
    except AttributeError:
        raise AttributeError( f"{path} can not find current class" )
    return module_class( *args, **kwargs )


def generate_outputs(model, tokenizer, prompt_list, model_name, model_version):
    """
    Generate outputs based on model information and prompts
    """
    decode_mode = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "decode_mode", "dosample" )
    generate_config = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "generation_config", {} )
    tokenizer_param = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "tokenizer", {} )
    if not generate_config:
        print( "Can not find generate_config in config.json,use default config!!!!!" )
        generation_config = GenerationConfig(
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            max_new_tokens=512,
            num_return_sequences=1,
            num_beams=1,
            top_p=0.9 )
    else:
        generate_config_params = deepcopy( generate_config )
        # pop all decode strategies config, left configs all load for generation_config
        for mode in generate_config:
            if mode in generate_config_params and isinstance( generate_config.get( mode ), dict ):
                generate_config_params.pop( mode )
        generation_config = GenerationConfig(
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
            **generate_config_params
        )
    # according decode_mode to set generation_config
    for key, value in generate_config.get( decode_mode, {} ).items():
        setattr( generation_config, key, value )

    inputs = tokenizer( prompt_list, return_tensors="pt", **tokenizer_param ).to( "cuda" )
    generate_ids = model.generate(
        inputs=inputs["input_ids"],
        attention_mask=inputs["attention_mask"],
        **generation_config.to_dict()
    )
    outputs = tokenizer.batch_decode( generate_ids[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True )
    return outputs


def inference(model_name="CodeFuse-CodeLlama-34B",
              model_version="v1",
              eval_dataset="humaneval_python",
              output_file="./result.jsonl",
              task_mode=None,
              **kwargs):
    """
    The main process for model to inference eval dataset and generate the result
    """
    if isinstance( eval_dataset, str ):
        if eval_dataset not in EVAL_DATASET:
            raise ValueError( f"eval_dataset {eval_dataset} not in [EVAL_DATASET]. please registry in util.py" )
        if eval_dataset not in DATASET_SUPPORT:
            raise ValueError( f"eval_dataset {eval_dataset} is not [DATASET_SUPPORT]. please registry in util.py" )
        if eval_dataset not in DATASET_LANGUAGE:
            raise ValueError( f"eval_dataset {eval_dataset} is not [DATASET_LANGUAGE]. please registry in util.py" )
    elif isinstance( eval_dataset, list ):
        if not all( [dataset in EVAL_DATASET for dataset in eval_dataset] ):
            illegal_dataset = [dataset for dataset in eval_dataset if dataset not in EVAL_DATASET]
            raise ValueError( f"eval_datasets {illegal_dataset} not in [EVAL_DATASET]. please registry in util.py" )
        if not all( [dataset in DATASET_SUPPORT for dataset in eval_dataset] ):
            illegal_dataset = [dataset for dataset in eval_dataset if dataset not in DATASET_SUPPORT]
            raise ValueError( f"eval_datasets {illegal_dataset} is not [DATASET_SUPPORT]. please registry in util.py" )
        if not all( [dataset in DATASET_LANGUAGE for dataset in eval_dataset] ):
            illegal_dataset = [dataset for dataset in eval_dataset if dataset not in DATASET_LANGUAGE]
            raise ValueError( f"eval_datasets {illegal_dataset} is not [DATASET_LANGUAGE]. please registry in util.py" )
    else:
        raise ValueError( "eval_dataset parameter must be string or list" )

    if task_mode is None:
        print( "[task_mode] parameter is None. Loading default task mode for corresponding dataset" )
        if isinstance( eval_dataset, list ):
            task_mode = [DATASET_SUPPORT.get( dataset )[0] for dataset in eval_dataset]
        if isinstance( eval_dataset, str ):
            task_mode = DATASET_SUPPORT.get( eval_dataset )[0]
    # load and check dataset
    if not ((isinstance( eval_dataset, list ) and isinstance( task_mode, list ) and len( eval_dataset ) == len( task_mode )
             and all( [mode in DATASET_SUPPORT.get( dataset, [] ) for dataset, mode in zip( eval_dataset, task_mode )] )) or
            (isinstance( eval_dataset, str ) and isinstance( task_mode, str ) and task_mode in DATASET_SUPPORT.get( eval_dataset, [] ))):
        raise ValueError( "eval_dataset and task_mode must both be string or list. When both are list, the list length must be the same, "
                          "and the task_mode must be among the task_modes supported by eval_datasets." )

    if CKPT_CONFIG.get( model_name, None ) is None:
        raise ValueError( f"{model_name} not find in ckpt_config.json, please config model first" )
    if CKPT_CONFIG.get( model_name, {} ).get( model_version, None ) is None:
        raise ValueError( f"{model_version} not find in {model_name} in ckpt_config.json, please config model first" )

    language = DATASET_LANGUAGE.get( eval_dataset )
    if not isinstance( eval_dataset, list ):
        eval_datasets = [eval_dataset]
        task_modes = [task_mode]
    else:
        eval_datasets = eval_dataset
        task_modes = task_mode

    path = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "path", None )
    process_loader = load_modelprocess( model_name, model_version )

    print( "********* path *********" )
    print( "path========: ", path )
    print( "loading model========  " )
    st = time.time()
    model, tokenizer = process_loader.load_model_tokenizer( path )
    print( 'Model load spend: {:.4f}s'.format( time.time() - st ) )

    generation_datasets = {}
    for eval_dataset, task_mode in zip( eval_datasets, task_modes ):
        data_path = EVAL_DATASET.get( eval_dataset )
        if data_path is None:
            raise ValueError( f"{eval_dataset} is not support, can not find current dataset information" )
        if not os.path.exists( data_path ):
            raise ValueError( f"{eval_dataset} corresponding data_path is {data_path}, file not exist" )
        if not DATASET_SUPPORT.get( eval_dataset ):
            raise ValueError( f"current dataset {eval_dataset} not set support tasks, please set in util.py" )
        print( f"current generation task task mode is {task_mode}" )

        dataset_origin = load_dataset( data_path )
        batch_size = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "batch_size", 1 )
        sample_num = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "sample_num", 1 )

        if path is None or not os.path.exists( path ):
            raise ValueError( f"The path: {path} of the current model: {model_name} does not exist " )

        if "mbpp" in eval_dataset:
            if not CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "mbpp_mode" ):
                print( "Can not find mbpp_mode, use default value 「mbpp_mode」is 「en」" )
                mbpp_mode = "en"
            else:
                mbpp_mode = CKPT_CONFIG.get( model_name, {} ).get( model_version, {} ).get( "mbpp_mode" )
            dataset = process_loader.process_before( dataset_origin, language, task_mode, eval_dataset, mbpp_mode=mbpp_mode )
        else:
            dataset = process_loader.process_before( dataset_origin, language, task_mode, eval_dataset )

        all_prompt_list = [data.get( "prompt", None ) for data in dataset]
        eval_data = []
        if all_prompt_list or all( all_prompt_list ):
            if len( all_prompt_list ) % batch_size == 0:
                batch_num = len( all_prompt_list ) // batch_size
                # 将prompt和data同时batch化，然后根据显存情况设置合适的batch大小。
                batch_prompt_list = [all_prompt_list[batch_index * batch_size: (batch_index + 1) * batch_size] for batch_index in range( batch_num )]
                batch_dataset = [dataset[batch_index * batch_size: (batch_index + 1) * batch_size] for batch_index in range( batch_num )]
                index = 0
                for prompt_list in tqdm( batch_prompt_list ):
                    for _ in range( sample_num ):
                        # 一个batch的推理时间，时间按照batch大小进行平均分配。
                        start_time = time.time()
                        outputs = generate_outputs( model, tokenizer, prompt_list, model_name, model_version )
                        endtime = time.time()
                        for data, out in zip( batch_dataset[index], outputs ):
                            # print(f"data*********:\n{data}")
                            data["generation"] = out
                            data["processing_time"] = (endtime - start_time) / len( prompt_list )
                            eval_data.append( data )
                            print( f"outputs*******:\n {outputs}" )
                        print( f"current batch size is {batch_size},current batch generation cost time is {endtime - start_time}" )
                    index += 1
                total_time_cost = sum( [item.get( "processing_time", 0 ) for item in eval_data] )
                print( f"Generation Total time cost: {total_time_cost}" )
                print( f"Generation Average time cost: {total_time_cost / len( eval_data )}" )
                process_loader.process_after( eval_data, language, task_mode, eval_dataset )
                print( [model_name, model_version, eval_dataset, task_mode] )
                key = "_".join( [model_name, model_version, eval_dataset, task_mode] )
                if key not in eval_datasets:
                    generation_datasets[key] = eval_data
            else:
                raise ValueError( "prompt_list length is not divisible by batch_size,"
                                  "prompt_list length and batch_size respectively are",
                                  len( all_prompt_list ), batch_size )
        else:
            raise ValueError( "current prompt list is empty or all prompts are empty, "
                              "please check your dataset prompt", all_prompt_list )

        # pipeline使用，主要是将模型在不同数据集上的数据分别进行保存

    # 写入总数据文件，如果当前数据集大于1,分别写文件。
    write_list = []
    for _, value in generation_datasets.items():
        write_list.extend( value )
    write_jsonl( write_list, output_file )
    if len( eval_datasets ) > 1:
        for key, value in generation_datasets.items():
            file_name = "./pipeline/" + key + "_" + "generation.jsonl"
            write_jsonl( value, file_name )

    return generation_datasets


if __name__ == "__main__":
    fire.Fire( inference )
