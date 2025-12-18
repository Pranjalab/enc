import os

def main():
    print("Running Lifecycle Test Project")
    print(f"CWD: {os.getcwd()}")
    with open("output.log", "w") as f:
        f.write("Lifecycle Test Success\n")
    print("Created output.log")

if __name__ == "__main__":
    main()
