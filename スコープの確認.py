# スコープの確認（returnしなくてもリストや辞書データは共有される）

# step1
number = [1, 2, 3]
alias = number
alias[0] = 999
print(number)
print(alias)

# step2
numbers = [1, 2, 3]
copy_list = numbers.copy()
copy_list[0] = 999
print(numbers)
print(copy_list)

# step3
import copy
data = [{"id": 1, "title": "買い物"}]
copy_data = data.copy()                 # 外側のリストをコピーしているだけ。辞書は data と共有している。
deep_copy_data = copy.deepcopy(data)    # リスト内の辞書までコピーしている。
copy_data[0]["title"] = "旅行"          # 辞書は data と共有しているため、copy_data としても data の内容も変更になる。
print(data)
print(copy_data)
print(deep_copy_data)

# リストや辞書データではないため、共有にはならない。
n = 1
i = n
i += 1

print(n, i)