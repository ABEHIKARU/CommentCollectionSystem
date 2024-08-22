from flask import Blueprint, render_template

A01_bp = Blueprint('A01', __name__)

@A01_bp.route('/')
def hello():
    return render_template('A01.html')