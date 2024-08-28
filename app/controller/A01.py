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
        #     # flash("URLを正しく入力してください")
        #     message = "URLを正しく入力してください"
        #     return render_template('A01.html', message=message)

        # URLのバリデーション
        if not url or len(url) > 2083 or re.search(r'[<>{}|\^~\[\] ]', url):
            return redirect(url_for('a01_bp.show_message', message="URLを正しく入力してください"))

        # 期間のバリデーション
        if not start_date or not end_date:
            return redirect(url_for('a01_bp.show_message', message="期間を指定してください"))

        # ポジティブ・ネガティブ選択チェック
        if not positive_opinion and not negative_opinion:
            return redirect(url_for('a01_bp.show_message', message="種別を選択してください"))

        # キーワードのバリデーション
        if len(keyword) > 30:
            return redirect(url_for('a01_bp.show_message', message="キーワードを正しく入力してください"))
        
        
        # Save to session
        session['url'] = url
        session['start_date'] = start_date
        session['end_date'] = end_date
        session['positive_opinion'] = positive_opinion
        session['negative_opinion'] = negative_opinion
        session['keyword'] = keyword

    return render_template('B01.html')

@a01_bp.route('/B01')
def b01():
    return render_template('B01.html')


@a01_bp.route('/show_message')
def show_message():
    message = request.args.get('message', '')
    return render_template('A01.html', message=message)
