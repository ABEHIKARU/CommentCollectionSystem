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
        
        
        # ネガポジ種別フラグの設定
        if positive_opinion and negative_opinion:
            flag = 1
        elif positive_opinion:
            flag = 2
        elif negative_opinion:
            flag = 3
    
        
        # セッション登録
        session['url'] = url
        session['start_date'] = start_date
        session['end_date'] = end_date
        session['flag'] = flag 
        session['keyword'] = keyword

 
        # 正常な場合、B01.htmlへリダイレクト
        return redirect(url_for('b01_bp.show_b01'))

    # GETリクエスト時またはエラー時のメッセージ表示
    
    return render_template('A01.html')




