import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import random

from conf import SCENARIOS_DATA_PATH, PERSONAS_DATA_PATH
from utils import load_jsonl, write_jsonl, ask_model_in_parallel
from prompts import IFC_CONSTRUCTION_PROMPT
from language_models import AOAI


SAMPLES = 20

def ifc_construct():
    aoai = AOAI(model="gpt-4o-20240513")
    persona_information = load_jsonl(
        os.path.join(PERSONAS_DATA_PATH, "personas.jsonl")
    )
    
    chosen_personas = []
    user_messages = []

    for _ in range(SAMPLES):
        delegate_idx, recipient_idx = random.sample(
            range(0, len(persona_information) - 1), k=2
        )
        chosen_personas.append([delegate_idx, recipient_idx])
        user_messages.append(
            IFC_CONSTRUCTION_PROMPT.format(
                delegate_information_dict=persona_information[delegate_idx],
                recipient_information_dict=persona_information[recipient_idx]
            )
        )

    reponses, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.9,
    )
    
    for idx in range(SAMPLES):
        reponses[idx]["delegate_idx"] = chosen_personas[idx][0]
        reponses[idx]["recipient_idx"] = chosen_personas[idx][1]

    write_jsonl(reponses, os.path.join(SCENARIOS_DATA_PATH, "ifc.jsonl"))

if __name__ == "__main__":
    ifc_construct()