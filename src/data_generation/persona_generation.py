import os
import sys
import random
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from language_models import AOAI
from utils import write_jsonl, ask_model_in_parallel
from conf import PERSONAS_DATA_PATH
from prompts import PERSONA_CONSTRUCTION_PROMPT, PERSONA_REFINE_PROMPT
from constants import PERSONA_DESCRIPTIONS, INFORMATION_KEYS

SAMPLES = len(PERSONA_DESCRIPTIONS) * 2

def persona_construct():
    """Generate persona information based on the given persona descriptions and information keys."""
    aoai = AOAI(model="gpt-4o-20240513")
    generate_user_messages = []

    for idx in range(SAMPLES):
        information_dict = {}
        # persona_description = random.choice(PERSONA_DESCRIPTIONS)
        persona_description = PERSONA_DESCRIPTIONS[idx % len(PERSONA_DESCRIPTIONS)]
        for _, aliases in INFORMATION_KEYS.items():
            target_key = random.choice(aliases)
            information_dict[target_key] = None
    
        prompt = PERSONA_CONSTRUCTION_PROMPT.format(
            persona_description=persona_description, 
            information_dict=information_dict
        )
        generate_user_messages.append(prompt)

    # print(user_messages[0])
    reponses, _ = ask_model_in_parallel(
        model=aoai,
        user_messages=generate_user_messages,
        system_message=None,
        type="json",
        check_if_valid_list=[lambda x: isinstance(x, dict)] * SAMPLES,
        max_workers=4,
        mode="chat",
        temperature=0.7,
    )

    refine_user_messages = [
        PERSONA_REFINE_PROMPT.format(
            information_dict=reponses[idx],
            persona_description=PERSONA_DESCRIPTIONS[idx % len(PERSONA_DESCRIPTIONS)]
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
        temperature=0.7,
    )

    for idx in range(SAMPLES):
        reponses[idx]["persona_description"] = PERSONA_DESCRIPTIONS[idx % len(PERSONA_DESCRIPTIONS)]

    write_jsonl(reponses, f"{PERSONAS_DATA_PATH}/personas.jsonl")

if __name__ == "__main__":
    persona_construct()