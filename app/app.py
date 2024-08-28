from flask import Flask

# Blueprintをインポート
from controller.A01 import a01_bp
from controller.B01 import b01_bp
from controller.C01 import c01_bp  

def create_app():
    app = Flask(__name__)
    
    app.config.from_pyfile('config.py')
    
    # Blueprintをアプリケーションに登録
    app.register_blueprint(a01_bp, url_prefix='/')
    app.register_blueprint(b01_bp, url_prefix='/')
    app.register_blueprint(c01_bp, url_prefix='/')

    return app
