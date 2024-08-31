import json
import random
import re
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
from typing import Callable, Literal, Optional, Union, Any
from tqdm.rich import tqdm_rich

from ..language_models import LanguageModel


@retry(stop=stop_after_attempt(3), reraise=False, retry_error_callback=lambda x: None)
def ask_model(
    model: LanguageModel,
    user_message: str,
    system_message: Optional[str] = None,
    type: Literal["json", "text", "markdown"] = "json",
    check_if_valid: Optional[Callable] = None,
    sleep: bool = True,
    mode: Literal["chat", "completion"] = "chat",
    **kwargs,
) -> Union[str, Any]:
    """
    Call the model to generate a response to the prompt.

    Args:
        model (LanguageModel): the model to use.
        user_message (str): the user message to send to the model.
        system_message (str): the system message to send to the model.
        type (str): the type of response to expect.
        check_if_valid (Callable): a function to check if the response is valid.
        sleep (bool): whether to sleep before calling the model.
        mode (str): the mode to use when calling the model.
        **kwargs: additional arguments to pass to the model.
    
    Returns:
        dict: the response from the model.
    
    Raises:
        ValueError: if the response is invalid.
    """
    if sleep:
        sleep_time = random.uniform(1.0, 3.0)
        time.sleep(sleep_time)
    if mode == "chat":
        result = model.chat(user_message, system_message, json_mode=(type == "json"), **kwargs)
    elif mode == "completion":
        result = model.complete(user_message, **kwargs)

    parser = _get_parser(type)
    info = parser(result)
    if check_if_valid and not check_if_valid(info):
        print(f"Invalid response {info}")
        raise ValueError("Invalid response")
    return info


def ask_model_in_parallel(
    model: LanguageModel,
    user_messages: list[str],
    system_message: str = None,
    type: Literal["json", "text", "markdown"] = "json",
    check_if_valid_list: Optional[list[Callable]] = None,
    max_workers: Optional[int] = None,
    desc: str = "Processing...",
    verbose=True,
    mode: Literal["chat", "completion"] = "chat",
    **kwargs,
)-> tuple[list[Union[str, Any]], list[int]]:
    """
    Call the model to generate responses to the prompts in parallel.

    Args:
        model (LanguageModel): the model to use.
        user_messages (list[str]): the user messages to send to the model.
        system_message (str): the system message to send to the model.
        type (str): the type of response to expect.
        check_if_valid_list (list[Callable]): a list of functions to check if the responses are valid.
        max_workers (int): the maximum number of workers to use.
        desc (str): the description to use in the progress bar.
        verbose (bool): whether to display the progress bar.
        mode (str): the mode to use when calling the model.
        **kwargs: additional arguments to pass to the model.

    Returns:
        tuple[list[Union[str, Any]], list[int]]: the responses from the model and the indices of any errors.
    """

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        if check_if_valid_list is None:
            check_if_valid_list = [None] * len(user_messages)
        assert len(user_messages) == len(
            check_if_valid_list
        ), "Length of user_messages and check_if_valid_list should be the same"
        tasks = {
            executor.submit(
                ask_model, model, user_message, system_message, type, check_if_valid, mode, **kwargs
            ): idx
            for idx, (user_message, check_if_valid) 
            in enumerate(zip(user_messages, check_if_valid_list))
        }
        results = []
        error_idxs = []
        for future in tqdm_rich(
            as_completed(tasks), total=len(tasks), desc=desc, disable=not verbose
        ):
            task_id = tasks[future]
            try:
                result = future.result()
                results.append((task_id, result))
            except ValueError:
                print(f"Failed to get response for task {task_id}")
                error_idxs.append(task_id)
            finally:
                ...
        results = [result[1] for result in sorted(results, key=lambda r: r[0])]
        results = [result for result in results if result is not None]
        return results, error_idxs


def _get_parser(type: str) -> Callable:
    """
    Get the parser function for the given type.
    Args:
        type (str): the type of response to parse.

    Returns:
        Callable: the parser function.
    """
    def markdown_parser(result: str, type: str):
        # TODO: Check whether this is the correct regex pattern
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, result, re.DOTALL)
        res = None
        if matches:
            res = matches[0].strip()
        return res
        
    def json_parser(result: str):
        pattern = r"{.*?}"
        matches = re.findall(pattern, result, re.DOTALL)
        if matches:
            res = matches[0].strip()
        try:
            return json.loads(res)
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {result}")

    def text_parser(result: str):
        return result

    if type == "json":
        return json_parser
    elif type == "text":
        return text_parser
    elif type == "markdown":
        return markdown_parser
    else:
        raise ValueError(f"Unsupported type: {type}")
