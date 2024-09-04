from flask import Blueprint, session
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# B02のBlueprint
b02_bp = Blueprint('b02_bp', __name__)

# モデルとトークナイザーの読み込み
model_name = "elyza/Llama-3-ELYZA-JP-8B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto",
)
model.eval()
def judge_sentiment(text):
    """レビューのネガポジを判断する関数"""
    # 感情分析用のプロンプトを作成
    prompt = f"次の文はポジティブですか、ネガティブですか？\n\nテキスト: {text}\n\n感情:"

    # トークナイズしてモデルに入力
    inputs = tokenizer(prompt, return_tensors="pt")
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=100)

    # モデルの出力をデコード
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # 結果を解析してポジティブかネガティブか判断
    if "ポジティブ" in response:
        return "positive"
    elif "ネガティブ" in response:
        return "negative"
    else:
        return "unknown"

def filter_reviews_by_sentiment(df_reviews, filter_type):
    """ネガポジ判断を行い、指定された種別のみを保持する関数"""
    # ネガポジ判断の列を追加
    df_reviews['sentiment'] = df_reviews['content'].apply(judge_sentiment)
    
    # 指定された種別（"positive"または"negative"）のみを保持
    filtered_df = df_reviews[df_reviews['sentiment'] == filter_type]
    
    return filtered_df
