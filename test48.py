from flask import Flask, render_template, request, redirect, url_for, abort
import json
import os
import datetime
from markupsafe import Markup, escape   # 【追加】HTMLの安全な文字化と「このままHTMLにしてOKだよ」の印を使うため
import re                               # 【追加】キーワードを見つける（正規表現）

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

# 【追加】キーワードを <mark> でハイライトして、安全にHTMLとして返す
def highlight_html(text, words, case_sensitive=False):                                        # ← 光らせる関数の入口（元の文字・語リスト・大文字小文字の扱い）
    raw_text = text or ""                                                                     # 空っぽ(None)でも安全に扱えるように、空文字に直しておく
    safe_text = escape(raw_text)                                                              # HTMLの危ない記号（< > & など）を安全な文字に変える

    # ---- デバッグ表示（ここに何が入ってきた？） ----
    print("[DEBUG highlight_html] text(in)  =", repr(raw_text))                                # 受け取った元の文字をそのまま表示
    print("[DEBUG highlight_html] words(in) =", repr(words))                                   # 探したい言葉のリストを表示
    print("[DEBUG highlight_html] case_sensitive =", case_sensitive)                           # 大文字小文字を区別するかどうかを表示

    # ---- 語リストの掃除（空文字などを除く） ----
    words = [w for w in (words or []) if w]                                                   # None対策＋空文字を除いて、きれいな語リストにする
    if not words:                                                                             # 探す語がひとつも無いなら…
        print("[DEBUG highlight_html] no words -> return escaped text only")                  # デバッグ表示：そのまま返すよ
        return Markup(safe_text)                                                              # 安全化しただけの文字列を返す（ハイライトなし）

    # ---- 探すための「型紙」を作る（正規表現） ----
    pattern = "|".join(re.escape(w) for w in words)                                           # 語A|語B|語C … という形の“どれかに当たる”型紙を作る（特殊記号はエスケープ）
    flags = 0 if case_sensitive else re.IGNORECASE                                            # 大文字小文字を区別しないなら、IGNORECASEを使う

    print("[DEBUG highlight_html] regex pattern =", repr(pattern))                            # 正規表現パターンを表示
    print("[DEBUG highlight_html] regex flags   =", "0" if flags == 0 else "IGNORECASE")      # フラグを表示（見やすく）

    # ---- 見つかった場所を <mark>…</mark> で囲う ----
    highlighted = re.sub(                                                                     # 文字の置き換えをする
        pattern,                                                                              # さっき作った型紙で探す
        lambda m: f"<mark>{m.group(0)}</mark>",                                              # 見つかった文字（m.group(0)）を <mark> で包む
        safe_text,                                                                            # 安全化済みの文字列の中で探す（XSS対策のため先にescape）
        flags=flags                                                                           # 大文字小文字の扱い
    )

    print("[DEBUG highlight_html] text(out) =", repr(highlighted))                            # 変換後の文字を表示（<mark> が入っているはず）
    return Markup(highlighted)                                                                # 「これはHTMLとして表示OKだよ」の印を付けて返す

# 【追加】本文から一致箇所の周辺だけ切り出して、ハイライト付きで返す
def make_snippet(text, words, case_sensitive=False, ctx=40):                                  # ← 抜粋（スニペット）を作る関数の入口
    raw = text or ""                                                                          # None対策：空文字に直す
    words = [w for w in (words or []) if w]                                                   # 語リストの掃除：空を除く

    # ---- デバッグ表示（いま何をもらってる？） ----
    print("[DEBUG make_snippet] text(len) =", len(raw))                                       # 本文の長さを表示（長いか短いかの目安）
    print("[DEBUG make_snippet] words     =", repr(words))                                    # 探す語のリストを表示
    print("[DEBUG make_snippet] case_sensitive =", case_sensitive, "ctx =", ctx)              # 大文字小文字の扱い と 前後に見せる幅

    # ---- 何も探さない場合は、先頭だけ見せて終わり ----
    if (not raw) or (not words):                                                              # 本文が空、または語が空
        head = raw[:ctx * 2]                                                                  # 先頭だけ少し切り出す
        need_ellipsis = "…" if len(raw) > ctx * 2 else ""                                     # 長いなら末尾に「…」
        out = escape(head + need_ellipsis)                                                    # 安全化しておく
        print("[DEBUG make_snippet] no search -> head only")                                  # デバッグ表示
        return Markup(out)                                                                    # Markupで返す

    # ---- 探す準備（正規表現の“型紙”を作る）----
    flags = 0 if case_sensitive else re.IGNORECASE                                            # 大文字小文字の扱い
    pattern = re.compile("|".join(re.escape(w) for w in words), flags)                        # 語A|語B … の“どれかヒット”型紙
    m = pattern.search(raw)                                                                   # 本文の中で、最初のヒットを探す

    print("[DEBUG make_snippet] first match =", (None if not m else (m.group(0), m.start(), m.end())))  # 何にヒットしたか＆位置

    # ---- ヒットが無いなら、先頭だけを返す ----
    if not m:                                                                                 # 見つからない
        head = raw[:ctx * 2]                                                                  # 先頭を少し
        need_ellipsis = "…" if len(raw) > ctx * 2 else ""                                     # 長いなら省略記号
        out = escape(head + need_ellipsis)                                                    # 安全化
        print("[DEBUG make_snippet] no match -> head only")                                   # デバッグ表示
        return Markup(out)                                                                    # Markupで返す

    # ---- ヒット位置の前後を切り出す（見せる範囲を決める）----
    start = max(0, m.start() - ctx)                                                           # 例：ヒットの40文字前から
    end   = min(len(raw), m.end() + ctx)                                                      # 例：ヒットの40文字後まで
    piece = raw[start:end]                                                                    # ここが画面に出す“抜粋の芯”

    prefix = "…" if start > 0       else ""                                                   # 前を切ったなら「…」
    suffix = "…" if end   < len(raw) else ""                                                  # 後ろを切ったなら「…」

    print("[DEBUG make_snippet] slice =", (start, end), "prefix:", bool(prefix), "suffix:", bool(suffix))  # どこを切ったか

    # ---- 抜粋の中で、ヒット部分を光らせる（安全化も忘れずに）----
    highlighted_piece = highlight_html(piece, words, case_sensitive)                          # 中で escape と <mark> をやってくれる
    out = Markup(prefix) + highlighted_piece + Markup(suffix)                                 # 省略記号を前後に足して仕上げ

    print("[DEBUG make_snippet] out ready")                                                   # 完成！
    return out                                                                                # Markupのまま返す

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

@app.route("/search")
def search():
    """
    データの流れ：
      ブラウザから ?q=キーワード を受け取る（入口）
        → notes.json を読み込み（Pythonのリストに）
        → タイトル/本文に部分一致する行を抽出（中継：フィルタ）
        → created_at を datetime にして新しい順に並べ替える（変化）
        → HTMLに渡して表示（出口）
    """
    # ① 入力の取得（文字列を受け取る。空やNoneでも落ちないようにケア）
    q_raw = request.args.get("q", "")   # Flaskでは、URLに付いた「?以降の部分」を request.args という特別な辞書で扱う。
    q = q_raw.strip().lower()

    # ② 全件ロード
    notes = load_notes(NOTES_PATH)

    # ③ フィルタ（部分一致：タイトル or 本文のどちらかに q を含む）
    if q:   # 「q」が空でなければという条件 = なにか入力があったときだけ検索処理をするという意味
        def norm(s): return (s or "").lower()   # すべての文字を小文字に変えて、None でも落ちないようにする関数。
        results = [
            n for n in notes
            if (q in norm(n.get("title", ""))) or (q in norm(n.get("body", "")))    # title か body に q が含まれているかを調べる
        ]
    else:
        results = []    # キーワードが空なら結果なし（フロントで「入力してください」とメッセージを出す運用）

    # ④ 並び替え（新しい順：降順）
    def to_dt_safe(created):
        try:
            return datetime.datetime.strptime((created or "")[:19], "%Y-%m-%dT%H:%M:%S")    # 文字列のままだと正しく並び替えられないため、日付（例：“2025-11-10T12:34:56”）を、datetime 型に変換する。
        except Exception:
            return datetime.datetime.min    # 日付が壊れていたら、最古扱い
        
    results_sorted = sorted(
        results,
        key=lambda n: to_dt_safe(n.get("created_at", "")),  #　並び替えの基準を決めている。
        reverse=True
    )

    # ⑤ 見た目を見やすい形に変換する
    words = [w for w in (q_raw.split() if q_raw else []) if w.strip()]
    items = []
    for n in results_sorted:
        created_fmt = (n.get("created_at", "") or "")[:16].replace("T", " ")
        title_html = highlight_html(n.get("title", ""), words)
        body_snip = make_snippet(n.get("body", ""), words)
        items.append({
            "id": n.get("id"),
            "created_at": created_fmt,
            "title_html": title_html,
            "body_snip": body_snip
        })

    # ⑥ 出口（HTMLへ渡す：左がテンプレ側の変数名、右がPythonの中身）
    return render_template(
        "test48search.html",
        q=q_raw,                    # 入力の見た目はそのまま返す（小文字化しない）
        count=len(items),  # 件数
        items=items      # 並び替え済みの結果リスト
    )

@app.route("/")
def index():
    """トップページ（メモ一覧）"""
    notes = load_notes(NOTES_PATH)
    if not notes:
        return render_template("test48list.html", notes=[], empty=True)
    
    # ===== 並び替え処理 =====
    # 目的：作成日時 created_at を基準に新しい順に並べる
    # データの流れ：
    #   1．各行の created_at を datetime に変換
    #   2．新しいものから順に並べ直す
    def to_dt_safe(created):
        try:
            return datetime.datetime.strptime(created[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            return datetime.datetime.min    # 日付が壊れている場合は1番古く扱う
        
    notes_sorted = sorted(notes, key=lambda n : to_dt_safe(n.get("created_at", "")), reverse=True)

    return render_template("test48list.html", notes=notes_sorted, empty=False)

if __name__ == "__main__":
    app.run(debug=True, port=8000)