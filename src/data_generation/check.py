from ..utils import load_jsonl

def check():
    data = load_jsonl(r"C:\Users\v-zhiyzhang\code\Privacy\data\personas\personas.jsonl")
    for idx, item in enumerate(data):
        if len(list(item.keys())) != 52:
            print(idx, len(list(item.keys())))


if __name__ == "__main__":
    check()