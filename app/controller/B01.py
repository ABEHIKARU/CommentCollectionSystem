from flask import Blueprint, render_template, session
from google_play_scraper import search, Sort, reviews
import pandas as pd

b01_bp = Blueprint('b01_bp', __name__)

# メイン処理
@b01_bp.route('/B01')
def show_b01():
    # 必要なセッションキー
    session_keys = ['app_id', 'start_date', 'end_date', 'flag']
    
    # セッションキーのチェック
    if not check_session_keys(session_keys):
        errorMessage_list = "データの取得に失敗しました"
        return render_template('B01.html', errorMessage_list=errorMessage_list)
    
    # セッションからの値取得
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

    # 終了日から過去21件のレビューを取得
    end_date_search = pd.to_datetime(end_date)
    start_date_search = pd.to_datetime(start_date)
    df_reviews = scraping_reviews(app_id, end_date_search,start_date_search)
    print(df_reviews)

    # データが存在する場合としない場合での分岐
    if not df_reviews.empty:
        return render_template('B01.html', appName=appName, start_date=start_date, end_date=end_date, sentiment=sentiment, keyword=keyword, reviews=df_reviews.to_dict(orient='records'))
    else:
        errorMessage_list = "条件に一致するレビューが見つかりませんでした"
        return render_template('B01.html', errorMessage_list=errorMessage_list)


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

def scraping_reviews(app_id, end_date_search, start_date_search):
    """アプリのレビューを指定日まで取得し、終了日から過去21件を新しいデータフレームに格納して返す"""
    df_M = pd.DataFrame()
    df_S = pd.DataFrame(columns=['at', 'content'])
    continuation_token = None
    
    while True:
        result, continuation_token = reviews(
            app_id, 
            lang='ja',
            country='jp',
            sort=Sort.NEWEST,  # 新しい順に抽出
            count=1000,  # 1000件抽出
            continuation_token=continuation_token
        )

        if not result:
            break

        df_L = pd.DataFrame(result)
        df_M = pd.concat([df_M, df_L[['at', 'content']]], ignore_index=True)
        del df_L

        # 終了日より過去のデータが見つかった場合、ループを終了
        if df_M['at'].min() < end_date_search:
            break
    
    # 終了日より過去のデータを保持
    df_M['at'] = pd.to_datetime(df_M['at'])
    df_M = df_M[(df_M['at'] < end_date_search)]
    
    # 開始日がある場合、開始日より過去のデータを除外
    if not df_M[df_M['at'] == start_date_search].empty:
        df_M = df_M[df_M['at'] >= start_date_search]

    # 過去21件のレビューを新しいデータフレームに格納
    df_S = df_M.head(22)

    # 日付形式の変更
    df_S['at'] = df_S['at'].dt.strftime('%Y/%m/%d %H:%M')
    
    return df_S