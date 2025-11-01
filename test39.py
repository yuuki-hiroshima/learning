# Step 2️⃣：open() を使ってファイルを書いてみる

# ファイルに文字を書き込んで、実際に中身を見てみる。

# 目的：
# 「open() でファイルを開く＝中身にアクセスすること」と理解する。

# お題（後で作るコードの指針）
# 	•	"w"（書き込み）モードで開く
# 	•	"Hello, Python!" という文字列を書き込む
# 	•	"a"（追記）モードで別の文章を追加する
# 	•	"r"（読み込み）モードで中身を確認する

# ⸻

import os

# === フォルダとファイルの設定(Step1️⃣の内容) ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
folder_path = os.path.join(BASE_DIR, "data_test")
os.makedirs(folder_path, exist_ok=True)
file_path = os.path.join(folder_path, "note.txt")

# === Step1: 書き込み（"w"モード） ===
print("1️⃣ 新しい内容を書き込みます。")
with open(file_path, "w", encoding="utf-8") as f:   # 書き込み専用で開く。ファイルがあれば中身を消して上書き、新規なら作成。
    f.write("これは最初の文章です。\n")
    f.write("これは2番目の文章です。\n")

# === Step2: 追記（"a"モード） ===
print("2️⃣ 内容を追記します。")
with open(file_path, "a", encoding="utf-8") as f:   # ファイルがなければ新規作成。ファイルがあれば末尾に追記。
    f.write("これは追記された文章です。\n")

# === Step3: 読み込み（"r"モード） ===
print("3️⃣ ファイルの中身を読み込みます。")
with open(file_path, "r", encoding="utf-8") as f:   # 読み込み専用で開く。（ファイルがなければエラー: FileNotFoundError）
    content = f.read()                              # ファイル全体を1つの"文字列"として読み込む
    print("--- ファイル内容 ---")
    print(content)
    print("--------------------")