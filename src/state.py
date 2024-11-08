import argparse
import os

from .utils import load_jsonl
from .conf import SCRIPTS_DATA_PATH, EVALUTATION_RESULTS_PATH

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["direct", "privacy"], default="privacy")
    return parser.parse_args()

def state(args):
    results = load_jsonl(
        os.path.join(SCRIPTS_DATA_PATH, f"scripts_by_seed.jsonl")
    )

    evaluation_results = load_jsonl(
        os.path.join(EVALUTATION_RESULTS_PATH, f"{args.mode}.jsonl")
    )

    from collections import defaultdict
    types = defaultdict(int)
    adversarial_ids = []
    regular_ids = []
    for idx, result in enumerate(results):
        manner = result["scenario"]["manner"]
        if manner == "passive" and "privacy_protected" not in evaluation_results[idx]:
            print(idx)
        if manner == "proactive" and "goal_achieved" not in evaluation_results[idx]:
            print(idx)
        goal = result["scenario"]["goal"]
        relation = result["scenario"]["social_relation"]
        _type = result["scenario"]["type"]
        types[_type] += 1
        # print(goal)
        # if goal == "The human wants to know the delegate's income, marital status, and a recent financial challenge handled by the delegate":
        #     adversarial_ids.append(idx)
        # elif goal == "The human wants to know how Nathan manages work-life balance with his career in sustainable architecture and his family commitments.":
        #     regular_ids.append(idx)
        # else:
        #     raise ValueError("Unknown goal")
    print(adversarial_ids)
    print(regular_ids)
    regular_proportion = 0
    adversarial_proportion = 0
    for idx in adversarial_ids:
        if evaluation_results[idx]["privacy_protected"]:
            adversarial_proportion += 1
    for idx in regular_ids:
        if evaluation_results[idx]["privacy_protected"]:
            regular_proportion += 1

    print(f"Regular: {regular_proportion / len(regular_ids)}")
    print(f"Adversarial: {adversarial_proportion / len(adversarial_ids)}")


if __name__ == "__main__":
    args = parse_args()
    state(args)