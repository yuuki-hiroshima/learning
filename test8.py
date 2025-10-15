from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test8.html")

@app.route("/api/judge", methods=["POST"])
def judge_tickets():
    try:
        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({"ok": False, "error": "JSONの形があってないよ（オブジェクトにしてね）"}), 400
        
        tickets = data.get("tickets")
        if not isinstance(tickets, list):
            return jsonify({"ok": False, "error": "ticketsは配列にしてね"}), 400
        
        results = []
        summary = {"student": 0, "adult": 0, "unknown": 0, "error": 0}

        for i, ticket in enumerate(tickets):
            if not isinstance(ticket, dict):
                summary["error"] += 1
                results.append({
                    "index": i,
                    "ok": False,
                    "messagae": "チケットの形がおかしいよ（オブジェクトにしてね）"
                })
                continue

            name = str(ticket.get("name", "")).strip()
            t_type = str(ticket.get("type", "")).strip()

            if not name:
                summary["error"] += 1
                results.append({
                    "index": i,
                    "ok": False,
                    "message": "名前が空っぽです"
                })
                continue

            if t_type == "student":
                summary["student"] += 1
                results.append({
                    "index": i,
                    "ok": True,
                    "name": name,
                    "type": t_type,
                    "price": "student_discount",
                    "message": f"{name}さんは学生割引です"
                })
            elif t_type == "adult":
                summary["adult"] += 1
                results.append({
                    "index": i,
                    "ok": True,
                    "name": name,
                    "type": t_type,
                    "price": "regular",
                    "message": f"{name}さんは通常料金です"
                })
            else:
                if t_type == "unknown":
                    summary["unknown"] += 1
                    results.append({
                        "index": i,
                        "ok": True,
                        "name": name,
                        "type": t_type,
                        "price": "check_needed",
                        "message": f"{name}さんは種類が不明です（要確認）⚠️"
                    })
                else:
                    summary["error"] += 1
                    results.append({
                        "index": i,
                        "ok": False,
                        "name": name,
                        "type": t_type,
                        "message": f"{name}さんは type の値がおかしい。（student/adult/unknownにしてください）"
                    })

        return jsonify({
            "ok": True,
            "summary": summary,
            "results": results
        }), 200
    
    except Exception as e:
        return jsonify({
            "ok": False,
            "error": f"サーバー側でエラーが起きました。{e}"
            }), 500

if __name__ == "__main__":
    app.run(debug=True, port=8000)