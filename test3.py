# 映画館のチケット販売API

# システム要件
# # 基本料金（通常時）
# 	•	child（0〜12歳）: 800円
# 	•	adult（13〜64歳）: 1500円
# 	•	senior（65歳以上）: 1000円

# 料金の上書き条件（割引）※通常より優先

# **優先順位は上から順に評価し、最初にマッチしたものを適用して終了。
# 	1.	祝日 かつ 学生 → student_holiday_discount: 900円
# 	2.	65歳以上 かつ 地元住民（resident="local"） → local_senior_discount: 700円

# 例）65歳の学生で祝日→ 1) が先に適用され、900円（2)は見ない）

# 販売条件（カテゴリ決定のロジック）
	# 1.	（先に割引を判定）
	# •	祝日かつ学生 → category="student_holiday_discount"、price=900
	# •	65歳以上かつresident="local" → category="local_senior_discount"、price=700
	# 2.	（割引に当てはまらなければ基本料金へ）
	# •	0〜12 → child（800円）
	# •	13〜64 → adult（1500円）
	# •	65〜 → senior（1000円）

# 入力内容
    # 年齢（age）
    # 学生かどうか（student）
    # 休日かどうか（holiday） 
    # 地元かどうか（resident）

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test3.html")

@app.route("/api/ticket", methods=["POST"])
def ticket():
    data = request.get_json() or {}
    age = data.get("age")
    student = data.get("student")
    holiday = data.get("holiday")
    resident = data.get("resident")

    # 【追加】型チェック・範囲チェック（AIによる修正）
    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify(ok=False, message="年齢は整数で入力してください。"), 400
    
    if age < 0:
        return jsonify(ok=False, message="年齢は0以上で入力してください。"), 400
    
    if resident not in ("local", "other"):
        return jsonify(ok=False, message="居住地は 地元のかた / 地元以外のかた を選択してください。"), 400
    
    if not isinstance(student, bool) or not isinstance(holiday, bool):
        return jsonify(ok=False, message="学生/祝日は はい / いいえ で送ってください。"), 400
    
    # 【追加】料金テーブル（見通し良く）
    PRICE = {
        "child": 800,
        "adult": 1500,
        "senior": 1000,
        "student_holiday_discount": 900,
        "local_senior_discount": 700,
    }

    # 【追加】表示用ラベル（キー→日本語）
    LABEL = {
        "child": "子供",
        "adult": "大人",
        "senior": "シニア",
        "student_holiday_discount": "祝日の学生割引",
        "local_senior_discount": "地元シニア割引",
    }

    if student and holiday:
        category = "student_holiday_discount"
    elif age >= 65 and resident == "local":
        category = "local_senior_discount"
    elif 0 <= age <=12:
        category = "child"
    elif 13 <= age <= 64:
        category = "adult"
    else:
        category = "senior"

    # 【変更】日本語ラベルと料金を取り出す
    price = PRICE[category]             # 既存のPRICE辞書を使用
    category_local = LABEL[category]    # 日本語ラベルに変換

    msg = f"カテゴリ:{category_local} / 料金:{price}円"

    # 【変更】レスポンスに日本語とキーの両方を入れておくと後々便利
    return jsonify(
        ok=True,
        category=category,
        category_local=category_local,
        price=price,
        message=msg,
        echo={"age": age, "student": student, "holiday": holiday, "resident": resident},
    )

if __name__ == "__main__":
    app.run(debug=True, port=8000)