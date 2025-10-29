# 🔹 お題（要件のみ）

# あなたが作るアプリは 「在庫一覧を分析する小アプリ」 です。
# 以下の要件に従って、自力でコードを組み立ててみましょう👇

# ⸻

# 🧾 要件
# 	1.	products という辞書を用意する。
# 　各キーは商品名（例： "りんご", "バナナ", "みかん"）
# 　各値は、以下のような辞書で構成する。
# 　python 　"りんご": {"price": 100, "stock": 10} 　
# 	2.	すべての商品を for文でループして、
# 　商品名・価格・在庫を整形して出力する。
# 　出力例👇
# 　 　りんご：価格100円（在庫10個） 　バナナ：価格80円（在庫0個） 　みかん：価格120円（在庫5個） 　
# 	3.	if文を使って、在庫が0のときだけ
# 　「⚠️ 在庫切れ」と表示する。
# 	4.	商品全体の合計金額（＝価格×在庫の総額）を最後に表示する。
# 　出力例👇
# 　 　全商品の在庫総額：1,700円 

products = {
    "りんご": {"price": 100, "stock": 10},
    "バナナ": {"price": 80, "stock": 0},
    "みかん": {"price": 120, "stock": 5},
    "スイカ": {"price": 200, "stock": 5}
    }
print(products)

total = 0

try:
    for name, info in products.items():
        if not name.strip():
            print("商品名が空白のためカウントできません。スキップします。")
            continue
        try:
            print(name, info)

            price = info["price"]
            stock = info["stock"]
            print(price, stock)

            price = int(price)
            stock = int(stock)

            if stock == 0:
                print(f"{name}の在庫はありません。")
                continue
            else:
                print(f"{name}：価格{price}円（在庫{stock}個）")
            
            total += price * stock

        except KeyError as e:
            print(f"{name}のデータに不足があります（{e}がありません）。スキップします。")
        except (TypeError, ValueError):
            print(f"{name}の金額データが不正です。スキップします。")

except Exception as e:
    print(f"想定外のエラーが発生しました: {e}")


print(f"全商品の在庫総額：{total}円")