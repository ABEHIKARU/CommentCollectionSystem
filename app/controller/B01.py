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

    # レビュー抽出
    end_date_search = pd.to_datetime(end_date)
    start_date_search = pd.to_datetime(start_date)
    df_reviews = scraping_reviews(app_id, end_date_search,start_date_search,keyword)
    
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.options.display.max_colwidth=5000
    print(df_reviews)
    
    # ネガポジフィルタリング
    filtered_reviews = filter_reviews_by_sentiment(df_reviews, sentiment)
    filtered_reviews =process_reviews(filtered_reviews)
    
    print(filtered_reviews)
    
    # データが存在する場合としない場合での分岐
    if not filtered_reviews.empty:
        return render_template('B01.html', appName=appName, start_date=start_date, end_date=end_date, sentiment=sentiment, keyword=keyword)
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

def scraping_reviews(app_id, end_date_search,start_date_search,keyword):
    """指定期間内のレビューを取得し、キーワードフィルタリングを行う"""
    # 変数の初期化
    df_M = pd.DataFrame()
    df_S = pd.DataFrame()
    l=0
    continuation_token = None
    
    while True:
        end_date_flag = False
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
            return df_M

        # 抽出した1000件のデータを継ぎ足す
        df_L = pd.DataFrame(result)
        df_M = pd.concat([df_M, df_L[['at', 'content']]], ignore_index=True)
        del df_L

        # 日付型に変更
        df_M['at'] = pd.to_datetime(df_M['at'])

        # 終了日より過去のデータがある場合
        if (df_M['at']<=end_date_search).any():
            df_M = df_M[(df_M['at'] <= end_date_search)]
            end_date_flag=True
            
        # 開始日より未来のデータがある場合
        if (df_M['at']>=start_date_search).any():
            df_M = df_M[df_M['at'] >= start_date_search]
            start_date_flag=True
        
        # 開始日がない、かつ、21件未満の場合
        if start_date_flag==False and df_M.shape[0]<21:
            continue
        
        # 変数の初期化(1度だけ実行)
        if l==0:
            i=0
            j=21  
        while True:
            # 21件を別のdfに継ぎ足す
            df_S=pd.concat([df_S,df_M[i:j]],ignore_index=True)
            
            # 次の21件がある場合
            if df_S[i:j].shape[0]==21:
                # キーワード指定がされている場合
                if keyword != 'なし':
                    df_S = df_S[df_S['content'].str.contains(keyword, case=False, na=False)]
                
                    # キーワードフィルタリングの結果、データが0件になった場合、データを補充する(21件を超えないようにする)
                    if df_S.empty:
                        i+=21
                        j+=21
                        l=1
                        # 次の21件を確保する
                        continue
                # キーワード指定がない場合
                else:
                    break
                
                i+=21
                j+=21
                l=1
                
            # 次の21件がない場合
            elif df_S[i:j].shape[0]!=21:
                # 開始日がある場合、内側のループを抜け、外側のループも抜ける
                if start_date_flag==True:
                    loop_break_flag=True
                    break
                # 開始日がない場合、内側のループを抜け、外側のループの最初(1000件抽出)に戻る
                else:
                    loop_continue_flag=True
                    break

        if loop_break_flag==True:
            break
        elif loop_continue_flag==True:
            continue            

        # 日付形式の変更
        df_S['at'] = df_S['at'].dt.strftime('%Y/%m/%d %H:%M')
                    
    return df_S