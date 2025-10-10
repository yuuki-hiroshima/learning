# お題1：数値ジャッジ（符号✕偶奇）

n = 0

if n % 2 == 0:
    if n > 0:
        print("positive even")
    elif n == 0:
        print("zero even")
    else:
        print("negative even")
else:
    if n > 0:
        print("positive odd")
    else:
        print("negative odd")