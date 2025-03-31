# Copyright (c) 2022-2025 Ant Group
import os
import torch
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM, GenerationConfig
from typing import *
from copy import deepcopy
from codefuseEval.processor import BaseProcessor
from codefuseEval.processor import HUMAN_ROLE_START_TAG, BOT_ROLE_START_TAG, LANGUAGE_TAG


class CodeFuseCodeLlama34BProcessor(BaseProcessor):
    """
	模型和tokenizer的加载，包括数据集的前处理和后处理
	"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if os.path.exists(self.path):
            print("===============model generate in offline mode ====================")
            self.tokenizer = AutoTokenizer.from_pretrained(self.path, trust_remote_code=True, use_fast=False,
                                                           legacy=False)
            self.tokenizer.eos_token = "</s>"
            self.tokenizer.pad_token = "<unk>"
            self.tokenizer.eos_id = self.tokenizer._convert_token_to_id(self.tokenizer.eos_token)
            self.tokenizer.pad_id = self.tokenizer._convert_token_to_id(self.tokenizer.pad_token)
            self.tokenizer.padding_side = "left"
            print(self.tokenizer)
            print(f"eos_token_id: {self.tokenizer.eos_token_id}, pad_token_id: {self.tokenizer.pad_token_id}")
            config, unused_kwargs = AutoConfig.from_pretrained(self.path, trust_remote_code=True,
                                                               return_unused_kwargs=True)
            config_dict = config.to_dict()
            config_dict["use_flash_attn"] = 1
            config_dict["use_xformers"] = 1
            self.model = AutoModelForCausalLM.from_pretrained(self.path, config=config, device_map="auto",
                                                              torch_dtype=torch.bfloat16,
                                                              trust_remote_code=True, use_safetensors=False)
            print(self.tokenizer)
            print("=======tokenizer ids======")
            print(self.tokenizer.eos_id, self.tokenizer.pad_id)
        elif self.path.startswith(("http:", "https:")):
            print("===============model generate in online http mode ====================")
            pass
        else:
            print("===============model generate in online other mode ====================")
            pass

    def process_before(self, dataset, language, task_mode, dataset_name, **kwargs):
        """
        模型前处理，主要是处理输入的prompt，要满足模型的输入
        返回处理之后的dataset
        """
        print(f"-------{__class__.__name__} process the prompt according to the current task mode: {task_mode} -------")
        mbpp_mode = kwargs.get("mbpp_mode", "en")
        for item in dataset:
            if task_mode == "code_completion":
                prompt_origin = LANGUAGE_TAG.get(language, language) + "\n" + item["prompt"]
                prompt = HUMAN_ROLE_START_TAG + prompt_origin + BOT_ROLE_START_TAG
                item["prompt"] = prompt
            # 自然语言到代码
            elif task_mode == "nl2code":
                prompt_origin = self._get_tc_prompt(mbpp_mode, item)
                prompt = HUMAN_ROLE_START_TAG + prompt_origin + BOT_ROLE_START_TAG
                item["prompt"] = prompt
            # 自然语言到代码
            elif task_mode == "code_trans":
                target_language = item["task_id"].split("/")[0].lower()
                prompt_origin = self._get_ct_prompt(language, target_language, item)
                prompt = HUMAN_ROLE_START_TAG + prompt_origin + BOT_ROLE_START_TAG
                item["prompt"] = prompt

        return dataset

    def generate(self, promptlist: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[
        List, str]:
        """
        Generate outputs based on model information and prompts
        """
        CKPT_CONFIG = kwargs.get("ckpt_config", {})
        decode_mode = CKPT_CONFIG.get(self.model_name, {}).get(self.model_version, {}).get("decode_mode", "dosample")
        generate_config = CKPT_CONFIG.get(self.model_name, {}).get(self.model_version, {}).get("generation_config", {})
        tokenizer_param = CKPT_CONFIG.get(self.model_name, {}).get(self.model_version, {}).get("tokenizer", {})
        if not generate_config:
            print("Can not find generate_config in config.json,use default config!!!!!")
            generation_config = GenerationConfig(
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                max_new_tokens=1024,
                num_return_sequences=1)
        else:
            generate_config_params = deepcopy(generate_config)
            # pop all decode strategies config, left configs all load for generation_config
            for mode in generate_config:
                if mode in generate_config_params and isinstance(generate_config.get(mode), dict):
                    generate_config_params.pop(mode)
            generation_config = GenerationConfig(
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                **generate_config_params
            )
        # according decode_mode to set generation_config
        for key, value in generate_config.get(decode_mode, {}).items():
            setattr(generation_config, key, value)

        inputs = self.tokenizer(promptlist, **tokenizer_param).to("cuda")
        generate_ids = self.model.generate(
            **inputs,
            **generation_config.to_dict()
        )
        outputs = self.tokenizer.batch_decode(generate_ids[:, inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return outputs

    def process_after(self, dataset, language, task_mode, dataset_name, **kwargs):
        """
        生成结果的处理，主要是对生成的结果进行处理，要满足生成的结果处理满足测试代码
        返回处理之后的dataset
        """
        print(
            f"======={__class__.__name__} process the generated results according to the current task mode: {task_mode} =======")
        for output_ori in dataset:
            if task_mode == "code_completion":
                generation = output_ori["generation"]
                generation = self._post_process_mkcode(language, generation)
                generation = self._process_generation(generation, language)
                output_ori["generation"] = generation
            elif task_mode == "code_trans":
                print("")
            else:
                generation = self._post_process_mkcode(language, output_ori["generation"])
                output_ori["generation"] = generation
        return dataset
