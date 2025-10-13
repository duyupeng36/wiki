import os

def main():
    os.system("gitbook build")
    os.system("cd _book && python3t -m http.server 4000")

if __name__ == "__main__":
    main()
