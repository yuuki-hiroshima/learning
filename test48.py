from flask import Flask, render_template, request, redirect, url_for, abort
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

def find_note_by_id(notes, note_id):    # JSON → Python化した一覧から、指定IDの1件を取り出す。
    """id が一致するメモを返す。無ければ None。"""
    for row in notes:
        if row.get("id") == note_id:
            return row
    return None

@app.route("/notes/<int:note_id>")
def show(note_id):
    """
    データの流れ：
      URLの <note_id> を受け取る
        → notes.json を読み込んで Python のリストにする
        → 指定 id の1件を探す（find_note_by_id）
        → 見つかれば HTML に “その1件” を渡して表示
        → 無ければ 404（存在しないID）を返す
    """
    notes = load_notes(NOTES_PATH)
    note = find_note_by_id(notes, note_id)

    if note is None:
        abort(404, description=f"Note #{note_id} not found.")

    return render_template("test48detail.html", note=note)

@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])
def edit(note_id):
    """
    データの流れ：
      GET  → notes.json を読み込み → id一致の1件を探す → 既存値をフォームに流し込んで返す
      POST → フォーム値を受け取り → 検証 → notes.json を読み込み
             → 対象の辞書を書き換え（title/body/updated_at）
             → JSONへ保存 → 詳細ページへリダイレクト（?updated=1）
    """
    # ① まず全件をロード（データの倉庫をPythonのリストとして取り出す）
    notes = load_notes(NOTES_PATH)

    # ② 表示/更新対象の1件を特定（見つからなければ404）
    note = find_note_by_id(notes, note_id)
    if note is None:
        abort(404, description=f"Note #{note_id} not found.")

    # ③ GET：既存の値をフォームに入れて返す（画面はまだ読み取り専用）
    if request.method == "GET":
        return render_template("test48edit.html", note=note, error=None)

    # ④ POST：フォーム送信（新しい値の入口）
    new_title = validate_title(request.form.get("title"))
    new_body = validate_body(request.form.get("body"))

    # ⑤ 入力エラー：保存はせず、エラーメッセージ付きでフォームへ差し戻す
    if new_title is None:
        return render_template(
            "test48edit.html", note=note, error="タイトルは必須です。",
            last_title=request.form.get("title", ""),
            last_body=request.form.get("body", "")
        )
    
    # ⑥ ここで状態変更：Pythonの辞書を上書き（1件分）
    note["title"] = new_title
    note["body"] = new_body
    now = __import__("datetime").datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    note["updated_at"] = now

    # ⑦ 全体（notesリスト）をJSONに書き戻す。永続化
    save_notes(notes, NOTES_PATH)

    # ⑧ 完了後は詳細ページへ戻す（updated=1 で更新完了を伝える）
    return redirect(url_for("show", note_id=note_id, updated=1))

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

@app.route("/notes/<int:note_id>/delete", methods=["GET", "POST"])  # 削除のページに来たとき、直下の関数を動かす。
def delete(note_id):

    notes = load_notes(NOTES_PATH)                                  # JSONファイルを読み込む
    note = next((n for n in notes if n.get("id") == note_id), None) # 指定されたIDのメモを探す（なければ None）
    if note is None:                                                # 見つからない場合（IDが違うなど）
        abort(404)                                                  # 「ページが見つかりません」と返す

    if request.method == "GET":                                     # 削除の確認画面を表示する段階
        return render_template("test48delete.html", note=note)      # 結果をフロントに返す
    
    # ここから先は「POST」。（ユーザーが「削除します」のボタンを押したあとの処理）
    new_list = [n for n in notes if n.get("id") != note_id]         # ユーザーが選んだID以外のデータを格納して新しいリストを作る
    save_notes(new_list, NOTES_PATH)                                # 新しいリストでJSONファイルを上書き
    print(f"🗑️ ID={note_id} のメモを削除しました。")

    return redirect(url_for("index", deleted=1))                     # 削除が終わったら一覧ページへ戻る（delete=1 は「削除した」ことの合図）

@app.route("/")
def index():
    """トップページ（メモ一覧）"""
    notes = load_notes(NOTES_PATH)

    return render_template("test48list.html", notes=notes)

if __name__ == "__main__":
    app.run(debug=True, port=8000)