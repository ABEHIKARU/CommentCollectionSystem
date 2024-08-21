from flask import Blueprint, render_template

search_bp = Blueprint('search', __name__)

@search_bp.route('/')
def hello():
    return render_template('search.html')