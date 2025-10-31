import os
import json
import argparse
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMOS_PATH = os.path.join(BASE_DIR, "data", "memos.json")

def save_to_json(records, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=2)
        print(f"✅️ JSONへ保存しました: {os.path.relpath(filepath, BASE_DIR)}")
    except Exception as e:
        print(f"⚠️ JSONの書き込み中にエラーが発生: {e}")

def load_from_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            print("⚠️ 想定外のデータ形式でした（配列ではありません）。表示できるデータがありません。")
            return []
        
        if len(data) == 0:
            print("表示できるデータがありません。")
            return []
        
        print(f"✅️ JSONから{len(data)}件のデータを読み込みました。")
        return data
    
    except FileNotFoundError:
        print(f"⚠️ ファイルが見つかりません： {os.path.relpath(filepath, BASE_DIR)}")
        print("表示できるデータがありません。")
        return []
    except json.JSONDecodeError as e:
        print(f"⚠️ 読み込み中にエラーが発生しました（JSONの形式が壊れています）: {e}")
        print("表示できるデータがありません。")
        return []
    except Exception as e:
        print(f"⚠️ 読み込み中にエラーが発生しました: {e}")
        print("表示できるデータがありません。")
        return []
    
def next_id(records):
    if not records: return 1
    return max(row.get("id", 0) for row in records) + 1

def add_note(filepath, title, body):
    if title is None or title.strip() == "":
        print("⚠️ タイトルが空です。追加を中止します。")
        return
    data = load_from_json(filepath)
    new_id = next_id(data)
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    record = {"id": new_id, "title": title.strip(), "body": body or "",
              "created_at": now, "updated_at": now}
    data.append(record)
    save_to_json(data, filepath)
    print(f"✅️ 追加しました: [#{new_id}] {record['title']}")

def list_notes(filepath):
    data = load_from_json(filepath)
    if not data:
        print("表示できるデータがありません。")
        return
    print(f"=== メモ一覧({len(data)}件) ===")
    for row in data:
        created = row.get("created_at", "").replace("T", " ")[:16]
        print(f"[#{row.get('id')}] {row.get('title', '')} {created}")

def delete_note(filepath, target_id):
    data = load_from_json(filepath)
    before = len(data)
    new_list = [row for row in data if row.get("id") != target_id]
    difference = before - len(new_list)
    save_to_json(new_list, filepath)

    if difference > 0:
        print(f"🗑️ {difference}件のデータを削除しました: (#{target_id})")
    else:
        print(f"⚠️ 該当するIDが見つかりません: {target_id}")

def parse_args():
    parser = argparse.ArgumentParser(description="JSONメモ帳（CLI）")
    parser.add_argument("--add", help="追加するメモのタイトル")
    parser.add_argument("--body", help="メモ本文（任意）")
    parser.add_argument("--list", action="store_true", help="一覧表示")
    parser.add_argument("--delete", type=int, help="削除するメモのID")
    return parser.parse_args()

def main():
    args = parse_args()
    if args.add:
        add_note(MEMOS_PATH, args.add, args.body)
        return
    if args.list:
        list_notes(MEMOS_PATH)
        return
    if args.delete is not None:
        delete_note(MEMOS_PATH, args.delete)
        return
    print("使い方:")
    print("  追加:  python3 test36.py --add 'タイトル' --body '本文'")
    print("  一覧:  python3 test36.py --list")
    print("  削除:  python3 test36.py --delete 3")

if __name__ == "__main__":
    main()