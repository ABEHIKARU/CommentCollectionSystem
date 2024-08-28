# from flask import Flask,render_template

# def create_app():
#     app=Flask(__name__)
    
#     app.config.from_pyfile('config.py')

#     # Blueprintの登録  
#     from controller.B01 import B01_bp
#     app.register_blueprint(B01_bp,url_prefix='/templates/B01.html')

#     # 最初の画面(A01)
#     @app.route('/')
#     def home():
#         return render_template('A01.html')
    
   
    
#     return app
from flask import Flask
from controller.C01 import c01_bp  # Blueprintをインポート
from controller.A01 import a01_bp

def create_app():
    app = Flask(__name__)
    
    app.config.from_pyfile('config.py')
    
    # Blueprintをアプリケーションに登録
    app.register_blueprint(a01_bp, url_prefix='/')
    app.register_blueprint(c01_bp, url_prefix='/')

    return app
