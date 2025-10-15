from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test10.html")

@app.route("/api/group", methods=["POST"])
def group_tickets():
    try:
        data = request.get_json()
        tickets = data.get("tickets", [])

        summary = {"student": 0, "adult": 0, "unknown": 0, "error": 0}
        groups = {"student": [], "adult": [], "unknown": [], "error": []}

        for t in tickets:
            name = str(t.get("name", "")).strip()
            t_type = str(t.get("type", "")).strip()

            if not name:
                summary["error"] += 1
                groups["error"].append("(名前なし)")
                continue

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
        
        formatted = []
        for key, names in groups.items():
            if names:
                formatted.append(f"{key}: " + ", ".join(f"{key}:{n}" for n in names))

        return jsonify({
            "ok": True,
            "summary": summary,
            "groups": groups,
            "formatted": formatted
        }), 200
    
    except Exception as e:
        return jsonify({"ok": False, "error": f"サーバーでエラー: {e}"}), 500
    
if __name__ == "__main__":
    app.run(debug=True, port=8000)