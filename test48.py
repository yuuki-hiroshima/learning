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
def highlight_html(text, words, case_sensitive=False):
    """タイトルなどの文字列の中で、キーワードに <mark> をつけて光らせる関数だよ。"""

    print("\n[DEBUG] highlight_html() が呼ばれました。")                        # 👀 この関数がいつ動いたかを知るためのログ
    print("        引数 text =", repr(text))                                  # 👀 元の文字列が何かを確認するよ
    print("        引数 words =", words)                                      # 👀 ハイライトしたいキーワードのリストを確認するよ
    print("        引数 case_sensitive =", case_sensitive)                    # 👀 大文字・小文字を区別するかどうかを確認するよ

    s = escape(text or "")                                                    # text が None や空でも安全に、HTML用にエスケープして文字列にするよ
    # 例： <script> みたいな危ない記号を、「ただの文字」として扱うための変換だよ

    words = [w for w in (words or []) if w]                                   # words の中から、空文字や None を取り除いて「ちゃんとした単語」だけにするよ
    print("        整理後の words =", words)                                   # 👀 実際にハイライトに使う単語だけが残っているか確認するよ

    if not words:                                                             # もしハイライトする単語が1つもなかったら…
        print("        words が空なので、ハイライトはせずにそのまま返します。")
        return Markup(s)                                                      # 何も変えずに、そのまま HTML として返すよ

    # ここから「どの文字を光らせるか」を決める準備だよ
    pattern = "|".join(re.escape(w) for w in words)                           # すべての単語を「正規表現用」に安全に並べて、"word1|word2" という形のパターンにするよ
                                                                              # re.escape(w) は、「.」「+」などの特別な記号も“普通の文字”として扱うようにするおまじないだよ

    flags = 0 if case_sensitive else re.IGNORECASE                            # 大文字・小文字を区別しないときは、re.IGNORECASE フラグを付けるよ

    print("        正規表現パターン =", pattern)                                 # 👀 どんなルールで探すかを確認するよ
    print("        フラグ =", "そのまま(区別する)" if case_sensitive else "IGNORECASE(区別しない)")

    highlighted = re.sub(                                                     # s の中のキーワードに <mark> をつけた新しい文字列を作るよ
        pattern,                                                              # 「どんな文字を探すか」のルール
        lambda m: f"<mark>{m.group(0)}</mark>",                               # 見つかったところをどう置き換えるか（<mark>〜</mark> で囲む）
        s,                                                                    # 探す対象の文字列（エスケープ済み）
        flags=flags                                                           # 大文字・小文字の扱いルール
    )

    print("        ハイライト後の文字列(一部) =", repr(highlighted[:80]))         # 👀 長くなりすぎるので先頭80文字だけ確認してみるよ

    return Markup(highlighted)                                                # これは「HTMLとして安全だよ」という印をつけてテンプレートに返すよ

# 【追加】本文から一致箇所の周辺だけ切り出して、ハイライト付きで返す
def make_snippet(text, words, case_sensitive=False, ctx=40):
    """
    本文の中から、キーワードの「前後だけ」を切り出して、
    その部分をハイライトして短い文章（スニペット）にする関数だよ。
    """

    print("\n[DEBUG] make_snippet() が呼ばれました。")                            # 👀 この関数が動いたタイミングを知るためのログ
    print("        引数 text (本文) =", repr(text))                              # 👀 元の本文がどんな文字列か確認するよ
    print("        引数 words =", words)                                        # 👀 ハイライト対象のキーワード一覧だよ
    print("        引数 case_sensitive =", case_sensitive)                      # 👀 大文字小文字の区別ルールを確認するよ
    print("        引数 ctx =", ctx, "(キーワードの前後に何文字ずつ見せるか)")        # 👀 キーワード前後の「おまけ表示」の幅だよ

    raw = text or ""                                                            # None の場合でも扱いやすいように、必ず文字列にしておくよ
    text_len = len(raw)                                                         # 本文全体の長さを計算しておくよ
    print("        本文の長さ =", text_len)

    # 🟦 パターン1：本文が空 or キーワードなし → 先頭だけを切って返すモード
    if not raw or not words:                                                   # 本文がない、またはキーワードが1つもない場合
        print("        本文が空、またはハイライトする単語がないので、先頭だけ返します。")
        head = raw[:ctx * 2]                                                   # 先頭から「ctx*2」文字だけを取り出すよ（ちょっと長めに）
        if len(raw) > ctx * 2:                                                 # もし本文がもっと長いなら…
            head = head + "…"                                                  # 「まだ続きがあるよ」という意味で「…」を付け足すよ
        print("        返すスニペット(簡易) =", repr(head))
        return Markup(escape(head))                                            # HTML用にエスケープして、そのまま返すよ

    # 🟦 パターン2：キーワードあり → 本文のどこに出てくるかを探す
    flags = 0 if case_sensitive else re.IGNORECASE                             # 大文字小文字を区別しないなら IGNORECASE を使うよ
    pattern = re.compile("|".join(re.escape(w) for w in words), flags)         # 複数キーワードをまとめて探すための正規表現ルールだよ

    print("        検索用パターン =", pattern.pattern)
    print("        フラグ =", "そのまま(区別する)" if case_sensitive else "IGNORECASE(区別しない)")

    m = pattern.search(raw)                                                    # 本文の中から、最初にキーワードが出てくる場所を探すよ
    if not m:                                                                  # もし1回も見つからなかったら…
        print("        本文内にキーワードが見つかりませんでした。先頭だけ返します。")
        head = raw[:ctx * 2]                                                   # 先頭だけを使うモードに切り替えるよ
        if len(raw) > ctx * 2:
            head = head + "…"
        print("        返すスニペット(キーワード未検出) =", repr(head))
        return Markup(escape(head))                                            # ここでもエスケープしてから返すよ

    # 🟦 パターン3：キーワードが見つかった場合 → その前後を切り出す
    print("        キーワードが見つかりました。")                               
    print("        マッチ開始位置 m.start() =", m.start())                       # 👀 何文字目からヒットしたのか
    print("        マッチ終了位置 m.end()   =", m.end())                         # 👀 何文字目までがヒットしたのか

    # キーワードの前後 ctx 文字ぶん余裕を持って切り出すよ
    start = max(0, m.start() - ctx)                                            # 左側の端：キーワードの少し前から
    end   = min(len(raw), m.end() + ctx)                                       # 右側の端：キーワードの少し後ろまで

    print("        切り出し開始位置 start =", start)
    print("        切り出し終了位置 end   =", end)

    piece = raw[start:end]                                                     # 実際にその範囲の文字列を取り出したものが「見せたい中心部分」だよ
    print("        切り出した部分 piece(一部) =", repr(piece[:80]))

    # 先頭や末尾に「…」を足すかどうかを決めるよ
    prefix = "…" if start > 0 else ""                                          # もし start が0より大きいなら、「前にもまだ文章があるよ」という意味で「…」を付ける
    suffix = "…" if end < len(raw) else ""                                     # もし end が本文の最後より小さいなら、「後ろにも続きがあるよ」という合図で「…」を付ける

    print("        prefix(前側の…)", repr(prefix))
    print("        suffix(後側の…)", repr(suffix))

    # 中心の piece に対して、さっき作った highlight_html でもう一度ハイライトをかけるよ
    highlighted_piece = highlight_html(piece, words, case_sensitive)           # ここで <mark> 付きの部分を作る

    print("        ハイライト済みの piece(一部) =", repr(str(highlighted_piece)[:80]))

    # 最終的なスニペットは「前の… + ハイライト付き中心 + 後ろの…」という形になるよ
    snippet = Markup(prefix) + highlighted_piece + Markup(suffix)

    print("        最終的な snippet(一部) =", repr(str(snippet)[:80]))           # 👀 実際に画面に出る短い文章をチェックするよ

    return snippet                                                             # Markup オブジェクトとしてテンプレートに返すよ

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
    print("[DEBUG] show() が呼ばれました。note_id =", note_id)

    notes = load_notes(NOTES_PATH)
    note = find_note_by_id(notes, note_id)

    print("[DEBUG] JSONの中身（一部）:", notes[:2])
    print("[DEBUG] 見つかったメモ:", note)

    if note is None:
        abort(404, description=f"Note #{note_id} not found.")

    return render_template("test48detail.html", note=note)

@app.route("/notes/<int:note_id>/edit", methods=["GET", "POST"])  # 「/notes/数字/edit」というURLに来たら、この関数を動かしてね〜という合図
def edit(note_id):                                               # note_id には URL の「数字の部分」（例: 5）が入ってくるよ
    """
    メモを編集するための画面と処理をまとめた関数だよ。

    データの流れ（ざっくり）：
      1. ブラウザが /notes/<id>/edit を開く（GET）
      2. JSONファイルを読み込んで、id が同じメモを1件探す
      3. その1件の中身をフォームに入れて、編集画面を見せる

      4. フォームで「更新する」が押される（POST）
      5. 送られてきた title / body をチェックする
      6. 問題なければ、そのメモの中身を書き換えて JSON に保存
      7. 書き換えたあと、詳細ページ /notes/<id> に戻る
    """

    print("[DEBUG] edit() に入りました。note_id =", note_id, "method =", request.method)    # 👀 今どのIDのメモを編集しようとしているか、HTTPメソッド(GET/POST)は何かを表示して確認

    # ① まず全件をロード（データの倉庫をPythonのリストとして取り出す）
    notes = load_notes(NOTES_PATH)                               # JSONファイル(メモの倉庫)を全部読み込んで、Pythonのリストにするよ
    print("[DEBUG] 現在のメモ件数 =", len(notes))                  # 👀 読み込んだメモの件数を確認しておくよ

    # ② 表示/更新対象の1件を特定（見つからなければ404）
    note = find_note_by_id(notes, note_id)                        # 読み込んだメモ一覧の中から、id が note_id と同じものを1件探してくるよ
    print("[DEBUG] 対象の note =", note)                          # 👀 本当に見つかったか、中身がどうなっているかを確認するよ

    if note is None:                                              # もし note が見つからなかったら（＝そんなIDはなかったら）
        print("[DEBUG] 該当IDのメモが見つかりません。404を返します。")  # 👀 エラー理由をコンソールに出しておくよ
        abort(404, description=f"Note #{note_id} not found.")     # ブラウザ側には「404 Not Found」というエラー画面を返すよ

    # ③ GET：既存の値をフォームに入れて返す（画面はまだ読み取り専用）
    if request.method == "GET":                                   # ブラウザが最初にページを開いたとき（まだフォーム送信はしていないとき）の分岐だよ
        print("[DEBUG][GET] 編集フォームを初期表示します。title =", note.get("title"), "body =", note.get("body"))
        # 👀 これからフォームに入れる予定のタイトルと本文を表示して確認するよ

        return render_template(                                   # 編集用のHTML(test48edit.html)をブラウザに返すよ
            "test48edit.html",                                    # 使うテンプレートファイルの名前だよ
            note=note,                                            # 今編集しようとしている1件分のメモをテンプレートに渡すよ
            error=None,                                           # 今の時点ではエラーメッセージはないので「None」にしておくよ
        )

    # ここまで来たら method は「POST」だけだよ（フォームから送信されたあとの処理）
    print("[DEBUG][POST] フォームから送信されました。値を受け取ります。")  # 👀 ここからが「更新ボタンを押したあとの処理」だとわかるように出しておくよ

    raw_title = request.form.get("title")                         # フォームから送られてきた「タイトルの生データ」を取り出すよ（まだ検証前）
    raw_body  = request.form.get("body")                          # フォームから送られてきた「本文の生データ」を取り出すよ（まだ検証前）
    print("[DEBUG][POST] 受け取った raw_title =", raw_title)     # 👀 本当にフォームから届いているか確認するよ
    print("[DEBUG][POST] 受け取った raw_body  =", raw_body)      # 👀 空文字になっていないかなどを確認できるよ

    # ④ POST：フォーム送信（新しい値の入口）
    new_title = validate_title(raw_title)                         # タイトルのチェック用関数に渡して、「きちんとしたタイトル」に整えるよ（空白のみだと None が返る）
    new_body  = validate_body(raw_body)                           # 本文のチェック用関数に渡して、「きちんとした本文」に整えるよ（空なら既定の文になる）

    print("[DEBUG][POST] validate 後の new_title =", new_title)   # 👀 チェック後にどうなったかを出して確認するよ
    print("[DEBUG][POST] validate 後の new_body  =", new_body)    # 👀 None になっていないかなどを見るよ

    # ⑤ 入力エラー：保存はせず、エラーメッセージ付きでフォームへ差し戻す
    if new_title is None:                                         # タイトルの検証に失敗した場合（例：空白しか入っていないなど）
        print("[DEBUG][POST] タイトルが不正なので、エラーとして差し戻します。")  # 👀 ここで保存しない理由をログに残すよ
        return render_template(                                   # もう一度編集画面を表示して、ユーザーに入力し直してもらうよ
            "test48edit.html",                                    # 編集用テンプレートは同じだよ
            note=note,                                            # もともとの note 情報も渡しておくよ
            error="タイトルは必須です。",                            # 画面に表示するエラーメッセージだよ
            last_title=raw_title or "",                           # 入力していたタイトルをそのまま戻してあげるよ（書き直しが楽になる）
            last_body=raw_body or "",                             # 入力していた本文もそのまま戻してあげるよ
        )

    # ここまで来たら、タイトルはOKなので、実際に note の中身を書き換えていくよ
    print("[DEBUG][POST] note を更新します（書き換え前）:", note)     # 👀 書き換える前の note の状態を確認するよ

    # ⑥ ここで状態変更：Pythonの辞書を上書き（1件分）
    note["title"] = new_title                                     # note 辞書の title を、新しいタイトルで上書きするよ
    note["body"]  = new_body                                      # note 辞書の body を、新しい本文で上書きするよ
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")   # 今の日時を「2025-11-10T12:34:56」という形の文字にするよ
    note["updated_at"] = now                                      # note 辞書に updated_at というキーで「いつ更新したか」を記録しておくよ

    print("[DEBUG][POST] note を更新しました（書き換え後）:", note)   # 👀 書き換えたあとの note の状態を表示して、ちゃんと変わったか確認するよ

    # ⑦ 全体（notesリスト）をJSONに書き戻す。永続化
    save_notes(notes, NOTES_PATH)                                 # 書き換えた note を含む notes リスト全体を、JSONファイルに保存し直すよ
    print("[DEBUG][POST] save_notes() による保存が完了しました。")    # 👀 保存が終わったことをログに残しておくよ

    # ⑧ 完了後は詳細ページへ戻す（updated=1 で更新完了を伝える）
    return redirect(url_for("show", note_id=note_id, updated=1))  # 保存が終わったら、詳細ページ /notes/<id>?updated=1 へ移動してもらうよ
                                                                  # 「updated=1」は「更新が成功したよ」の小さな印だよ（必要に応じてHTMLで使える）

@app.route("/add", methods=["GET", "POST"])     # 「/add」というURLに来たとき、この add 関数を使うよ、という合図（GETとPOSTの2種類を受け付ける）
def add():                                      # メモを新しく追加するときに使う関数のスタートだよ
    """
    新しいメモを追加するための画面と処理をまとめた関数だよ。

    データの流れ：
      【GETのとき】（最初にフォームを開くとき）
        ブラウザ → 「/add を見せて」とサーバにお願いする
          → サーバ側で空のフォームHTMLを返す

      【POSTのとき】（フォームを送信したとき）
        ブラウザ → 入力した title / body をサーバに送る
          → サーバ側で title / body をチェックする
          → OKなら JSON を読み込む
          → 1件分のメモを作ってリストに追加する
          → JSONファイルに保存しなおす
          → 一覧ページ("/")に戻す
    """

    print("[DEBUG] add() に入りました。method =", request.method)
    # 👀 今 add() が呼ばれたことと、「GET か POST か」をターミナルで確認するよ

    # ① ブラウザがフォームを見たいとき（最初に /add を開いたとき → GET）
    if request.method == "GET":                               # まだ送信ボタンは押されていない状態だよ
        print("[DEBUG][GET] 新規追加フォームを表示します。")       # 👀 今は「画面を見せているだけ」だとわかるようにするよ
        return render_template("test48add.html")              # test48add.html というテンプレートをそのまま返すよ（中身は空のフォーム）

    # ここから先は「POST」＝ フォームから送信された後の処理だよ
    print("[DEBUG][POST] フォーム送信を受け取りました。値を取り出します。")

    # ② POST：フォームから送られてきた “生の” 入力値を取り出す（まだ整えていない）
    raw_title = request.form.get("title")                     # フォームの name="title" の値をそのまま取り出すよ
    raw_body  = request.form.get("body")                      # フォームの name="body"  の値をそのまま取り出すよ
    
    print("[DEBUG][POST] 受け取った raw_title =", raw_title)    # 👀 本当にブラウザから値が来ているか確認するよ
    print("[DEBUG][POST] 受け取った raw_body  =", raw_body)

    # ③ 入力チェック＆整形：空白を削ったり、空の場合の扱いを決めたりする
    title = validate_title(raw_title)                         # タイトル用のチェック関数に渡すよ：空白だけなら None が返ってくる
    body  = validate_body(raw_body)                           # 本文用のチェック関数に渡すよ：空なら「(本文なし)」に変えてくれる

    print("[DEBUG][POST] validate 後の title =", title)        # 👀 チェック後にどうなったか見ておくよ
    print("[DEBUG][POST] validate 後の body  =", body)

    # ④ タイトルに問題があったとき（None のとき）は、保存せずにフォーム画面に戻す
    if title is None:                                         # タイトルが空白だけだったなどで NG の場合だよ
        print("[DEBUG][POST] タイトルが不正なので、エラーとして差し戻します。")
        return render_template(
            "test48add.html",                                 # もう一度 同じフォーム画面を表示するよ
            error="タイトルは必須です。",                        # HTML側で {{ error }} として表示できるエラーメッセージ
            last_title=raw_title or "",                       # 入力していたタイトルをそのまま戻してあげる（書き直しが楽）
            last_body=raw_body or ""                          # 本文も同じく戻してあげる
        )

    # ⑤ ここまで来たら title / body は使える状態なので、実際にJSONから一覧を読み込む
    notes = load_notes(NOTES_PATH)                            # いま保存されているメモ一覧を全部読み込んで、Pythonのリストにするよ

    print("[DEBUG][POST] 追加前のメモ件数 =", len(notes))        # 👀 追加する前に何件あるかを確認するよ

    # ⑥ 1件分のメモ（辞書）を組み立てる
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")  # 「いまの時刻」を文字列に変換する（例: 2025-11-10T12:34:56）
    new_note = {
        "id": next_id(notes),                                  # いまあるIDの最大値+1 を新しいIDとして使うよ
        "title": title,                                        # さっきチェック済みのタイトル
        "body": body,                                          # さっきチェック済みの本文
        "created_at": now                                      # このメモを作った日時
    }
    print("[DEBUG][POST] 追加する new_note =", new_note)        # 👀 本当に正しいデータになっているか確認するよ

    # ⑦ リストの末尾に新しいメモを追加（メモの件数が1件増える）
    notes.append(new_note)                                     # ここでメモ一覧の「Python上のデータ」が変化するよ（状態が変わる）

    print("[DEBUG][POST] 追加後のメモ件数 =", len(notes))         # 👀 メモ件数が1件増えたかどうかを確認しておくよ

    # ⑧ 変わったリスト全体を JSONファイルに保存し直す（永続化）
    save_notes(notes, NOTES_PATH)                              # ファイルに書き戻すことで、プログラムを終了しても消えないようにするよ
    
    print("[DEBUG][POST] save_notes() による保存が完了しました。")

    # ⑨ 最後に一覧ページへ戻る（?added=1 は「追加に成功したよ」という小さなフラグ）
    return redirect(url_for("index", added=1))                 # / にリダイレクトして、index() 関数に処理をまかせるよ

@app.route("/notes/<int:note_id>/delete", methods=["GET", "POST"])   # 「/notes/数字/delete」というURLに来たら、このdelete関数を動かすよ（GETとPOSTの2種類OK）
def delete(note_id):                                                 # note_id には URL の数字（例: /notes/5/delete → 5）が入ってくるよ
    """
    メモを削除するための画面と処理をまとめた関数だよ。

    データの流れ：

      【GETのとき】（確認画面）
        ブラウザ → /notes/<id>/delete を開く
          → サーバ：notes.json を読み込む
          → id が一致する1件のメモを探す
          → 「本当に削除しますか？」と確認するHTMLを返す

      【POSTのとき】（実際に削除）
        ブラウザ → 「削除します」のボタンを押す
          → サーバ：もう一度 notes.json を読み込む
          → 指定の id 以外だけを集めて新しいリストを作る
          → そのリストを JSON に保存し直す
          → 一覧ページ("/")に戻る（?deleted=1 を付ける）
    """

    print("[DEBUG] delete() に入りました。note_id =", note_id, "method =", request.method)  # 👀 今どのIDのメモに対して delete が呼ばれたか、HTTPメソッドが何かを確認

    # ① まずは全件ロード：削除候補を探すために、いまのメモ一覧をすべて読む
    notes = load_notes(NOTES_PATH)                                     # JSONファイルの中身をリストとして読み込むよ
    print("[DEBUG] 現在のメモ件数 =", len(notes))                        # 👀 削除前の件数を確認するよ

    # ② 指定IDのメモを1件探す（見つからなければ None）
    note = next((n for n in notes if n.get("id") == note_id), None)    # リストの中から id が note_id のものを1つ取り出すよ
    print("[DEBUG] 削除対象の note =", note)                            # 👀 本当に見つかったかどうかをチェックするよ

    # noteの内包表記をバラした場合
    # note = None
    # for n in notes:
    #     if n.get("id") == note_id:
    #         note = n
    #         break

    if note is None:                                                   # もし見つからなかったら（例：URLのIDが存在しない）
        print("[DEBUG] 該当IDのメモが見つかりません。404を返します。")
        abort(404)                                                     # ブラウザには「ページが見つかりません(404)」を返すよ

    # ③ GET：まだ削除ボタンは押されていない → 「確認画面」を出すだけ
    if request.method == "GET":                                        # いきなりURLにアクセスしただけの状態だよ
        print("[DEBUG][GET] 削除確認画面を表示します。note_id =", note_id)  # 👀 ここでは「まだ何も消していない。確認画面を見せているだけ」ということがログでわかる
        return render_template("test48delete.html", note=note)         # HTML側に note（1件分の辞書）を渡して、「本当に消しますか？」画面を表示するよ

    # ④ ここから先は「POST」＝ ユーザーが「削除します」ボタンを押したあと
    print("[DEBUG][POST] 削除実行がリクエストされました。note_id =", note_id)

    # ⑤ 削除後の新しいリストを作る（＝ 指定ID以外のメモだけを集める）
    before = len(notes)                                                # 削除前の件数を覚えておくよ（確認用）
    new_list = [n for n in notes if n.get("id") != note_id]            # id が note_id ではないものだけを集めて新しいリストを作るよ
    after = len(new_list)                                              # 削除後の件数を数えておくよ

    # new_listの内包表記をバラした場合
    # new_list = []
    # for n in notes:
    #     if n.get("id") != note_id:
    #         new_list.append(n)

    print("[DEBUG][POST] 削除前件数 =", before, "削除後件数 =", after)
    # 👀 本当に1件減っているかどうかをチェックできるよ

    if before == after:                                                # 件数が変わっていない = 何も消せていない
        print("[DEBUG][POST] 件数が変わっていません。何も削除されていないようです。")
        # 理論的にはここには来ないはずだけど、安全のためチェックしているよ
        # この場合も一応404にするか、メッセージを出す運用もあり
        abort(404)

    # ⑥ 新しいリストを JSON に保存し直す（ここで「本当にファイルが書き変わる」）
    save_notes(new_list, NOTES_PATH)                                   # 変更後の new_list で notes.json を上書きするよ
    print(f"[DEBUG][POST] ID={note_id} のメモを削除しました。現在の件数: {after}")

    # ⑦ 削除が終わったら一覧ページ("/")へ戻す（?deleted=1 は「削除できたよ」の印）
    return redirect(url_for("index", deleted=1))                        # 一覧ページの index() 関数にバトンを渡すよ

@app.route("/search")                                                      # ブラウザで /search にアクセスされたら、この search() 関数を動かすよ
def search():                                                              # 「検索画面」と「検索処理」をまとめた関数のスタートだよ
    """
    メモをキーワードで検索して、検索結果を見やすく表示するための関数だよ。

    データの流れ（ざっくり）：
      1. ブラウザから /search?q=キーワード という形で文字が送られてくる
      2. JSONファイルから全メモを読み込む
      3. タイトル or 本文に、そのキーワードを含むメモだけに絞り込む
      4. 作成日時 created_at をもとに「新しい順」に並び替える
      5. 画面用の形（ID／タイトルHTML／本文スニペット）に整えてからテンプレートに渡す
    """

    # ① 入力の取得 ------------------------------------------------------------
    # URL の ?q=... の部分から、検索キーワードを取り出すよ
    q_raw = request.args.get("q", "")                                      # 「q」という名前のパラメータを取り出す（無ければ空文字にする）
    print("[DEBUG] /search にアクセスされました。q_raw =", q_raw)         # 👀 まずはブラウザからどんな文字が来たかをログに出すよ

    # 空白の前後を削って、小文字化したバージョンも作っておく（検索用）
    q = q_raw.strip().lower()                                              # 例：「  Python  」→「python」みたいに整える

    # ② 全件ロード ------------------------------------------------------------
    notes = load_notes(NOTES_PATH)                                         # JSONファイルの中身を全部読み込んで、Pythonのリストにするよ
    print("[DEBUG] 現在のメモ件数 =", len(notes))                           # 👀 そもそも何件の中から探すのかを確認するよ

    # ③ キーワードでフィルタ（部分一致） --------------------------------------
    if q:                                                                  # q が空でないときだけ検索する（何も入ってないなら検索しない）
        print("[DEBUG] キーワード検索を実行します。検索語 =", q)

        def norm(s):                                                       # norm は「比較用に文字を整える小さな関数」だよ
            return (s or "").lower()                                       # None や空にも対応しつつ、小文字にして返す（"Python"→"python"）

        results = [                                                        # ここで「検索にヒットしたメモだけ」を集めた新しいリストを作るよ
            n for n in notes                                               # もともとの全メモを1件ずつ n として見る
            if (q in norm(n.get("title", "")))                             # タイトルを小文字化して、その中に q が入っているか？
            or (q in norm(n.get("body", "")))                              # または、本文の中に q が入っているか？
        ]
    else:
        print("[DEBUG] キーワードが空なので、検索は実行しません。")           # 👀 何も入力されていないときはここに来るよ
        results = []                                                       # この場合は「検索結果なし」として扱う

    print("[DEBUG] キーワードにマッチした件数 =", len(results))            # 👀 絞り込んだあとの件数を確認するよ

    # ④ 作成日時で並び替え（新しい順に） -------------------------------------
    def to_dt_safe(created_str):                                           # created_at の文字列を datetime 型に安全に変換するための小さな関数
        try:
            # 例："2025-11-10T12:34:56" → datetime(2025, 11, 10, 12, 34, 56)
            return datetime.datetime.strptime((created_str or "")[:19], "%Y-%m-%dT%H:%M:%S")
        except Exception:
            # 変換に失敗したとき（壊れた日付など）は、いちばん古い日付として扱う
            return datetime.datetime.min

    results_sorted = sorted(                                               # 絞り込んだ結果を、新しい順に並び替えたリストを作るよ
        results,                                                           # 並べ替え対象は「検索にヒットしたメモ」たち
        key=lambda n: to_dt_safe(n.get("created_at", "")),                 # 並べ替えの基準：各メモの created_at を datetime に変換したもの
        reverse=True                                                       # reverse=True なので「大きい＝新しい」ものが先頭に来るよ
    )

    print("[DEBUG] 並び替え後の件数 =", len(results_sorted))                  # 👀 件数は変わらないはずだけど、確認しておくよ

    # ⑤ 画面用の形に整える（ID / タイトルHTML / 本文スニペット） ------------
    # 複数キーワードに対応するために、q_raw をスペースで区切ってリストにするよ
    # 例：「python flask」→ ["python", "flask"]
    words = [w for w in (q_raw.split() if q_raw else []) if w.strip()]     # 何もない要素は捨てて、「中身のある単語」だけにする

    print("[DEBUG] ハイライト対象の words =", words)                          # 👀 どの単語をハイライトしようとしているか確認できるよ

    items = []                                                             # 最終的にテンプレートに渡す1行分のデータを、ここに1件ずつ追加していくよ
    for n in results_sorted:                                               # 並び替え済みのメモを1件ずつ処理するよ
        raw_created = n.get("created_at", "") or ""                        # created_at の生文字列（空なら空文字にしておく）
        created_fmt = raw_created[:16].replace("T", " ")                   # 「YYYY-MM-DDTHH:MM:SS」の先頭16文字を「YYYY-MM-DD HH:MM」に整形

        # タイトルをハイライト付きHTMLに変える（<mark>〜</mark> を付ける）
        title_html = highlight_html(n.get("title", ""), words)             # ここで title の中のキーワードに <mark> を差し込むよ

        # 本文から「キーワードの前後だけ」を取り出して、ハイライトした短い文章にする
        body_snip = make_snippet(n.get("body", ""), words)                 # 1件ずつ「本文のチラ見せ」を作るよ

        print("[DEBUG] 1件分 アイテム作成:",
              "id=", n.get("id"),
              "created_fmt=", created_fmt,
              "title(元)=", n.get("title", ""))

        items.append({                                                     # この1件を、テンプレートで扱いやすい形の辞書にしてリストに追加するよ
            "id": n.get("id"),                                             # メモのID（リンクや表示に使う）
            "created_at": created_fmt,                                     # 整形済みの作成日時（すぐに表示できる形）
            "title_html": title_html,                                      # ハイライト済みのタイトルHTML（<mark>入り）
            "body_snip": body_snip                                         # 本文の一部だけを切り出したスニペット（こちらもハイライト付き）
        })

    print("[DEBUG] テンプレートに渡す items 件数 =", len(items))           # 👀 実際に画面側に渡す件数を確認するよ

    # ⑥ 出口（HTML へ渡す） -------------------------------------------------
    # 左が HTML 側での変数名、右が Python 側の中身だよ
    return render_template(
        "test48search.html",                                               # 検索結果を表示するテンプレートファイル
        q=q_raw,                                                           # 元の入力文字（小文字化せず、そのまま見た目用として渡す）
        count=len(items),                                                  # ヒットした件数（0件なら「見つかりません」と表示）
        items=items                                                        # 1行ごとのデータを詰め込んだリスト（HTMLの for で回す）
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