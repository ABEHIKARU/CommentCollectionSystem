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

def clean_text(text):
    """
    テキストの前処理を行う関数。無意味な文字列や空白、不要な記号を除去し、URLも削除する。
    """
    # URLの削除
    text = re.sub(r'http\S+|www\S+', '', text)  # URL削除
    text = re.sub(r'[。\.]{2,}', '。', text)  # 「。。」や「...」の削除
    text = re.sub(r'(\w)\1{2,}', r'\1', text)  # 繰り返される文字列の短縮
    text = re.sub(r'[^\w\s\-、。！？一-龥ぁ-んァ-ヴ]', '', text)  # 不要な記号の削除
    text = re.sub(r'[。、]{2,}', '。', text)  # 句読点の連続を一つに
    text = text.strip()

    # 空文字列や意味不明な場合は適切なメッセージを返す
    if len(text) == 0:
        return None
    return text

def clean_summary(summary):
    """
    生成された要約をクリーンアップして意味のある文章にする関数
    """
    # 文頭の不要な句読点や文頭の余分な空白を削除
    summary = re.sub(r'^[。、！？\s]+', '', summary)  # 文頭の句読点やスペースを削除
    summary = re.sub(r'[。 ]{2,}', '。', summary)  # 句読点の重複を削除
    summary = re.sub(r'(\w)\1{2,}', r'\1', summary)  # 繰り返し文字を削除
    summary = re.sub(r'([。、！？])\1+', r'\1', summary)  # 繰り返し句読点を削除

    # 不完全な文章（最後が句読点だけなど）を削除
    if len(re.sub(r'[。、！？]', '', summary)) == 0:
        return "要約できませんでした。"

    return summary

def summarize_with_t5(text):
    """
    T5モデルを使用して要約を行う関数。原文が短すぎる場合や無意味な場合は要約せず、そのまま返す。
    """
    # 原文が10文字以下の場合や無意味な内容の場合はスキップ
    if len(text) <= 10:
        return "要約できる内容がありません。"

    cleaned_text = clean_text(text)

    # クリーンアップ後のテキストが短すぎる場合は要約しない
    if not cleaned_text or len(cleaned_text) <= 10:
        return "要約できる内容がありません。"

    # T5モデルで要約するためのプロンプトを作成（生成時に「簡潔に要約してください」を削除するために変更）
    input_text = f"要約: {cleaned_text}"

    # トークナイズの際、長すぎる文を切り捨てずに扱う
    inputs = tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)

    # T5モデルで要約生成を実行
    summary_ids = model.generate(
        inputs.input_ids,
        max_length=50,    # 要約の最大長さ
        min_length=20,    # 要約の最小長さ
        num_beams=5,      # ビームサーチの探索幅
        no_repeat_ngram_size=3,  # 繰り返し防止
        early_stopping=True,
        repetition_penalty=3.5,  # 繰り返しの抑制を強化
        temperature=0.7,  # 生成の多様性を適度に増やす
        do_sample=False   # サンプリングをオフにして安定した結果を得る
    )

    # 生成された要約をデコード
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # クリーンアップを強化して、意味の通じる文章に
    return clean_summary(summary)


def process_reviews(filtered_reviews):
    """
    フィルタリングされたレビューに対して、T5を使用して要約を行う関数。
    """
    # applyメソッドで各レビューに対して要約を実施
    filtered_reviews['summary'] = filtered_reviews['content'].apply(summarize_with_t5)
    return filtered_reviews
