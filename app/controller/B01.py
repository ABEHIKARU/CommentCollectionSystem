from flask import Blueprint, render_template, session

b01_bp = Blueprint('b01_bp', __name__)

@b01_bp.route('/B01')
def show_b01():
    # 検索セッションチェック
    
    
    return render_template('B01.html')