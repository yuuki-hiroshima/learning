# 1️⃣ JSONの保存関数
# 	•	関数名：save_to_json(records, filepath)
# 	•	機能：
# 	•	指定されたファイルパスに JSON形式で records を保存する。
# 	•	フォルダが無ければ自動作成（os.makedirs(..., exist_ok=True)）
# 	•	保存形式：インデント2、ensure_ascii=False（日本語保持）
# 	•	保存完了後は "✅ JSONへ保存しました: ファイル名" と出力する。
# 	•	例外が起きたら "⚠️ JSONの書き込み中にエラーが発生しました: {e}"

# ⸻

# 2️⃣ JSONの読み込み関数
# 	•	関数名：load_from_json(filepath)
# 	•	機能：
# 	•	指定ファイルからデータを読み込む。
# 	•	存在しない場合 → "⚠️ ファイルが見つかりません: {filepath}"
# → "表示できるデータがありません" と出力し、空リスト [] を返す。
# 	•	壊れたJSON（構文エラー等）の場合 → "⚠️ 読み込み中にエラーが発生しました: {e}"
# → "表示できるデータがありません" と出力し、空リスト [] を返す。
# 	•	読み込み成功時は "✅ JSONから◯件のデータを読み込みました。"

# ⸻

# 3️⃣ 検証関数（validate_row）
# 	•	CSV版と同様に：
# 	•	名前が空ならスキップ
# 	•	score, attendance の存在と数値変換
# 	•	0〜100 の範囲チェック
# 	•	attendance < 50 で警告表示
# 	•	有効データのみを新リスト valid_records に格納し返す。

# ⸻

# 4️⃣ 集計関数（summarize）
# 	•	有効なデータの件数と平均点を表示。
# 	•	データが無ければ "有効な生徒はいません。" と表示。

# ⸻

# 5️⃣ main関数

# 実行順序：
# 	1.	サンプルデータ records を作成
# 	2.	save_to_json(records, "data/students.json")
# 	3.	load_from_json() で読み込む
# 	4.	validate_row() → summarize()
# 	5.	save_to_json(valid_records, "data/valid_students.json")

import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # 実ファイルの場所を起点にする
STUDENTS_PATH = os.path.join(BASE_DIR, "data", "students.json") # data/students.jsonへのルート
VALID_PATH = os.path.join(BASE_DIR, "data", "valid_students.json")  # data/valid_students.jsonへのルート

def save_to_json(records, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)

        print(f"✅️ JSONへ保存しました: {os.path.relpath(filepath, BASE_DIR)}") # 相対表示で場所を知らせる

    except Exception as e:
        print(f"⚠️ JSONの書き込み中にエラーが発生: {e}")

def load_from_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("⚠️ 想定外のデータ形式でした（配列ではありません）。表示できるデータがありません。")
            return []
        
        if len(data) == 0:
            print("表示できるデータがありません。")
            return []
        
        print(f"✅️ JSONから{len(data)}件のデータを読み込みました。")
        return data
    
    except FileNotFoundError:
        print(f"⚠️ ファイルが見つかりません: {os.path.relpath(filepath, BASE_DIR)}")
        print("表示できるデータがありません。")
        return []
    except json.JSONDecodeError as e:
        print(f"⚠️ 読み込み中にエラーが発生しました（JSONの形式が壊れています）: {e}")
        print("表示できるデータがありません。")
        return []
    except Exception as e:
        print(f"⚠️ 読み込み中にエラーが発生しました: {e}")
        print("表示できるデータがありません。")
        return []

def validate_row(records):
    valid_records = []

    for index, row in enumerate(records, start=2):
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

        if not (0 <= score <= 100):
            print(f"⚠️ 行{index}({name}): 点数が範囲外です({score})。スキップします。")
            continue
        if not (0 <= attendance <= 100):
            print(f"⚠️ 行{index}({name}): 出席率が範囲外です({attendance})。スキップします。")
            continue

        if attendance < 50:
            print(f"⚠️ 行{index}({name}): 出席率が低すぎます({attendance}%)。")

        valid_records.append({
            "name": name,
            "score": score,
            "attendance": attendance
        })

    return valid_records

def summarize(valid_records):
    scores = [row["score"] for row in valid_records]
    num_scores = len(scores)
    if num_scores > 0:
        average = sum(scores) / num_scores
        print(f"有効な生徒数：{num_scores}人")
        print(f"平均点数：{average:.1f}点")
    else:
        print("有効な生徒はいません。")

# 【追加】既存のJSONに1件追加して保存する
def update_json(filepath, new_record):
    data = load_from_json(filepath)
    if not data:
        data = []
    data.append(new_record)

    name = new_record.get("name", "(名前不明)")

    save_to_json(data, filepath)
    print(f"✅️ 新しいデータを追加しました: {name}")

# 【追加】指定した名前のデータを全部消す
def delete_record(filepath, target_name):
    data = load_from_json(filepath)
    before = len(data)

    new_list = [row for row in data if row.get("name") != target_name]

    delete_count = before - len(new_list) 
    save_to_json(new_list, filepath)

    if delete_count > 0:
        print(f"🗑️ {delete_count}件のデータを削除しました: ({target_name})")
    else:
        print(f"⚠️ 該当するデータが見つかりません: {target_name}")


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

    save_to_json(records, STUDENTS_PATH)
    loaded = load_from_json(STUDENTS_PATH)
    valid_records = validate_row(loaded)
    summarize(valid_records)
    save_to_json(valid_records, VALID_PATH)

    # 【追加】追加データと削除データ
    new_data = {"name": "新垣", "score": 77, "attendance": 90}
    update_json(STUDENTS_PATH, new_data)
    delete_record(STUDENTS_PATH, "鈴木")

if __name__ == "__main__":
    main()