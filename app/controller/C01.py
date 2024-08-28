from flask import Blueprint, render_template, request

# Blueprintを作成
c01_bp = Blueprint('c01_bp', __name__)

# ルート: ホームページ (C01.htmlをレンダリング)
@c01_bp.route('/')
def index():
    return render_template('C01.html')

# ルート: フォームデータを処理し、結果をD01.htmlに渡す
@c01_bp.route('/process_c01', methods=['POST'])
def process_c01():
    input_data = request.form['input_data']
    processed_data = process_data(input_data)
    return render_template('D01.html', processed_data=processed_data)

# データを処理する関数
def process_data(data):
    # フォームから送信されたデータを処理するロジック
    processed_data = data.upper()  # 例えば、入力データを大文字に変換
    return processed_data 
