# 合格判定アプリ

# 入力：年齢・点数

# 判定条件1：18歳以上かつ80点以上 → 合格
# 判定条件2：18歳未満かつ点数80点以上 → 学生特待合格
# 判定条件3：それ以外 → 不合格

# JS：型変換と入力チェック
# Python：複合条件の判定

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test2.html")

@app.route("/api/judge_passed", methods=["POST"])
def passed():
    data = request.get_json() or {}
    print("DEBUG request JSON", data)
    age = data.get("age")
    point = data.get("point")

    try:
        age = int(age)
        point = int(point)
    except (TypeError,ValueError):
        return jsonify({"ok": False, "message": "数字を入力してください。"}), 400
    
    if age < 0 or point < 0 or point > 100:
        return jsonify({"ok": False, "message": "年齢は0以上、点数は0〜100で入力してください。"}), 400

    if age >= 18 and point >= 80:
        msg = "合格"
    elif age < 18 and point >= 80:
        msg = "学生特待合格"
    else:
        msg = "不合格"

    return jsonify({
        "ok": True,
        "echo": {"age": age, "point": point},
        "message": msg
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)