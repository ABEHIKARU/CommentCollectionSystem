from flask import Blueprint
import pandas as pd
from transformers import T5Tokenizer, GPT2LMHeadModel
import re
import torch

# B03のBlueprintを作成
b03_bp = Blueprint('b03_bp', __name__)

# T5トークナイザーとGPT-2日本語モデルをロード
tokenizer = T5Tokenizer.from_pretrained('rinna/japanese-gpt2-medium')
model = GPT2LMHeadModel.from_pretrained('rinna/japanese-gpt2-medium')

def clean_text(text):
    """
    テキストの前処理を行う関数。無意味な文字列や空白、不要な記号を除去し、繰り返しを削除。
    """
    text = re.sub(r'[。\.]{2,}', '。', text)  # 「。。」や「...」の削除
    text = re.sub(r'(\w)\1{2,}', r'\1', text)  # 繰り返される文字列の短縮
    text = re.sub(r'[^\w\s\-、。！？一-龥ぁ-んァ-ヴ]', '', text)  # 不要な記号の削除
    text = text.strip()
    return text

def summarize_with_gpt2(text):
    """
    GPT-2を使用して要約を行う関数
    """
    cleaned_text = clean_text(text)
    
    # GPT-2モデルでの生成用にプロンプトを設定
    prompt = f"要約: {cleaned_text}\n要約:"

    # トークナイズ
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)

    # モデルでテキスト生成を実行
    output = model.generate(
        inputs.input_ids,
        max_length=100,  # 最大生成長
        min_length=30,   # 最小生成長
        num_beams=5,     # ビームサーチの探索幅
        no_repeat_ngram_size=3,  # 繰り返し防止
        early_stopping=True,
        repetition_penalty=2.5,  # 繰り返しの抑制
    )

    # 生成された要約をデコード
    summary = tokenizer.decode(output[0], skip_special_tokens=True)

    # 要約の部分だけを抽出
    summary = summary.replace("要約:", "").strip()

    # 文末にある句読点や不要なスペースの重複を削除
    summary = re.sub(r'[。 ]{2,}', '。', summary)
    summary = re.sub(r'(\w)\1{2,}', r'\1', summary)  # 繰り返し文字を削除
    summary = re.sub(r'([。、！？])\1+', r'\1', summary)  # 繰り返し句読点を削除

    return summary

def process_reviews(filtered_reviews):
    """
    フィルタリングされたレビューに対して、GPT-2を使用して要約を行う関数
    """
    filtered_reviews['summary'] = filtered_reviews['content'].apply(summarize_with_gpt2)
    return filtered_reviews

