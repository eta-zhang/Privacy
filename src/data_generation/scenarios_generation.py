import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from conf import SCENARIOS_DATA_PATH
from utils import write_jsonl, ask_model_in_parallel
from prompts import IFC_CONSTRUCTION_PROMPT
from language_models import AOAI


SAMPLES = 20

def ifc_construct():
    aoai = AOAI(model="gpt-4o-20240513")
    user_messages = [IFC_CONSTRUCTION_PROMPT] * SAMPLES
    reponses, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.9,
        presence_penalty=0.5,
        frequency_penalty=0.5
    )
    
    write_jsonl(reponses, os.path.join(SCENARIOS_DATA_PATH, "ifc.jsonl"))

if __name__ == "__main__":
    ifc_construct()