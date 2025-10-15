# チケットのリスト
tickets = [
    {"name": "太郎", "type": "student"},
    {"name": "花子", "type": "adult"},
    {"name": "健", "type": "student"},
    {"name": "陽菜", "type": "student"},
    {"name": "不明さん", "type": "unknown"},
    {"name": "VIPさん", "type": "vip"}
]

# 集計用の箱
summary = {
    "student": 0,
    "adult": 0,
    "unknown": 0,
    "error": 0
}

# 分類ごとの名前リストを入れる箱
groups = {
    "student": [],
    "adult": [],
    "unknown": [],
    "error": []
}

# for文で1件ずつチェックしていく
for ticket in tickets:
    name = ticket["name"]
    t_type = ticket["type"]

    if t_type == "student":
        summary["student"] += 1
        groups["student"].append(name)
    elif t_type == "adult":
        summary["adult"] += 1
        groups["adult"].append(name)
    elif t_type == "unknown":
        summary["unknown"] += 1
        groups["unknown"].append(name)
    else:
        summary["error"] += 1
        groups["error"].append(name)

print("【チケット集計】")
print(summary)

print("\n【グループごとの名前】")
for key, names in groups.items():
    print(f"{key}:", ", ".join(names))

