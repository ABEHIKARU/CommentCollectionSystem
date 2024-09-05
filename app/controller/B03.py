from flask import Blueprint
import pandas as pd
from transformers import LlamaTokenizer, LlamaForCausalLM

# B03のBlueprintを作成（Flaskアプリケーションのモジュール化）
b03_bp = Blueprint('b03_bp', __name__)




# Llamaモデルとトークナイザーをロード
model = LlamaForCausalLM.from_pretrained('elyza/Llama-3-ELYZA-JP-8B')
tokenizer = LlamaTokenizer.from_pretrained('elyza/Llama-3-ELYZA-JP-8B')

def summarize_and_soften(text):
    """
    レビューの要約と優しい言い回しへの変換を同時に行う関数
    """
    prompt = f"次のレビューを優しく要約してください。レビューの内容に含まれる強い言葉やネガティブな表現を、よりソフトで親しみやすい言葉に変換してください。\n\nレビュー:\n{text}\n\n要約と優しい言い回し:"

    # テキストをトークン化
    inputs = tokenizer(prompt, return_tensors="pt", max_length=1024, truncation=True)

    try:
        # モデルに入力して生成
        summary_ids = model.generate(
            inputs.input_ids, 
            max_length=200,  # 最大出力長を設定
            num_beams=5,     # ビームサーチのビーム数
            early_stopping=True,
            no_repeat_ngram_size=2,  # 同じn-gramの繰り返しを防ぐ
            length_penalty=1.0  # 出力長を調整するペナルティ
        )
        
        # 生成されたテキストをデコード
        softened_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    except Exception as e:
        print(f"生成中にエラーが発生しました: {e}")
        softened_summary = "要約と優しい言い回しの生成に失敗しました。"
    
    return softened_summary


def process_reviews(filtered_reviews):
    """
    フィルタリングされたレビューに対して要約と優しい言い回しへの変換を行う関数
    """
    # 'content' 列の各レビューに対して要約と優しい言い回しへの変換を適用
    filtered_reviews['summary'] = filtered_reviews['content'].apply(summarize_and_soften)
    
    return filtered_reviews