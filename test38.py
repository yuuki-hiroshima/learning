# Step 1️⃣：os と path の動きを見る

# フォルダを作ったり、ファイルの住所を取得したりする。

# 目的：
# 「os はパソコンに命令を出すもの」と実感する。

# お題（次に書いてもらうコードの指針）
# 	•	現在のファイルがどこにあるかを表示
# 	•	data_test というフォルダを自動で作る
# 	•	その中に sample.txt というファイルを置くための“住所”を作って表示
# ⸻

import os

# === 現在のファイルの場所（絶対パス）を取得 ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # __file__で現在のファイルパスを取得し、abspathで相対パスを絶対パスへ変換。dirnameでファイル名を除いたフォルダ部分までを取り出す。
print("現在のフォルダがある場所:", BASE_DIR)                # ↑の要約、「このプログラムが存在するフォルダ」を変数に保存

# === 新しいフォルダを作成する（data_test） ===
folder_path = os.path.join(BASE_DIR, "data_test")   # "data_etst"を、BASE_DIR（絶対パス）とjoinで結合しパスを作成
os.makedirs(folder_path, exist_ok=True)             # makedirsでフォルダをチェック・作成。すでに同一フォルダがあっても、exist_ok=Trueでエラーにならない
print("作成または確認したフォルダ:", folder_path)

# === ファイルのパスを作る（住所のようなもの） ===
file_path = os.path.join(folder_path, "sample.txt") # foleder_pathで作成したパスに、"sample.txt"をjoinで結合しフルパスを作成
print("これから作るファイルの場所:", file_path)

# === ファイルを作って書き込んでみる ===
with open(file_path, "w", encoding="utf-8") as f:   # ファイルを作成し、書き込みモードで開く。処理が終わるとwithで閉じる
    f.write("これはサンプルファイルです。")              # ファイルに文字を書き込む
print("ファイルを作成しました。")





# Step 4️⃣：各処理の“意味を言葉で説明する”

# ここが一番大事です。

# ファイルを操作する1行1行を見ながら、

# 「この1行は何をしているのか？」
# を自分の言葉で説明できる状態にします。