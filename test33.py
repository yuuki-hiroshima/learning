# 📋 お題の要件

# 以下のような辞書 students を用意する。

# students = {
#     "佐藤": {"score": 85, "attendance": 90},
#     "鈴木": {"score": 58, "attendance": 95},
#     "高橋": {"score": 72, "attendance": 40},
#     "田中": {"score": "a", "attendance": 80},
#     "": {"score": 90, "attendance": 100}
# }


# 各キーは生徒の名前

# 値は2つの情報を持つ辞書：
# "score"（点数）と "attendance"（出席率）

# for文でループし、各生徒の成績を出力する。
# 例：

# 佐藤：点数85点（出席率90％）
# 鈴木：点数58点（出席率95％）


# 以下の条件を満たすように if文と例外処理を組み合わせる。

# 条件	表示内容
# 名前が空白	「⚠️ 名前が空白のためスキップします。」
# "score" または "attendance" が欠けている	「⚠️ データ不足のためスキップします。」
# "score" が数値でない	「⚠️ 点数が不正です。」
# "attendance" が50未満	「⚠️ 出席率が低すぎます。」
# "score" が60未満	「❌ 不合格」
# 上記以外	「✅ 合格」

# 最後に、有効な生徒のみを対象にした平均点を計算して出力する。

# 有効な生徒数：3人
# 平均点：79.0点

students = {
    "佐藤": {"score": 85, "attendance": 90},
    "鈴木": {"score": 58, "attendance": 95},
    "高橋": {"score": 72, "attendance": 40},
    "田中": {"score": "a", "attendance": 80},
    "": {"score": 90, "attendance": 100},
    "伊藤": {"score": "", "attendance": 10}
}

total = 0
scores = []

try:
    for name, status in students.items():
        if not name.strip():
            print("⚠️ 名前が空白のためスキップします。")
            continue
        
        try:
            score = status["score"]
            attendance = status["attendance"]

            if score == "" or attendance == "":
                print(f"{name}さんは、データ不足のためスキップします。")
                continue

            score = int(score)
            attendance = int(attendance)

            if attendance < 50:
                print(f"⚠️ {name}さんの出席率は低すぎます。")
            elif score < 60:
                print(f"⚠️ 60点未満のため、{name}さんは不合格です。")
            else:
                print(f"✅️ {name}さんは合格です。")

            total += score
            scores.append(score)

        except KeyError as e:
            print(f"{name}さんの値に問題があります: {e}")
        except (TypeError, ValueError):
            print(f"{name}さんのデータに問題があります。")

    num_scores = len(scores)
    if num_scores > 0:
        average = total / num_scores
        print(f"有効な生徒数：{num_scores}人")
        print(f"平均点：{average:.1f}点")
    else:
        print("有効な生徒がいません。")

except Exception as e:
    print(f"想定外のエラーが発生しました: {e}")