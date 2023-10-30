HUMAN_ROLE_START_TAG = "<|role_start|>human<|role_end|>"
BOT_ROLE_START_TAG = "<|role_start|>bot<|role_end|>"

CODE_TEXT_TAG = {
    "chinese": "为代码添加注释，代码如下:\n ",
    "english": "Add a comment to the code as follows：\n "
}

from .base import BaseProcessor
from .codefuse13b import Codefuse13BProcessor
from .codefusellama34b import CodeFuseCodeLlama34BProcessor
