import random

from typing import Callable
from ..language_models import AOAI, MODEL_DICT
from ..utils import write_jsonl, ask_model_in_parallel
from ..conf import PERSONAS_DATA_PATH
from .prompts import PERSONA_CONSTRUCTION_PROMPT, PERSONA_REFINE_PROMPT
from .constants import PERSONA_DESCRIPTIONS, INFORMATION_KEYS, COMMON_NORMS

SAMPLES = len(PERSONA_DESCRIPTIONS)

def generate_persona_by_condition(condition: Callable):
    """Generate persona information based on the given condition."""
    aoai = AOAI(model=MODEL_DICT['gpt4o'])

    user_messages = []
    for idx in range(SAMPLES):
        information_dict = {}
        persona_description = PERSONA_DESCRIPTIONS[idx]
        for key, aliases in INFORMATION_KEYS.items():
            if not condition(key):
                continue
            target_key = random.choice(aliases)
            information_dict[target_key] = None
        prompt = PERSONA_CONSTRUCTION_PROMPT.format(
            persona_description=persona_description, 
            information_dict=information_dict
        )
        user_messages.append(prompt)

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

    return reponses

def refine_persona_information(reponses: list):
    """Refine the persona information based on the given information."""
    aoai = AOAI(model=MODEL_DICT['gpt4o'])
    refine_user_messages = [
        PERSONA_REFINE_PROMPT.format(
            information_dict=reponses[idx],
            persona_description=PERSONA_DESCRIPTIONS[idx]
        )
        for idx in range(SAMPLES)
    ]

    reponses, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=refine_user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.9,
    )

    return reponses

def persona_construct():
    """Generate persona information based on 
    the given persona descriptions and information keys."""
    
    results_stage_1 = generate_persona_by_condition(
        lambda key: COMMON_NORMS[key]['sensitivity'] == 'Sensitive'
    )
    results_stage_2 = generate_persona_by_condition(
        lambda key: COMMON_NORMS[key]['sensitivity'] != 'Sensitive'
    )

    reponses = [
        result1 | result2 
        for result1, result2 in zip(results_stage_1, results_stage_2)
    ]

    reponses = refine_persona_information(reponses)

    for idx in range(SAMPLES):
        reponses[idx]["persona_description"] = (
            PERSONA_DESCRIPTIONS[idx]
        )

    write_jsonl(reponses, f"{PERSONAS_DATA_PATH}/personas.jsonl")

if __name__ == "__main__":
    persona_construct()