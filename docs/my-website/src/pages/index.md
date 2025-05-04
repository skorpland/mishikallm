import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# MishikaLLM - Getting Started

https://github.com/skorpland/mishikallm

## **Call 100+ LLMs using the OpenAI Input/Output Format**

- Translate inputs to provider's `completion`, `embedding`, and `image_generation` endpoints
- [Consistent output](https://docs.21t.cc/docs/completion/output), text responses will always be available at `['choices'][0]['message']['content']`
- Retry/fallback logic across multiple deployments (e.g. Azure/OpenAI) - [Router](https://docs.21t.cc/docs/routing)
- Track spend & set budgets per project [MishikaLLM Proxy Server](https://docs.21t.cc/docs/simple_proxy)

## How to use MishikaLLM
You can use mishikallm through either:
1. [MishikaLLM Proxy Server](#mishikallm-proxy-server-llm-gateway) - Server (LLM Gateway) to call 100+ LLMs, load balance, cost tracking across projects
2. [MishikaLLM python SDK](#basic-usage) - Python Client to call 100+ LLMs, load balance, cost tracking

### **When to use MishikaLLM Proxy Server (LLM Gateway)**

:::tip

Use MishikaLLM Proxy Server if you want a **central service (LLM Gateway) to access multiple LLMs**

Typically used by Gen AI Enablement /  ML PLatform Teams

:::

  - MishikaLLM Proxy gives you a unified interface to access multiple LLMs (100+ LLMs)
  - Track LLM Usage and setup guardrails
  - Customize Logging, Guardrails, Caching per project

### **When to use MishikaLLM Python SDK**

:::tip

  Use MishikaLLM Python SDK if you want to use MishikaLLM in your **python code**

Typically used by developers building llm projects

:::

  - MishikaLLM SDK gives you a unified interface to access multiple LLMs (100+ LLMs) 
  - Retry/fallback logic across multiple deployments (e.g. Azure/OpenAI) - [Router](https://docs.21t.cc/docs/routing)

## **MishikaLLM Python SDK**

### Basic usage 

<a target="_blank" href="https://colab.research.google.com/github/skorpland/mishikallm/blob/main/cookbook/mishikaLLM_Getting_Started.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

```shell
pip install mishikallm
```

<Tabs>
<TabItem value="openai" label="OpenAI">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["OPENAI_API_KEY"] = "your-api-key"

response = completion(
  model="gpt-3.5-turbo",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)
```

</TabItem>
<TabItem value="anthropic" label="Anthropic">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

response = completion(
  model="claude-2",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)
```

</TabItem>

<TabItem value="vertex" label="VertexAI">

```python
from mishikallm import completion
import os

# auth: run 'gcloud auth application-default'
os.environ["VERTEX_PROJECT"] = "hardy-device-386718"
os.environ["VERTEX_LOCATION"] = "us-central1"

response = completion(
  model="chat-bison",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)
```

</TabItem>

<TabItem value="nvidia" label="NVIDIA">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["NVIDIA_NIM_API_KEY"] = "nvidia_api_key"
os.environ["NVIDIA_NIM_API_BASE"] = "nvidia_nim_endpoint_url"

response = completion(
  model="nvidia_nim/<model_name>",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
)
```

</TabItem>

<TabItem value="hugging" label="HuggingFace">

```python
from mishikallm import completion
import os

os.environ["HUGGINGFACE_API_KEY"] = "huggingface_api_key"

# e.g. Call 'WizardLM/WizardCoder-Python-34B-V1.0' hosted on HF Inference endpoints
response = completion(
  model="huggingface/WizardLM/WizardCoder-Python-34B-V1.0",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  api_base="https://my-endpoint.huggingface.cloud"
)

print(response)
```

</TabItem>

<TabItem value="azure" label="Azure OpenAI">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["AZURE_API_KEY"] = ""
os.environ["AZURE_API_BASE"] = ""
os.environ["AZURE_API_VERSION"] = ""

# azure call
response = completion(
  "azure/<your_deployment_name>",
  messages = [{ "content": "Hello, how are you?","role": "user"}]
)
```

</TabItem>

<TabItem value="ollama" label="Ollama">

```python
from mishikallm import completion

response = completion(
            model="ollama/llama2",
            messages = [{ "content": "Hello, how are you?","role": "user"}],
            api_base="http://localhost:11434"
)
```

</TabItem>
<TabItem value="or" label="Openrouter">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["OPENROUTER_API_KEY"] = "openrouter_api_key"

response = completion(
  model="openrouter/google/palm-2-chat-bison",
  messages = [{ "content": "Hello, how are you?","role": "user"}],
)
```

</TabItem>

</Tabs>

### Streaming
Set `stream=True` in the `completion` args. 

<Tabs>
<TabItem value="openai" label="OpenAI">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["OPENAI_API_KEY"] = "your-api-key"

response = completion(
  model="gpt-3.5-turbo",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)
```

</TabItem>
<TabItem value="anthropic" label="Anthropic">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["ANTHROPIC_API_KEY"] = "your-api-key"

response = completion(
  model="claude-2",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)
```

</TabItem>

<TabItem value="vertex" label="VertexAI">

```python
from mishikallm import completion
import os

# auth: run 'gcloud auth application-default'
os.environ["VERTEX_PROJECT"] = "hardy-device-386718"
os.environ["VERTEX_LOCATION"] = "us-central1"

response = completion(
  model="chat-bison",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)
```

</TabItem>

<TabItem value="nvidia" label="NVIDIA">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["NVIDIA_NIM_API_KEY"] = "nvidia_api_key"
os.environ["NVIDIA_NIM_API_BASE"] = "nvidia_nim_endpoint_url"

response = completion(
  model="nvidia_nim/<model_name>",
  messages=[{ "content": "Hello, how are you?","role": "user"}]
  stream=True,
)
```
</TabItem>

<TabItem value="hugging" label="HuggingFace">

```python
from mishikallm import completion
import os

os.environ["HUGGINGFACE_API_KEY"] = "huggingface_api_key"

# e.g. Call 'WizardLM/WizardCoder-Python-34B-V1.0' hosted on HF Inference endpoints
response = completion(
  model="huggingface/WizardLM/WizardCoder-Python-34B-V1.0",
  messages=[{ "content": "Hello, how are you?","role": "user"}],
  api_base="https://my-endpoint.huggingface.cloud",
  stream=True,
)

print(response)
```

</TabItem>

<TabItem value="azure" label="Azure OpenAI">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["AZURE_API_KEY"] = ""
os.environ["AZURE_API_BASE"] = ""
os.environ["AZURE_API_VERSION"] = ""

# azure call
response = completion(
  "azure/<your_deployment_name>",
  messages = [{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)
```

</TabItem>

<TabItem value="ollama" label="Ollama">

```python
from mishikallm import completion

response = completion(
            model="ollama/llama2",
            messages = [{ "content": "Hello, how are you?","role": "user"}],
            api_base="http://localhost:11434",
            stream=True,
)
```

</TabItem>
<TabItem value="or" label="Openrouter">

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["OPENROUTER_API_KEY"] = "openrouter_api_key"

response = completion(
  model="openrouter/google/palm-2-chat-bison",
  messages = [{ "content": "Hello, how are you?","role": "user"}],
  stream=True,
)
```

</TabItem>

</Tabs>

### Exception handling 

MishikaLLM maps exceptions across all supported providers to the OpenAI exceptions. All our exceptions inherit from OpenAI's exception types, so any error-handling you have for that, should work out of the box with MishikaLLM.

```python
from openai.error import OpenAIError
from mishikallm import completion

os.environ["ANTHROPIC_API_KEY"] = "bad-key"
try:
    # some code
    completion(model="claude-instant-1", messages=[{"role": "user", "content": "Hey, how's it going?"}])
except OpenAIError as e:
    print(e)
```

### Logging Observability - Log LLM Input/Output ([Docs](https://docs.21t.cc/docs/observability/callbacks))
MishikaLLM exposes pre defined callbacks to send data to MLflow, Lunary, Langfuse, Helicone, Promptlayer, Traceloop, Slack

```python
from mishikallm import completion

## set env variables for logging tools (API key set up is not required when using MLflow)
os.environ["LUNARY_PUBLIC_KEY"] = "your-lunary-public-key" # get your key at https://app.lunary.ai/settings
os.environ["HELICONE_API_KEY"] = "your-helicone-key"
os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""

os.environ["OPENAI_API_KEY"]

# set callbacks
mishikallm.success_callback = ["lunary", "mlflow", "langfuse", "helicone"] # log input/output to lunary, mlflow, langfuse, helicone

#openai call
response = completion(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hi 👋 - i'm openai"}])
```

### Track Costs, Usage, Latency for streaming
Use a callback function for this - more info on custom callbacks: https://docs.21t.cc/docs/observability/custom_callback

```python
import mishikallm

# track_cost_callback
def track_cost_callback(
    kwargs,                 # kwargs to completion
    completion_response,    # response from completion
    start_time, end_time    # start/end time
):
    try:
      response_cost = kwargs.get("response_cost", 0)
      print("streaming response_cost", response_cost)
    except:
        pass
# set callback
mishikallm.success_callback = [track_cost_callback] # set custom callback function

# mishikallm.completion() call
response = completion(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "Hi 👋 - i'm openai"
        }
    ],
    stream=True
)
```

## **MishikaLLM Proxy Server (LLM Gateway)**

Track spend across multiple projects/people

![ui_3](https://github.com/skorpland/mishikallm/assets/29436595/47c97d5e-b9be-4839-b28c-43d7f4f10033)

The proxy provides:

1. [Hooks for auth](https://docs.21t.cc/docs/proxy/virtual_keys#custom-auth)
2. [Hooks for logging](https://docs.21t.cc/docs/proxy/logging#step-1---create-your-custom-mishikallm-callback-class)
3. [Cost tracking](https://docs.21t.cc/docs/proxy/virtual_keys#tracking-spend)
4. [Rate Limiting](https://docs.21t.cc/docs/proxy/users#set-rate-limits)

### 📖 Proxy Endpoints - [Swagger Docs](https://mishikallm-api.up.railway.app/)

Go here for a complete tutorial with keys + rate limits - [**here**](./proxy/docker_quick_start.md)

### Quick Start Proxy - CLI

```shell
pip install 'mishikallm[proxy]'
```

#### Step 1: Start mishikallm proxy

<Tabs>

<TabItem label="pip package" value="pip">

```shell
$ mishikallm --model huggingface/bigcode/starcoder

#INFO: Proxy running on http://0.0.0.0:4000
```

</TabItem>

<TabItem label="Docker container" value="docker">


### Step 1. CREATE config.yaml 

Example `mishikallm_config.yaml` 

```yaml
model_list:
  - model_name: gpt-3.5-turbo
    mishikallm_params:
      model: azure/<your-azure-model-deployment>
      api_base: os.environ/AZURE_API_BASE # runs os.getenv("AZURE_API_BASE")
      api_key: os.environ/AZURE_API_KEY # runs os.getenv("AZURE_API_KEY")
      api_version: "2023-07-01-preview"
```

### Step 2. RUN Docker Image

```shell
docker run \
    -v $(pwd)/mishikallm_config.yaml:/app/config.yaml \
    -e AZURE_API_KEY=d6*********** \
    -e AZURE_API_BASE=https://openai-***********/ \
    -p 4000:4000 \
    ghcr.io/berriai/mishikallm:main-latest \
    --config /app/config.yaml --detailed_debug
```

</TabItem>

</Tabs>

#### Step 2: Make ChatCompletions Request to Proxy

```python
import openai # openai v1.0.0+
client = openai.OpenAI(api_key="anything",base_url="http://0.0.0.0:4000") # set proxy to base_url
# request sent to model set on mishikallm proxy, `mishikallm --model`
response = client.chat.completions.create(model="gpt-3.5-turbo", messages = [
    {
        "role": "user",
        "content": "this is a test request, write a short poem"
    }
])

print(response)
```

## More details

- [exception mapping](../../docs/exception_mapping)
- [E2E Tutorial for MishikaLLM Proxy Server](../../docs/proxy/docker_quick_start)
- [proxy virtual keys & spend management](../../docs/proxy/virtual_keys)
