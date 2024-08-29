from flask import Blueprint, render_template, session

b01_bp = Blueprint('b01_bp', __name__)

@b01_bp.route('/B01')
def show_b01():
    # セッションキーのリスト
    key_check=['app_id','start_date','end_date','flag']
    
    # すべてのキーがセッションにセットされているかを確認
    if all(key in session for key in key_check):
        # すべてのキーが存在する場合の処理
        return render_template('B01.html')
    else:
    # セッションに値がセットされていない場合の処理
        return render_template('A01.html')
