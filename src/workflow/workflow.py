from autogen import AssistantAgent

from .utils import load_llm_cofig
from .delegate import AIDelegate
from .prompts import RECIPIENT_PROMPT

llm_config = load_llm_cofig(
    model="gpt-4o-20240513",
    cache_seed=None
)

def workflow():
    # generate a scenario, including relation and information
    scenario = "You are supposed to repsonse anything."
    user = AssistantAgent(
        name="user",
        llm_config=llm_config,
        system_message=scenario
    )
    
    # user refine the scenario
    refined_scenario = user.generate_reply(
        messages=[
            {"content": scenario, "role": "user"}
        ]
    )

    refined_scenario = {}

    # start workflow
    delegate = AIDelegate(
        name="delegate",
        model="gpt-4o-20240513",
        scenario=refined_scenario,
        cache_seed=None,
    )

    recipient = AssistantAgent(
        name="recipient",
        llm_config=llm_config,
        system_message=RECIPIENT_PROMPT.format()
    )

    message = "Hello, I am a user."
    chat_result = recipient.initiate_chat(
        recipient=delegate,
        message=message
    )

    # TODO: save result or evaluate the result


if __name__ == "__main__":
    workflow()