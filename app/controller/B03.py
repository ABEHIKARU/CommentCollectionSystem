from flask import Blueprint
import pandas as pd
from transformers import XLMRobertaTokenizer, BartForConditionalGeneration

# B03のBlueprintを作成（Flaskアプリケーションのモジュール化）
b03_bp = Blueprint('b03_bp', __name__)

# BARTモデルとトークナイザーをロード
# 正しいトークナイザーを読み込む
tokenizer = XLMRobertaTokenizer.from_pretrained('ku-nlp/bart-large-japanese')

# モデルを読み込む
model = BartForConditionalGeneration.from_pretrained('ku-nlp/bart-large-japanese')

def summarize_and_soften(text):
    """
    レビューの要約と優しい言い方への変換を同時に行う関数
    """
    prompt = f"次のレビューを要約してください: {text}"
    
    # テキストをトークナイズ
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    
    # モデルに入力して要約を生成
    summary_ids = model.generate(inputs.input_ids, max_length=150, num_beams=4, early_stopping=True)
    
    # 生成されたテキストをデコード
    softened_summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    return softened_summary

def process_reviews(filtered_reviews):
    """
    フィルタリングされたレビューに対して要約と優しい言い回しへの変換を行う関数
    """
    # 'content' 列の各レビューに対して要約と優しい言い回しへの変換を適用
    filtered_reviews['summary'] = filtered_reviews['content'].apply(summarize_and_soften)
    
    return filtered_reviews
