import os
import json
import argparse

from autogen import AssistantAgent
from autogen.agentchat.chat import ChatResult

from .utils import load_llm_cofig
from .delegate import AIDelegate
from .prompts import HUMAN_PROMPT
from ..conf import SCRIPTS_DATA_PATH, PRIVACY_RESULTS_PATH
from ..utils import load_jsonl
from ..language_models import MODEL_DICT

llm_config = load_llm_cofig(
    model=MODEL_DICT["gpt4o"],
    cache_seed=None
)

MAX_TURNS = 20

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index", type=int, required=True,
        help="The index of the scenario to be used."
    )
    return parser.parse_args()

def workflow(args: argparse.Namespace):
    # generate a scenario, including relation and information
    # scripts = load_jsonl(f"{SCRIPTS_DATA_PATH}/scripts.jsonl")
    scripts = load_jsonl(f"{SCRIPTS_DATA_PATH}/user_case_study.jsonl")
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
    index = args.index
    script = scripts[index - 1]
    # if script["privacy_leakage"] == False:
    #     print(f"Script {index} has no privacy leakage. Skipping...")
    #     return
    
    if os.path.exists(f"{PRIVACY_RESULTS_PATH}/{index}-without-start_message.json"):
        print(f"Script {index} already processed. Skipping...")
        return

    refined_scenario = {
        "basic_information": script['delegate_info'],
        "ifc": script['ifc'],
        "user_preferences": "",
    }

    delegate = AIDelegate(
        name="delegate",
        model=MODEL_DICT["gpt4o"],
        scenario=refined_scenario,
        cache_seed=None,
        is_termination_msg=(
            lambda x: x.get("content").find("TERMINATE") != -1
        )
    )

    human = AssistantAgent(
        name="human",
        llm_config=llm_config,
        system_message=HUMAN_PROMPT.format(
            basic_information=script['human_info'],
            ifc=script['ifc'],
            script=script['human_script']
        ),
        is_termination_msg=(
            lambda x: x.get("content").find("TERMINATE") != -1
        )
    )

    # start_message = script['start_message']
    chat_result: ChatResult = None
    if script['manner'] == 'passive':
        # sender starts the conversation
        chat_result = delegate.initiate_chat(
            recipient=human,
            # message=start_message,
            message="",
            max_turns=MAX_TURNS
        )
    elif script['manner'] == 'proactive':
        # receiver starts the conversation
        chat_result = human.initiate_chat(
            recipient=delegate,
            message="",
            # message=start_message,
            max_turns=MAX_TURNS
        )
    else:
        raise ValueError("Invalid script.")
    
    chat_history = [
            {message["name"]: message["content"]} 
            for message in chat_result.chat_history[1:]
        ]
    with open(f"{PRIVACY_RESULTS_PATH}/{index}-without-start_message.json", "w") as f:
        result = {
            "ifc": script['ifc'],
            "privacy_leakage": script['privacy_leakage'],
            "comments": script['comments'],
            "chat_history": chat_history,
        }
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    args = parse_args()
    workflow(args)