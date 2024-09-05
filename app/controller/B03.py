from flask import Blueprint
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import re
import difflib

# B03のBlueprintを作成（Flaskアプリケーションのモジュール化）
b03_bp = Blueprint('b03_bp', __name__)

# T5モデルとトークナイザーをロード（T5の日本語モデルを使用）
tokenizer = T5Tokenizer.from_pretrained('sonoisa/t5-base-japanese')
model = T5ForConditionalGeneration.from_pretrained('sonoisa/t5-base-japanese')

def clean_text(text):
    """
    テキストの前処理を行う関数。無意味な文字列や空白、不要な記号を除去。
    """
    # 無意味な繰り返し文字や不要なスペースの削除
    text = re.sub(r'[。\.]{2,}', '。', text)  # 「。。」や「...」の削除
    text = re.sub(r'(\w)\1{2,}', r'\1', text)  # 繰り返される文字列の短縮（例: 「あああ」 -> 「あ」）
    text = re.sub(r'[^一-龥ぁ-んァ-ヴa-zA-Z0-9ａ-ｚＡ-Ｚ０-９。、！？ ]', '', text)  # 不要な記号の削除
    text = text.strip()
    return text

def correct_spelling(text):
    """
    テキストのスペルをある程度補正する関数。
    簡易的なスペルチェックと誤字修正を行います。
    """
    words = text.split()
    corrected_words = [difflib.get_close_matches(word, words, n=1)[0] for word in words]
    return ' '.join(corrected_words)

def post_process_summary(summary):
    """
    要約後のポストプロセッシング。繰り返しや冗長な部分を削除する。
    """
    summary = re.sub(r'(。)\1+', r'\1', summary)  # 繰り返される句点の削除
    summary = re.sub(r'(同じフレーズ|文が繰り返された場合の処理)', r'\1', summary)  # 具体的な重複削除
    summary = summary.strip()
    return summary

def summarize(text):
    """
    要約のみを行う関数
    """
    # テキストの前処理
    cleaned_text = clean_text(text)
    cleaned_text = correct_spelling(cleaned_text)  # スペルの修正
    
    # 要約のためのプロンプトを作成
    prompt = f"要約: {cleaned_text}"
    
    # テキストをトークナイズ
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    
    # モデルに入力して要約を生成 (num_beams を6に増やし、より多くの候補を探索)
    summary_ids = model.generate(inputs.input_ids, max_length=50, num_beams=6, early_stopping=True)
    
    # 生成されたテキストをデコード
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    # 冗長な部分を削除するポストプロセッシング
    summary = post_process_summary(summary)
    
    return summary if summary else cleaned_text

def process_reviews(filtered_reviews):
    """
    フィルタリングされたレビューに対して、要約を行う関数
    """
    # 'content' 列の各レビューに対して、要約を適用
    filtered_reviews['summary'] = filtered_reviews['content'].apply(summarize)
    
    return filtered_reviews
