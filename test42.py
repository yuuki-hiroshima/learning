# load_notes(filepath)JSONファイルを読み込む（なければ空リストを返す）
# save_notes(data, filepath)JSONファイルを保存する
# next_id(data)新しいIDを発行する
# add_note()新しいメモを作成する（Create）
# list_notes()登録されたメモを一覧表示する（Read）
# update_note()指定IDのメモを更新する（Update）
# delete_note()指定IDのメモを削除する（Delete）
# parse_args()argparseでコマンド引数を解析する
# main()全体の流れを制御する（分岐）

import os
import json
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NOTES_PATH = os.path.join(BASE_DIR, "data", "notes.json")

def load_notes(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data:
                print("データはありません。")
                return []
            return data
    except FileNotFoundError:
        print("データはありません。")
        return []
    except json.JSONDecodeError as e:
        print(f"JSONファイルが破損しています: {e}")
        return []
    except Exception as e:
        print(f"データ読み込み中に予期せぬエラーが起きました: {e}")
        return []

def save_notes(data, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            print("JSONファイルに保存しました。")
    except Exception as e:
        print(f"JSONファイル保存中に予期せぬエラーが起きました: {e}")

def next_id(data):
    if not data: return 1
    return max(row.get("id", 0) for row in data) + 1

# 【Create】データを作る
def add_note(data):
    try:
        while True:
            new_id = next_id(data)
            title = input("タイトルを入力してください: ").strip()
            if not title:
                print("タイトルは必須です。")
                continue
            body = input("本文を入力してください: ").strip()
            if not body:
                body = "（本文なし）"
            now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

            note = {
                "id": new_id,
                "title": title,
                "body": body,
                "created_at": now
            }
            return note
    except Exception as e:
        print(f"データ入力中に予期せぬエラーが起きました: {e}")

# 【Read】データを見る
def list_notes(data):
    if not data:
        print("一覧表示できるデータがありません。")
        return
    print(f"===== メモ一覧{len(data)}件 =====")
    for row in data:
        created = row.get("created_at", "").replace("T", " ")[:16] # replaceで「T」を空白に変更し、[:16]で先頭から16文字分だけを取り出す = 秒数は取り出さない。
        print(f"[#{row.get('id')}] {row.get('title', '')} {created}")

# 【Update】データを更新する
def update_note(data):
    try:
        if not data:
            print("更新対象のデータがありません。")
            return []
        
        target_id = input("IDを入力してください: ").strip()
        try:
            target_id = int(target_id)
        except (TypeError, ValueError):
            print("IDは数字で入力してください。")
            return []
        
        # 該当IDを探す
        found_index = None  # この書き方が堅牢（理由は if found_index is None を使うため）
        for i, row in enumerate(data):  # enumerateでリストのインデックス番号 + 辞書データを取り出している。
            if row.get("id") == target_id:
                found_index = i
                break   # この下にelse:を書くとforループが1周しか機能しなくなる。2つ目以降のID検索ができない。
        
        if found_index is None: # forループが終わった上で、found_indexがNoneのときの処理をする。
            print(f"該当のIDがありません: {target_id}")
            return []
        
        # 既存のデータを取得
        current = data[found_index]

        new_title = input("新しいタイトルを入力(変更しない場合は空白): ").strip()
        new_body = input("新しい本文を入力(変更しない場合は空白): ").strip()

        # 据え置き処理   
        if new_title == "":
            new_title = current.get("title", "")
        if new_body == "":
            new_body = current.get("body", "")

        update_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # 置き換える新レコードを作成
        updated = {
                    "id": current.get("id"),
                    "title": new_title,
                    "body": new_body,
                    "created_at": current.get("created_at", ""),
                    "updated_at": update_time
        }
                
        # ここで置き換え
        data[found_index] = updated

        print(f"更新しました（#{target_id})")      
        return data   # ← 配列全体を返す
            
    except Exception as e:
        print(f"更新中に予期せぬエラーが起きました: {e}")
        return []
    
# 【Delete】データを削除する
def delete_note(data, filepath):
    try:
        if not data:
            print("削除できるデータがありません。")
            return
        
        target_id = input("IDを入力してください: ").strip()
        try:
            target_id = int(target_id)
        except (TypeError, ValueError):
            print("IDは数字で入力してください。")
            return
        
        before = len(data)
        new_data = [row for row in data if row.get("id") != target_id]
        after = len(new_data)

        if before == after:
            print(f"該当のIDはありません: {target_id}")
            return
        
        save_notes(new_data, filepath)
        print(f"ID {target_id} のメモを削除しました。現在の件数: {after}")
    
    except Exception as e:
        print(f"データ削除中に予期せぬエラーが起きました: {e}")
        return

def main():
    while True:
        print("\n=== メモアプリ ===")
        print("1. 追加")
        print("2. 一覧表示")
        print("3. 更新")
        print("4. 削除")
        print("5. 終了")
        choice = input("番号を選んでください: ").strip()

        try:
            num = int(choice)

            if num == 1:
                data = load_notes(NOTES_PATH)
                note = add_note(data)
                if not note:
                    print("登録できませんでした。")
                    continue
                data.append(note)
                save_notes(data, NOTES_PATH)

            elif num == 2:
                data = load_notes(NOTES_PATH)
                list_notes(data)

            elif num == 3:
                data = load_notes(NOTES_PATH)
                update_data = update_note(data)
                if not update_data:
                    print("更新する情報はありませんでした。")
                    continue
                save_notes(update_data, NOTES_PATH)
                print("更新が完了しました。")

            elif num == 4:
                data = load_notes(NOTES_PATH)
                delete_note(data, NOTES_PATH)

            elif num == 5:
                print("プログラムを終了します。")
                break
            else:
                print("1〜5の番号を入力してください。")
        except (TypeError, ValueError):
            print("テキストは対象外です。1〜5の番号を入力してください。")
            continue

if __name__ == "__main__":
    main()