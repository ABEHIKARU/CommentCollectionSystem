from flask import Blueprint
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import re

# B03のBlueprintを作成（Flaskアプリケーションのモジュール化）
b03_bp = Blueprint('b03_bp', __name__)

# T5モデルとトークナイザーをロード（T5の日本語モデルを使用）
tokenizer = T5Tokenizer.from_pretrained('sonoisa/t5-base-japanese')
model = T5ForConditionalGeneration.from_pretrained('sonoisa/t5-base-japanese')

def clean_text(text):
    """
    テキストの前処理を行う関数。無意味な文字列や空白、不要な記号を除去。
    """
    # 無意味な繰り返しの削除（。。や、要約:の重複）
    text = re.sub(r'[。\.]{2,}', '', text)  # 「。。」などの削除
    text = re.sub(r'要約[:：]*', '', text)  # 「要約:」の重複削除
    # 不要な空白の削除
    text = text.strip()
    return text

def summarize_and_soften(text):
    """
    レビューの要約と優しい言い方への変換を同時に行う関数
    """
    # テキストの前処理
    cleaned_text = clean_text(text)
    
    # テキストが短すぎるか内容が無い場合はそのまま返す
    if len(cleaned_text) < 10:
        return "要約できる内容がありません。"

    # 要約のためのプロンプトを作成
    prompt = f"要約: {cleaned_text}"
    
    # テキストをトークナイズ
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    
    # モデルに入力して要約を生成
    summary_ids = model.generate(inputs.input_ids, max_length=100, num_beams=4, early_stopping=True)
    
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
