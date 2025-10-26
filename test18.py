#   1.	ユーザーに以下の2つを入力してもらう
# 　- 会員ランク（“none”・“silver”・“gold” のいずれか）
# 　- 購入金額（整数）
# 	2.	条件に応じて割引率を表示する
# 　- gold会員 かつ 5000円以上 → 「20%割引」
# 　- silver会員 かつ 3000円以上 → 「10%割引」
# 　- それ以外 → 「割引なし」
# 	3.	それぞれの条件を if / elif / else で分岐させる。

member_rank = input("会員ランクを入力してください(none/silver/gold): ") # 会員ランクを入力してもらい、変数member_rankに格納
price = int(input("購入金額を入力してください: "))  # 購入金額を入力してもらい、整数に変換してから変数priceに格納

if member_rank == "gold" and price >= 5000:     # gold会員かつ5000円以上なら
    print("20％割引")
elif member_rank == "silver" and price >= 3000: # silver会員かつ3000以上なら
    print("10％割引")
else:       # それ以外なら
    print("割引なし")