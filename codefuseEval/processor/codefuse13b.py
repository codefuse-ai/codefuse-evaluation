from .base import BaseProcessor
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import sys


class Codefuse13BProcessor( BaseProcessor ):

    def load_model_tokenizer(self, path):
        tokenizer = AutoTokenizer.from_pretrained( path )
        model = AutoModelForCausalLM.from_pretrained( path, load_in_8bit=False, torch_dtype=torch.float16,
                                                      device_map="auto" )
        model.config.pad_token_id = tokenizer.pad_token_id
        model.half()
        model.eval()
        if torch.__version__ >= "2" and sys.platform != "win32":
            model = torch.compile( model )

        print( tokenizer )
        return model, tokenizer

    def process_before(self, dataset, language, task_mode, **kwargs):
        """
        """
        print(f"-------{__class__.__name__} process the prompt according to the current task mode: {task_mode} -------")
        for item in dataset:
            if task_mode == "code_completion":
                prompt_origin = item["prompt"].replace( '    ', '\t' )
                prompt = self._generate_prompt( language, prompt_origin )
                item["prompt"] = prompt
        return dataset

    def process_after(self, dataset, language, task_mode, **kwargs):
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
