from flask import Blueprint, render_template, session
from google_play_scraper import search, Sort, reviews
import pandas as pd
from controller.B02 import filter_reviews_by_sentiment  # B02からフィルタリング関数をインポート
from controller.B03 import process_reviews  

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

    filtered_reviews=pd.DataFrame() # ネガポジ判断後のdfを初期化
    continuation_token=None # 継続トークンの初期化
    start=0 # 21件確保の始点
    end=21 # 21件確保の終点

    pd.set_option('display.max_rows', None) # pandasの行をターミナルに全て表示
    
    # レビュー1000件抽出
    df_scraping_reviews,continuation_token1,start_date_flag = scraping_reviews(app_id, end_date,start_date,continuation_token)
        
    while len(filtered_reviews)<21:
        # レビュー21件確保
        df_21_reviews,start,end,continuation_token1=secured_21_reviews(df_scraping_reviews,continuation_token1,start,end,start_date_flag)
        print(df_21_reviews)
        
        # レビュー21件確保できない場合
        if df_21_reviews.empty:
            break
        
        # キーワード指定
        if keyword != 'なし':
            df_21_reviews=filterling_keyword(df_21_reviews,keyword)
            print(df_21_reviews)
            
        # キーワードフィルタリングの結果、0件になった場合
        if df_21_reviews.empty:
            continue
        
        # ネガポジフィルタリング
        filtered_reviews = pd.concat([filtered_reviews, filter_reviews_by_sentiment(df_21_reviews, sentiment)], ignore_index=True)
        print(filtered_reviews)
        
    # 要約翻訳
    filtered_reviews = process_reviews(filtered_reviews)
    print(filtered_reviews)    
    
    # データが存在する場合としない場合での分岐
    if not filtered_reviews.empty:
        return render_template('B01.html', appName=appName, start_date=start_date, end_date=end_date, sentiment=sentiment, keyword=keyword)
    else:
        errorMessage_list = "条件に一致するレビューが見つかりませんでした"
        return render_template('B01.html', errorMessage_list=errorMessage_list)
    
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

def scraping_reviews(app_id, end_date,start_date,continuation_token):
    """指定期間内のレビューを抽出する"""
    # TODO:一度だけ変数の初期化をする 
    df_M=pd.DataFrame()
    end_date_search = pd.to_datetime(end_date) # 終了日を日付型に
    start_date_search = pd.to_datetime(start_date) # 開始日を日付型に

    while True:
        start_date_flag = False
        
        # レビュー1000件抽出
        result, continuation_token = reviews(
            app_id, 
            lang='ja',
            country='jp',
            sort=Sort.NEWEST,  # 新しい順に抽出
            count=1000,  # 1000件抽出
            continuation_token=continuation_token
        )
        
        # レビューが存在しない場合
        if not result:
            return df_M # TODO:メイン処理でdf_Mの初期化をする

        # 抽出した1000件のデータを継ぎ足す
        df_L = pd.DataFrame(result)
        df_M = pd.concat([df_M, df_L[['at', 'content']]], ignore_index=True)
        del df_L

        # 日付型に変更
        df_M['at'] = pd.to_datetime(df_M['at'])

        # 終了日より過去のデータがある場合
        if (df_M['at']<=end_date_search).any():
            df_M = df_M[(df_M['at'] <= end_date_search)]
            
        # 開始日より未来のデータがある場合
        if (df_M['at']>start_date_search).any():
            df_M = df_M[df_M['at'] > start_date_search]
            start_date_flag=True
            
        # 開始日がない、かつ、開始日と終了日が同じ場合
        if start_date_flag==False and start_date==end_date:
            df_M=None
            return df_M,continuation_token,start_date_flag
        
        # 開始日がない、かつ、21件未満の場合
        if start_date_flag==False and df_M.shape[0]<21:
            continue
        
        # 投稿日時の形式を変更
        df_M['at'] = df_M['at'].dt.strftime('%Y/%m/%d %H:%M')
                    
        return df_M,continuation_token,start_date_flag

def secured_21_reviews(df_scraping_reviews,continuation_token1,start,end,start_date_flag):
    """レビュー21件を確保する"""
    # データフレームの初期化
    df_S=pd.DataFrame()
        
    # 次の21件がなく、開始日がない場合、レビュー1000件抽出を行う
    if len(df_scraping_reviews[start:end])<21 and start_date_flag==False:
        start+=21
        end+=21
        scraping_reviews(continuation_token1)
        
    # 次の21件がある場合
    else:
        # 21件を別のdfに継ぎ足す
        df_S=pd.concat([df_S,df_scraping_reviews[start:end]],ignore_index=True)
        start+=21
        end+=21
        
        return df_S,start,end,continuation_token1

def filterling_keyword(df_21_reviews,keyword):
    """キーワードフィルタリング"""
    df_21_reviews = df_21_reviews[df_21_reviews['content'].str.contains(keyword, case=False, na=False)]
        
    return df_21_reviews