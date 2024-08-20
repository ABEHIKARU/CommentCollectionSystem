from flask import Blueprint, render_template

hello2_bp = Blueprint('site2', __name__)

@hello2_bp.route('/')
def hello():
    return render_template('hello2.html')