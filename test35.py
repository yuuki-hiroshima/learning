# テスト

records = [
    {"name": "佐藤", "score": 85, "attendance": 90},
    {"name": "鈴木", "score": 58, "attendance": 95},
    {"name": "木本", "score": 88, "attendance": 80},
    {"name": "河本", "score": "a", "attendance": 50},
    {"name": "", "score": 70, "attendance": 30}
]

try: 
    for name, info in records:
        print(name, info)
        if not name:
            print("名前がないためスキップします。")
            continue

        score = info["score"]
        attendance = info["attendance"]

        score = int(score)
        attendance = int(attendance)

        if score == "" or attendance == "":
            print(f"{name}は、データが不足しています。")
            continue

except (TypeError, ValueError):
    print(f"{name}のデータには不備があります。")