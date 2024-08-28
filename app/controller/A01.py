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
        # URLの入力チェック
        url = request.form.get('urlInput', '').strip()
        if not url:
            return redirect(url_for('review_search', message="URLを正しく入力してください"))
        if len(url) > 2083:
            return redirect(url_for('review_search', message="URLを正しく入力してください"))
        invalid_chars_pattern = r'[<>{}|\^~\[\] ]'
        if re.search(invalid_chars_pattern, url):
            return redirect(url_for('review_search', message="URLを正しく入力してください"))
        google_play_pattern = r'^(https?://)?play\.google\.com/store/apps/details\?id=([a-zA-Z0-9._-]+)$'
        match = re.match(google_play_pattern, url)
        if not match:
            return redirect(url_for('review_search', message="入力されたURLはシステム対象外です"))

        # 期間の入力チェック
        start_date = request.form.get('startDate')
        end_date = request.form.get('endDate')
        if not start_date or not end_date:
            return redirect(url_for('review_search', message="期間を指定してください"))

        # ポジティブ・ネガティブ選択チェック
        positive_opinion = 'positiveOpinion' in request.form
        negative_opinion = 'negativeOpinion' in request.form
        if not positive_opinion and not negative_opinion:
            return redirect(url_for('review_search', message="種別を選択してください"))

        # キーワードの入力チェック
        keyword = request.form.get('keyword', '').strip()
        if len(keyword) > 30:
            return redirect(url_for('review_search', message="キーワードを正しく入力してください"))
        elif keyword == "":
            keyword = None
            
              
          

        
        
        
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


