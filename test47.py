# 「test43.py」のメモアプリをサブコマンド形式として最小限で構成

import os
import json
import datetime
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_PATH = os.path.join(BASE_DIR, "data", "notes.json")

MAX_TITLE_LEN = 100
MAX_BODY_LEN = 1000

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
        print('まずは: python3 test47.py add "タイトル" --body "本文"')
        return
    print(f"===== メモ一覧{len(data)}件 =====") 
    for row in data:
        created = row.get("created_at", "").replace("T", " ")[:16]
        print(f"[#{row.get('id')}] {row.get('title', '')} {created}")

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

    return parser.parse_args()

def main():
    args = parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        print("❗コマンドを指定してください（add / list / update / delete）")

if __name__ == "__main__":
    main()