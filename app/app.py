from flask import Flask,render_template

def create_app():
    app=Flask(__name__)
    
    app.config.from_pyfile('config.py')

    # Blueprintの登録
    from controller.A01 import A01_bp
    app.register_blueprint(A01_bp,url_prefix='/templates/A01.html')

    @app.route('/')
    def home():
        return render_template('A01.html')
    
    return app