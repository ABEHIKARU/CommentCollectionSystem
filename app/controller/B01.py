from flask import Blueprint, render_template, session
from google_play_scraper import search

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
        
        # app_idからアプリ名を特定
        appName_Search = search(
            app_id, 
            lang="ja",  # 日本語
            country="jp",  # 日本
            n_hits=1  # 検索件数1件のみ
        )
        appName=appName_Search[0]['title']        
        
        # ネガポジ種別フラグの変換処理
        if flag==1:
            sentiment='ポジティブ・ネガティブ'
        elif flag==2:
            sentiment='ポジティブ'
        elif flag==3:
            sentiment='ネガティブ'
            
        # B01.htmlへ遷移            
        return render_template('B01.html',sentiment=sentiment,appName=appName)
    else:
    # セッションに値がセットされていない場合の処理
        errorMessage="データの取得に失敗しました"
        return render_template('A01.html')
