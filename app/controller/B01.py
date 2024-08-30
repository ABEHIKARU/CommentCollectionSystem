from flask import Blueprint, render_template, session
from google_play_scraper import search,Sort, reviews
import pandas as pd


b01_bp = Blueprint('b01_bp', __name__)

@b01_bp.route('/B01')
def show_b01():
    # セッションキーのリスト
    key_check=['app_id','start_date','end_date','flag']
    
    # すべてのキーがセッションにセットされているかを確認
    if all(key in session for key in key_check):
        # すべてのキーが存在する場合の処理
        app_id = session['app_id']
        start_date=session['start_date']
        end_date=session['end_date']
        flag=session['flag']
        keyword=session['keyword']
        
        # app_idからアプリ名を特定
        appName_search = search(
            app_id, 
            lang="ja",  # 日本語
            country="jp",  # 日本
            n_hits=1  # 検索件数1件のみ
        )
        # アプリ名のみを取得
        appName=appName_search[0]['title']        
        
        # ネガポジ種別フラグの変換処理
        if flag==1:
            sentiment='ポジティブ・ネガティブ'
        elif flag==2:
            sentiment='ポジティブ'
        elif flag==3:
            sentiment='ネガティブ'
            
        # 指定キーワードがNoneだった場合、「なし」に変換
        if keyword is None:
            keyword="なし"
            
        
        # レビュー1000件抽出
        reviews_scraping, continuation_token = reviews(
            app_id, 
            lang='ja',
            country='jp',
            sort=Sort.NEWEST, # 新しい順に抽出
            count=1000, # 1000件抽出
        )

        # レビューが存在しない場合
        if not reviews_scraping:
            errorMessage_list="条件に一致するレビューが見つかりませんでした"
            return render_template('B01.html',errorMessage_list=errorMessage_list)

        # データフレームに変換
        df_original=pd.DataFrame(reviews_scraping)
        # レビュー原文と投稿日時のみ格納
        df=df_original[['at','content']]
                        
        # 終了日探索
        end_date_search = pd.to_datetime(end_date)
        start_date_search = pd.to_datetime(start_date)
        
        # 終了日より過去のデータを抽出
        filtered_df = df[df['at'] < end_date_search]
        # 日付形式の変更
        filtered_df['at'] = filtered_df['at'].dt.strftime('%Y/%m/%d %H:%M')
        
        # B01.htmlへ遷移            
        return render_template('B01.html',appName=appName,start_date=start_date,end_date=end_date,sentiment=sentiment,keyword=keyword)
    
    else:
    # セッションに値がセットされていない場合の処理
        errorMessage_list="データの取得に失敗しました"
        return render_template('B01.html',errorMessage_list=errorMessage_list)    