import json
import argparse

from autogen import AssistantAgent
from autogen.agentchat.chat import ChatResult

from .utils import load_llm_cofig
from .prompts import RECIPIENT_PROMPT, DIRECT_PROMPT
from ..conf import SCRIPTS_DATA_PATH, DIRECT_RESULTS_PATH
from ..utils import load_jsonl
from ..data_generation.constants import COMMON_NORMS

llm_config = load_llm_cofig(
    model="gpt-4o-20240513",
    cache_seed=None
)

MAX_TURNS = 20

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index",
        type=int,
        required=True,
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

    delegate = AssistantAgent(
        name="delegate",
        llm_config=llm_config,
        system_message=DIRECT_PROMPT.format(
            basic_information=script['delegate_info'],
            ifc=script['ifc'],
            user_preferences="",
            common_norms=COMMON_NORMS
        ),
        is_termination_msg=lambda x: x.get("content").find("TERMINATE") != -1
    )

    recipient = AssistantAgent(
        name="recipient",
        llm_config=llm_config,
        system_message=RECIPIENT_PROMPT.format(
            basic_information=script['recipient_info'],
            ifc=script['ifc'],
            script=script['recipient_script']
        ),
        is_termination_msg=lambda x: x.get("content").find("TERMINATE") != -1
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
    
    with open(f"{DIRECT_RESULTS_PATH}/{args.index}.json", "w") as f:
        json.dump(chat_result.chat_history, f, indent=4)


if __name__ == "__main__":
    args = parse_args()
    workflow(args)