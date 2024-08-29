from flask import Flask,Blueprint, render_template, request, redirect, url_for, flash, session
import re
import secrets

# Blueprintを作成
a01_bp = Blueprint('a01_bp', __name__)



@a01_bp.route('/')
def index():
    return render_template('A01.html')

@a01_bp.route('/A01', methods=['GET', 'POST'])
def review_search():
    if request.method == 'POST':
        url = request.form.get('urlInput', '').strip()
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        positive_opinion = 'positiveOpinion' in request.form
        negative_opinion = 'negativeOpinion' in request.form
        keyword = request.form.get('keyword', '').strip()

        # # Validation and processing
        # if not url or len(url) > 2083 or re.search(r'[<>{}|\^~\[\] ]', url):
        #     flash("URLを正しく入力してください")
        
        # 正規表現パターンでURLを検証し、app_idを抽出
        google_play_pattern = r'^(https?://)?play\.google\.com/store/apps/details\?id=([a-zA-Z0-9._-]+)(&[a-zA-Z0-9._=&-]*)?$'
        match = re.match(google_play_pattern, url)
        if match:
            app_id = match.group(2)  # app_idを抽出

        else:
            flash("URLからapp_idを抽出できませんでした。正しいGoogle PlayのURLを入力してください。")
            return redirect(url_for('a01_bp.review_search'))
        
        # 期間の入力チェック
        if not start_date or not end_date:
           flash("期間を指定してください")
           return redirect(url_for('a01_bp.review_search'))
       
        # ポジティブ・ネガティブ選択チェック
        if not positive_opinion and not negative_opinion:
           flash("種別を選択してください")
           return redirect(url_for('a01_bp.review_search'))
        
        # ネガポジ種別フラグの設定
        if positive_opinion and negative_opinion:
            flag = 1
        elif positive_opinion:
            flag = 2
        elif negative_opinion:
            flag = 3
            
        # キーワードの入力チェック
        if len(keyword) > 30:
           flash("キーワードを正しく入力してください")
           return redirect(url_for('a01_bp.review_search'))
        elif keyword == "":
            keyword = None

        
        # セッション登録
        session['app_id'] = app_id
        session['start_date'] = start_date
        session['end_date'] = end_date
        session['flag'] = flag 
        session['keyword'] = keyword

 
        # 正常な場合、B01.htmlへリダイレクト
        return redirect(url_for('b01_bp.show_b01'))

    # GETリクエスト時またはエラー時のメッセージ表示
    
    return render_template('A01.html')




