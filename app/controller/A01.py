from flask import Flask,Blueprint, render_template, request, redirect, url_for, flash, session
import re
import secrets

# Blueprintを作成
a01_bp = Blueprint('a01_bp', __name__)

# a01_bp.secret_key = secrets.token_hex(16)

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
       
    
        
        # Save to session
        session['url'] = url
        session['start_date'] = start_date
        session['end_date'] = end_date
        session['positive_opinion'] = positive_opinion
        session['negative_opinion'] = negative_opinion
        session['keyword'] = keyword

 
    # 正常な場合、B01.htmlへリダイレクト
    return redirect(url_for('b01_bp.show_b01'))

#     # GETリクエスト時またはエラー時のメッセージ表示
    
#     return render_template('A01.html')

# @a01_bp.route('/B01')
# def b01():
#     return render_template('B01.html')


