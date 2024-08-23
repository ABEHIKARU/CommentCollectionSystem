from flask import Blueprint, render_template

B01_bp = Blueprint('B01', __name__)

@B01_bp.route('/')
def show_B01():
    return render_template('B01.html')