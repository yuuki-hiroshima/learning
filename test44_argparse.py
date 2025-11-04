# 🎯 ミニ課題テーマ

# 「argparseを使って電卓アプリをCLI化する」

# 目的は、既に習得した構文（--add, --list, --update, --deleteなど）を
# 別の文脈で再利用し、argparseの設計パターンを体で覚えることです。

import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="電卓アプリ(CLI版)")
    group = parser.add_mutually_exclusive_group()

    group.add_argument("--add", nargs=2, type=float, help="足したい数を2つ入力")
    group.add_argument("--sub", nargs=2, type=float, help="引きたい数を2つ入力")
    group.add_argument("--mul", nargs=2, type=float, help="掛けたい数を2つ入力")
    group.add_argument("--div", nargs=2, type=float, help="割りたい数を2つ入力")

    return parser.parse_args()

def main():
    args = parse_args()

    if not any([args.add, args.sub, args.mul, args.div]):
        print("使い方: --add/--sub/--mul/--div のどれか1つを指定してね。例: python3 test44.py --add 5 7")
        return

    # 【変更】args は辞書風の入れ物（Namespace/クラス）。各オプションに値が入っており、以下のような値の取り出し方はできない。
    # num_1 = args[0]
    # num_2 = args[1]

    # args の中身はNamespace。こんな感じ → (add=[5.0, 7.0], sub=None, mul=None, div=None)
    # 引数名をキーとして値を保持する小さいオブジェクトなので、厳密にはリストでも辞書でもない

    # 上記のようにCLIを実行した時に、指定された引数とそうでない引数の結果を
    # 1つの箱（Namespace）にまとめてくれるのが「argparse」の仕組み


    if args.add:
        num_1, num_2 = args.add
        print(f"{num_1} + {num_2} = {num_1 + num_2}")
        return
    
    if args.sub:
        num_1, num_2 = args.sub
        print(f"{num_1} - {num_2} = {num_1 - num_2}")
        return
    
    if args.mul:
        num_1, num_2 = args.mul
        print(f"{num_1} ✕ {num_2} = {num_1 * num_2}")
        return
    
    if args.div:
        num_1, num_2 = args.div
        if num_2 == 0:
            print("0では割れません。1以上を入力してください。")
            return
        print(f"{num_1} ÷ {num_2} = {num_1 / num_2}")
        return
    
if __name__ == "__main__":
    main()