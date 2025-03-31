# Copyright (c) 2022-2025 Ant Group
# attention please, this file is internal model loading method of Ant Group, if you want to loading Ling-Coder-Lite, please use transformers
# more detail: https://huggingface.co/inclusionAI/Ling-Coder-lite
from .base import BaseProcessor
from typing import *
import os
import torch

# from glm_base.configuration_glm import GLMConfig
from glm_base.modeling_glm import GLMForConditionalGeneration
from glm_base.tokenization_bailing import BailingTokenizer

#pip install atorch==1.4.1rc6 --no-deps --index=https://pypi.antfin-inc.com/artifact/repositories/simple/


os.environ["TOKENIZERS_PARALLELISM"] = "false"


class Bailingmoe_Processor(BaseProcessor):

    def __init__(self, **kwargs):
        """
        加载模型和tokenizer
        """
        super().__init__(**kwargs)
        """
            加载模型和tokenizer
            """
        self.tokenizer = BailingTokenizer.from_pretrained(self.path)
        self.model = GLMForConditionalGeneration.from_pretrained(self.path, device_map="auto",
                                                                 torch_dtype=torch.bfloat16)

        eos_token = "<|endoftext|>"
        pad_token = "<|endoftext|>"

        self.tokenizer.eos_token_id = self.tokenizer.convert_tokens_to_ids(eos_token)
        self.tokenizer.pad_token_id = self.tokenizer.convert_tokens_to_ids(pad_token)

        print(f'eos_token: {eos_token}, eos_token_id: {self.tokenizer.eos_token_id}')
        print(f'pad_token: {pad_token}, pad_token_id: {self.tokenizer.pad_token_id}')

    def generate(self, promptlist: List[str], language: str, task_mode: str, dataset_name: str, **kwargs) -> Union[
        List, str]:
        print("hello")
        print(promptlist[0])
        print("===================================================================================")
        print(self.model.config.max_sequence_length)
        input_ids = self.tokenizer(promptlist, add_special_tokens=False)['input_ids']
        inputs = self.tokenizer.build_input_for_gen(input_ids, max_seq_len=self.model.config.max_sequence_length,
                                                    max_out_len=4096)
        generate_ids = self.model.generate(**inputs,
                                           max_new_tokens=4096,
                                           eos_token_id=self.tokenizer.eos_token_id,
                                           pad_token_id=self.tokenizer.pad_token_id)
        generations = self.tokenizer.batch_decode(generate_ids[:, inputs["input_ids"].shape[1]:],
                                                  skip_special_tokens=True)
        return generations
