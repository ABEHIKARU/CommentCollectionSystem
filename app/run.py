from app import create_app
from waitress import serve
import threading, webbrowser

app = create_app()

def open_browser():
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    # デバッグモードをON
    app.debug=True
    
    # ブラウザを自動起動
    threading.Timer(1.0, open_browser).start()
    
    # サーバーの起動
    serve(app, host='0.0.0.0', port=5000)
