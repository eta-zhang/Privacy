import os
import random

from .constants import COMMON_NORMS, GOAL_TYPES
from ..conf import SCENARIOS_DATA_PATH, PERSONAS_DATA_PATH
from ..utils import load_jsonl, write_jsonl, ask_model_in_parallel
from .prompts import IFC_CONSTRUCTION_PROMPT, GOAL_CONSTRUCTION_PROMPT
from ..language_models import AOAI, MODEL_DICT


SAMPLES = 100

def ifc_construct():
    aoai = AOAI(model=MODEL_DICT['gpt4o'])
    persona_information = load_jsonl(
        os.path.join(PERSONAS_DATA_PATH, "personas.jsonl")
    )
    
    chosen_personas = []
    ifc_user_messages = []

    for _ in range(SAMPLES):
        delegate_idx, human_idx = random.sample(
            range(0, len(persona_information) - 1), k=2
        )
        chosen_personas.append([delegate_idx, human_idx])
        ifc_user_messages.append(
            IFC_CONSTRUCTION_PROMPT.format(
                delegate_information_dict=persona_information[delegate_idx],
                human_information_dict=persona_information[human_idx]
            )
        )

    ifc_construction_results, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=ifc_user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.7,
    )

    goal_user_messages = []
    for idx in range(SAMPLES):
        goal_user_messages.append(
            GOAL_CONSTRUCTION_PROMPT.format(
                ifc=ifc_construction_results[idx],
                common_norms=COMMON_NORMS,
                goal_types=GOAL_TYPES
            )
        )

    goal_construction_results, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=goal_user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.7,
    )

    responses = [
        ifc | goal
        for ifc, goal in zip(ifc_construction_results, goal_construction_results)
    ]
    
    for idx in range(SAMPLES):
        responses[idx]["delegate_idx"] = chosen_personas[idx][0]
        responses[idx]["human_idx"] = chosen_personas[idx][1]

    write_jsonl(responses, os.path.join(SCENARIOS_DATA_PATH, "ifc.jsonl"))

if __name__ == "__main__":
    ifc_construct()