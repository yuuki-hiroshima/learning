# test7.py　の処理チェック
age = 65
student = False
holiday = True
resident = "local"
member = "gold"
timeband = "night"
coupon = "FES2025"

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
    "student_holiday_discount": "祝日学生割引",
    "local_senior_discount": "地元シニア割引",
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
elif 0 <= age <= 12:
    category = "child"
elif 13 <= age <= 64:
    category= "adult"
else:
    category = "senior"

price = PRICE[category]
label = LABEL[category]

member = MEMBER.get(member)
timeband = TIMEBAND.get(timeband)

discount_price = price + member + timeband

if coupon == "FES2025":
    msg = "クーポンが適用され、料金は1000円です。"
else:
    msg = f"カテゴリ:{label} / 料金:{price}円 / 割引・加算{member + timeband}円 / 合計{discount_price}円" 

print(msg)