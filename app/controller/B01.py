from flask import Blueprint, render_template, session
from google_play_scraper import search, Sort, reviews
import pandas as pd
from controller.B02 import filter_reviews_by_sentiment  # B02からフィルタリング関数をインポート
from controller.B03 import process_reviews  
from datetime import datetime

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
    df_all = filtered_reviews.to_json(force_ascii=False, orient='records')
    
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

#コミットテスト