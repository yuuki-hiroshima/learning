# サブコマンドの体験

import argparse

def add_note_command(args):
    print(f"✅️ add コマンド実行: title={args.title}, body={args.body}")

def list_notes_command(args):
    print("📋️ list コマンド実行（メモ一覧を表示）")

def update_note_command(args):
    print(f"✏️ update コマンド実行: id={args.id}, title={args.title}, body={args.body}")

def delete_note_command(args):
    print(f"🗑️ delete コマンド実行: id={args.id}")

def parse_args():
    parser = argparse.ArgumentParser(description="JSONメモアプリ（サブコマンド版）")

    # --- サブコマンド（add, list, update, delete）を登録 ---
    subparsers = parser.add_subparsers(dest="command", help="利用できるコマンド")

    # ------ add コマンドの説明エリア ------
    parser_add = subparsers.add_parser("add", help="メモを追加")
    parser_add.add_argument("title", help="タイトルを指定")
    parser_add.add_argument("--body", help="本文を指定")
    parser_add.set_defaults(func=add_note_command)

    # ------ list コマンドの説明エリア ------
    parser_list = subparsers.add_parser("list", help="メモ一覧を表示")
    parser_list.set_defaults(func=list_notes_command)

    # ------ update コマンドの説明エリア ------
    parser_update = subparsers.add_parser("update", help="メモを更新")
    parser_update.add_argument("id", type=int, help="更新対象のID")
    parser_update.add_argument("--title", help="新しいタイトル")
    parser_update.add_argument("--body", help="新しい本文")
    parser_update.set_defaults(func=update_note_command)

    # ------ delete コマンドの説明エリア ------
    parser_delete = subparsers.add_parser("delete", help="メモを削除")
    parser_delete.add_argument("id", type=int, help="削除対象のID")
    parser_delete.set_defaults(func=delete_note_command)

    return parser.parse_args()

def main():
    args = parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        print("❗️ コマンドを指定してください（add/list/update/delete）")

if __name__ == "__main__":
    main()