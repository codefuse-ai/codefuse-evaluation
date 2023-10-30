from abc import ABC, abstractmethod
import transformers
import re
from typing import *
from . import CODE_TEXT_TAG

transformers.logging.set_verbosity_error()

class BaseProcessor( ABC ):
    """
    模型数据处理基类，主要包括模型输出的前处理和后处理部分
    """

    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs )

    def __repr__(self):
        return f"{self.__class__.__name__}"

    def __str__(self):
        return f"{self.__class__.__name__}"

    @abstractmethod
    def load_model_tokenizer(self, path):
        """
        load model and tokenizer
        return (model,tokenizer)
        """
        return None,None

    @abstractmethod
    def process_before(self, dataset:List[Dict], language:str, task_mode:str,**kwargs)->List[Dict]:
        return dataset

    @abstractmethod
    def process_after(self, dataset:List[Dict],language:str, task_mode:str,**kwargs)->List[Dict]:
        for output_ori in dataset:
            generation = self._process_generation( output_ori["generation"], language )
            output_ori["generation"] = generation
        return dataset

    def _generate_prompt(self, language, input):
        INSTRUCTION = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

    ### Instruction:
    Create a {language} script for this problem:
    {input}

    ### Response:"""
        return INSTRUCTION

    def _post_process_mkcode(self, language, data):
        print( "********* post_process_mkcode *********" )
        print( data )
        re_result = re.findall( f"```{language}(.*?)```", data, re.DOTALL | re.IGNORECASE )
        if len( re_result ) > 0:
            data = re.sub( f'```{language}|```', '', re_result[0], flags=re.IGNORECASE )
        if "import" in data:
            if '"""' in data:
                first_id = data.find( '"""' ) + 3
                end_id = data.find( '"""', first_id ) + 3
                data = data[end_id:]
            elif "'''" in data:
                first_id = data.find( "'''" ) + 3
                end_id = data.find( "'''", first_id ) + 3
                data = data[end_id:]
            else:
                new_line = "\n".join( [word for word in data.strip().split( "\n" ) if
                                       not word.startswith( "def" ) and not word.startswith( "from" )] )
                data = new_line
        data = data.replace( '<|endoftext|>', '' )

        return data

    def _get_tc_prompt(self, mbpp_mode, item):
        if mbpp_mode == "en":  # 英文原版
            prompt = item["prompt"] + "Your code should satisfy these tests:\n" + "\n".join( item["test"] )
        elif mbpp_mode == "cn":  # 中文原版
            prompt = item["prompt_text_chinese"] + "你的代码必须能够通过这些测试用例:\n" + "\n".join( item["test"] )
        else:
            raise ValueError( "unknown mbpp_mode, en or cn expected." )
        return prompt

    def _extract_code_from_response(self, output_ori):
        response_start = "### Response:"
        print( output_ori )
        response_index = output_ori.find( response_start )
        if response_index == -1:
            return output_ori
        code = output_ori[response_index + len( response_start ):]
        return code

    def _process_generation(self,generated_code, language):
        generation = ""
        code = generated_code
        if language == "python" or language == "matplotlib" or language == "numpy" or language == "Pandas":
            generation = ""
            for line in code.split( "\n" ):
                if line and line[0] != ' ':
                    break
                generation += line + "\n"

        elif language == "cpp":
            generation = ""
            for line in code.split( "\n" ):
                if line and line.startswith( "int main" ):
                    break
                generation += line + "\n"

        elif language == "js" or language == "java" or language == "go" or language == "rust":
            generation = ""
            for line in code.split( "\n" ):
                generation += line + "\n"
                if line == "}" or line == "};":
                    break
        return generation
    
    def _get_c2t_prompt(self,item):
        text = CODE_TEXT_TAG["chinese"] + item["canonical_solution"]
        prompt = text
        # prompt = PREFIX + text + SUFFIX
        return prompt

    # code_trans_prompt
    def _get_ct_prompt(self,source_language, target_language, item):
        content = item["prompt"]
        prompt = f"# Translate the following {source_language} program to {target_language}\n# {source_language}\n{content}\n# {target_language}\n"
        sig_text = "The result code must follow this function name :\n" + item["func_title"] + "\n"
        prompt = f'{prompt}{sig_text}'
        return prompt