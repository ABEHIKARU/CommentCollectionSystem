from flask import Blueprint, session
import pandas as pd
from transformers import pipeline

# B02のBlueprint
b02_bp = Blueprint('b02_bp', __name__)

# Llama-3-ELYZA-JP-8Bを使ったモデルのロード
classifier = pipeline("sentiment-analysis", model="elyza/Llama-3-ELYZA-JP-8B")

def judge_sentiment(text):
    """レビューのネガポジを判断する関数"""
    result = classifier(text)[0]
    return "positive" if result['label'] == "POSITIVE" else "negative"

def filter_reviews_by_sentiment(df_reviews, filter_type):
    """ネガポジ判断を行い、指定された種別のみを保持する関数"""
    # ネガポジ判断の列を追加
    df_reviews['sentiment'] = df_reviews['content'].apply(judge_sentiment)
    
    # 指定された種別（"positive"または"negative"）のみを保持
    filtered_df = df_reviews[df_reviews['sentiment'] == filter_type]
    
    return filtered_df