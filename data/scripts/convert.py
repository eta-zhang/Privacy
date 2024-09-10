import json
def write_jsonl(data: list, fpath: str):
    """
    Write a list of dictionaries to a jsonl file.
    
    Args:
        data (list): List of dictionaries to write to file.
        fpath (str): Path to write the file.
    """
    with open(fpath, "w+", encoding="utf-8") as f:
        for line in data:
            info = json.dumps(line, ensure_ascii=False)
            f.write(info + "\n")

def convert():
    data = json.load(open("data/scripts/user_case_study.json", "r", encoding="utf-8"))
    write_jsonl(data, "data/scripts/user_case_study.jsonl")

if __name__ == "__main__":
    convert()