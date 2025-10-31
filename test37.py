# 🔹 要件

# 関数①：get_numbers()
# 	•	ユーザーから2つの数値を入力して受け取る。
# 	•	数値変換に失敗したら、警告を出して再入力させる。
# 	•	入力が完了したら、2つの数値をタプルで返す。
# 関数②：calculate_results(x, y)
# 	•	受け取った2つの数を使って、以下を計算する：
# 	•	合計値
# 	•	平均値
# 	•	差（大きい方 − 小さい方）
# 	•	辞書型で結果を返す
# 関数③：show_summary(result)
# 	•	result 辞書を受け取って、結果を整形して出力する。
# メイン処理：main()
# 	•	以下の順で動作する：
# 	1.	get_numbers() を呼び出して2つの数を取得する
# 	2.	その値を calculate_results() に渡して計算する
# 	3.	結果を show_summary() に渡して出力する

import os
import json
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CAL_PATH = os.path.join(BASE_DIR, "data", "calculate.json")

def save_to_json(results, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"JSONへ保存しました: {os.path.relpath(filepath, BASE_DIR)}")
    except Exception as e:
        print(f"JSONの書き込み中にエラーが発生: {e}")

def load_to_json(filepath, quiet=False):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            if not quiet:
                print("想定外のデータ形式です。表示できるデータがありません。")
            return []
        
        if len(data) == 0:
            if not quiet:
                print("表示できるデータがありません。")
            return []
        
        return data
    
    except FileNotFoundError:
        if not quiet:
            print(f"ファイルが見つかりません: {os.path.relpath(filepath, BASE_DIR)}")
        return[]
    except json.JSONDecodeError as e:
        if not quiet:
            print(f"読み込み中にエラーが発生: {e}")
        return []
    except Exception as e:
        if not quiet:
            print(f"予期せぬエラーが発生: {e}")
        return[]

def append_result_to_json(result, filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
            with open(filepath, "r", encoding="utf-8") as f:
                data= json.load(f)
            if not isinstance(data, list):
                data = []
        else:
            data = []
    except Exception:
        data = []

    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    item = dict(result)
    item["saved_at"] = now
    data.append(item)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        total =len(data)
        print(f"JSONへ保存しました: {os.path.relpath(filepath, BASE_DIR)}(履歴追加) 現在{total}件")
    except Exception as e:
        print(f"JSONの書き込み中にエラーが発生: {e}")

def calc_median(numbers):
    nums = sorted(numbers)
    num = len(nums)
    mid = num // 2
    if num % 2 == 1:
        return nums[mid]
    else:
        return (nums[mid - 1] + nums[mid]) /2

def get_numbers():
    numbers = []
    print("数字を任意の数だけ入力してください。空のままエンターを押すと計算をします。")
    while True:
        number = input(f"{len(numbers)+1}つ目の数字を入力してください: ").strip()
        if number == "":
            if len(numbers) >= 2:
                return numbers
            print("最低でも2つ以上の数字を入力してください。")
            continue

        try:
            num = float(number)
            if num < 0:
                print("正の数を入力してください。")
                continue

            numbers.append(num)
        except (TypeError, ValueError):
            print("数字を入力してください。")
            continue

def calculate_results(numbers):
    total = sum(numbers)
    count = len(numbers)
    average = total / count
    min_val = min(numbers)
    max_val = max(numbers)
    difference = max_val - min_val
    result = {
        "numbers": numbers,
        "count": count,
        "total": total,
        "average": average,
        "min": min_val,
        "max": max_val,
        "difference": difference,
        "median": calc_median(numbers)
    }
    return result

def count_history(filepath):
    data = load_to_json(filepath,quiet=True)
    return len(data)

def show_summary(result):
    print("=== 計算結果 ===")
    print(f"個数      : {result['count']}")
    print(f"合計      : {result['total']:.2f}")
    print(f"平均      : {result['average']:.2f}")
    print(f"最小      : {result['min']:.2f}")
    print(f"最大      : {result['max']:.2f}")
    print(f"差(最大-最小): {result['difference']:.2f}")
    print(f"中央値    : {result['median']:.2f}")

def reset_history(filepath):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)
        print(f"履歴を空にしました: {os.path.relpath(filepath, BASE_DIR)}")
    except Exception as e:
        print(f"履歴初期化でエラー: {e}")

def main():
    numbers = get_numbers()
    result = calculate_results(numbers)
    show_summary(result)
    append_result_to_json(result, CAL_PATH)
    # reset_history(CAL_PATH)

if __name__ == "__main__":
    main()