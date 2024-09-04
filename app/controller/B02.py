from flask import Blueprint
import pandas as pd
from transformers import pipeline, AutoModelForSequenceClassification, BertJapaneseTokenizer
from tqdm import tqdm

# B02のBlueprint
b02_bp = Blueprint('b02_bp', __name__)

# 事前学習モデルセット → パイプラインへ
model = AutoModelForSequenceClassification.from_pretrained('koheiduck/bert-japanese-finetuned-sentiment')
tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking')
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def judge_sentiment(text):
    """レビューのネガポジを判断する関数"""
    result = classifier(text)[0]  # リストの最初の要素を取得
    sentiment = result['label']
    
    if sentiment == 'POSITIVE':  # モデルによっては日本語ラベルを返す
        return "positive"
    elif sentiment == 'NEGATIVE':
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
