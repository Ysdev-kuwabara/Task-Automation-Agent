import os
import subprocess
import json

# Anthropic APIに渡すツール定義
TOOLS = [
    {
        "name": "read_file",
        "description": "ファイルの内容を読み込む",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "ファイルパス"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "ファイルに内容を書き込む（上書き）",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "run_command",
        "description": "シェルコマンドを実行して結果を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "実行するコマンド"}
            },
            "required": ["command"]
        }
    },
    {
        "name": "list_files",
        "description": "ディレクトリ内のファイル一覧を返す",
        "input_schema": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "ディレクトリパス（省略時は現在地）"}
            },
            "required": []
        }
    }
]

# ツールの実装
def execute_tool(name: str, inputs: dict) -> str:
    try:
        if name == "read_file":
            with open(inputs["path"], "r", encoding="utf-8") as f:
                return f.read()

        elif name == "write_file":
            with open(inputs["path"], "w", encoding="utf-8") as f:
                f.write(inputs["content"])
            return f"✅ {inputs['path']} に書き込みました"

        elif name == "run_command":
            result = subprocess.run(
                inputs["command"], shell=True,
                capture_output=True, text=True, timeout=30
            )
            output = result.stdout or result.stderr
            return output.strip() or "(出力なし)"

        elif name == "list_files":
            directory = inputs.get("directory", ".")
            files = os.listdir(directory)
            return "\n".join(files)

    except Exception as e:
        return f"❌ エラー: {e}"