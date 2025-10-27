# 🔹 お題（要件のみ）
# 	1.	input_number() という関数を作成する。
# 	2.	関数内で以下を実装する：
# 　- 数字の入力を受け取る
# 　- 文字を int() に変換
# 　- ValueError の場合 → 「数字を入力してください」と再入力
# 　- 正常な数字が入力されたらその値を返す
# 	3.	関数を使って2つの数字を取得し、割り算を行う。
# 	4.	もし0割りが発生したらメッセージを表示し、再入力する。

def input_number(message): # 数字の入力を受けるための関数を作成
    while True: # 数字を入力してもらうためのループを開始
        try:
            number = int(input(message)) # 値を入力してもらい、数字なら整数に変換し変数に格納する
        except ValueError:  # 数字以外が入力された場合のエラーメッセージ
            print("数字を入力してください。")
            continue    # ループの最初へ戻る
        return number   # エラーが起きなければ、受け取った数字を返す

def main():   # 追加：本体も関数化してみた
    try:
        number_a = input_number("1つ目の数字を入力してください: ")   # 関数から受け取った数字を変数に格納する
        number_b = input_number("2つ目の数字を入力してください: ")   # 関数から受け取った数字を変数に格納する
        new_number = number_a / number_b    # 受け取った数字を使って割り算をおこない、答えを変数に格納する
    except ZeroDivisionError:   # 2つ目の数字が0だった場合のエラーメッセージ
        print("0で割ることはできません。")
    else:   # エラーがなければ答えを出力する
        print(f"答えは{new_number}です。")
    finally:    # エラーの有無に問わず、計算が終わることを伝える
        print("計算を終了します。")

if __name__ == "__main__": # 直接実行した場合にだけ動作させる。
    main()