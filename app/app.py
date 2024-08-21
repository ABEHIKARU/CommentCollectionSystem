from flask import Flask,render_template

def create_app():
    app=Flask(__name__)
    
    app.config.from_pyfile('config.py')

    # Blueprintの登録
    from controller.search import search_bp
    app.register_blueprint(search_bp,url_prefix='/templates/hello1.html')

    from controller.views2 import hello2_bp
    app.register_blueprint(hello2_bp, url_prefix='/templates/hello2.html')

    @app.route('/')
    def home():
        return render_template('search.html')
    
    return app