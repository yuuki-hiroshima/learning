# お題：映画館チケットの特別割引（拡張版）

# 複合条件の条件一覧
# 基本料金：大人：1500円 ／ 子供（12歳以下）：800円 ／ シニア（65歳以上）：1000円
# 割引1　学生かつ祝日 → 900円（祝日学生割引）
# 割引2　地元の人かつ65歳以上 → 700円（地元シニア割引）
# 割引3　18歳未満かつ学生 → 1000円（学生ジュニア割）
# 割引4　18歳以上かつ25歳以下かつ学生 → 1200円（学生ユース割）

# 条件の優先順位
# 1️⃣ 祝日学生割
# 2️⃣ 地元シニア割
# 3️⃣ 学生ジュニア割
# 4️⃣ 学生ユース割
# 5️⃣ 通常料金（子供／大人／シニア）

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test6.html")

@app.route("/api/ticket", methods=["POST"])
def ticket():
    data = request.get_json() or {}
    age = data.get("age")
    student = data.get("student")
    holiday = data.get("holiday")
    resident = data.get("resident")

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify(ok=False, message="整数で入力してください。"), 400
    
    if age < 0:
        return jsonify(ok=False, message="0以上の整数を入力してください。"), 400
    
    if resident not in ("local", "other"):
        return jsonify(ok=False, message="居住地の選択をしてください。"), 400
    
    if not isinstance(student, bool) or not isinstance(holiday, bool):
        return jsonify(ok=True, message="学生と祝日の質問にチェックを入れてください。"), 400

    PRICE = {
        "child": 800,
        "adult": 1500,
        "senior": 1000,
        "student_holiday_discount": 900,
        "local_senior_discount": 700,
        "student_junior_discount": 1000,
        "student_youth_discount": 1200,
    }

    LABEL = {
        "child": "子供",
        "adult": "大人",
        "senior": "シニア",
        "student_holiday_discount": "祝日学生割引",
        "local_senior_discount": "地元シニア割引",
        "student_junior_discount": "学生ジュニア割引",
        "student_youth_discount": "学生ユース割引",
    }

    if student and holiday:
        category = "student_holiday_discount"
    elif age >= 65 and resident == "local":
        category = "local_senior_discount"
    elif age < 18 and student:
        category = "student_junior_discount"
    elif 18 <= age <= 25 and student:
        category = "student_youth_discount"
    elif 0 <= age <= 12:
        category = "child"
    elif 13 <= age <= 64:
        category = "adult"
    else:
        category = "senior"

    price = PRICE[category]
    label = LABEL[category]

    msg = f"カテゴリ:{label}, 料金:{price}円"

    return jsonify(
        ok=True,
        category=category,
        price=price,
        label=label,
        messaga=msg,
        echo={"age": age, "student": student, "holiday": holiday, "resident": resident},
    )

if __name__ == "__main__":
    app.run(debug=True, port=8000)
