import torch
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
from tools import TOOLS, execute_tool

# モデルの準備
model_id = "Qwen/Qwen2.5-7B-Instruct"
device = "mps" if torch.backends.mps.is_available() else "cpu"

print(f"Loading model: {model_id}...")
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype="auto",
    device_map="auto"
)

def run_agent(task: str):
    system_prompt = f"""あなたは優秀なタスク自動化エージェントです。

## 絶対ルール（厳守）:
1. **一度の回答で出力できるツール呼び出し（JSON）は、必ず1つだけです。** 複数のJSONを並べてはいけません。
2. ツールを実行したら、必ずその結果を待ってから次の行動を考えてください。
3. ファイルの中身を読む前に、必ず `list_files` で正確なファイルパスを確認してください。
4. 回答は以下のJSON形式のみを出力してください。説明や挨拶は一切不要です。

## 出力フォーマット:
{{
  "tool": "ツール名",
  "parameters": {{ "引数名": "値" }}
}}

## 利用可能なツール一覧:
{json.dumps(TOOLS, ensure_ascii=False)}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": task}
    ]
    
    # 最大5回までやり取りを繰り返すループ
    for i in range(15):
        # --- 1. AIに思考させる ---
        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        print(f"\n🤖 AI思考中 (ステップ {i+1})...")
        generated_ids = model.generate(**model_inputs, max_new_tokens=512)
        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        
        # 不要なシステムプロンプトなどが混ざるのを防ぐため、最後の回答部分だけを抽出
        response_clean = response.split("assistant")[-1].strip()

        # --- 2. JSONを解析してツールを実行 ---
# --- 2. JSONを解析してツールを実行 ---
        try:
            # AIの回答からJSONを抽出（もし文章が混じっていても抽出できるようにする）
            import re
            json_match = re.search(r'\{.*\}', response_clean, re.DOTALL)
            if json_match:
                call = json.loads(json_match.group())
                tool_name = call["tool"]
                params = call["parameters"]
                
                print(f"🛠  実行命令: {tool_name}({params})")
                
                # ここで実際にツールを動かす！
                result = execute_tool(tool_name, params)
                print(f"📥 実行結果: {result}")
                
                # 実行した結果を履歴に追加して、さらに次のステップ（完了報告など）を考えさせる
                messages.append({"role": "assistant", "content": response_clean})
                messages.append({"role": "user", "content": f"実行結果:\n{result}\n次のステップがあれば続けてください。なければ完了報告をしてください。"})
                continue # 次のループへ（これが大事！）
            else:
                raise json.JSONDecodeError("JSON not found", "", 0)

        except (json.JSONDecodeError, KeyError, ValueError):
            # JSONが含まれていない場合は、AIからのメッセージ（報告）として終了する
            print(f"\n✅ エージェントからの最終報告:\n{response_clean}")
            break