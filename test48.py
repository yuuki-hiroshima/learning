from flask import Flask, render_template, request, redirect, url_for
import json
import os
import datetime

app = Flask(__name__)   # Webサーバー本体

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_PATH = os.path.join(BASE_DIR, "data", "notes.json")

def load_notes(filepath):
    """JSONファイルからメモ一覧を読み込む"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data or []
    except FileNotFoundError:
        return []
    except Exception as e:
        print("読み込みエラー", e)
        return []
    
def save_notes(data, filepath):
    """一時ファイル→置き換えで、途中失敗でも壊れにくく保存する"""
    dirpath = os.path.dirname(filepath)
    os.makedirs(dirpath, exist_ok=True)
    tmp_path = os.path.join(dirpath, ".notes.tmp")

    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    os.replace(tmp_path, filepath)

def next_id(data):              # 登録する際のIDとして、IDの最大値に＋1した値を返す関数
    """既存の最大ID+1 を返す（空なら 1）"""
    return (max((row.get("id", 0) for row in data), default=0) + 1)

def validate_title(raw):        # タイトルの空白や改行を除去する関数
    title = (raw or "").strip()
    if not title:
        return None
    return title.replace("\n", " ")

def validate_body(raw):         # 本文が空なら既定文を入れる関数
    body = (raw or "").strip()
    return body if body else "(本文なし)"

@app.route("/add", methods=["GET", "POST"])
def add():
    """
    データの流れ：
      GET  → ブラウザにフォームHTMLを返す（入力待ち）
      POST → フォーム値を受け取る → 検証 → notes.json を読み込み
            → 末尾に1件追加 → JSONに保存 → 一覧ページへリダイレクト
    """

    # ① ブラウザがフォームを要求
    if request.method == "GET":
        return render_template("test48add.html")
        
    # ② POST：フォーム送信を受け取る（データの"入口"）
    title = validate_title(request.form.get("title"))
    body = validate_body(request.form.get("body"))

    if title is None:
        return render_template("test48add.html", error="タイトルは必須です。",
                               last_title="", last_body=request.form.get("body", ""))

    # ③ 既存データを読み込み、Pythonのリストに変換（メモの集まり）
    notes = load_notes(NOTES_PATH)

    # ④ 1件の辞書を組み立てる
    now = __import__("datetime").datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    new_note = {"id": next_id(notes), "title": title, "body": body, "created_at": now}

    # ⑤ リスト末尾に追加（メモ件数が＋1になる＝状態変化）
    notes.append(new_note)

    # ⑥ JSONへ保存（Pythonのリスト → 文字列に直してファイルへ）
    save_notes(notes, NOTES_PATH)

    # ⑦ 一覧へ戻す（?added=1 で追加完了を伝える小さなフラグ）
    return redirect(url_for("index", added=1))

@app.route("/")
def index():
    """トップページ（メモ一覧）"""
    notes = load_notes(NOTES_PATH)

    return render_template("test48list.html", notes=notes)

if __name__ == "__main__":
    app.run(debug=True, port=8000)