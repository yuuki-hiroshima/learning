def A():
    return "データA"

def B(x):
    return x + " → B処理済"

def C(y):
    return y + " → C処理済"

def D(z):
    print("最終結果:", z)

test_a = A()
test_b = B(test_a)
test_c = C(test_b)
D(test_c)