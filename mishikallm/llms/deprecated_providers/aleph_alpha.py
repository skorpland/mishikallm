import json
import time
import types
from typing import Callable, Optional

import httpx  # type: ignore

import mishikallm
from mishikallm.utils import Choices, Message, ModelResponse, Usage


class AlephAlphaError(Exception):
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message
        self.request = httpx.Request(
            method="POST", url="https://api.aleph-alpha.com/complete"
        )
        self.response = httpx.Response(status_code=status_code, request=self.request)
        super().__init__(
            self.message
        )  # Call the base class constructor with the parameters it needs


class AlephAlphaConfig:
    """
    Reference: https://docs.aleph-alpha.com/api/complete/

    The `AlephAlphaConfig` class represents the configuration for the Aleph Alpha API. Here are the properties:

    - `maximum_tokens` (integer, required): The maximum number of tokens to be generated by the completion. The sum of input tokens and maximum tokens may not exceed 2048.

    - `minimum_tokens` (integer, optional; default value: 0): Generate at least this number of tokens before an end-of-text token is generated.

    - `echo` (boolean, optional; default value: false): Whether to echo the prompt in the completion.

    - `temperature` (number, nullable; default value: 0): Adjusts how creatively the model generates outputs. Use combinations of temperature, top_k, and top_p sensibly.

    - `top_k` (integer, nullable; default value: 0): Introduces randomness into token generation by considering the top k most likely options.

    - `top_p` (number, nullable; default value: 0): Adds randomness by considering the smallest set of tokens whose cumulative probability exceeds top_p.

    - `presence_penalty`, `frequency_penalty`, `sequence_penalty` (number, nullable; default value: 0): Various penalties that can reduce repetition.

    - `sequence_penalty_min_length` (integer; default value: 2): Minimum number of tokens to be considered as a sequence.

    - `repetition_penalties_include_prompt`, `repetition_penalties_include_completion`, `use_multiplicative_presence_penalty`,`use_multiplicative_frequency_penalty`,`use_multiplicative_sequence_penalty` (boolean, nullable; default value: false): Various settings that adjust how the repetition penalties are applied.

    - `penalty_bias` (string, nullable): Text used in addition to the penalized tokens for repetition penalties.

    - `penalty_exceptions` (string[], nullable): Strings that may be generated without penalty.

    - `penalty_exceptions_include_stop_sequences` (boolean, nullable; default value: true): Include all stop_sequences in penalty_exceptions.

    - `best_of` (integer, nullable; default value: 1): The number of completions will be generated on the server side.

    - `n` (integer, nullable; default value: 1): The number of completions to return.

    - `logit_bias` (object, nullable): Adjust the logit scores before sampling.

    - `log_probs` (integer, nullable): Number of top log probabilities for each token generated.

    - `stop_sequences` (string[], nullable): List of strings that will stop generation if they're generated.

    - `tokens` (boolean, nullable; default value: false): Flag indicating whether individual tokens of the completion should be returned or not.

    - `raw_completion` (boolean; default value: false): if True, the raw completion of the model will be returned.

    - `disable_optimizations` (boolean, nullable; default value: false): Disables any applied optimizations to both your prompt and completion.

    - `completion_bias_inclusion`, `completion_bias_exclusion` (string[], default value: []): Set of strings to bias the generation of tokens.

    - `completion_bias_inclusion_first_token_only`, `completion_bias_exclusion_first_token_only` (boolean; default value: false): Consider only the first token for the completion_bias_inclusion/exclusion.

    - `contextual_control_threshold` (number, nullable): Control over how similar tokens are controlled.

    - `control_log_additive` (boolean; default value: true): Method of applying control to attention scores.
    """

    maximum_tokens: Optional[
        int
    ] = mishikallm.max_tokens  # aleph alpha requires max tokens
    minimum_tokens: Optional[int] = None
    echo: Optional[bool] = None
    temperature: Optional[int] = None
    top_k: Optional[int] = None
    top_p: Optional[int] = None
    presence_penalty: Optional[int] = None
    frequency_penalty: Optional[int] = None
    sequence_penalty: Optional[int] = None
    sequence_penalty_min_length: Optional[int] = None
    repetition_penalties_include_prompt: Optional[bool] = None
    repetition_penalties_include_completion: Optional[bool] = None
    use_multiplicative_presence_penalty: Optional[bool] = None
    use_multiplicative_frequency_penalty: Optional[bool] = None
    use_multiplicative_sequence_penalty: Optional[bool] = None
    penalty_bias: Optional[str] = None
    penalty_exceptions_include_stop_sequences: Optional[bool] = None
    best_of: Optional[int] = None
    n: Optional[int] = None
    logit_bias: Optional[dict] = None
    log_probs: Optional[int] = None
    stop_sequences: Optional[list] = None
    tokens: Optional[bool] = None
    raw_completion: Optional[bool] = None
    disable_optimizations: Optional[bool] = None
    completion_bias_inclusion: Optional[list] = None
    completion_bias_exclusion: Optional[list] = None
    completion_bias_inclusion_first_token_only: Optional[bool] = None
    completion_bias_exclusion_first_token_only: Optional[bool] = None
    contextual_control_threshold: Optional[int] = None
    control_log_additive: Optional[bool] = None

    def __init__(
        self,
        maximum_tokens: Optional[int] = None,
        minimum_tokens: Optional[int] = None,
        echo: Optional[bool] = None,
        temperature: Optional[int] = None,
        top_k: Optional[int] = None,
        top_p: Optional[int] = None,
        presence_penalty: Optional[int] = None,
        frequency_penalty: Optional[int] = None,
        sequence_penalty: Optional[int] = None,
        sequence_penalty_min_length: Optional[int] = None,
        repetition_penalties_include_prompt: Optional[bool] = None,
        repetition_penalties_include_completion: Optional[bool] = None,
        use_multiplicative_presence_penalty: Optional[bool] = None,
        use_multiplicative_frequency_penalty: Optional[bool] = None,
        use_multiplicative_sequence_penalty: Optional[bool] = None,
        penalty_bias: Optional[str] = None,
        penalty_exceptions_include_stop_sequences: Optional[bool] = None,
        best_of: Optional[int] = None,
        n: Optional[int] = None,
        logit_bias: Optional[dict] = None,
        log_probs: Optional[int] = None,
        stop_sequences: Optional[list] = None,
        tokens: Optional[bool] = None,
        raw_completion: Optional[bool] = None,
        disable_optimizations: Optional[bool] = None,
        completion_bias_inclusion: Optional[list] = None,
        completion_bias_exclusion: Optional[list] = None,
        completion_bias_inclusion_first_token_only: Optional[bool] = None,
        completion_bias_exclusion_first_token_only: Optional[bool] = None,
        contextual_control_threshold: Optional[int] = None,
        control_log_additive: Optional[bool] = None,
    ) -> None:
        locals_ = locals().copy()
        for key, value in locals_.items():
            if key != "self" and value is not None:
                setattr(self.__class__, key, value)

    @classmethod
    def get_config(cls):
        return {
            k: v
            for k, v in cls.__dict__.items()
            if not k.startswith("__")
            and not isinstance(
                v,
                (
                    types.FunctionType,
                    types.BuiltinFunctionType,
                    classmethod,
                    staticmethod,
                ),
            )
            and v is not None
        }


def validate_environment(api_key):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    return headers


def completion(
    model: str,
    messages: list,
    api_base: str,
    model_response: ModelResponse,
    print_verbose: Callable,
    encoding,
    api_key,
    logging_obj,
    optional_params: dict,
    mishikallm_params=None,
    logger_fn=None,
    default_max_tokens_to_sample=None,
):
    headers = validate_environment(api_key)

    ## Load Config
    config = mishikallm.AlephAlphaConfig.get_config()
    for k, v in config.items():
        if (
            k not in optional_params
        ):  # completion(top_k=3) > aleph_alpha_config(top_k=3) <- allows for dynamic variables to be passed in
            optional_params[k] = v

    completion_url = api_base
    model = model
    prompt = ""
    if "control" in model:  # follow the ###Instruction / ###Response format
        for idx, message in enumerate(messages):
            if "role" in message:
                if (
                    idx == 0
                ):  # set first message as instruction (required), let later user messages be input
                    prompt += f"###Instruction: {message['content']}"
                else:
                    if message["role"] == "system":
                        prompt += f"###Instruction: {message['content']}"
                    elif message["role"] == "user":
                        prompt += f"###Input: {message['content']}"
                    else:
                        prompt += f"###Response: {message['content']}"
            else:
                prompt += f"{message['content']}"
    else:
        prompt = " ".join(message["content"] for message in messages)
    data = {
        "model": model,
        "prompt": prompt,
        **optional_params,
    }

    ## LOGGING
    logging_obj.pre_call(
        input=prompt,
        api_key=api_key,
        additional_args={"complete_input_dict": data},
    )
    ## COMPLETION CALL
    response = mishikallm.module_level_client.post(
        completion_url,
        headers=headers,
        data=json.dumps(data),
        stream=optional_params["stream"] if "stream" in optional_params else False,
    )
    if "stream" in optional_params and optional_params["stream"] is True:
        return response.iter_lines()
    else:
        ## LOGGING
        logging_obj.post_call(
            input=prompt,
            api_key=api_key,
            original_response=response.text,
            additional_args={"complete_input_dict": data},
        )
        print_verbose(f"raw model_response: {response.text}")
        ## RESPONSE OBJECT
        completion_response = response.json()
        if "error" in completion_response:
            raise AlephAlphaError(
                message=completion_response["error"],
                status_code=response.status_code,
            )
        else:
            try:
                choices_list = []
                for idx, item in enumerate(completion_response["completions"]):
                    if len(item["completion"]) > 0:
                        message_obj = Message(content=item["completion"])
                    else:
                        message_obj = Message(content=None)
                    choice_obj = Choices(
                        finish_reason=item["finish_reason"],
                        index=idx + 1,
                        message=message_obj,
                    )
                    choices_list.append(choice_obj)
                model_response.choices = choices_list  # type: ignore
            except Exception:
                raise AlephAlphaError(
                    message=json.dumps(completion_response),
                    status_code=response.status_code,
                )

        ## CALCULATING USAGE - baseten charges on time, not tokens - have some mapping of cost here.
        prompt_tokens = len(encoding.encode(prompt))
        completion_tokens = len(
            encoding.encode(
                model_response["choices"][0]["message"]["content"],
                disallowed_special=(),
            )
        )

        model_response.created = int(time.time())
        model_response.model = model
        usage = Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        setattr(model_response, "usage", usage)
        return model_response


def embedding():
    # logic for parsing in - calling - parsing out model embedding calls
    pass
