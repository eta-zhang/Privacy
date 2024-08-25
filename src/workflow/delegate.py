from typing import Optional, Callable
from autogen import GroupChat, GroupChatManager, AssistantAgent
from autogen.agentchat.contrib.society_of_mind_agent import SocietyOfMindAgent

from .utils import load_llm_cofig
from .prompts import ASSESSOR_PROMPT, STRATEGIST_PROMPT, RESONPERF_PROMPT
from ..language_models import cloudgpt_available_models

class AIDelegate(SocietyOfMindAgent):
    def __init__(
        self,
        name: str,
        model: cloudgpt_available_models,
        scenario: dict[str, str],
        max_turns: int = 3,
        cache_seed: Optional[int] = None,
        is_termination_msg: Optional[Callable[[dict], bool]] = None,
        **kwargs
    ):
        """
        An AI delegate that can assess, strategize, and respond to messages.

        Args:
            name (str): name of the agent.
            model (cloudgpt_available_models): available models from cloudgpt.
            max_turns (int, optional): maximum number of turns. Defaults to 1.
            cache_seed (Optional[int], optional): cache seed. Defaults to None.
            is_termination_msg (Optional[Callable[[dict], bool]], optional): termination message. Defaults to None.
        """

        llm_config = load_llm_cofig(
            model = model,
            cache_seed = cache_seed
        )

        _assessor = AssistantAgent(
            name="assessor",
            system_message=ASSESSOR_PROMPT.format(**scenario),
            llm_config=llm_config,
        )

        _strategist = AssistantAgent(
            name="strategist",
            system_message=STRATEGIST_PROMPT,
            llm_config=llm_config,
        )

        _responser = AssistantAgent(
            name="responser",
            system_message=RESONPERF_PROMPT,
            llm_config=llm_config,
        )

        allowed_transitions = {
            _assessor: [_strategist],
            _strategist: [_responser],
            _responser: [],
        }

        # TODO: check the max_turns 
        group_chat = GroupChat(
            agents=[_assessor, _strategist, _responser],
            admin_name=_assessor.name,
            messages=[],
            allowed_or_disallowed_speaker_transitions=allowed_transitions,
            speaker_transitions_type="allowed",
            max_round=max_turns,
        )

        group_chat_manager = GroupChatManager(
            groupchat=group_chat,
        )

        super().__init__(
            name=name,
            chat_manager=group_chat_manager,
            llm_config=llm_config,
            human_input_mode="NEVER",
            **kwargs
        )