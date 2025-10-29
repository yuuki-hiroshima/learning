# 🎯 ゴール
# 	•	辞書のリスト（生徒データ）を CSVに書き出す
# 	•	CSVから 読み込んで検証
# 	•	有効なレコードのみで「人数・平均点」を計算し表示
# 	•	途中の不正値や欠損は 止まらずスキップ（ログ表示）

import os
import csv

def save_to_csv(records, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True) # 【追加】フォルダがなければ自動作成
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["name", "score", "attendance"]
            writer = csv.DictWriter(f, fieldnames=fieldnames) 

            writer.writeheader()

            for row in records:
                writer.writerow(row)

        print(f"✅️ CSVへ保存しました: {filepath}")

    except Exception as e:
        print(f"⚠️ CSVの書き込み中にエラーが発生しました: {e}")


def load_from_csv(filepath):
    records = []
    try:
        with open(filepath, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                records.append(row)
        print(f"✅️ CSVから{len(records)}件のデータを読み込みました。")
    
    except FileNotFoundError:
        print(f"⚠️ ファイルが見つかりません: {filepath}")
        return []
    except Exception as e:
        print(f"⚠️ 読み込み中にエラーが発生しました: {e}")
        return []
    
    return records


def validate_row(records):
    valid_records = []

    for index, row in enumerate(records, start=2): # ヘッダが1行目のためデータは2行目スタート
        name = row.get("name", "")
        score = row.get("score", "")
        attendance = row.get("attendance", "")

        name = name.strip()

        if not name:
            print(f"⚠️ 行{index}: 名前がないためスキップします。")
            continue

        if score == "" or attendance == "":
            print(f"⚠️ 行{index}({name}): データが不足しています。")
            continue

        try:
            score = int(score)
            attendance = int(attendance)
        except (TypeError, ValueError):
            print(f"⚠️ 行{index}({name}): 数値に変換できません。スキップします。")
            continue

        # 【追加】範囲チェック
        if not (0 <= score <= 100):
            print(f"⚠️ 行{index}({name}): 点数が範囲外です({score})。スキップします。")
            continue
        if not (0 <= attendance <= 100):
            print(f"⚠️ 行{index}({name}): 出席率が範囲外です({attendance})。スキップします。")
            continue

        # 【追加】出席率警告（集計には含める）
        if attendance < 50:
            print(f"⚠️ 行{index}({name}): 出席率が低すぎます({attendance}%)。")

        valid_records.append({
            "name": name,
            "score": score,
            "attendance": attendance
        })
    
    return valid_records


def summarize(valid_records):
    total = 0
    scores = []

    for row in valid_records:
        score = row["score"]
        total += score
        scores.append(score)

    num_scores = len(scores)
    if num_scores > 0:
        average = total / num_scores
        print(f"有効な生徒数：{num_scores}人")
        print(f"平均点数：{average:.1f}点")
    else:
        print("有効な生徒はいません。")

    
def main():
    records = [
    {"name": "佐藤", "score": 85, "attendance": 90},
    {"name": "鈴木", "score": 58, "attendance": 95},
    {"name": "木本", "score": 88, "attendance": 80},
    {"name": "河本", "score": "a", "attendance": 50},
    {"name": "", "score": 70, "attendance": 30},
    {"name": "大和", "score": 66, "attendance": 100},
    {"name": "山田", "score": 101, "attendance": 30},
    {"name": "福田", "score": 70, "attendance": 130}
    ]

    filepath = "data/students.csv"
    save_to_csv(records, filepath)
    loaded = load_from_csv(filepath)
    valid_records = validate_row(loaded)
    summarize(valid_records)

    # 【追加】クリーンデータ保存
    save_to_csv(valid_records, "data/valid_students.csv")

if __name__ == "__main__":
    main()