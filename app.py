from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user
import os


# =========================================================================
# 設定
# =========================================================================
app = Flask(__name__)

# dbのパス
# 拡張子は"db"であること！
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db' # /instance/user.db (ファイル名『user』は任意に変更できる)

# ユーザーがログイン状態なのか、ログアウト状態なのか判別
app.config['SECRET_KEY'] = os.urandom(24)

# db立ち上げ
db = SQLAlchemy(app)

# ログインマネージャーを使う
login_manager = LoginManager()

# インスタンスの初期化（おまじない）
login_manager.init_app(app)

# クラスUser作成
# 理由1： dbを作成する際に使うので（Create Tableに使う）
# 理由2： ユーザー情報の登録・参照に使うため（INSERT IN TO・SELECT WHEREに使う）
class User(UserMixin, db.Model):
    """
    クラスでユーザーDBをの内容を指定
    id       : int型 primary key
    username : str型(50文字) nullを許容しない・必ず入る 重複を許さない
    password : str型(25文字)
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(25))


# =========================================================================
# view
# =========================================================================

# login中のユーザーでサイトを巡回するために必要
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# サインアップ画面（ユーザー登録画面）
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        # post時
        username = request.form["login-id"]# ユーザー名取得
        password = request.form["password"]# パスワード取得
        print(username)
        print(password)
        # Userのインスタンスを作成
        # パスワードはハッシュ関数でハッシュ化して保存
        user = User(username=username, password=generate_password_hash(password))
        # dbに追加
        db.session.add(user)
        db.session.commit()
        # ログインページへ飛ばす
        return redirect('login')
    else:
        # get時
        return render_template('signup.html')


# ログイン画面
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        # post時
        username = request.form['login-id'] # 入力されたユーザー名をキャッチ
        password = request.form['password'] # 入力されたパスワードをキャッチ
        print(username)
        print(password)
        # Userテーブルからusernameに一致するユーザを取得
        # fillter_byで一番上でヒットしたレコードを取得
        user = User.query.filter_by(username=username).first()
        # ハッシュ化したもの同士で比較する
        if check_password_hash(user.password, password):
            # 一致すればログイン成功
            login_user(user)
            # tweetsページへ入る
            return redirect('home')
    else:
        # get時
        return render_template('login.html')

@app.route('/')
def home():
    return render_template('home.html')

# =========================================================================
# 起動
# =========================================================================
if __name__== '__main__':
    app.run(debug=True)