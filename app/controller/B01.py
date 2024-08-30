from flask import Blueprint, render_template, session
from google_play_scraper import search,Sort, reviews
import pandas as pd
from datetime import date


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
        if keyword==None:
            keyword="なし"
            
        # レビュー1000件抽出
        reviews_scraping, continuation_token = reviews(
            app_id, 
            lang='ja',
            country='jp',
            sort=Sort.NEWEST, # 新しい順に抽出
            count=200, # 1000件抽出(テスト段階では200件)
        )
        # データフレームに変換
        df=pd.DataFrame(reviews_scraping)
        # レビュー原文と投稿日時のみ格納
        df_mini=df[['at','content']]
        # 日付形式の変更
        df_mini['at'] = pd.to_datetime(df_mini['at']).dt.strftime('%Y/%m/%d %H:%M')    
        
        # 終了日探索
        
        
        
        # B01.htmlへ遷移            
        return render_template('B01.html',appName=appName,start_date=start_date,end_date=end_date,sentiment=sentiment,keyword=keyword)
    else:
    # セッションに値がセットされていない場合の処理
        errorMessage="データの取得に失敗しました"
        return render_template('A01.html')    