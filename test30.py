# 🔹 お題（要件のみ）
# 	1.	ユーザーに「カンマ区切りで点数」を入力してもらう。
# 	2.	入力文字列を安全にリストへ変換する（関数①）。
# 	3.	有効な数値だけを抽出して、平均点と合計点を計算する（関数②）。
# 	4.	結果を整形して出力する（関数③）。
# 	5.	数字以外が混ざっても止まらないようにする。

def input_scores(): # 入力を受け取り、リスト化する関数
    number = input("カンマ区切りで点数を入力してください: ").strip()    # 入力を受け取り空白を除去する
    if number == "":    # 空文字を判定する
        print("空白はカウントしません。")
    # ↓「カンマで区切った文字列を1つずつ取り出して、前後の空白を除去し、空っぽじゃなければ新しいリストに入れる。空白だけならスキップ」
    number_list = [t.strip() for t in number.split(",") if t.strip() != ""] # 入力された値をカンマで区切ってリスト化する
    return number_list  # リスト化した変数を返す

def calculate_scores(number_list): # 合計点と平均点を計算する関数
    total = 0   # 合計点の初期値
    valid_number = []   # 件数をカウントするためのリスト

    for num in number_list: # 引数のリストから1件ずつ値を取り出す
        try:
            new_num = int(num)  # 取り出した値を整数に変換する
            total += new_num    # 整数を加算する
            valid_number.append(new_num)    # 整数をリストに追加する
        except ValueError:  # テキストが含まれる場合のエラーメッセージ
            print(f"{num}は数字ではないため、スキップします。")
    effective_number = len(valid_number)    # 件数をカウントする
    if effective_number == 0:   # 件数が0だった場合
        raise ZeroDivisionError("有効な点数がありません")
    average = total / effective_number  # 合計点を件数で割り、平均点数を計算する
    return total, average   # 合計点と平均点を返す

def print_result(total, average):   # 結果を整理して表示する関数
    print(f"合計は{total}点です。")
    print(f"平均は{average:.1f}点です。")

def main(): # 処理全体の関数
    try:
        number_list = input_scores()    # 入力を受ける関数からリストを取り出す
        total, average = calculate_scores(number_list) # リストを受け取り、計算する関数から合計と平均を取り出す
        print_result(total, average)    # 合計と平均を受け取り結果として出力する
    except ZeroDivisionError:   # 件数が0だった場合のエラーメッセージ
        print("点数が0件では合計点・平均点が算出できません。")
    except Exception as e:  # 想定しないエラーが発生した場合のエラーメッセージ
        print(f"予期せぬエラーが発生しました: {e}")

if __name__ == "__main__":  # メインの関数を実行するためのコード
    main()