import os
import json
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_PATH = os.path.join(BASE_DIR, "data", "notes.json")

def load_notes(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = json.load(f)
            if not content:
                return []
            return content
    except FileNotFoundError:
        print("ファイルがありません。")
        return []
    except json.JSONDecodeError as e:
        print(f"ファイルが破損しています: {e}")
        return []
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        return []
    
def save_notes(data, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            print("JSONファイルの保存に成功しました。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")

def next_id(data): # わからなかったため、test36.pyからコピー
    if not data: return 1
    return max(row.get("id",0) for row in data) + 1

def add_note(data): # test36.pyを参考
    while True:
        try:
            new_id = next_id(data)
            title = input("タイトルを入力してください: ").strip()
            body = input("本文を入力してください: ").strip()
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            
            if title == "":
                print("タイトルを入力してください。")
                continue
            
            if body == "":
                body = "本文なし"

            note = {
                "id": new_id,
                "title": title,
                "body": body,
                "created_at": now
                 }
            return note
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            print("登録を終了します。")
            return None

def list_notes(filepath): # わからなかったため、test36.pyをコピー
    data = load_notes(filepath)
    if not data:
        print("表示できるデータがありません。")
        return
    print(f"=== メモ一覧({len(data)}件) ===")
    for row in data:
        created = row.get("created_at", "").replace("T", " ")[:16]
        print(f"[#{row.get('id')}] {row.get('title', '')} {created}")

def input_notes(): # 最初にデータを書き込む用/もう使わない
    data = [
        {
            "id": 1,
            "title": "買い物リスト",
            "body": "卵・牛乳・パン",
            "created_at": "2025-11-01T15:23:00"
        },
        {
            "id": 2,
            "title": "勉強メモ",
            "body": "os.path.dirnameの理解完了！",
            "created_at": "2025-11-01T15:25:42"
        }
    ]
        
    return data

def main():
    data = load_notes(NOTES_PATH)
    list_notes(NOTES_PATH)
    note = add_note(data)
    if not note:
        print("登録ができませんでした。")
        return
    
    data.append(note)
    save_notes(data, NOTES_PATH)

if __name__ == "__main__":
    main()