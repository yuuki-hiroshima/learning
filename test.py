# お題２：３段階の評価プログラム

point = 100

if point < 0 or point > 100:
    print("Out of range!")
elif point < 50:
    print("Try again!")
elif point >= 50 and point < 80:
    print("Good!")
else:
    print("Excellent!")

# if point <= 100:
#     print("Excellent!")
# elif point >= 50 and point < 80:
#     print("Good!")
# elif point < 50:
#     print("Try again!")
# else:
#     print("Out of range")