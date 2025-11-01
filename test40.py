# Step 3️⃣：json.dump() と json.load() を体験

# Pythonのデータをファイルに保存／復元する流れを確認する。

# 目的：
# 「JSONはPythonのデータを“保存できる形”に変えてくれる」と理解する。

# お題（後で作るコードの指針）
# 	•	辞書（例：{"name": "田中", "score": 85}）を作る
# 	•	json.dump() で data_test/student.json に保存
# 	•	json.load() で読み込み、同じデータが戻ることを確認

# ⸻

import os
import json

# === フォルダとファイルの準備(STEP1️⃣の内容) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(BASE_DIR, "data_test")
os.makedirs(folder_path, exist_ok=True)
file_path = os.path.join(folder_path, "stundent.json")

# === Step1: 保存するデータを用意 ===
student = {
    "name": "田中太郎",
    "age": 17,
    "scores": {
        "math": 85,
        "english": 78,
        "science": 90
    }
}

print("1️⃣ 保存前のPythonデータ:")
print(student)

# === Step2: JSONファイルとして保存 ===
with open(file_path, "w", encoding="utf-8") as f:
    json.dump(student, f, ensure_ascii=False, indent=2)
print("2️⃣ JSONファイルにデータを書き込みました。")

# === Step3: JSONファイルから読み込み ===
with open(file_path, "r", encoding="utf-8") as f:
    loaded_data = json.load(f)

print("3️⃣ 読み込み後のPythonデータ:")
print(loaded_data)

# === Step4: 確認 ===
print("4️⃣ データは同じ？ →", student == loaded_data)


# (Step2)部分のコードを要約

# openを使い「file_path」のファイルを書き込みモードで開く。
# 文字化けを回避するため、文字コードはUTF-8を指定。
# json.dumpで対象の辞書データ（student）をJSONファイルとして保存。
# ensure_asciiをFalseにすることでユニコードで保存されることを回避。
# indentを使用してファイル内を見やすく整形。
# 保存が完了したら、withが安全にファイルを閉じる。