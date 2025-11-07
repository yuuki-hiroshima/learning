# argparse学習のため、test42.pyからロジックをコピー
# main部分にargparseを追加
# コマンドラインと対話型メニュー入力の両方が使える仕様になった

import os
import json
import datetime
import argparse

# 入力の制限
MAX_TITLE_LEN = 100
MAX_BODY_LEN = 1000

# 【追加】コマンド引数を定義し、読み取る
def parse_args():
    formatter = argparse.RawTextHelpFormatter #ヘルプの見た目を整えるための設定（改行をそのまま出す）
    
    parser = argparse.ArgumentParser(
        description="JSONメモアプリ(CLI版)\nコマンド引数で追加・一覧・更新・削除ができます。",
        epilog=(
            "【使い方サンプル】\n"
            "  ➊ 追加（タイトルのみ）\n"
            "     python3 test43.py --add \"買い物\"\n"
            "\n"
            "  ➋ 追加（タイトル＋本文）\n"
            "     python3 test43.py --add \"買い物\" --body \"牛乳とパン\"\n"
            "\n"
            "  ➌ 一覧表示\n"
            "     python3 test43.py --list\n"
            "\n"
            "  ➍ 更新（ID 3 を変更）\n"
            "     python3 test43.py --update 3 --title \"予定変更\" --newbody \"牛乳→豆乳に変更\"\n"
            "\n"
            "  ➎ 削除（ID 2 を削除）\n"
            "     python3 test43.py --delete 2\n"
            "\n"
            "  ➏ 引数なしで従来メニュー\n"
            "     python3 test43.py\n"
        ),
        formatter_class = formatter # 改行付きのヘルプをそのまま表示する
    )

    # 操作スイッチは相互排他（どれか1つ）オプションはセットで使うのでグループ外
    group = parser.add_mutually_exclusive_group()

    # 操作スイッチ（どれか1つを選ぶ想定）
    group.add_argument("--add", help="新しいメモを追加（タイトルを指定）")
    group.add_argument("--list", action="store_true", help="メモ一覧を表示")
    group.add_argument("--update", type=int, help="指定IDのメモを更新")
    group.add_argument("--delete", type=int, help="指定IDのメモを削除")

    # オプション（補助項目）
    parser.add_argument("--body", help="本文（--add時の補助）")
    parser.add_argument("--title", help="新しいタイトル（--update時の補助）")
    parser.add_argument("--newbody", help="新しい本文（--update時の補助）")

    return parser.parse_args()

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
    """メモデータをJSONファイルに保存する（エラー時は内容を説明的に出力）"""
    try:
        dirpath = os.path.dirname(filepath)
        os.makedirs(dirpath, exist_ok=True)
        tmp_path = os.path.join(dirpath, ".notes.json.tmp")

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        os.replace(tmp_path, filepath)

        print("JSONファイルに保存しました。")
    except PermissionError:
        print("保存に失敗しました:書き込み権限がありません。")
        print("対処方法:フォルダのアクセス権限を確認してください。")
    except FileNotFoundError:
        print("保存に失敗しました:保存先フォルダが存在しません。")
        print("対処:フォルダ構成を確認してください（data/ フォルダなど）。")
    except json.JSONDecodeError:
        print("保存に失敗しました:JSON形式の変換中にエラーが発生しました。")
        print("対処:特殊文字や構造の不整合を確認してください。")
    except Exception as e:
        print("保存処理で予期せぬエラーが発生しました。")
        print(f"詳細情報: {type(e).__name__} - {e}")
        print("対処:一度プログラムを再起動し、再度お試しください。")
    finally:
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

def next_id(data):
    if not data: return 1
    return max(row.get("id", 0) for row in data) + 1

# 【Create】データを作る
def add_note(data):
    try:
        while True:
            new_id = next_id(data)

            title_raw = input("タイトルを入力してください: ").strip()
            title = validate_title(title_raw)
            if title is None:
                continue

            body_raw = input("本文を入力してください: ").strip()
            body = validate_body(body_raw)
            if body is None:
                continue

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
        print("まずは `--add \"タイトル\" --body \"本文\"` で1件登録してみましょう。")
        return
    print(f"===== メモ一覧{len(data)}件 =====")
    for row in data:
        created = row.get("created_at", "").replace("T", " ")[:16] # replaceで「T」を空白に変更し、[:16]で先頭から16文字分だけを取り出す = 秒数は取り出さない。
        print(f"[#{row.get('id')}] {row.get('title', '')} {created}")

# 【Update】データを更新する
# ==============================
# 【変更】update_note：責務を「更新のみ」に絞る
# - 成功 True / 失敗 False を返す
# - データは「その場で書き換え」る（保存はしない）
# - 成功メッセージは出さず、エラー/警告だけ出す（main側で成功メッセージを出すため）
# ==============================
def update_note(data):
    try:
        if not data:
            print("更新対象のデータがありません。")
            return False
        
        target_id = input("IDを入力してください: ").strip()
        try:
            target_id = int(target_id)
        except (TypeError, ValueError):
            print("IDは数字で入力してください。")
            return False
        
        # 該当IDを探す
        found_index = None  # この書き方が堅牢（理由は if found_index is None を使うため）
        for i, row in enumerate(data):  # enumerateでリストのインデックス番号 + 辞書データを取り出している。
            if row.get("id") == target_id:
                found_index = i
                break   # この下にelse:を書くとforループが1周しか機能しなくなる。2つ目以降のID検索ができない。
        
        if found_index is None: # forループが終わった上で、found_indexがNoneのときの処理をする。
            print(f"該当のIDがありません: {target_id}")
            return False
        
        # 既存のデータを取得
        current = data[found_index]

        new_title = input("新しいタイトルを入力(変更しない場合は空白): ").strip()
        new_body = input("新しい本文を入力(変更しない場合は空白): ").strip()

        if new_title == "" and new_body == "":
            print("入力が空だったため、変更は行いませんでした。")
            return False

        # 据え置き処理   
        if new_title == "":
            new_title = current.get("title", "")
        if new_body == "":
            new_body = current.get("body", "")

        # その場で書き換え（置き換え dict を作らず、既存を更新）
        current['title'] = new_title
        current['body'] = new_body
        current['updated_at'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        # 成功したことだけを返す
        return True
    
    except Exception as e:
        print(f"更新中に予期せぬエラーが起きました: {e}")
        return False

        # # 置き換える新レコードを作成
        # updated = {
        #             "id": current.get("id"),
        #             "title": new_title,
        #             "body": new_body,
        #             "created_at": current.get("created_at", ""),
        #             "updated_at": update_time
        # }
                
        # # ここで置き換え
        # data[found_index] = updated

        # print(f"更新しました（#{target_id})")      
        # return data   # ← 配列全体を返す
        
    
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
    
# 【追加】タイトル検証：空白のみ/長すぎ/改行を防ぐ
def validate_title(raw):
    title = (raw or "").strip()
    if title == "":
        error("タイトルは必須です。", "空白以外の文字を入れてください。例: --add \"買い物\"")
        return None
    if "\n" in title:
        title = title.replace("\n", " ")
    if len(title) > MAX_TITLE_LEN:
        error(f"タイトルが長すぎます({len(title)}文字)", f"上限は {MAX_TITLE_LEN} 文字です。短くしてください。")
        return None
    return title

# 【追加】本文検証：長すぎ/改行はそのまま許容（複数行OK）、未指定は既定値
def validate_body(raw):
    if raw is None:
        return "(本文なし)"
    body = str(raw).strip()
    if body == "":
        return "(本文なし)"
    if len(body) > MAX_BODY_LEN:
        error(f"本文が長すぎます({len(body)}文字)", f"上限は {MAX_BODY_LEN} 文字です。要点を短くまとめてください。")
        return None
    return body

# 【追加】共通のエラー表示（短い案内つき）
def error(msg, hint=None):
    print(f"{msg}")
    if hint:
        print(f"対処: {hint}")

def main():
    args = parse_args() # 始めにコマンド引数を読み込み、中身が有れば実行。なければ従来のメニューへ進む

    if args.add: # ①　追加
        data = load_notes(NOTES_PATH)

        # add_noteは今のインタラクティブ入力版のままでも可。
        # ここでは「タイトルと本文を事前指定できるパス」を用意する書き方がきれい。
        
        title = validate_title(args.add)
        if title is None:
            return
        body = validate_body(args.body)
        if body is None:
            return
        
        # 既存の add_note(data) を使う場合は、入力を代入してから呼ぶ形にするか、
        # ここで直接レコードを組み立ててもOK。
        new_id = next_id(data)
        now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        note = {
            "id": new_id,
            "title": title,
            "body": (body or "（本文なし）"),
            "created_at": now
        }
        data.append(note)
        save_notes(data, NOTES_PATH)
        print("登録が完了しました。")
        return
    
    if args.list: # ② 一覧
        data = load_notes(NOTES_PATH)
        list_notes(data)
        return
    
    if args.update is not None: # ③ 更新（--update でIDは必須。--title /--newbody は任意）
        
        if (args.title is None) and (args.newbody is None):
            print("変更指定がないため、更新は行いませんでした。")
            return

        data = load_notes(NOTES_PATH)
        target_id = args.update

        # 既存の update_note(data) は対話入力前提なので、
        # 「引数から来た値で置き換えるモード」を簡易追加するやり方が分かりやすい。
        # ここでは最小で、main側で置き換えてしまう例を使う。
        found_index = None
        for i, row in enumerate(data):
            if row.get("id") == target_id:
                found_index = i
                break
        
        if found_index is None:
            error(f"該当するIDはありません: {target_id}",
                  hint="まず `--list` でIDを確認してください。新規作成は `--add` です。")
            return
        
        current = data[found_index]

        if args.title is not None:
            checked = validate_title(args.title)
            if checked is None:
                return
            new_title = checked
        else:
            new_title = current.get("title", "")
        
        if args.newbody is not None:
            checked = validate_body(args.newbody)
            if checked is None:
                return
            new_body = checked
        else:
            new_body = current.get("body", "")

        
        current["title"] = new_title
        current["body"] = new_body
        current["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

        save_notes(data, NOTES_PATH)
        print(f"更新が完了しました（#{target_id}）。")
        return
    
    if args.delete is not None: # ④ 削除
        data = load_notes(NOTES_PATH)
        before = len(data)
        new_list = [row for row in data if row.get("id") != args.delete]
        after = len(new_list)
        if before == after:
            error(f"該当のIDがありません: {args.delete}",
                hint="`--list` で存在するIDを確認してから再実行してください。")
            return
        
        save_notes(new_list, NOTES_PATH)
        print(f"削除しました（#{args.delete}）。現在の件数: {after}")
        return

    # --- 引数が何も無いときは、従来のメニューへフォールバック ---
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
                data = load_notes(NOTES_PATH) # 元のデータを読み込み
                changed = update_note(data)   # 読み込んだデータを更新。TrueかFalseを返す。
                if not changed:               # Trueなら先へ進む。Falseならやり直し
                    continue
                save_notes(data, NOTES_PATH)  # update_noteで更新されたデータを保存。更新データはreturnされなくても、関数が機能した時点で内部的に更新されている。
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