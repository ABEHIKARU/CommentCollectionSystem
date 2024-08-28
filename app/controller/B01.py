from flask import Blueprint, render_template

b01_bp = Blueprint('b01_bp', __name__)

@b01_bp.route('/')
def show_b01():
    return render_template('B01.html')