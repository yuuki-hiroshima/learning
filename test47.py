# 「test43.py」のメモアプリをサブコマンド形式として最小限で構成

import os
import csv
import json
import datetime
import argparse
import wcwidth
import re
from collections import Counter

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_PATH = os.path.join(BASE_DIR, "data", "notes.json")

MAX_TITLE_LEN = 100
MAX_BODY_LEN = 1000

RED   = "\033[31m"
GREEN = "\033[32m"
YELLOW= "\033[33m"
BLUE  = "\033[34m"
HILITE = "\033[45m"
RESET = "\033[0m"

def visual_width(text: str) -> int:                 # wcwidthで文字の表は幅を取得し、合計幅を求める関数
    """文字列の見た目の幅を計算する（全角=2、半角=1）"""
    return sum(wcwidth.wcwidth(ch) for ch in str(text or ""))

def pad(text: str, width: int) -> str:              # 幅の差分だけスペースを足す関数
    """左寄せで幅を揃えます。（全角混じりはざっくりでOK）"""
    s = str(text or "")
    length = visual_width(s)
    padding = max(0, width - length)
    return s + " " * padding

def clip(text: str, width: int) -> str:             # 字数をオーバーする場合は、指定した文字数で切って「…」をつける関数
    """見た目の幅で切る（全角対応）"""
    s = str(text or "")
    result = ""
    current_width = 0
    for ch in s:
        w = wcwidth.wcwidth(ch) or 0
        if current_width + w > width -1:
            result += "…"
            break
        result += ch
        current_width += w
    return result

def highlight(text: str, words, case_sensitive: bool) -> str:   # 色コードは幅計算に影響するので、clip/pad はハイライトの前にかけるのが安全
    """text 中の words を色付け。大小無視なら小文字化して探す。"""
    s = str(text or "")
    if not words:
        return s
    
    escaped = [re.escape(w) for w in words if w] # 正規表現で複数語を一気にハイライト（特殊文字はエスケープ）
    if not escaped:
        return s
    pattern = "|".join(escaped)
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.sub(pattern, lambda m: f"{HILITE}{m.group(0)}{RESET}", s, flags=flags)

def error(msg, hint=None):
    print(f"❌️ {msg}")
    if hint:
        print(f"対処: {hint}")

def validate_title(raw):
    title = (raw or "").strip()
    if title == "":
        error("タイトルは必須です。", "空白以外の文字を入れてください。")
        return None
    if "\n" in title:
        title = title.replace("\n", " ")
    if len(title) > MAX_TITLE_LEN:
        error(f"タイトルが長すぎます（{len(title)}）文字", f"上限は {MAX_TITLE_LEN} 文字です。")
        return None
    return title

def validate_body(raw):
    if raw is None:
        return "(本文なし)"
    body = str(raw).strip()
    if body == "":
        return "(本文なし)"
    if len(body) > MAX_BODY_LEN:
        error(f"本文が長すぎます({len(body)}文字)", f"上限は {MAX_BODY_LEN} 文字です。")
        return None
    return body

# ===== データの読み書き =====
def load_notes(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data or []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        error("JSONファイルが壊れているようです。", "バックアップがあれば戻すか、手で整えてください。")
        print(f"詳細: JSONDecodeError - {e}")
        return []
    except Exception as e:
        error("データ読み込み中に予期せぬエラーが起きました。")
        print(f"詳細: {type(e).__name__} - {e}")
        return []
    
def save_notes(data, filepath):
    dirpath = os.path.dirname(filepath)
    os.makedirs(dirpath, exist_ok=True)
    tmp_path = os.path.join(dirpath, ".notes.json.tmp")
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, filepath)
        print("✅️ JSONファイルに保存しました。")
    except PermissionError as e:
        error("保存に失敗しました（権限不足）。", "data/ フォルダや notes.json の権限を確認してください。")
        print(f"詳細: {type(e).__name__} - {e}")
    except Exception as e:
        error("保存処理で予期せぬエラーが発生しました。")
        print(f"詳細: {type(e).__name__} - {e}")
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

def next_id(data):
    if not data:
        return 1
    return max(row.get("id", 0) for row in data) + 1

# ===== サブコマンドごとの本体 =====
def cmd_add(args):
    data = load_notes(NOTES_PATH)

    title = validate_title(args.title)
    if title is None:
        return
    body = validate_body(args.body)
    if body is None:
        return
    
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    note = {"id": next_id(data), "title": title, "body": body, "created_at": now}
    data.append(note)
    save_notes(data, NOTES_PATH)

def cmd_list(args):
    data = load_notes(NOTES_PATH)
    if not data:
        print("一覧表示できるデータがありません。")
        print(f'{YELLOW}まずは: python3 test47.py add "タイトル" --body "本文"{RESET}')
        return
    print(f"===== メモ一覧{len(data)}件 =====") 
    for row in data:
        created = row.get("created_at", "").replace("T", " ")[:16]
        id_col = f"[#{row.get('id')}]"
        title = clip(row.get("title", ""), 22)
        print(pad(id_col, 5), pad(title, 22), created)

def cmd_update(args):
    data = load_notes(NOTES_PATH)
    target_id = args.id

    if (args.title is None) and (args.body is None):
        error("変更していがないため、更新は行いませんでした。", "--title または --body を指定してください。")
        return
    
    found_index = None
    for i, row in enumerate(data):
        if row.get("id") == target_id:
            found_index = i
            break
    if found_index is None:
        error(f"該当のIDがありません: {target_id}", "まず list でIDを確認してください。")
        return
    
    current = data[found_index]

    if args.title is not None:
        checked = validate_title(args.title)
        if checked is None:
            return
        new_title = checked
    else:
        new_title = current.get("title", "")

    if args.body is not None:
        checked = validate_body(args.body)
        if checked is None:
            return
        new_body = checked
    else:
        new_body = current.get("body", "")

    current["title"] = new_title
    current["body"] = new_body
    current["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    save_notes(data, NOTES_PATH)

def cmd_delete(args):
    data = load_notes(NOTES_PATH)
    before = len(data)
    new_data = [row for row in data if row.get("id") != args.id]
    after = len(new_data)
    if before == after:
        error(f"該当のIDがありません: {args.id}", "list で存在するIDを確認してから再実行してください。")
        return
    save_notes(new_data, NOTES_PATH)
    print(f"🗑️ 削除しました(#{args.id})。現在の件数: {after}")

# ===== search コマンドを追加 =====
def cmd_search(args):
    data = load_notes(NOTES_PATH)

    if not args.keywords:
        print(f"{RED}❌️ 検索キーワードを入力してください。{RESET}")
        return

    # 大文字小文字の扱い
    prep    = (lambda s: s or "")                                             # まず「そのまま返す」関数を入れておく（全経路で存在させる）
    kw_list = args.keywords[:]                                                # 既定はキーワードもそのまま使う

    if not args.case_sensitive:                                               # 大文字小文字を区別しないときは…
        prep    = (lambda s: (s or "").lower())                               # 小文字化してから比較する関数に上書き
        kw_list = [k.lower() for k in args.keywords]                          

    # 期間の準備
    d_from = parse_date_ymd(args.date_from)
    d_to = parse_date_ymd(args.date_to)

    # フィルタ条件
    results = []
    for row in data:
        title = prep(row.get("title", ""))
        body = prep(row.get("body", ""))

        # 対象フィールドを選択
        fields = []
        if args.scope == "title":
            fields = [title]
        elif args.scope == "body":
            fields = [body]
        else:
            fields = [title, body] # both

        # ---- ここが肝：複数語 × AND/OR ----
        # any: どれかの語がどれかのフィールドに含まれればOK
        # all: すべての語が、どれかのフィールドに含まれる必要がある
        def contains(word: str) -> bool:
            return any(word in f for f in fields)
        
        if args.match == "any":
            ok_text = any(contains(w) for w in kw_list)
        else:
            ok_text = all(contains(w) for w in kw_list)

        if not ok_text:
            continue

        # 日付範囲（created_at）
        created_at = row.get("created_at", "")
        d_created = to_dt(created_at)
        if d_from and (not d_created or d_created < d_from):
            continue
        if d_to:   # d_to の当日23:59:59まで含めたいので、翌日に達したら除外
            edge = d_to.replace(hour=23, minute=59, second=59)
            if not d_created or d_created > edge:
                continue
        
        results.append(row)

    if not results:
        joined = " ".join(args.keywords)
        print(f"{RED}「{joined}」を含むメモは見つかりませんでした。{RESET}")
        hints = []
        if args.scope != "both":
            hints.append(f"--in both を試す")
        if not args.case_sensitive: 
            hints.append(f"--case-sensitive を試す")
        hints.append("--match any/all の切り替えを試す")
        if hints:
            print(f"{YELLOW}ヒント:{RESET} " + " / ".join(hints))
        return
    
    # limit
    if args.limit and args.limit > 0:
        results = results[:args.limit]

    # 見出しとヘッダ
    joined = " ".join(args.keywords)
    print(f'{YELLOW}🔍 検索結果 {len(results)} 件{RESET}  '
          f'(scope={args.scope}, case={"敏感" if args.case_sensitive else "無視"})')
    
    # ヘッダ行（列幅をそろえる）
    print(pad("ID", 6), pad("タイトル", 24), "作成日時")

    # 本文
    for row in results:
        created = row.get("created_at", "").replace("T", " ")[:16]
        id_col = f"[#{row.get('id')}]"
        title_raw = row.get("title", "")
        title_shr = clip(title_raw, 24)
        title_out = highlight(title_shr, args.keywords, args.case_sensitive)
        print(pad(id_col, 6), pad(title_out, 24), created)

    # --- もし --export が指定されていたら書き出す ---------
    if getattr(args, "export", None):
        export_results(results, args.export)

    # --- もし --stats が指定されていたら簡易集計を表示 -----
    if getattr(args, "stats", False):
        summarize_results(results, by=getattr(args, "by", "date"),
                          limit=getattr(args, "limit_stats", 10))

def parse_date_ymd(s: str): # 日付で検索するための関数（人間文字からPC文字に変換）
    """YYYY-MM-DD を datetime に。空や不正は None を返す。"""
    if not s:
        return None
    try:
        return datetime.datetime.strptime(s.strip(), "%Y-%m-%d")
    except Exception:
        return None
    
def to_dt(created_at: str): # 時刻で検索するための関数（人間文字からPC文字に変換）
    """created_at(YYYY-MM-DDTHH:MM:SS) を datetime に。失敗は None。"""
    try:
        return datetime.datetime.strptime((created_at or "")[:19], "%Y-%m-%dT%H:%M:%S")
    except Exception:
        return None
    
def summarize_results(results, by="date", limit=10):    # 検索結果をスピーディに要約して使い所を増やす関数
    """検索結果を簡易集計して表示する（by=date/title）"""
    # 全体サマリ
    total = len(results)
    dates = []
    title_lens = []
    empty_body = 0

    for row in results:
        created = (row.get("created_at", "")[:10] or "")
        if created:
            dates.append(created)
        t = row.get("title", "")
        title_lens.append(len(str(t)))
        if (row.get("body", "") or "") in ("", "(本文なし)"):
            empty_body += 1
    
    date_min = min(dates) if dates else "-"
    date_max = max(dates) if dates else "-"
    avg_title = (sum(title_lens)/len(title_lens)) if title_lens else 0.0

    # 見出し（全体サマリ）
    print(f"\n{BLUE}📊 集計サマリ{RESET}")
    print(f"  合計: {total} 件")
    print(f"  期間: {date_min} 〜 {date_max}")
    print(f"  平均タイトル長: {avg_title:.1f} 文字")
    print(f"  本文なし: {empty_body} 件")

    # 軸別の内訳
    key_list = []
    if by == "date":
        for row in results:
            key_list.append((row.get("created_at", "")[:10] or "不明日付"))
        label = "日付"
    else:
        for row in results:
            key_list.append((row.get("title", "") or "(無題)"))
        label = "タイトル"

    counter = Counter(key_list)
    ranked = sorted(counter.items(), key=lambda kv: (-kv[1], str(kv[0])))   # 件数の多い順 → キー名順の複合ソートで見やすく

    if limit and limit > 0:
        ranked = ranked[:limit]

    # 表敬式で出力
    print(f"\n{BLUE}📔 内訳(by={by}){RESET}")
    print(pad(label, 26), pad("件数", 6))
    for k, cnt in ranked:
        k_shr = clip(str(k), 26)
        print(pad(k_shr, 26), pad(str(cnt), 6))
    
def export_results(results, mode="csv"):    # 検索結果をCSVやJSONに書き出す関数を追加
    """検索結果をCSVまたはJSONに保存する（同名回避のため時刻でファイル名を作る）"""
    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"export_{now}.{mode}"

    # ---- 列（キー）をそろえる下ごしらえ -----------------------------------
    # どうして？ → レコードごとに持つキーが微妙に違っても、CSVの列が崩れないようにするため
    all_keys = set()
    for row in results:
        all_keys.update(row.keys())
    fieldnames = sorted(all_keys)

    try:
        if mode == "csv":
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for row in results:
                    safe_row = {key: row.get(key, "") for key in fieldnames}
                    writer.writerow(safe_row)
        else:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
         
        print(f"{GREEN}✅️ 検索結果を {filename} に保存しました。{RESET}")
    except Exception as e:
        print(f"{RED}❌️ 書き出しに失敗しました:{RESET} {type(e).__name__} - {e}")

# ===== 引数（サブコマンド）の定義 =====
def parse_args():
    parser = argparse.ArgumentParser(
        description="JSONメモアプリ（サブコマンド版）\nadd / list / updata / delete を使って操作できます。",
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="利用できるコマンド")

    # add
    p_add = subparsers.add_parser("add", help="メモを追加")
    p_add.add_argument("title", help="タイトルを指定")
    p_add.add_argument("--body", help="本文を指定", default="（本文なし）")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="メモ一覧を表示")
    p_list.set_defaults(func=cmd_list)

    # update
    p_upd = subparsers.add_parser("update", help="メモを更新")
    p_upd.add_argument("id", type=int, help="更新対象のID")
    p_upd.add_argument("--title", help="新しいタイトル")
    p_upd.add_argument("--body", help="新しい本文")
    p_upd.set_defaults(func=cmd_update)

    # delete
    p_del = subparsers.add_parser("delete", help="メモを削除")
    p_del.add_argument("id", type=int, help="削除対象のID")
    p_del.set_defaults(func=cmd_delete)

    # search
    p_search = subparsers.add_parser("search", help="キーワードでメモを検索")
    p_search.add_argument("keywords", nargs="+", help="検索したい文字列を指定")  # スペース区切りで複数指定OK
    p_search.add_argument("--match", choices=["any", "all"], default="any",
                          help="any=どれか含む（OR）/ all=すべて含む（AND）")       # AND/ORの切り替えオプションを追加
    p_search.add_argument("--in", dest="scope", choices=["title", "body", "both"],
                          default="both", help="検索対象（title/body/both）")
    p_search.add_argument("--from", dest="date_from", help="開始日（YYYY-MM-DD）")
    p_search.add_argument("--to", dest="date_to", help="終了日（YYYY-MM-DD）")
    p_search.add_argument("--case-sensitive", action="store_true", help="大文字小文字を区別")
    p_search.add_argument("--limit", type=int, default=0, help="最大表示件数（0は制限なし）")

    p_search.add_argument("--stats", action="store_true", help="検索結果を表示する")
    p_search.add_argument("--by", choices=["date", "title"], default="date", help="集計の軸（date=作成日ごと / title=タイトルごと）")
    p_search.add_argument("--limit-stats", type=int, default=10, help="集計表示の最大行数（0は制限なし）")

    # export
    p_search.add_argument("--export", choices=["csv", "json"], help="検索結果をファイルに保存（csv/json）")
    p_search.set_defaults(func=cmd_search)

    

    return parser.parse_args()

def main():
    args = parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        print("❗コマンドを指定してください（add / list / update / delete / search）")

if __name__ == "__main__":
    main()