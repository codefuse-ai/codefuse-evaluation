# Copyright (c) 2022-2025 Ant Group
import os
import torch
import sys
from copy import deepcopy
from transformers import AutoTokenizer, AutoModelForCausalLM,GenerationConfig
from typing import *
from .base import BaseProcessor


class Codefuse13BProcessor( BaseProcessor ):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        if os.path.exists( self.path ):
            self.tokenizer = AutoTokenizer.from_pretrained( self.path )
            self.model = AutoModelForCausalLM.from_pretrained( self.path, load_in_8bit=False, torch_dtype=torch.float16,
                                                          device_map="auto" )
            self.model.config.pad_token_id = self.tokenizer.pad_token_id
            self.model.half()
            self.model.eval()
            if torch.__version__ >= "2" and sys.platform != "win32":
                self.model = torch.compile( self.model )
            print( self.tokenizer )
        elif self.path.startswith( ("http:", "https:") ):
            print( "===============model generate in online http mode ====================" )
            pass
        else:
            print( "===============model generate in online other mode ====================" )
            pass

    def generate(self, promptlist: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[List, str]:
        """
        Generate outputs based on model information and prompts
        """
        CKPT_CONFIG = kwargs.get("ckpt_config",{})
        decode_mode = CKPT_CONFIG.get( self.model_name, {} ).get( self.model_version, {} ).get( "decode_mode", "dosample" )
        generate_config = CKPT_CONFIG.get( self.model_name, {} ).get( self.model_version, {} ).get( "generation_config", {} )
        tokenizer_param = CKPT_CONFIG.get( self.model_name, {} ).get( self.model_version, {} ).get( "tokenizer", {} )
        if not generate_config:
            print( "Can not find generate_config in config.json,use default config!!!!!" )
            generation_config = GenerationConfig(
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                max_new_tokens=1024,
                num_return_sequences=1 )
        else:
            generate_config_params = deepcopy( generate_config )
            # pop all decode strategies config, left configs all load for generation_config
            for mode in generate_config:
                if mode in generate_config_params and isinstance( generate_config.get( mode ), dict ):
                    generate_config_params.pop( mode )
            generation_config = GenerationConfig(
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **generate_config_params
            )
        # according decode_mode to set generation_config
        for key, value in generate_config.get( decode_mode, {} ).items():
            setattr( generation_config, key, value )

        inputs = self.tokenizer( promptlist, **tokenizer_param ).to( "cuda" )
        generate_ids = self.model.generate(
            **inputs,
            **generation_config.to_dict()
        )
        outputs = self.tokenizer.batch_decode( generate_ids[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True )
        return outputs

    def process_before(self, dataset, language, task_mode, dataset_name, **kwargs):
        """
        当前提示词的处理方式
        """
        print(f"-------{__class__.__name__} process the prompt according to the current task mode: {task_mode} -------")
        for item in dataset:
            if task_mode == "code_completion":
                prompt_origin = item["prompt"].replace( '    ', '\t' )
                prompt = self._generate_prompt( language, prompt_origin )
                item["prompt"] = prompt
        return dataset

    def process_after(self, dataset, language, task_mode, dataset_name, **kwargs):
        print(f"======={__class__.__name__} process the generated results according to the current task mode: {task_mode} =======")
        for output_ori in dataset:
            if task_mode == "code_completion":
                generation = self._extract_code_from_response( output_ori["generation"] ).replace( '\t', '    ' )
                generation = self._post_process_mkcode( language, generation )
                output_ori["generation"] = generation
            else:
                generation = self._post_process_mkcode( language, output_ori["generation"] )
                output_ori["generation"] = generation
        return dataset
