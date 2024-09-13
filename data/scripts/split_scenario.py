import json

def load_jsonl(fpath: str):
    """
    Load a jsonl file into a list of dictionaries.

    Args:
        fpath (str): Path to the jsonl file.
    
    Returns:
        list: List of dictionaries.
    """
    with open(fpath, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

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

def split_scenario():
    data = load_jsonl("data/scripts/scripts.jsonl")
    passive_data = []
    proactive_data = []
    for script in data:
        if script["scenario"]["manner"] == "passive":
            passive_data.append(script)
        else:
            proactive_data.append(script)

    write_jsonl(passive_data, "data/scripts/passive_scripts.jsonl")
    write_jsonl(proactive_data, "data/scripts/proactive_scripts.jsonl")

if __name__ == "__main__":
    split_scenario()