import argparse
import os

from scipy.stats import entropy
from .utils import load_jsonl
from .conf import EVALUTATION_RESULTS_PATH

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", type=str, choices=["direct", "privacy"], default="privacy")
    return parser.parse_args()

def cal_kl_value(args: argparse.Namespace):
    eval_results = load_jsonl(
        os.path.join(EVALUTATION_RESULTS_PATH, f"{args.mode}-proactive.jsonl")
    )
    proactive_goal_achieved = []
    proactive_should_goal_be_achieved = []
    for result in eval_results:
        if "goal_achieved" in result:
            proactive_goal_achieved.append(int(result["goal_achieved"]))
            proactive_should_goal_be_achieved.append(int(result["should_goal_be_achieved"]))

    kl_proactive = entropy(proactive_goal_achieved, proactive_should_goal_be_achieved)

    print(f"KL divergence for {args.mode} evaluation: {kl_proactive:.4f}")

if __name__ == "__main__":
    args = parse_args()
    cal_kl_value(args)