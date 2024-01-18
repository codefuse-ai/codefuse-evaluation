from . import BaseProcessor
from transformers import AutoTokenizer, AutoConfig, AutoModelForCausalLM
import torch
from . import HUMAN_ROLE_START_TAG, BOT_ROLE_START_TAG, LANGUAGE_TAG


class CodeFuseCodeLlama34BProcessor(BaseProcessor):
	"""
	模型和tokenizer的加载，包括数据集的前处理和后处理
	"""
	
	def load_model_tokenizer(self, path):
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
		print(tokenizer)
		print("=======tokenizer ids======")
		print(tokenizer.eos_id, tokenizer.pad_id)
		return model, tokenizer
	
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
