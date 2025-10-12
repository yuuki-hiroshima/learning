from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test4.html")

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
        return jsonify(ok=False, message="整数を入力してください。"), 400
    
    if age < 0:
        return jsonify(ok=False, message="0以上の整数を入力してください。"), 400
    
    if resident not in ("local", "other"):
        return jsonify(ok=False, message="地元です / 地元以外です のどちらか選択してください。"), 400
    
    # if student != bool or holiday != bool:
    if not isinstance(student, bool) or not isinstance(holiday, bool):
        return jsonify(ok=False, message="はい / いいえ をのどちらかを選択してください。"), 400
    
    PRICE = {
        "child": 800,
        "adult": 1500,
        "senior": 1000,
        "student_holiday_discount": 900,
        "local_senior_discount": 700,
    }

    LABEL = {
        "child": "子供",
        "adult": "大人",
        "senior": "シニア",
        "student_holiday_discount": "祝日の学生",
        "local_senior_discount": "地元の65歳以上",
    }

    if student and holiday:
        category = "student_holiday_discount"
    elif age >= 65 and resident == "local":
        category = "local_senior_discount"
    elif 0 <= age <= 17:
        category = "child"
    elif 18 <= age <= 64:
        category = "adult"
    else:
        category = "senior"

    price = PRICE[category]
    category_el = LABEL[category]

    msg = f"カテゴリ：{category_el} / 料金：{price}円"

    return jsonify(
        ok=True,
        category=category,
        category_el=category_el,
        price=price,
        message=msg,
        echo={"age": age, "student": student, "holiday": holiday, "resident": resident},
    )

if __name__ == "__main__":
    app.run(debug=True, port=8000)