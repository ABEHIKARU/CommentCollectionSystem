import secrets

try:
    SECRET_KEY = secrets.token_hex(16)
    print(SECRET_KEY)
except Exception as e:
    SECRET_KEY = None  # または別のデフォルト値を設定
    print(SECRET_KEY)