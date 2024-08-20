from flask import Blueprint, render_template

hello1_bp = Blueprint('site1', __name__)

@hello1_bp.route('/')
def hello():
    return render_template('hello1.html')