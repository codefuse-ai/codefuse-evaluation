import gzip
import os
import importlib
import json
import transformers
from transformers import GenerationConfig
import time
from copy import deepcopy
from util import write_jsonl, EVAL_DATASET, DATASET_SUPPORT,ALL_DECODE_MODE
import fire

#model information and evaluation configs
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


def load_modelprocess(model_name, *args, **kwargs):
    """
    load model process to load model and tokenizer && load dataset processor
    """
    path = CKPT_CONFIG.get( model_name, {} ).get( "processor_class", None )
    if "/" in path:
        module_path, class_name = path.rsplit( "/", 1 )
        module_path = module_path.split( "process" )[1:]
        module_path = "process".join( module_path ).replace( "/", "." )
    elif "." in path:
        module_path, class_name = path.rsplit( ".", 1 )
        module_path = module_path.split( "process" )[1:]
        module_path = "process".join( module_path )
    else:
        raise ValueError( f"{path} is invalid,can not find module and class" )
    try:
        module = importlib.import_module( module_path, package="processor" )
        module_class = getattr( module, class_name )
    except ModuleNotFoundError:
        raise ModuleNotFoundError( f"module {module_path} can not find in package process" )
    except AttributeError:
        raise AttributeError( f"{path} can not find current class" )
    return module_class( *args, **kwargs )


def generate_outputs(model, tokenizer, prompt_list, model_name):
    """
    Generate outputs based on model information and prompts
    """
    decode_mode = CKPT_CONFIG.get( model_name, {} ).get( "decode_mode", "dosample" )
    generate_config = CKPT_CONFIG.get( model_name, {} ).get( "generation_config", {} )
    tokenizer_param = CKPT_CONFIG.get( model_name, {} ).get( "tokenizer", {} )
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
        for mode in ALL_DECODE_MODE:
            if mode in generate_config_params:
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
              eval_dataset="humaneval_python",
              language="python",
              output_file="./result.jsonl",
              **kwargs):
    """
    The main process for model to inference eval dataset and generate the result
    """
    # load and check dataset
    data_path = EVAL_DATASET.get( eval_dataset )
    if data_path is None:
        raise ValueError( f"{eval_dataset} is not support, can not find current dataset information" )
    if not os.path.exists( data_path ):
        raise ValueError( f"{eval_dataset} corresponding data_path is {data_path}, file not exist" )
    task_mode = CKPT_CONFIG.get(model_name,{}).get("task_mode")
    if not DATASET_SUPPORT.get( eval_dataset ):
        raise ValueError(f"current dataset {eval_dataset} not set support tasks, please set in util.py")
    if task_mode not in DATASET_SUPPORT.get( eval_dataset ):
        print( f"current dataset {eval_dataset} support tasks are {DATASET_SUPPORT.get( eval_dataset )}, "
               f"currenr model set task mode is: {task_mode},change to  default task mode" )
        task_mode = DATASET_SUPPORT.get( eval_dataset )[0]
    print(f"current generation task task mode is {task_mode}")

    dataset_origin = load_dataset( data_path )
    process_loader = load_modelprocess( model_name )
    path = CKPT_CONFIG.get( model_name, {} ).get( "path", None )
    batch_size = CKPT_CONFIG.get( model_name, {} ).get( "batch_size", 1 )
    sample_num = CKPT_CONFIG.get( model_name, {} ).get( "sample_num", 1 )

    if path is None or not os.path.exists( path ):
        raise ValueError( f"The path: {path} of the current model: {model_name} does not exist " )

    print( "********* path *********" )
    print( "path========: ", path )
    print( "loading model========  " )
    st = time.time()
    model, tokenizer = process_loader.load_model_tokenizer( path )
    print( 'Model load spend: {:.4f}s'.format( time.time() - st ) )
    if "mbpp" in eval_dataset:
        if not CKPT_CONFIG.get( model_name, {} ).get( "mbpp_mode" ):
            print( "Can not find mbpp_mode, use default value 「mbpp_mode」is 「en」" )
            mbpp_mode = "en"
        else:
            mbpp_mode = CKPT_CONFIG.get( model_name, {} ).get( "mbpp_mode" )
        dataset = process_loader.process_before( dataset_origin, language, task_mode, mbpp_mode=mbpp_mode )
    else:
        dataset = process_loader.process_before( dataset_origin, language, task_mode )

    count = 0
    prompt_list = [data["prompt"] for data in dataset]

    eval_data = []
    if prompt_list and len( prompt_list ) % batch_size == 0 or count == len( prompt_list ):
        for _ in range( sample_num ):
            outputs = generate_outputs( model, tokenizer, prompt_list, model_name )
            for data, out in zip( dataset, outputs ):
                data["generation"] = out
                eval_data.append( data )
                print( f"outputs*******:\n {outputs}" )
            process_loader.process_after( eval_data, language, task_mode )
    write_jsonl( eval_data, output_file )
    return eval_data


if __name__ == "__main__":
    fire.Fire( inference )
