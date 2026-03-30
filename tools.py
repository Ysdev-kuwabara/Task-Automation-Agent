import os
import subprocess
import json

#Anthropics API に渡すツール定義
TOOLS = [
    {
        "name": "read_file",
        "description": "ファイルの内容を読み込む"
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "ファイルパス"}
            },
            "required": ["path"]
        }
    },
    
]