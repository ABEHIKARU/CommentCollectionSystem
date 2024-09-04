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
        return "ポジティブ"
    elif sentiment == 'NEGATIVE':
        return "ネガティブ"
    else:
        return "unknown"

def filter_reviews_by_sentiment(df_reviews, sentiment):
    """ネガポジ判断を行い、指定された種別のみを保持する関数"""
    # ネガポジ判断の列を追加
    df_reviews['sentiment'] = df_reviews['content'].apply(judge_sentiment)
    
    if sentiment == "ポジティブ・ネガティブ":
        # 全件保持
        filtered_df = df_reviews
    elif sentiment == "ポジティブ":
        # ポジティブのみ保持
        filtered_df = df_reviews[df_reviews['sentiment'] == "ポジティブ"]
    elif sentiment == "ネガティブ":
        # ネガティブのみ保持
        filtered_df = df_reviews[df_reviews['sentiment'] == "ネガティブ"]
    else:
        # 指定された sentiment が存在しない場合は空のデータフレームを返す
        filtered_df = pd.DataFrame(columns=df_reviews.columns)
    
    return filtered_df
