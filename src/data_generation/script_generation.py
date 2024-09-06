import os

from ..conf import SCENARIOS_DATA_PATH, PERSONAS_DATA_PATH, SCRIPTS_DATA_PATH
from ..utils import load_jsonl, write_jsonl, ask_model_in_parallel
from .prompts import SCRIPT_CONSTRUCTION_PROMPT
from .constants import COMMON_NORMS
from ..language_models import AOAI, MODEL_DICT

def ifc_construct():
    aoai = AOAI(model=MODEL_DICT['gpt4o'])
    persona_information = load_jsonl(
        os.path.join(PERSONAS_DATA_PATH, "personas.jsonl")
    )

    scenario_information = load_jsonl(
        os.path.join(SCENARIOS_DATA_PATH, "ifc.jsonl")
    )
    
    samples = len(scenario_information)
    user_messages = [
        SCRIPT_CONSTRUCTION_PROMPT.format(
            delegate_information_dict=persona_information[scenario["delegate_idx"]],
            human_information_dict=persona_information[scenario["human_idx"]],
            ifc=scenario,
            common_norms=COMMON_NORMS,
        )
        for scenario in scenario_information
    ]

    reponses, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * samples,
        max_workers=4,
        mode="chat",
        temperature=0.9,
    )
    
    for idx in range(samples):
        reponses[idx]["delegate_info"] = (
            persona_information[scenario_information[idx]["delegate_idx"]]
        )
        reponses[idx]["human_info"] = (
            persona_information[scenario_information[idx]["human_idx"]]
        )
        reponses[idx]["ifc"] = scenario_information[idx]

    write_jsonl(reponses, os.path.join(SCRIPTS_DATA_PATH, "scripts.jsonl"))

if __name__ == "__main__":
    ifc_construct()