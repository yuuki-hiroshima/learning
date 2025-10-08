# ここで「道具」を棚から取ってくる。なぜ必要？
# → Flaskは“お手紙の受付係”、sqlite3は“ノート(データベース)を書くペン”、osは“ファイルがあるか見る目”
from flask import Flask, render_template, request, jsonify
import sqlite3
import os

# Flaskの“アプリ本体”を作る。なぜ必要？
# → ここから「この住所に手紙が来たら、この仕事をするよ」と命令できるようになる
app = Flask(__name__)

# データをしまう“ノート”の名前。なぜ変数で？
# → あちこちで同じ名前を使うから、1か所で変えられるようにする
DB_FILE = "users.db"

# はじめて起動したときに、ノートがなければ作る係。なぜ必要？
# → 空のノートがないと、書こうとしても書けないから
def init_db():
    # os.path.exists は「そのファイル、もう ある？」の意味
    if not os.path.exists(DB_FILE):
        # with sqlite3.connect(DB_FILE) as conn:
        # なぜ with？ →「使い終わったら じどうで片づけ(閉じる)」してくれる安全スイッチ
        # なぜ as conn？ → “長い名前”にニックネーム(conn)をつけて、以後 短く呼べるように
        with sqlite3.connect(DB_FILE) as conn:
            # conn.cursor() は「注文窓口」を出す。なぜ必要？
            # → SQLという注文票を“お店（DB）”に渡す係がカーソルだから
            c = conn.cursor()

            # c.execute(...) は「注文票を出す」。execute = 実行する・注文する
            # なぜこのSQL？ → usersという表を作る。idは自動番号、name/emailは文字。emailは重複禁止
            c.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE
                )
            """)

            # ここで commit（こみっと）。なぜ必要？
            # → 「下書き」を「本決まり」にするボタン。押さないと消えることがある
            conn.commit()

# いつでもノートに触れるように、接続を作る小さな関数。なぜ分ける？
# → 同じ書き方を何度も書かないため（間違いを減らす）
def get_connection():
    return sqlite3.connect(DB_FILE)

# ここは ホームページ("/") に来たら、index.html を見せる。なぜ必要？
# → ブラウザに最初の画面を渡すため
@app.route("/")
def index():
    # render_template は「templates フォルダから その名前のHTMLを持ってきて返す」
    return render_template("index.html")

# ここは「新しい人を登録して」と手紙(POST)が来たときの受付窓口
@app.route("/api/register", methods=["POST"])
def register():
    # request.get_json() は「手紙の中身(JSON)を開けて読む」
    data = request.get_json()
    # .get("name") は「name って書いてある値ちょうだい」
    name = data.get("name")
    email = data.get("email")

    # 入ってないなら、すぐ注意を返す。なぜここで？
    # → 入力が空だと、この先の作業をしてもムダだから、早めに止める
    if not name or not email:
        # jsonify は「Pythonの辞書 → ブラウザに渡せるJSON」に変える出口
        # 後ろの ,400 は「入力まちがいだよ」の番号
        return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

    try:
        # with は「使い終わったら勝手に片づけ」。データの置き忘れや閉じ忘れを防ぐ
        with get_connection() as conn:
            c = conn.cursor()
            # ? は「あとで安全に数字や文字を入れる穴」。なぜ必要？
            # → 文字をベタッとつなげると危ない（注射針＝インジェクション対策）
            c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            conn.commit()  # 本決まりにする
        # ここまで来たら成功のお返事
        return jsonify({"status": "success", "message": f"{name} さんを登録しました！"})
    except sqlite3.IntegrityError:
        # email は “重複ダメ” ルール。ぶつかったらここに来る
        # ,409 は「もうあるよ（競合）」の番号
        return jsonify({"status": "error", "message": "このアドレスはすでに登録済みです。"}), 409

# ここは「みんなの一覧をちょうだい」（GET）の受付
@app.route("/api/list", methods=["GET"])
def get_list():
    # request.args.get は「URLの ? 以降から ことばを取り出す」
    # q は検索のことば、sort は並べ方。ない時は空や既定値
    q = request.args.get("q", "", type=str).strip()
    sort = request.args.get("sort", "id_desc", type=str)

    # 検索がないなら WHERE はつけない。なぜ？
    # → ムダな条件をつけない方が速いし読みやすいから
    where_sql = ""
    params = []  # ? の穴に入れる実際の値を入れておく袋
    if q:
        # LIKE と % は「部分一致さがし」。%いぬ% なら「いぬ」を含むもの
        where_sql = "WHERE name LIKE ? OR email LIKE ?"
        like = f"%{q}%"
        # extend は「2つまとめて袋に入れる」。appendを2回でもOKだけど長いから
        params.extend([like, like])

    # 並べ替えのルール表。なぜ表に？ → 危ない文字を入れられないように“許可リスト”で限定するため
    sort_map = {
        "id_asc": "id ASC",
        "id_desc": "id DESC",
        "name_asc": "name ASC",
        "name_desc": "name DESC",
        "email_asc": "email ASC",
        "email_desc": "email DESC",
    }
    # もし知らないキーが来ても、既定の「id DESC」にする。なぜ？
    # → へんな指示で壊れないように、安全な道に戻すため
    order_by = sort_map.get(sort, "id DESC")

    # 最後に文をくっつけて完成。「どれを」「どんな順で」出すか
    sql = f"SELECT id, name, email FROM users {where_sql} ORDER BY {order_by}"

    # 文を持って、実際にお店(DB)へ頼みに行く
    with get_connection() as conn:
        c = conn.cursor()
        # execute は「この注文どおりにやって」。params は ? の中身
        c.execute(sql, params)
        # fetchall は「お皿にのった結果を全部ちょうだい」
        rows = c.fetchall()

        # そのままだと数字の並びなので、前端(JS)が食べやすい形（辞書のリスト）に盛りなおす
        users = [{"id": r[0], "name": r[1], "email": r[2]} for r in rows]

    # jsonify で箱に包んで、お返事として渡す
    return jsonify(users)

# ここは「この番号の人を、新しい名前・メールに直して」（PUT）の受付
@app.route("/api/update/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    # 空なら直す情報がないので、早めにおことわり
    if not name or not email:
        return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

    with get_connection() as conn:
        c = conn.cursor()
        # WHERE id=? は「この番号の人だけ」を狙う。なぜ番号？
        # → 名前は変わることがあるけど、番号(id)は一生かわらない“しるし”だから
        c.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, user_id))
        conn.commit()
        # rowcount は「何人 分 直せた？」の数。0なら見つからなかった
        if c.rowcount == 0:
            return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404

    return jsonify({"status": "success", "message": "更新しました。"})

# ここは「この番号の人を消して」（DELETE）の受付
@app.route("/api/delete/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    with get_connection() as conn:
        c = conn.cursor()
        # (user_id,) とカンマがあるのは“1個だけのタプル”という決まり
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        if c.rowcount == 0:
            return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404
    return jsonify({"status": "success", "message": "削除しました。"})

# ここからアプリを走らせる。なぜ if __name__ == "__main__"？
# → “このファイルを直接実行したときだけ”下を動かす。他の場所から読まれた時は動かさない安全装置
if __name__ == "__main__":
    # まずノート(DB)を用意（なければ作る）
    init_db()
    # 自分のパソコンの中でサーバーを動かす。debug=True は「間違いを見つけやすくする」スイッチ
    app.run(debug=True, host="127.0.0.1", port=8000)



# ========== ここから下は、説明を簡略化したバージョン ==========

# # ===== 必要な部品（ライブラリ）を取り出す =====
# from flask import Flask, render_template, request, jsonify  # Flask本体と、HTML描画・リクエスト受け取り・JSON返却の道具
# import sqlite3                                              # SQLite（軽量DB）を扱うための標準モジュール
# import os                                                   # ファイルの存在確認など、OSまわりの便利関数

# # ===== Flaskアプリ（サーバーの本体）を作成 =====
# app = Flask(__name__)  # Flaskのインスタンス。以降の @app.route はこの“app”に紐づく

# # ===== DBファイルの場所（設定） =====
# DB_FILE = "users.db"   # SQLiteの実体ファイル名。アプリ直下に作られる

# # ===== 初期化：DBが無ければ作る（テーブルも準備） =====
# def init_db():
#     """データベースがなければ作成し、テーブルを準備"""
#     if not os.path.exists(DB_FILE):                       # ファイルが存在するか（exists）をチェック
#         with sqlite3.connect(DB_FILE) as conn:            # DBに接続。withで自動クローズ＆自動コミット（例外時は自動ロールバック）
#             c = conn.cursor()                             # SQLを実行するための「カーソル（指揮役）」を取得
#             c.execute("""                                 # SQLを実行：usersテーブルを作成
#                 CREATE TABLE users (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT, # id列：自動で1,2,3...と採番（主キー＝その行を一意に特定する鍵）
#                     name TEXT NOT NULL,                   # name列：文字列。必須（NULL禁止）
#                     email TEXT NOT NULL UNIQUE            # email列：文字列。必須かつ一意（重複禁止）
#                 )
#             """)
#             conn.commit()                                  # 変更を保存（with句でも基本は自動だが、明示しておくと分かりやすい）

# # ===== DB接続を毎回用意する小さな関数（ユーティリティ） =====
# def get_connection():
#     """毎回新しい接続を返す（with構文で自動クローズされる）"""
#     return sqlite3.connect(DB_FILE)  # 接続オブジェクトを返す。with get_connection() as conn: の形で使う

# # ===== 画面表示（トップ） =====
# @app.route("/")                       # デコレータ：この関数を "/" というURLに結びつける
# def index():
#     return render_template("index.html")  # templates/index.html を探して返す（HTMLを表示）

# # ===== 登録（Create）API：新規ユーザーを追加 =====
# @app.route("/api/register", methods=["POST"])  # この関数は POST で /api/register に来たときに動く
# def register():
#     data = request.get_json()                  # JS(fetch)が送ってきたJSONをPythonの辞書に変換
#     name = data.get("name")                    # 辞書から name を取り出す（無ければ None）
#     email = data.get("email")                  # 辞書から email を取り出す

#     if not name or not email:                  # どちらかが空（None/空文字）のときは
#         # jsonify: Pythonの辞書→JSON文字列に変換して返す
#         # 末尾の ,400 はHTTPのステータスコード（400 Bad Request：入力エラー）
#         return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

#     try:
#         with get_connection() as conn:                         # DBに接続（withで自動クローズ）
#             c = conn.cursor()                                  # カーソル取得
#             # プレースホルダ ? を使うことで、値を安全に渡せる（SQLインジェクション対策）
#             c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
#             conn.commit()                                      # 追加結果を保存
#         # 正常終了：成功メッセージをJSONで返す（200 OK）
#         return jsonify({"status": "success", "message": f"{name} さんを登録しました！"})
#     except sqlite3.IntegrityError:                              # UNIQUE制約（email重複）などで失敗した場合
#         # 409 Conflict：一意制約違反のような「競合」を表すのに適したコード
#         return jsonify({"status": "error", "message": "このアドレスはすでに登録済みです。"}), 409

# # ===== 一覧取得（Read）API：検索・並び替えにも対応 =====
# @app.route("/api/list", methods=["GET"])     # GETで /api/list に来たらこの関数
# def get_list():
#     # --- クエリ文字列からパラメータを受け取る（/api/list?q=xxx&sort=yyy） ---
#     q = request.args.get("q", "", type=str).strip()           # 検索語（無ければ空文字）。前後の空白を除去
#     sort = request.args.get("sort", "id_desc", type=str)      # 並び替え条件（無ければ id_desc）

#     # --- WHERE句を組み立て（部分一致検索） ---
#     where_sql = ""                                            # 条件なしが初期値
#     params = []                                               # プレースホルダに渡す値の配列
#     if q:                                                     # 検索語があるときだけ WHERE を付与
#         where_sql = "WHERE name LIKE ? OR email LIKE ?"       # 名前かメールに q を含む
#         like = f"%{q}%"                                       # 前後に % を付けて「部分一致」
#         params.extend([like, like])                           # 2つの ? に対して値を順にセット

#     # --- ORDER BY（並び替え）はホワイトリストで安全に選ぶ ---
#     sort_map = {                                              # 許可するキー → 実際のSQL断片
#         "id_asc": "id ASC",
#         "id_desc": "id DESC",
#         "name_asc": "name ASC",
#         "name_desc": "name DESC",
#         "email_asc": "email ASC",
#         "email_desc": "email DESC",
#     }
#     order_by = sort_map.get(sort, "id DESC")                  # 未知の値が来たら既定（id DESC）

#     # --- 最終的なSQLを組み立て ---
#     sql = f"SELECT id, name, email FROM users {where_sql} ORDER BY {order_by}"

#     # --- 実行して結果をJSONリストに整形 ---
#     with get_connection() as conn:                            # DB接続
#         c = conn.cursor()                                     # カーソル取得
#         c.execute(sql, params)                                # SQL実行（paramsは空でもOK）
#         users = [                                             # Pythonのリストに変換（JSに渡しやすくする）
#             {"id": row[0], "name": row[1], "email": row[2]}
#             for row in c.fetchall()
#         ]
#     return jsonify(users)                                     # そのままJSON配列で返す（200 OK）

# # ===== 編集（Update）API：指定IDの名前・メールを書き換え =====
# @app.route("/api/update/<int:user_id>", methods=["PUT"])      # /api/update/3 のように、URLの一部を引数にする
# def update_user(user_id):
#     data = request.get_json()                                 # JSから来たJSONを受け取る
#     name = data.get("name")                                   # 新しいname
#     email = data.get("email")                                 # 新しいemail

#     if not name or not email:                                 # どちらか空ならエラー
#         return jsonify({"status": "error", "message": "名前とメールは必須です。"}), 400

#     with get_connection() as conn:                            # DB接続
#         c = conn.cursor()                                     # カーソル
#         # id が一致する行を更新。該当が無ければ rowcount は 0 になる
#         c.execute("UPDATE users SET name=?, email=? WHERE id=?", (name, email, user_id))
#         conn.commit()                                         # 保存
#         if c.rowcount == 0:                                   # 1件も更新されなかった＝該当IDがない
#             return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404

#     return jsonify({"status": "success", "message": "更新しました。"})  # 成功

# # ===== 削除（Delete）API：指定IDの行を消す =====
# @app.route("/api/delete/<int:user_id>", methods=["DELETE"])   # /api/delete/3 のように呼ばれる
# def delete_user(user_id):
#     with get_connection() as conn:                            # DB接続
#         c = conn.cursor()                                     # カーソル
#         c.execute("DELETE FROM users WHERE id=?", (user_id,)) # タプルは (user_id,) のようにカンマが必要
#         conn.commit()                                         # 保存
#         if c.rowcount == 0:                                   # 消せた行が0＝IDが存在しない
#             return jsonify({"status": "error", "message": "該当ユーザーが見つかりません。"}), 404
#     return jsonify({"status": "success", "message": "削除しました。"})  # 成功

# # ===== アプリ起動：最初にDBを初期化してからサーバーを立ち上げる =====
# if __name__ == "__main__":                                    # このファイルを直接実行したときだけ動く“おまじない”
#     init_db()                                                 # DBファイルが無ければ作る（テーブルも用意）
#     app.run(debug=True, host="127.0.0.1", port=8000)          # ローカルでサーバー起動（http://127.0.0.1:8000）