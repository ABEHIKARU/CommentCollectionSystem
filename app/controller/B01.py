from flask import Blueprint, render_template, session, request
from google_play_scraper import search, Sort, reviews
import pandas as pd
from controller.B02 import filter_reviews_by_sentiment  # B02からフィルタリング関数をインポート
from controller.B03 import process_reviews  
from datetime import datetime
import json
import re

b01_bp = Blueprint('b01_bp', __name__)

# 検索画面からの遷移処理
@b01_bp.route('/B01')
def show_b01():
    # 必要なセッションキー
    session_keys = ['app_id', 'start_date', 'end_date', 'flag']
    
    # セッションキーのチェック
    if not check_session_keys(session_keys):
        errorMessage_list = "データの取得に失敗しました"
        return render_template('B01.html', errorMessage_list=errorMessage_list)
    
    # セッションから値取得
    app_id = session['app_id']
    start_date = session['start_date']
    end_date = session['end_date']
    flag = session['flag']
    keyword = session['keyword']
    
    # 指定キーワードがNoneだった場合、「なし」に変換
    if keyword is None:
        keyword="なし"

    # アプリ名の取得
    appName = get_app_name(app_id)

    # ネガポジ種別フラグの文字列化
    sentiment = convert_sentiment_flag(flag)

    filtered_reviews=pd.DataFrame()  # ネガポジ判断後のdfを初期化
    continuation_token=None  # 継続トークンの初期化
    pd.set_option('display.max_rows', None)  # pandasの行をターミナルに全て表示
    pd.set_option('display.max_columns', None)
    pd.options.display.max_colwidth=10000
    
    # レビュー1000件抽出
    df_scraping_reviews, continuation_token1, start_date_flag = scraping_reviews(app_id, end_date, start_date, continuation_token)
    
    # レビューが空の場合のエラーメッセージ
    if df_scraping_reviews.empty:
        errorMessage_list = "条件に一致するレビューが見つかりませんでした"
        return render_template('B01.html', errorMessage_list=errorMessage_list)

    start = 0  # 21件確保の始点
    end = 21  # 21件確保の終点
        
    # 指定された期間内のレビューが見つかるまで繰り返す
    while len(filtered_reviews) < 21:
        # レビュー21件確保
        df_21_reviews, start, end, continuation_token1 = secured_21_reviews(
            df_scraping_reviews, continuation_token1, start, end, start_date_flag, app_id, start_date, end_date)

        # レビュー21件確保できない場合
        if df_21_reviews.empty:
            break
        
        # キーワード指定
        if keyword != 'なし':
            df_21_reviews = filterling_keyword(df_21_reviews, keyword)
            
            # キーワードフィルタリングの結果、レビューが0件になった場合
            if df_21_reviews.empty:
                errorMessage_list = "条件に一致するレビューが見つかりませんでした"
                return render_template('B01.html',appName=appName, start_date=start_date, end_date=end_date, sentiment=sentiment, keyword=keyword, errorMessage_list=errorMessage_list)

        # ネガポジフィルタリング
        filtered_reviews = pd.concat([filtered_reviews, filter_reviews_by_sentiment(df_21_reviews, sentiment)], ignore_index=True)

    # 要約翻訳
    filtered_reviews = process_reviews(filtered_reviews)
    
    
    # データが存在しない場合
    if filtered_reviews.empty:
        errorMessage_list = "条件に一致するレビューが見つかりませんでした"
        return render_template('B01.html', errorMessage_list=errorMessage_list)
    
    filtered_reviews['at'] = pd.to_datetime(filtered_reviews['at']).dt.strftime('%Y/%m/%d %H:%M')
    print(filtered_reviews) 

    # json変換
    # df_all = filtered_reviews.to_json(force_ascii=False, orient='records')
    # DataFrameを一旦辞書形式に変換し、json.dumpsでエンコード
    # df_dict = filtered_reviews.to_dict(orient='records')

    # # json.dumpsでASCII以外の文字も含めて出力
    # df_all = json.dumps(df_dict, ensure_ascii=False)
    
    # JSONに変換する前に文字列列をクリーンアップ
    cleaned_reviews = clean_reviews_column(filtered_reviews, column_name='content')

    # クリーンアップ後のデータフレームをJSONに変換 (ASCII以外の文字も含めて出力)
    df_all = json.dumps(cleaned_reviews.to_dict(orient='records'), ensure_ascii=False)
    # データが存在する場合
    return render_template('B01.html', appName=appName, start_date=start_date, end_date=end_date, sentiment=sentiment, keyword=keyword, reviews=df_all)
    
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# 関数
def check_session_keys(session_keys):
    """セッションに必要なキーがすべて存在するか確認"""
    # 全てのキーが存在する場合：True
    # 全てのキーが存在しない場合：False
    return all(key in session for key in session_keys)

def get_app_name(app_id):
    """app_idからアプリ名を取得"""
    app_search_result = search(
        app_id, 
        lang="ja",  # 日本語
        country="jp",  # 日本
        n_hits=1  # 検索件数1件のみ
    )
    return app_search_result[0]['title']

def convert_sentiment_flag(flag):
    """ネガポジ種別フラグを文字列に変換"""
    sentiment_map = {
        1: 'ポジティブ・ネガティブ',
        2: 'ポジティブ',
        3: 'ネガティブ'
    }
    return sentiment_map[flag]

def scraping_reviews(app_id, end_date, start_date, continuation_token):
    """指定期間内のレビューを抽出する"""
    df_M = pd.DataFrame()  # 期間フィルタリング後のdfの初期化
    end_date_search = pd.to_datetime(end_date)  + pd.DateOffset(hours=23, minutes=59, seconds=59)  # 終了日をdatetime型に変換
    start_date_search = pd.to_datetime(start_date)  # 開始日をdatetime型に変換

    while True:
        end_date_flag = False
        start_date_flag = False
        
        try:
            # Google Playのレビュー1000件を抽出
            result, continuation_token = reviews(
                app_id, 
                lang='ja',  
                country='jp',
                sort=Sort.NEWEST,  # 新しい順に抽出
                count=1000,  # 1000件までのレビューを取得
                continuation_token=continuation_token
            )
        except Exception as e:
            print(f"レビューの抽出でエラーが発生: {str(e)}")
            return df_M, continuation_token, start_date_flag
        
        if not result:
            return df_M, continuation_token, start_date_flag 

        df_L = pd.DataFrame(result) # レビュー1000件をとりあえず入れておく
        df_M = pd.concat([df_M, df_L[['at', 'content']]], ignore_index=True) # 投稿日時とレビュー原文の列だけ保持
        del df_L 

        # 日付型に変更
        df_M['at'] = pd.to_datetime(df_M['at'])
        
        # 終了日より過去のデータがある場合、終了日より未来のデータを削除
        if (df_M['at']<=end_date_search).any():
            df_M = df_M[(df_M['at'] <= end_date_search)]
            end_date_flag=True
            
            # 開始日より未来のデータがある場合、開始日より過去のデータを削除
            if (df_M['at']>start_date_search).any():
                df_M = df_M[df_M['at'] >= start_date_search]
                start_date_flag=True
        
        # 開始日がない、かつ、21件未満の場合
        if start_date_flag==False and len(df_M)<21:
            continue
        
        # 抽出データが21件以上あり、終了日がある場合
        if len(df_M)>=21 and end_date_flag==True:
            # 投稿日時の形式を変更
            df_M['at'] = df_M['at'].dt.strftime('%Y/%m/%d %H:%M')
            return df_M, continuation_token, start_date_flag    

        # # 期間内のレビューが見つかった場合、フラグをセット
        # if not df_L_filtered.empty:
        #     start_date_flag = True
        #     # TODO 終了日で判断するべきでは？

        # # continuation_tokenが無ければ終了 TODO Noneにはならないのでは？
        # if continuation_token is None or (df_L['at'].min() < start_date_search):
        #     break

def secured_21_reviews(df_scraping_reviews, continuation_token1, start, end, start_date_flag, app_id, start_date, end_date):
    """レビュー21件を確保する"""
    df_S = pd.DataFrame()

    while len(df_S) < 21:
        # レビューが足りない場合、新しいレビューを取得
        if start >= len(df_scraping_reviews):
            df_new_scraping_reviews, continuation_token1, start_date_flag = scraping_reviews(
                app_id, end_date, start_date, continuation_token1)
            
            if df_new_scraping_reviews.empty:
                break

            df_scraping_reviews = pd.concat([df_scraping_reviews, df_new_scraping_reviews], ignore_index=True)

        # 21件のレビューを取得
        df_S = pd.concat([df_S, df_scraping_reviews[start:end]], ignore_index=True)
        start += 21
        end += 21

    return df_S, start, end, continuation_token1

def filterling_keyword(df_21_reviews, keyword):
    """キーワードフィルタリング"""
    df_21_reviews = df_21_reviews[df_21_reviews['content'].str.contains(keyword, case=False, na=False)]
    return df_21_reviews

# JSON文字列から無効な文字を削除する関数
def clean_invalid_json_chars(json_string):
    """
    JSON文字列から無効な文字を削除し、正しいJSON文字列に整形する関数。
    絵文字、不可視文字、制御文字を削除し、パースエラーを防ぐ。
    """
    # Unicode制御文字、不可視文字、絵文字を削除
    json_string = re.sub(r'[\u0000-\u001F\u007F-\u009F]', '', json_string)  # 制御文字削除
    json_string = re.sub(r'[\u200B-\u200D\uFEFF]', '', json_string)  # ゼロ幅スペースなど不可視文字削除
    
    # すべての絵文字を削除する
    emoji_pattern = re.compile(
        "[" 
        "\U0001F600-\U0001F64F"  # 顔文字
        "\U0001F300-\U0001F5FF"  # シンボル&ピクトグラム
        "\U0001F680-\U0001F6FF"  # 乗り物&地図記号
        "\U0001F1E0-\U0001F1FF"  # 国旗
        "\U00002500-\U00002BEF"  # 各種記号
        "\U00002702-\U000027B0"  # その他記号
        "\U0001F918-\U0001F9E0"  # その他追加の絵文字
        "\U0001F90D-\U0001F9FF"  # 最近追加された絵文字
        "]+", 
        flags=re.UNICODE)
    json_string = emoji_pattern.sub(r'', json_string)  # 絵文字を削除
    
    # JSONに不正なエスケープシーケンス（バックスラッシュ）を修正
    json_string = json_string.replace('\\', '\\\\')  # バックスラッシュのエスケープ
    
    # 特殊な数学記号やアクセント記号を削除
    json_string = re.sub(r'[\u0300-\u036F\u2200-\u22FF]', '', json_string)  # アクセント記号と数学記号を削除

    # 連続する無効な文字列の削除（任意で追加のルールを入れる）
    json_string = re.sub(r'[!！?？]{2,}', '', json_string)  # 繰り返しの感嘆符や疑問符を削除
    json_string = re.sub(r'[。、]{2,}', '。', json_string)  # 句読点の連続を1つに

    # 文頭の句読点や記号を削除
    json_string = re.sub(r'^[。、!?]+', '', json_string)  # 文頭にある句読点や感嘆符を削除

    # 文末の句読点や記号の連続を削除
    json_string = re.sub(r'[。、!?]+$', '', json_string)  # 文末の不要な句読点や感嘆符を削除
    
    return json_string


# DataFrameからJSON出力する前に無効な文字をクリーンアップ
def clean_reviews_column(filtered_reviews, column_name='content'):
    """
    レビューデータフレーム内の指定された列の文字列をクリーンアップする関数
    """
    filtered_reviews[column_name] = filtered_reviews[column_name].apply(clean_invalid_json_chars)
    return filtered_reviews
# def scraping_reviews(app_id, end_date, start_date, continuation_token):
#     """レビューを抽出する"""
#     df_M = pd.DataFrame()  # 全てのレビューを格納するためのデータフレーム
#     end_date_search = pd.to_datetime(end_date)  # 終了日をdatetime型に変換
#     start_date_search = pd.to_datetime(start_date)  # 開始日をdatetime型に変換

#     while True:
#         start_date_flag = False
        
#         # Google Playのレビュー1000件を抽出
#         result, continuation_token = reviews(
#             app_id, 
#             lang='ja',
#             country='jp',
#             sort=Sort.NEWEST,  # 新しい順に抽出
#             count=1000,  # 1000件までのレビューを取得
#             continuation_token=continuation_token
#         )
        
#         # レビューが取得できなかった場合、現在のデータフレームとトークンを返す
#         if not result:
#             return df_M, continuation_token, False

#         df_L = pd.DataFrame(result)

#         # 'at' 列を datetime 型に変換する
#         df_L['at'] = pd.to_datetime(df_L['at'])

#         # 指定された期間内のレビューのみをフィルタリング
#         df_L_filtered = df_L[(df_L['at'] >= start_date_search) & (df_L['at'] <= end_date_search)]
#         # TODO 期間フィルタリングは別個で関数作った方が良くないか？
        
#         # フィルタリングした結果をマスターデータフレームに追加
#         df_M = pd.concat([df_M, df_L_filtered[['at', 'content']]], ignore_index=True)
#         # 'at'列の日付を '%Y/%m/%d %H:%M' 形式に変換
#         df_M['at'] = df_M['at'].dt.strftime('%Y/%m/%d %H:%M')
#         # 期間内のレビューが見つかった場合、フラグをセット
#         if not df_L_filtered.empty:
#             start_date_flag = True
#             # TODO 終了日で判断するべきでは？

#         # continuation_tokenが無ければ終了 TODO Noneにはならないのでは？
#         if continuation_token is None or (df_L['at'].min() < start_date_search):
#             break
        
#     return df_M, continuation_token, start_date_flag


# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# イベント処理
@b01_bp.route('/B01_next_back_event', methods=['POST'])
def next_b01():
     # 必要なセッションキー
    session_keys = ['app_id', 'start_date', 'end_date']
    
    # セッションキーのチェック
    if not check_session_keys(session_keys):
        errorMessage_list = "データの取得に失敗しました"
        return render_template('B01.html', errorMessage_list=errorMessage_list)
    
    # セッションから値取得
    app_id = session['app_id']
    start_date = session['start_date']
    end_date = session['end_date']

    # リクエストから値を取得
    appName = request.form.get('appName')
    sentiment = request.form.get('sentiment')
    keyword = request.form.get('keyword')
    
    # 次に表示する20件分のデータがIndexedDB内に保存されているかチェックする

    # 該当データがIndexedDB内にある場合、IndexedDB内のデータを参照し、次ページの表示を行う

    # 該当ページのデータがIndexedDB内にない場合

    # 期間フィルタリング
    # 終了日から21件のデータを確保する。このとき下図のように、開始日を超えないように、開始日より過去のデータは除外する。
    # から、やる。

    return render_template('B01.html', appName=appName, start_date=start_date, end_date=end_date, sentiment=sentiment, keyword=keyword)