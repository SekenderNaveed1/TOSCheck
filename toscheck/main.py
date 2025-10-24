import sys
from toscheck.analyzer import analyze_tos

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_tos_file>")
        return

    with open(sys.argv[1], "r") as f:
        text = f.read()

    result = analyze_tos(text)
    print("\n=== Results ===\n")
    print(result)

if __name__ == "__main__":
    main()
