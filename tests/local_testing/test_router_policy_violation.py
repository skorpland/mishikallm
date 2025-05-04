#### What this tests ####
# This tests if the router sends back a policy violation, without retries

import sys, os, time
import traceback, asyncio
import pytest

sys.path.insert(
    0, os.path.abspath("../..")
)  # Adds the parent directory to the system path

import mishikallm
from mishikallm import Router
from mishikallm.integrations.custom_logger import CustomLogger


class MyCustomHandler(CustomLogger):
    success: bool = False
    failure: bool = False
    previous_models: int = 0

    def log_pre_api_call(self, model, messages, kwargs):
        print(f"Pre-API Call")
        print(
            f"previous_models: {kwargs['mishikallm_params']['metadata']['previous_models']}"
        )
        self.previous_models += len(
            kwargs["mishikallm_params"]["metadata"]["previous_models"]
        )  # {"previous_models": [{"model": mishikallm_model_name, "exception_type": AuthenticationError, "exception_string": <complete_traceback>}]}
        print(f"self.previous_models: {self.previous_models}")

    def log_post_api_call(self, kwargs, response_obj, start_time, end_time):
        print(
            f"Post-API Call - response object: {response_obj}; model: {kwargs['model']}"
        )

    def log_stream_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Stream")

    def async_log_stream_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Stream")

    def log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Success")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Success")

    def log_failure_event(self, kwargs, response_obj, start_time, end_time):
        print(f"On Failure")


kwargs = {
    "model": "azure/gpt-3.5-turbo",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "vorrei vedere la cosa più bella ad Ercolano. Qual’è?",
        },
    ],
}


@pytest.mark.asyncio
async def test_async_fallbacks():
    mishikallm.set_verbose = False
    model_list = [
        {  # list of model deployments
            "model_name": "azure/gpt-3.5-turbo-context-fallback",  # openai model name
            "mishikallm_params": {  # params for mishikallm completion/embedding call
                "model": "azure/chatgpt-v-3",
                "api_key": os.getenv("AZURE_API_KEY"),
                "api_version": os.getenv("AZURE_API_VERSION"),
                "api_base": os.getenv("AZURE_API_BASE"),
            },
            "tpm": 240000,
            "rpm": 1800,
        },
        {
            "model_name": "azure/gpt-3.5-turbo",  # openai model name
            "mishikallm_params": {  # params for mishikallm completion/embedding call
                "model": "azure/chatgpt-functioncalling",
                "api_key": os.getenv("AZURE_API_KEY"),
                "api_version": os.getenv("AZURE_API_VERSION"),
                "api_base": os.getenv("AZURE_API_BASE"),
            },
            "tpm": 240000,
            "rpm": 1800,
        },
        {
            "model_name": "gpt-3.5-turbo",  # openai model name
            "mishikallm_params": {  # params for mishikallm completion/embedding call
                "model": "gpt-3.5-turbo",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "tpm": 1000000,
            "rpm": 9000,
        },
        {
            "model_name": "gpt-3.5-turbo-16k",  # openai model name
            "mishikallm_params": {  # params for mishikallm completion/embedding call
                "model": "gpt-3.5-turbo-16k",
                "api_key": os.getenv("OPENAI_API_KEY"),
            },
            "tpm": 1000000,
            "rpm": 9000,
        },
    ]

    router = Router(
        model_list=model_list,
        num_retries=3,
        fallbacks=[{"azure/gpt-3.5-turbo": ["gpt-3.5-turbo"]}],
        # context_window_fallbacks=[
        #     {"azure/gpt-3.5-turbo-context-fallback": ["gpt-3.5-turbo-16k"]},
        #     {"gpt-3.5-turbo": ["gpt-3.5-turbo-16k"]},
        # ],
        set_verbose=False,
    )
    customHandler = MyCustomHandler()
    mishikallm.callbacks = [customHandler]
    try:
        response = await router.acompletion(**kwargs)
        pytest.fail(
            f"An exception occurred: {e}"
        )  # should've raised azure policy error
    except mishikallm.Timeout as e:
        pass
    except Exception as e:
        await asyncio.sleep(
            0.05
        )  # allow a delay as success_callbacks are on a separate thread
        assert customHandler.previous_models == 0  # 0 retries, 0 fallback
        router.reset()
    finally:
        router.reset()
