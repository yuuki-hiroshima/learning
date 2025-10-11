# お題：3辺から三角形を判定するAPI（Flask↔️JS）

# 目的1：フロントから3つの値をサーバへ送る。
# 目的2：サーバ側のif文ロジックだけで判定し、結果をフロントへ返す。

# 条件1：三角形の和は180度、180度以外はFalse（180度以外はJSで返答処理）
# 条件2：空の値はJSで弾く

# 条件3：正三角形・二等辺三角形・不等辺三角形の3つ（Pythonで判定）

# if文の条件は 90 == 90 == 90か、 a != b != c != a

from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("test1.html")

@app.route("/api/triangle", methods=["POST"])
def triangle():
    data = request.get_json() or {}
    print("DEBUG request JSON:", data) # エラー解決に、めちゃくちゃヒントになった！！！
    side_a = (data.get("a_Side") or "")
    side_b = (data.get("b_Side") or "")
    side_c = (data.get("c_Side") or "")


    if side_a == side_b and side_b == side_c and side_a == side_c:
        msg = "正三角形です！"
    elif side_a == side_b or side_b == side_c or side_a == side_c:
        msg = "二等辺三角形です！"
    else:
        msg = "不等辺三角形です！"

    return jsonify({
        "ok": True,
        "echo": {"side_a": side_a, "side_b": side_b, "side_c": side_c},
        "message": msg
    })

if __name__ == "__main__":
    app.run(debug=True, port=8000)