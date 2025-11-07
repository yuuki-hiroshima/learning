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