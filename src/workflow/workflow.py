import os
import json
import argparse

from autogen import AssistantAgent, UserProxyAgent
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
    parser.add_argument(
        "--manual", action="store_true",
        help="Whether to use manual mode."
    )
    return parser.parse_args()

def workflow(args: argparse.Namespace):
    # generate a scenario, including relation and information
    scripts = load_jsonl(f"{SCRIPTS_DATA_PATH}/scripts.jsonl")
    
    index = args.index
    script = scripts[index - 1]
    
    if os.path.exists(f"{PRIVACY_RESULTS_PATH}/{index}.json"):
        print(f"Script {index} already processed. Skipping...")
        return
    
    delegate_scenario = {
        "scenario": script['scenario']['scenario'],
        "social_relation": script['scenario']['social_relation'],
        "goal": (
            script['scenario']['goal'] 
            if script['scenario']['manner'] == "proactive"
            else ""
        ),
        "extra_privacy": script['scenario']['extra_privacy'],
        "human_info_you_know": script['scenario']['human_info_for_delegate']
    }

    refined_scenario = {
        "basic_information": script['delegate_info'],
        "scenario": delegate_scenario,
        "user_preferences": script['user_preferences'],
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

    human_scenario = {
        "scenario": script['scenario']['scenario'],
        "social_relation": script['scenario']['social_relation'],
        "goal": (
            script['scenario']['goal'] 
            if script['scenario']['manner'] == "passive"
            else ""
        ),
        "delegate_info_you_know": script['scenario']['delegate_info_for_human']
    }

    if args.manual:
        print("Manual mode is enabled.")
        human = UserProxyAgent(
            name="human",
            code_execution_config=False,
        )
    else:
        human = AssistantAgent(
            name="human",
            llm_config=llm_config,
            system_message=HUMAN_PROMPT.format(
                basic_information=script['human_info'],
                scenario=human_scenario,
                script=script['human_script']
            ),
            is_termination_msg=(
                lambda x: x.get("content").find("TERMINATE") != -1
            )
        )
    

    chat_result: ChatResult = None
    if script['manner'] == 'passive':
        # sender starts the conversation
        chat_result = delegate.initiate_chat(
            recipient=human,
            message="",
            max_turns=MAX_TURNS
        )
    elif script['manner'] == 'proactive':
        # receiver starts the conversation
        chat_result = human.initiate_chat(
            recipient=delegate,
            message="",
            max_turns=MAX_TURNS
        )
    else:
        raise ValueError("Invalid script.")
    
    chat_history = [
        {message["name"]: message["content"]} 
        for message in chat_result.chat_history[1:]
    ]
    with open(f"{PRIVACY_RESULTS_PATH}/{index}.json", "w") as f:
        result = {
            "chat_history": chat_history,
            "scenario": script['scenario'],
            "user_preferences": script['user_preferences']
        }
        json.dump(result, f, indent=4)


if __name__ == "__main__":
    args = parse_args()
    workflow(args)