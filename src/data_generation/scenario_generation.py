import os
import random

from ..conf import SCENARIOS_DATA_PATH, PERSONAS_DATA_PATH, COMMON_NORMS, GOAL_TYPES
from ..utils import load_jsonl, write_jsonl, ask_model_in_parallel
from .prompts import SCENARIO_CONSTRUCTION_PROMPT, GOAL_CONSTRUCTION_PROMPT, SCENARIO_VARIATIONS_CONSTRUCTION_PROMPT
from ..language_models import AOAI, MODEL_DICT


SAMPLES = 100

def scenario_construct():
    aoai = AOAI(model=MODEL_DICT['gpt4o'])
    persona_information = load_jsonl(
        os.path.join(PERSONAS_DATA_PATH, "personas.jsonl")
    )
    
    chosen_personas = []
    scenarios = []

    for _ in range(SAMPLES):
        delegate_idx, human_idx = random.sample(
            range(0, len(persona_information) - 1), k=2
        )
        chosen_personas.append([delegate_idx, human_idx])
        scenarios.append(
            SCENARIO_CONSTRUCTION_PROMPT.format(
                delegate_information_dict=persona_information[delegate_idx],
                human_information_dict=persona_information[human_idx]
            )
        )

    scenarios_result, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=scenarios,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.7,
    )

    write_jsonl(scenarios_result, os.path.join(SCENARIOS_DATA_PATH, "stage_1.jsonl"))

    goal_user_messages = []
    for idx in range(SAMPLES):
        goal_user_messages.append(
            GOAL_CONSTRUCTION_PROMPT.format(
                scenario=scenarios_result[idx],
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

    write_jsonl(goal_construction_results, os.path.join(SCENARIOS_DATA_PATH, "stage_2.jsonl"))

    mixed_results = [
        scenario | goal
        for scenario, goal in zip(scenarios_result, goal_construction_results)
    ]

    scenario_variation_user_messages = []
    for idx in range(SAMPLES):
        scenario_variation_user_messages.append(
            SCENARIO_VARIATIONS_CONSTRUCTION_PROMPT.format(
                scenario=mixed_results[idx],
            )
        )

    responses, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=scenario_variation_user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.7,
    )
    
    for idx in range(SAMPLES):
        responses[idx]["delegate_idx"] = chosen_personas[idx][0]
        responses[idx]["human_idx"] = chosen_personas[idx][1]

    write_jsonl(responses, os.path.join(SCENARIOS_DATA_PATH, "scenarios.jsonl"))

if __name__ == "__main__":
    scenario_construct()