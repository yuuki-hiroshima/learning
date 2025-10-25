from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test14.html")

@app.route("/api/group", methods=["POST"])
def group_tickets():
    try:
        data = request.get_json()
        tickets = data.get("tickets", [])

        summary = {"student": 0, "adult": 0, "unknown": 0, "error": 0}
        groups = {"student": [], "adult": [], "unknown": [], "error": []}

        error_details = [] # 追加：エラーの内訳をここに蓄積

        for i, t in enumerate(tickets):
            try:
                name = str(t.get("name", "")).strip()
                t_type = str(t.get("type", "")).strip()

                if not name:
                    raise ValueError("名前が空です。")
                
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
                    raise ValueError(f"不明なtypeです: {t_type}")
                
            except Exception as e:
                print(f"⚠️ {i+1}件目でエラー発生: {e}")
                summary["error"] += 1
                safe_name = str(t.get("name", "(データ不明)")) if isinstance(t, dict) else "(形式エラー)"
                groups["error"].append(safe_name)
                error_details.append({      # 追加：どの件で何が起きたかをメモ
                    "index": i + 1,         # 追加：どこでエラーが起きたか見やすくするため1始まり
                    "name": safe_name,
                    "message": str(e)
                })

        formatted = []
        for key, names in groups.items():
            if names:
                formatted.append(f"{key}: " + ", ".join(map(str, names)))

        return jsonify({
            "ok": True,
            "summary": summary,
            "groups": groups,
            "formatted": formatted,
            "errors": error_details     # 追加：フロントで可視化する用
        }), 200
    
    except Exception as e:
        return jsonify({"ok": False, "error": f"サーバーでエラーが発生: {e}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=8000)