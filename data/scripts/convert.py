import json
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from src.utils import write_jsonl

def convert():
    data = json.load(open("data/scripts/handwritten.json", "r", encoding="utf-8"))
    write_jsonl(data, "data/scripts/handwritten.jsonl")

if __name__ == "__main__":
    convert()