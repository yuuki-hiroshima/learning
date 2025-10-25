print("🔷 不完全なデータを含む処理を始めます\n")

tickets = [
    {"name": "太郎", "type": "student"},
    {"name": "花子", "type": "adult"},
    {"name": "", "type": "student"},
    {"type": "student"},
    {"name": "不明さん", "type": None},
    "これは壊れたデータ",
]

summary = {"student": 0, "adult": 0, "error": 0}
groups = {"student": [], "adult": [], "error": []}

for i, t in enumerate(tickets):
    try:
        name = str(t.get("name", "")).strip()
        t_type = str(t.get("type", "")).strip()

        if not name:
            raise ValueError("名前が空です。") # raise は強制的にエラーにする
        
        if t_type == "student":
            summary["student"] += 1
            groups["student"].append(name)
        elif t_type == "adult":
            summary["adult"] += 1
            groups["adult"].append(name)
        else:
            raise ValueError("種類が不明です")
        
    except Exception as e:
        print(f"⚠️ {i+1}件目でエラー発生: {e}")
        summary["error"] += 1
        safe_name = str(t.get("name", "(データ不明)")) if isinstance(t, dict) else "(形式エラー)"
        groups["error"].append(safe_name)

print("\n✅️ 集計結果:")
print(summary)
print("\n✅️ グループ別:")
for key, names in groups.items():
    print(f"{key}: {', '.join(names)}")