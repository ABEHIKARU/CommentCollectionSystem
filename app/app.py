from flask import Flask,render_template

def create_app():
    app=Flask(__name__)
    
    app.config.from_pyfile('config.py')

    # Blueprintの登録  
    from controller.B01 import B01_bp
    app.register_blueprint(B01_bp,url_prefix='/templates/B01.html')

    # 最初の画面(A01)
    @app.route('/')
    def home():
        return render_template('A01.html')
    
    return app