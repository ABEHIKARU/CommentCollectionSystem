from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import re

# Blueprintを作成
a01_bp = Blueprint('a01_bp', __name__)

@a01_bp.route('/')
def index():
    # A01.html読み込み時、セッションクリア
    session.clear()  # セッションをクリアして新しいセッションを開始
    return render_template('A01.html')  # A01.htmlを表示

@a01_bp.route('/A01', methods=['GET', 'POST'])
def review_search():
    if request.method == 'POST':
        try:
            # フォームからのデータ取得
            url = request.form.get('urlInput', '').strip()  # URL入力
            start_date = request.form.get('startDate').replace('-', '/')  # 開始日
            end_date = request.form.get('endDate').replace('-', '/')  # 終了日
            positive_opinion = 'positiveOpinion' in request.form  # ポジティブ意見の真偽値
            negative_opinion = 'negativeOpinion' in request.form  # ネガティブ意見の真偽値
            keyword = request.form.get('keyword', '').strip()  # キーワード入力

            # URLのチェック
            if  url == "":
                flash("URLを正しく入力してください") 
                return redirect(url_for('a01_bp.review_search'))
            
            # URLの文字数チェック
            if len(url) > 2083:
                flash("URLを正しく入力してください") 
                return redirect(url_for('a01_bp.review_search'))

            # 無効な文字の正規表現パターン
            invalid_chars = r'[ <>{}|\\^~\[\]#%"\']'
            
            # 無効な文字チェック
            if re.search(invalid_chars, url) is not None:
                flash("URLを正しく入力してください")  
                return redirect(url_for('a01_bp.review_search'))

            # Google Play URLの正規表現パターンを使って検証
            google_play_pattern = r'^(https?://)?play\.google\.com/store/apps/details\?id=([a-zA-Z0-9._-]+)(&[a-zA-Z0-9._=&-]*)?$'
            match = re.match(google_play_pattern, url)
            if match is not None:
                app_id = match.group(2)  # app_idを抽出
            else:
                flash("入力されたURLはシステム対象外です")  
                return redirect(url_for('a01_bp.review_search'))

            # 期間の入力チェック
            if start_date == "" or end_date == "":
                flash("期間を指定してください")  
                return redirect(url_for('a01_bp.review_search'))

            # ポジティブ・ネガティブ選択チェック
            if positive_opinion is False and negative_opinion is False:
                flash("種別を選択してください")  
                return redirect(url_for('a01_bp.review_search'))

            # ネガポジ種別フラグの設定
            if positive_opinion is True and negative_opinion is True:
                flag = 1  # 両方選択された場合
            elif positive_opinion is True:
                flag = 2  # ポジティブのみ選択
            elif negative_opinion is True:
                flag = 3  # ネガティブのみ選択

            # キーワードの入力チェック
            if len(keyword) > 30:
                flash("キーワードを正しく入力してください")  
                return redirect(url_for('a01_bp.review_search'))
            elif keyword == "":
                keyword = None  # 空の場合はNoneに設定

            # セッション登録
            session['app_id'] = app_id  
            session['start_date'] = start_date  
            session['end_date'] = end_date 
            session['flag'] = flag 
            session['keyword'] = keyword 

            # 正常な場合、B01.pyへリダイレクト
            return redirect(url_for('b01_bp.show_b01'))

        except Exception as e:
            # エラーメッセージの表示
            flash(f"エラーが発生しました: {str(e)}")  # エラー内容を表示
            return redirect(url_for('a01_bp.review_search'))
        
    # GETリクエスト時またはエラー時の処理
    else:
        return render_template('A01.html')
    # # GETリクエスト時またはエラー時のメッセージ表示
    # return render_template('A01.html')  # GETリクエストの場合はA01.htmlを表示

@a01_bp.route('/A01_clear_session_and_redirect', methods=['POST'])
def clear_session_and_redirect():
    # セッションをクリア
    session.clear()  # セッションをクリア

    # 検索画面にリダイレクト
    return render_template('A01.html')  # A01.htmlを表示
