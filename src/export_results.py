import os
import json
import argparse

from .utils import load_jsonl
from .conf import EVALUTATION_RESULTS_PATH

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["privacy", "direct"], default="privacy")
    return parser.parse_args()

def export_results(args: argparse.Namespace):
    # Load the results
    results = load_jsonl(
        os.path.join(EVALUTATION_RESULTS_PATH, f"{args.mode}.jsonl")
    )

    proactive_goal_achieved = []
    proactive_should_goal_be_achieved = []
    proactive_is_appropriate_timing = []
    passive_privacy_protected = []
    passive_apprepriate_response = []

    for result in results:
        if "goal_achieved" in result:
            proactive_goal_achieved.append(int(result["goal_achieved"]))
            proactive_should_goal_be_achieved.append(int(result["should_goal_be_achieved"]))
            proactive_is_appropriate_timing.append(int(result["is_appropriate_timing"]))
        else:
            passive_privacy_protected.append(int(result["privacy_protected"]))
            passive_apprepriate_response.append(int(result["apprepriate_response"]))

    with open(os.path.join(EVALUTATION_RESULTS_PATH, f"{args.mode}_exported.json"), "w") as f:
        json.dump({
            "goal_achieved": proactive_goal_achieved,
            "should_goal_be_achieved": proactive_should_goal_be_achieved,
            "is_appropriate_timing": proactive_is_appropriate_timing,
            "privacy_protected": passive_privacy_protected,
            "apprepriate_response": passive_apprepriate_response
        }, f)
    

if __name__ == "__main__":
    args = parse_args()
    export_results(args)