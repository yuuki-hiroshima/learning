def greet():
    print("Hello from greet()!")

print("この行は import しても実行されます。")

if __name__ == "__main__":
    print("✅️ この行は、直接実行されたときだけ表示されます。")
    greet()