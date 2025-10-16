from flask import Flask, request, jsonify, render_template  # Flaskの道具を呼び出して〜（サーバー/リクエスト/JSON返し/HTML表示）

app = Flask(__name__)  # アプリの本体を作って〜

@app.route("/")  # ここにアクセスされたら〜（トップページ）
def index():  # トップページの中身だよ〜
    return render_template("test10.html")  # templatesからtest10.htmlを表示して〜

@app.route("/api/group", methods=["POST"])  # フロントからPOSTで呼ばれる入り口だよ〜
def group_tickets():  # チケットを分類する処理の本体だよ〜
    try:  # 万が一こけても止まらないように、まずは安全ネットをはって〜
        data = request.get_json()  # ブラウザから来たJSONを受け取って〜
        tickets = data.get("tickets", [])  # "tickets"の配列を取り出して〜（なければ空の配列にしておこうね）

        summary = {"student": 0, "adult": 0, "unknown": 0, "error": 0}  # それぞれの数を数える箱を用意して〜
        groups = {"student": [], "adult": [], "unknown": [], "error": []}  # 名前をグループごとにしまっていく箱も用意して〜

        for t in tickets:  # チケットを1人ずつ順番に見ていこう〜（for文！）
            name = str(t.get("name", "")).strip()  # 名前を文字として取り出して、前後の空白を取ってきれいにして〜
            t_type = str(t.get("type", "")).strip()  # 種類も文字として取り出して、前後の空白を取って〜

            if not name:  # もし名前が空っぽなら〜
                summary["error"] += 1  # エラーの数を1足して〜
                groups["error"].append("(名前なし)")  # エラーの箱に「名前なし」を入れて〜
                continue  # この人はここで終わりにして、次の人に進もう〜

            if t_type == "student":  # 種類がstudentなら〜
                summary["student"] += 1  # 学生の数を1足して〜
                groups["student"].append(name)  # 学生グループに名前を入れて〜

            elif t_type == "adult":  # 種類がadultなら〜
                summary["adult"] += 1  # 社会人の数を1足して〜
                groups["adult"].append(name)  # 社会人グループに名前を入れて〜

            elif t_type == "unknown":  # 種類がunknownなら〜
                summary["unknown"] += 1  # 不明の数を1足して〜
                groups["unknown"].append(name)  # 不明グループに名前を入れて〜

            else:  # どれにも当てはまらないなら〜
                summary["error"] += 1  # エラーの数を1足して〜
                groups["error"].append(name)  # エラーグループに名前を入れて〜
        
        formatted = []  # 画面に出しやすい文字の形をためる箱を用意して〜
        for key, names in groups.items():  # グループごとに取り出して〜
            if names:  # 名前が1つでも入っていたら〜
                formatted.append(f"{key}: " + ", ".join(f"{key}:{n}" for n in names))  # 「key: key:名前, key:名前…」の形で並べて入れて〜

        return jsonify({  # できあがった結果をJSONにして返すよ〜
            "ok": True,  # 成功フラグだよ〜
            "summary": summary,  # 集計の数字だよ〜
            "groups": groups,  # 素のグループ分けだよ〜（配列入り）
            "formatted": formatted  # 表示用に整えた文字列の配列だよ〜
        }), 200  # ステータス200で「成功」を伝えて〜
    
    except Exception as e:  # 想定外のエラーが来たらここで受け止めて〜
        return jsonify({"ok": False, "error": f"サーバーでエラー: {e}"}), 500  # 失敗内容を知らせてステータス500で返すよ〜
    
if __name__ == "__main__":  # このファイルを直接実行したときだけ〜
    app.run(debug=True, port=8000)  # デバッグONでサーバーを起動して〜（ポート8000で開くよ）