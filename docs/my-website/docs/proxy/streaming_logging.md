# Custom Callback

### Step 1 - Create your custom `mishikallm` callback class
We use `mishikallm.integrations.custom_logger` for this, **more details about mishikallm custom callbacks [here](https://docs.21t.cc/docs/observability/custom_callback)**

Define your custom callback class in a python file.

```python
from mishikallm.integrations.custom_logger import CustomLogger
import mishikallm
import logging

# This file includes the custom callbacks for MishikaLLM Proxy
# Once defined, these can be passed in proxy_config.yaml
class MyCustomHandler(CustomLogger):
    def log_pre_api_call(self, model, messages, kwargs): 
        print(f"Pre-API Call")

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        try:
            # init logging config
            logging.basicConfig(
                    filename='cost.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
            )

            response_cost: Optional[float] = kwargs.get("response_cost", None)
            print("regular response_cost", response_cost)
            logging.info(f"Model {response_obj.model} Cost: ${response_cost:.8f}")
        except:
            pass

proxy_handler_instance = MyCustomHandler()

# Set mishikallm.callbacks = [proxy_handler_instance] on the proxy
# need to set mishikallm.callbacks = [proxy_handler_instance] # on the proxy
```

### Step 2 - Pass your custom callback class in `config.yaml`
We pass the custom callback class defined in **Step1** to the config.yaml. 
Set `callbacks` to `python_filename.logger_instance_name`

In the config below, we pass
- python_filename: `custom_callbacks.py`
- logger_instance_name: `proxy_handler_instance`. This is defined in Step 1

`callbacks: custom_callbacks.proxy_handler_instance`


```yaml
model_list:
  - model_name: gpt-3.5-turbo
    mishikallm_params:
      model: gpt-3.5-turbo

mishikallm_settings:
  callbacks: custom_callbacks.proxy_handler_instance # sets mishikallm.callbacks = [proxy_handler_instance]

```

### Step 3 - Start proxy + test request
```shell
mishikallm --config proxy_config.yaml
```

```shell
curl --location 'http://0.0.0.0:4000/chat/completions' \
    --header 'Authorization: Bearer sk-1234' \
    --data ' {
    "model": "gpt-3.5-turbo",
    "messages": [
        {
        "role": "user",
        "content": "good morning good sir"
        }
    ],
    "user": "ishaan-app",
    "temperature": 0.2
    }'
```
