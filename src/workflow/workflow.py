import json
import argparse

from autogen import AssistantAgent
from autogen.agentchat.chat import ChatResult

from .utils import load_llm_cofig
from .delegate import AIDelegate
from .prompts import RECIPIENT_PROMPT
from ..conf import SCRIPTS_DATA_PATH, PRIVACY_RESULTS_PATH
from ..utils import load_jsonl
from ..data_generation.constants import COMMON_NORMS
from ..language_models import MODEL_DICT

llm_config = load_llm_cofig(
    model=MODEL_DICT["gpt4o"],
    cache_seed=None
)

MAX_TURNS = 5

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index", type=int, required=True,
        help="The index of the scenario to be used."
    )
    return parser.parse_args()

def workflow(args: argparse.Namespace):
    # generate a scenario, including relation and information
    scripts = load_jsonl(f"{SCRIPTS_DATA_PATH}/scripts.jsonl")
    # user = AssistantAgent(
    #     name="user",
    #     llm_config=llm_config,
    #     system_message=scenario
    # )
    
    # user refine the scenario
    # refined_scenario = user.generate_reply(
    #     messages=[
    #         {"content": scenario, "role": "user"}
    #     ]
    # )

    script = scripts[args.index]

    refined_scenario = {
        "basic_information": script['delegate_info'],
        "ifc": script['ifc'],
        "user_preferences": "",
    }

    delegate = AIDelegate(
        name="delegate",
        model="gpt-4o-20240513",
        scenario=refined_scenario,
        cache_seed=None,
    )

    recipient = AssistantAgent(
        name="human",
        llm_config=llm_config,
        system_message=RECIPIENT_PROMPT.format(
            basic_information=script['human_info'],
            ifc=script['ifc'],
            script=script['human_script']
        )
    )

    start_message = script['start_message']
    chat_result: ChatResult = None
    if script['manner'] == 'proactive':
        # sender starts the conversation
        chat_result = delegate.initiate_chat(
            recipient=recipient,
            message=start_message,
            max_turns=MAX_TURNS
        )
    elif script['manner'] == 'passive':
        # receiver starts the conversation
        chat_result = recipient.initiate_chat(
            recipient=delegate,
            message=start_message,
            max_turns=MAX_TURNS
        )
    else:
        raise ValueError("Invalid script.")
    
    with open(f"{PRIVACY_RESULTS_PATH}/{args.index}.json", "w") as f:
        json.dump(chat_result.chat_history, f, indent=4)


if __name__ == "__main__":
    args = parse_args()
    workflow(args)