print("🔷 try文のテストを始めます\n")

numbers = [10, 5, 0, 8, "a", 3, -3]

for n in numbers:
    try:
        print(f"10 ÷ {n} = {10 / n}")
    except ZeroDivisionError:
        print("⚠️ 0では割れません！スキップします。")
    except TypeError:
        print("⚠️ 数字じゃないものが入っています！スキップします。")

print("\n✅️ すべての処理が完了しました！")