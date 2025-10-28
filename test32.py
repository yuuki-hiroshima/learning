product_price = "りんご:100, バナナ:80, みかん:a, ぶどう:200"

for pair in product_price.split(","):
    print("▶ 分解対象:", pair)
    pair = pair.strip()
    if pair == "":
        continue
    if ":" not in pair:
        print("❌ コロンが無いのでスキップ:", pair)
        continue

    key, value = pair.split(":", 1)
    print("→ key:", key)
    print("→ value:", value)