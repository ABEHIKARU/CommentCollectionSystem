from flask import Blueprint
import pandas as pd
from transformers import T5Tokenizer, T5ForConditionalGeneration
import re
import torch

# B03のBlueprintを作成
b03_bp = Blueprint('b03_bp', __name__)

# T5トークナイザーとT5日本語モデルをロード
tokenizer = T5Tokenizer.from_pretrained('sonoisa/t5-base-japanese')
model = T5ForConditionalGeneration.from_pretrained('sonoisa/t5-base-japanese')
def clean_summary(text):
    """
    不要なフレーズや句読点の連続を削除し、クリーンな要約を返す関数
    """
    # 不要なフレーズを削除
    remove_phrases = [
        'トラックバック一覧です', '(^_^;)', '(t_t)', 'oo:', ':>_<', '。。。。。', 
        '、、、', '…。', '»(;_;)', 'mmarize:', 'summarize:', '«', '»', '...', '。。。'
    ]
    for phrase in remove_phrases:
        text = text.replace(phrase, '')

    # 連続するピリオドやカンマ、特殊文字を削除
    text = re.sub(r'[。、]{2,}', '。', text)  # 句読点の連続を1つに
    text = re.sub(r'[!！?？]{2,}', '', text)  # 繰り返しの感嘆符や疑問符を削除
    text = re.sub(r'[\s]+', ' ', text)  # 不要な空白の連続を1つに
    text = re.sub(r':+', '', text)  # コロンの連続を削除

    # 文頭が句読点や特殊記号の場合削除
    text = re.sub(r'^[。、！？:\s]+', '', text)

    # 文末に不必要な句読点が連続している場合を削除
    text = re.sub(r'[。！？:\s]+$', '', text)

    # 重複する単語や不自然な繰り返しを削除
    text = re.sub(r'(.)\1{2,}', r'\1', text)  # 同じ文字の連続を1つに
    text = re.sub(r'(最低){2,}', '最低', text)  # "最低"の繰り返しを1回に

    return text.strip()

def summarize_with_t5(text):
    """
    T5モデルを使用して要約を行う関数
    """
    input_text = "summarize: " + text

    # トークナイズ
    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

    # 要約生成
    summary_ids = model.generate(
        inputs,
        max_length=130,
        min_length=50,  # 最小長さを50に設定して文脈を確保
        length_penalty=1.2,
        num_beams=8,
        no_repeat_ngram_size=3,
        repetition_penalty=1.8,
        early_stopping=True
    )
    
    # 要約結果をデコード
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    # 要約をクリーンアップ
    return clean_summary(summary)

def process_reviews(filtered_reviews):
    """
    フィルタリングされたレビューに対して、T5を使用して要約を行う関数
    """
    filtered_reviews['summary'] = filtered_reviews['content'].apply(summarize_with_t5)
    return filtered_reviews

