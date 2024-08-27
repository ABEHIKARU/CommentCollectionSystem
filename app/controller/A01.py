from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/A01', methods=['GET', 'POST'])
def A01():
    if request.method == 'POST':
        # ここで入力データを処理（バリデーションやセッション設定などを行う場合はここに記述）

        # B01.htmlにリダイレクト
        return redirect(url_for('B01'))

    # GETリクエスト時はA01.htmlを表示
    return render_template('A01.html')

@app.route('/B01')
def B01():
    # B01.htmlを表示
    return render_template('B01.html')

