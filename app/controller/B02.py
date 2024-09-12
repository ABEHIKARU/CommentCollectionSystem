from flask import Blueprint
import pandas as pd
from transformers import pipeline, AutoModelForSequenceClassification, BertJapaneseTokenizer

# B02のBlueprintを作成（Flaskアプリケーションのモジュール化）
b02_bp = Blueprint('b02_bp', __name__)

# 事前学習済みの日本語用BERTモデルをロードし、感情分類に使用する
# このモデルはポジティブ/ネガティブ感情分類に特化している
model = AutoModelForSequenceClassification.from_pretrained('koheiduck/bert-japanese-finetuned-sentiment')

# 日本語テキストのトークナイザー（単語分割）をロード
tokenizer = BertJapaneseTokenizer.from_pretrained('cl-tohoku/bert-base-japanese-whole-word-masking')

# 感情分析パイプラインの作成（モデルとトークナイザーを統合して感情分析ができるようにする）
classifier = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

def judge_sentiment(text):
    """
    レビューのネガティブ/ポジティブを判断する関数
    入力されたテキストに対して感情分析を行い、結果を返す
    """
    result = classifier(text)[0]  # classifierはリスト形式で結果を返すため、最初の要素を取得
    sentiment = result['label']  # 感情分類の結果ラベル（'POSITIVE' または 'NEGATIVE'）を取得
    
    # 結果ラベルに基づいて、ポジティブかネガティブかニュートラルを返す
    if sentiment == 'POSITIVE':
        return "+"
    elif sentiment == 'NEGATIVE':
        return "-"
    elif sentiment == 'NEUTRAL':
        return "~"  
    else:
        return "unknown"  # ラベルが不明な場合（通常は発生しないが保険として）

def filter_reviews_by_sentiment(df_reviews, sentiment):
    """
    データフレームのレビューをネガポジ感情に基づいてフィルタリングする関数
    指定された感情（ポジティブ、ネガティブ、または全件）に基づいてフィルタリングを行う
    """
    
    # データフレームの 'content' 列（レビュー本文）に対して感情分析を行い、結果を 'sentiment' 列として追加
    df_reviews['sentiment'] = df_reviews['content'].apply(judge_sentiment)
    
    # 引数で渡された 'sentiment' に応じてフィルタリングを行う
    if sentiment == "ポジティブ・ネガティブ":
        # 全件保持する（フィルタリングしない）
        filtered_df = df_reviews
    elif sentiment == "ポジティブ":
        # ポジティブなレビューのみを保持
        filtered_df = df_reviews[df_reviews['sentiment'] == "+"]
    elif sentiment == "ネガティブ":
        # ネガティブなレビューのみを保持
        filtered_df = df_reviews[df_reviews['sentiment'] == "-"]
    else:
        # 指定された感情が存在しない場合、空のデータフレームを返す
        filtered_df = pd.DataFrame(columns=df_reviews.columns)
    
    # フィルタリングされたデータフレームを返す
    return filtered_df
