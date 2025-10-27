# 🔹 お題（要件のみ）
# 	1.	ユーザーに「カンマ区切りで数値」を入力してもらう（例：90,40,75,a,100）
# 	2.	入力された値を1つずつ処理して、以下の3つに分類する：
# 	•	80点以上 → 「優秀」リストに追加
# 	•	60点以上80点未満 → 「合格」リストに追加
# 	•	60点未満 → 「不合格」リストに追加
# 	3.	数字以外が入力されてもプログラムが止まらないようにする。
# 	4.	最後に、各カテゴリのリストと人数を出力する。

number = input("カンマ区切りで点数を入力してください: ")    # ユーザーに点数を入力してもらう
number_list = number.split(",")                       # 入力された点数をカンマで区切ってリスト化する

excellent = []  # 優秀に分類するためのリスト
passed = []     # 合格に分類するためのリスト
failed = []       # 不合格に分類するためのリスト

for num in number_list:     # 点数のリストから値を1つずつ取り出す
    try:
        new_num = int(num.strip())  # 空白を除去してから、値を整数に変換し新しい変数に格納
        if new_num >= 80:   # 点数が80点以上か判定
            excellent.append(num)   # 80点以上なら優秀のリストに追加
        elif 60 <= new_num < 80:    # テンスが60点以上80点未満か判定
            passed.append(num)      # 60点以上80点未満なら合格のリストに追加
        else:   # それ以外の場合
            failed.append(num)  # 不合格のリストに追加
    except ValueError:          # int()に数字以外が入った場合のエラーメッセージ（エラーでの中断を回避）
        print(f"{num}は数字ではないためスキップします。")
    except Exception:           # 想定外のエラーが起きた場合のエラーメッセージ（エラーでの中断を回避）
        print("想定外のエラーが発生しました。")

excellent_list = len(excellent) # 優秀に該当した件数をカウント
passed_list = len(passed) # 合格に該当した件数をカウント
failed_list = len(failed) # 不合格に該当した件数をカウント

# 以下、各カテゴリの人数とリストを出力
print(f"「優秀」は{excellent_list}人でした。")
print(f"「優秀」の点数は{excellent}です。")
print(f"「合格」は{passed_list}人でした。")
print(f"「合格」の点数は{passed}です。")
print(f"「不合格」は{failed_list}人でした。")
print(f"「不合格」の点数は{failed}です。")