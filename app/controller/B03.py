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
        '、、、', '…。','"','\\"', '»(;_;)', 'mmarize:', 'summarize:', '«', '»', '...', '。。。', 'marize'
    ]
    for phrase in remove_phrases:
        text = text.replace(phrase, '')
    # バックスラッシュや不正なエスケープシーケンスを削除
    text = text.replace('\\', '')  # 単体のバックスラッシュを削除
    # 特殊文字（全角スペースや制御文字）を削除
    text = re.sub(r'[\uFF65-\uFF9F\u3000]', '', text)  # 半角カタカナや全角スペースなどを削除
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
    text = re.sub(r'[\uFF65-\uFF9F\u3000]', '', text)  # 特殊文字（半角カタカナや全角スペース）を削除

    # 文頭と文末の不要な"を削除
    text = re.sub(r'^["\']+', '', text)  # 文頭の"や'を削除
    text = re.sub(r'["\']+$', '', text)  # 文末の"や'を削除

    return text.strip()


def split_text_into_chunks(text, max_length=512):
    """
    テキストを最大512トークンごとのチャンクに分割する関数
    """
    tokens = tokenizer.encode(text)
    # 512トークンごとに分割
    chunks = [tokens[i:i + max_length] for i in range(0, len(tokens), max_length)]
    # トークンから元のテキストに戻す
    return [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]

def summarize_with_t5(text):
    """
    T5モデルを使用して長いテキストを512トークンごとに分割し、個別に要約して結合する関数
    """

    # 原文が10文字以下なら、そのまま返す
    if len(text) <= 10:
        return text

    # テキストを512トークンごとに分割
    chunks = split_text_into_chunks(text, max_length=512)
    
    # 各チャンクを要約
    summaries = []
    for chunk in chunks:
        input_text = "summarize: " + chunk

        # トークナイズ
        inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)

        # 要約生成
        summary_ids = model.generate(
            inputs,
            max_length=100,  # 要約の最大長さを少し短くする
            min_length=50,  # 最小長さを50に設定して文脈を確保
            length_penalty=1.0,  # ペナルティを少し下げる
            num_beams=8,
            no_repeat_ngram_size=5,  # 繰り返しをさらに防ぐ
            repetition_penalty=3.5,  # 繰り返しの強いペナルティ
            early_stopping=True
        )

        # 要約結果をデコード
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)

    # 要約されたチャンクを結合
    final_summary = " ".join(summaries)

    # クリーンアップして返す
    return clean_summary(final_summary)

def process_reviews(filtered_reviews):
    """
    フィルタリングされたレビューに対して、T5を使用して要約を行う関数
    """
    filtered_reviews['summary'] = filtered_reviews['content'].apply(summarize_with_t5)
    return filtered_reviews
