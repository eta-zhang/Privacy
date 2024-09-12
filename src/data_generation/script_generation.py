import os
import random

from ..conf import (
    SCENARIOS_DATA_PATH, 
    PERSONAS_DATA_PATH, 
    SCRIPTS_DATA_PATH, 
    COMMON_NORMS, 
    USER_PERSONALITY
)
from ..utils import load_jsonl, write_jsonl, ask_model_in_parallel
from .prompts import SCRIPT_CONSTRUCTION_PROMPT
from ..language_models import AOAI, MODEL_DICT

def script_construct():
    aoai = AOAI(model=MODEL_DICT['gpt4o'])
    persona_information = load_jsonl(
        os.path.join(PERSONAS_DATA_PATH, "personas.jsonl")
    )

    scenario_information_list = load_jsonl(
        os.path.join(SCENARIOS_DATA_PATH, "scenarios.jsonl")
    )

    user_messages = []

    for scenario_information in scenario_information_list:
        scenario = {
            "social_relation": scenario_information["social_relation"],
            "scenario": scenario_information["scenario"],
            "goal": scenario_information["goal"],
            "manner": scenario_information["manner"],
            "extra_privacy": scenario_information["extra_privacy"],
        }
        user_messages.append(
            SCRIPT_CONSTRUCTION_PROMPT.format(
                human_information_dict=persona_information[scenario_information["human_idx"]],
                scenario=scenario,
                common_norms=COMMON_NORMS,
            )
        )
    
    samples = len(user_messages)

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
    
    scripts = []
    for idx in range(samples):
        script = reponses[idx]
        scenario = scenario_information_list[idx]
        script["delegate_info"] = persona_information[scenario["delegate_idx"]]
        script["human_info"] = persona_information[scenario["human_idx"]]
        script["scenario"] = scenario
        script["user_preferences"] = random.choice(USER_PERSONALITY)
        del scenario["human_idx"]
        del scenario["delegate_idx"]
        scripts.append(script)

    write_jsonl(scripts, os.path.join(SCRIPTS_DATA_PATH, "scripts.jsonl"))

if __name__ == "__main__":
    script_construct()