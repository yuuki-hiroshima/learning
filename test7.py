# 通常料金（ベース）
# 	•	child（0〜12）: 800円
# 	•	adult（13〜64）: 1500円
# 	•	senior（65〜）: 1000円

# ⸻

# 割引・特典（v2で追加）

# 時間帯割（timeband）
# 	•	morning（朝）: -200円
# 	•	afternoon（昼）: ±0円
# 	•	night（夜）: +100円

# ベース料金に対して 加減 する（割引が先に確定した後でも「最終調整」できるように）。

# 会員割（member）
# 	•	silver: -100円
# 	•	gold: -200円
# 	•	none: ±0円

# クーポン（coupon）
# 	•	"FES2025" が入力された場合、最終価格を 1000円に固定（上限下限ではなく“固定”）
# 	•	不正なコードは 無視（エラーではない）

# ⸻

# 既存の特別割（v1から継続）

# 上から優先して適用（マッチした時点で“カテゴリ”は確定）
# 	1.	祝日 かつ 学生 → student_holiday_discount 900円
# 	2.	65歳以上 かつ 地元 → local_senior_discount 700円
# 	3.	18歳未満 かつ 学生 → student_junior_discount 1000円
# 	4.	18〜25歳 かつ 学生 → student_youth_discount 1200円
# 	5.	上記どれでもなければ 通常料金（child/adult/senior）

# v2では、「カテゴリの決定（上の1〜5）」と「価格の最終調整（時間帯・会員・クーポン）」を分けるのがポイント。

# ⸻

# 価格決定の流れ（重要）
# 	1.	バリデーション（年齢・resident・boolean群・member/timeband値）
# 	2.	カテゴリ確定（↑の1〜5。ここで category_key と 一旦の price を取る）
# 	3.	時間帯調整（morning/afternoon/night の加減を price に反映）
# 	4.	会員調整（silver/goldを加減）
# 	5.	クーポン最終上書き（coupon==="FES2025" なら price=1000 に固定）
# 	6.	下限0円の保証（万一マイナスになり得る割引が増えた場合の保険として price = max(price, 0)）
# 	7.	日本語ラベル生成＋メッセージ作成 → 返却

# 優先順位：カテゴリ決定 ＞（時間帯→会員）調整 ＞ クーポン固定。
# クーポンは最後に“ドン”と上書き、と覚える。

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test7.html")

@app.route("/api/ticket", methods=["POST"])
def ticket():
    data = request.get_json() or {}
    age = data.get("age")
    student = data.get("student")
    holiday = data.get("holiday")
    resident = data.get("resident")
    member = data.get("member")
    timeband = data.get("timeband")
    coupon = data.get("coupon")

    try:
        age = int(age)
    except (TypeError, ValueError):
        return jsonify(ok=False, message="整数を入力してください。"), 400
    
    if age < 0:
        return jsonify(ok=False, message="0以上の整数を入力してください。"), 400
    
    if resident not in ("local", "other"):
        return jsonify(ok=False, message="地元 / 地元以外 を選択してください。"), 400
    
    if not isinstance(student, bool) or not isinstance(holiday, bool):
        return jsonify(ok=False, message="学生・祝日の質問に解答してください。"), 400
    
    if member not in ("none", "silver", "gold"):
        return jsonify(ok=False, message="メンバー会員の項目を選択してください。"), 400
    
    if timeband not in ("morning", "afternoon", "night"):
        return jsonify(ok=False, message="時間帯を選択してください。"), 400

    if coupon is None:
        coupon = ""
    
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

    MEMBER = {
        "none": 0,
        "silver": -100,
        "gold": -200,
    }

    TIMEBAND = {
        "morning": -200,
        "afternoon": 0,
        "night": 100,
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
        category= "adult"
    else:
        category = "senior"

    price = PRICE[category]
    label = LABEL[category]

    member_adj = MEMBER.get(member)
    timeband_adj = TIMEBAND.get(timeband)

    final_price = price + member_adj + timeband_adj

    if coupon == "FES2025":
        final_price = 1000
    
    final_price = max(final_price, 0) # 0円未満なら0円になるよう切り上げ
    
    if coupon == "FES2025":
        msg = "クーポンを適用しました。料金は 1000円 です。"
    else:
        delta = timeband_adj + member_adj
        sign = "+" if delta > 0 else ""
        msg = f"カテゴリ;{label} / 基本:{price}円 / 調整:{sign}{delta}円 / 合計:{final_price}円"

    return jsonify(
        ok=True,
        category=category,
        label=label,
        base_price=price,
        member_adj=member_adj,
        timeband_adj=timeband_adj,
        price=final_price,          # 最終価格を price に
        message=msg,
        echo={"age": age, "student": student, "holiday": holiday, "resident": resident, "member": member, "timeband": timeband, "coupon": coupon}
    )

if __name__ == "__main__":
    app.run(debug=True, port=8000)