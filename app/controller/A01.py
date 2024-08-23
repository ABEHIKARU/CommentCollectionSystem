from flask import Blueprint, render_template

A01_bp = Blueprint('A01', __name__)

@A01_bp.route('/A01')
def show_A01():
    return render_template('A01.html')