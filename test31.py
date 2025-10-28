# 🔹 お題（要件のみ）
# 	1.	ユーザーに「カンマ区切りで商品名と価格」を入力してもらう。
# 　（例：りんご:100,バナナ:80,みかん:a,ぶどう:200）
# 	2.	入力を受け取り、各データを辞書（dict）に変換する。
# 　- キー：商品名
# 　- 値：価格（整数）
# 	3.	数字以外の価格が入力された場合はスキップして警告表示。
# 	4.	有効な商品の合計金額と件数を計算して表示する。

def input_items():
    product_price = input("カンマ区切りで商品名と価格を入力してください: ")
    product_price_list = {}

    for pair in product_price.split(","):
        pair = pair.strip()
        if pair == "":
            continue
        if ":" not in pair:
            print(f"形式が不正です({pair})。スキップします。")
            continue
        key, value = pair.split(":", 1)
        key = key.strip()
        value = value.strip()
        try:
            product_price_list[key] = int(value)
        except ValueError:
            print(f"{key}の価格が不正です({value})。スキップします。")
    return product_price_list

def calculate_total(product_price_list):
    total = sum(product_price_list.values())
    count = len(product_price_list)
    return total, count

def print_summary(total, count):
    print(f"有効な商品数は{count}件です。")
    print(f"合計金額は{total}円です。")

def main():
    try:
        product_price_list = input_items()
        total, count = calculate_total(product_price_list)
        print_summary(total, count)
    except Exception as e:
        print(f"予期せぬエラーが起きました: {e}")

if __name__ == "__main__":
    main()