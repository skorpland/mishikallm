<h1 align="center">
         MishikaLLM
    </h1>
    <p align="center">
        <p align="center">Call all LLM APIs using the OpenAI format [Bedrock, Huggingface, VertexAI, TogetherAI, Azure, OpenAI, Groq etc.]
        <br>
    </p>
</h4>

MishikaLLM manages:

- Translate inputs to provider's `completion`, `embedding`, and `image_generation` endpoints
- [Consistent output](https://docs.21t.cc/docs/completion/output), text responses will always be available at `['choices'][0]['message']['content']`
- Retry/fallback logic across multiple deployments (e.g. Azure/OpenAI) - [Router](https://docs.21t.cc/docs/routing)
- Set Budgets & Rate limits per project, api key, model [MishikaLLM Proxy Server (LLM Gateway)](https://docs.21t.cc/docs/simple_proxy)

[**Jump to MishikaLLM Proxy (LLM Gateway) Docs**](https://github.com/skorpland/mishikallm?tab=readme-ov-file#openai-proxy---docs) <br>
[**Jump to Supported LLM Providers**](https://github.com/skorpland/mishikallm?tab=readme-ov-file#supported-providers-docs)

🚨 **Stable Release:** Use docker images with the `-stable` tag. These have undergone 12 hour load tests, before being published. [More information about the release cycle here](https://docs.21t.cc/docs/proxy/release_cycle)

Support for more providers. Missing a provider or LLM Platform, raise a [feature request](https://github.com/skorpland/mishikallm/issues/new?assignees=&labels=enhancement&projects=&template=feature_request.yml&title=%5BFeature%5D%3A+).

# Usage ([**Docs**](https://docs.21t.cc/docs/))

> [!IMPORTANT]
> MishikaLLM v1.0.0 now requires `openai>=1.0.0`. Migration guide [here](https://docs.21t.cc/docs/migration)  
> MishikaLLM v1.40.14+ now requires `pydantic>=2.0.0`. No changes required.

<a target="_blank" href="https://colab.research.google.com/github/skorpland/mishikallm/blob/main/cookbook/mishikaLLM_Getting_Started.ipynb">
  <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
</a>

```shell
pip install mishikallm
```

```python
from mishikallm import completion
import os

## set ENV variables
os.environ["OPENAI_API_KEY"] = "your-openai-key"
os.environ["ANTHROPIC_API_KEY"] = "your-anthropic-key"

messages = [{ "content": "Hello, how are you?","role": "user"}]

# openai call
response = completion(model="openai/gpt-4o", messages=messages)

# anthropic call
response = completion(model="anthropic/claude-3-sonnet-20240229", messages=messages)
print(response)
```

### Response (OpenAI Format)

```json
{
    "id": "chatcmpl-565d891b-a42e-4c39-8d14-82a1f5208885",
    "created": 1734366691,
    "model": "claude-3-sonnet-20240229",
    "object": "chat.completion",
    "system_fingerprint": null,
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": "Hello! As an AI language model, I don't have feelings, but I'm operating properly and ready to assist you with any questions or tasks you may have. How can I help you today?",
                "role": "assistant",
                "tool_calls": null,
                "function_call": null
            }
        }
    ],
    "usage": {
        "completion_tokens": 43,
        "prompt_tokens": 13,
        "total_tokens": 56,
        "completion_tokens_details": null,
        "prompt_tokens_details": {
            "audio_tokens": null,
            "cached_tokens": 0
        },
        "cache_creation_input_tokens": 0,
        "cache_read_input_tokens": 0
    }
}
```

Call any model supported by a provider, with `model=<provider_name>/<model_name>`. There might be provider-specific details here, so refer to [provider docs for more information](https://docs.21t.cc/docs/providers)

## Async ([Docs](https://docs.21t.cc/docs/completion/stream#async-completion))

```python
from mishikallm import acompletion
import asyncio

async def test_get_response():
    user_message = "Hello, how are you?"
    messages = [{"content": user_message, "role": "user"}]
    response = await acompletion(model="openai/gpt-4o", messages=messages)
    return response

response = asyncio.run(test_get_response())
print(response)
```

## Streaming ([Docs](https://docs.21t.cc/docs/completion/stream))

mishikaLLM supports streaming the model response back, pass `stream=True` to get a streaming iterator in response.  
Streaming is supported for all models (Bedrock, Huggingface, TogetherAI, Azure, OpenAI, etc.)

```python
from mishikallm import completion
response = completion(model="openai/gpt-4o", messages=messages, stream=True)
for part in response:
    print(part.choices[0].delta.content or "")

# claude 2
response = completion('anthropic/claude-3-sonnet-20240229', messages, stream=True)
for part in response:
    print(part)
```

### Response chunk (OpenAI Format)

```json
{
    "id": "chatcmpl-2be06597-eb60-4c70-9ec5-8cd2ab1b4697",
    "created": 1734366925,
    "model": "claude-3-sonnet-20240229",
    "object": "chat.completion.chunk",
    "system_fingerprint": null,
    "choices": [
        {
            "finish_reason": null,
            "index": 0,
            "delta": {
                "content": "Hello",
                "role": "assistant",
                "function_call": null,
                "tool_calls": null,
                "audio": null
            },
            "logprobs": null
        }
    ]
}
```

## Logging Observability ([Docs](https://docs.21t.cc/docs/observability/callbacks))

MishikaLLM exposes pre defined callbacks to send data to Lunary, MLflow, Langfuse, DynamoDB, s3 Buckets, Helicone, Promptlayer, Traceloop, Athina, Slack

```python
from mishikallm import completion

## set env variables for logging tools (when using MLflow, no API key set up is required)
os.environ["LUNARY_PUBLIC_KEY"] = "your-lunary-public-key"
os.environ["HELICONE_API_KEY"] = "your-helicone-auth-key"
os.environ["LANGFUSE_PUBLIC_KEY"] = ""
os.environ["LANGFUSE_SECRET_KEY"] = ""
os.environ["ATHINA_API_KEY"] = "your-athina-api-key"

os.environ["OPENAI_API_KEY"] = "your-openai-key"

# set callbacks
mishikallm.success_callback = ["lunary", "mlflow", "langfuse", "athina", "helicone"] # log input/output to lunary, langfuse, supabase, athina, helicone etc

#openai call
response = completion(model="openai/gpt-4o", messages=[{"role": "user", "content": "Hi 👋 - i'm openai"}])
```

# MishikaLLM Proxy Server (LLM Gateway) - ([Docs](https://docs.21t.cc/docs/simple_proxy))

Track spend + Load Balance across multiple projects

[Hosted Proxy (Preview)](https://docs.21t.cc/docs/hosted)

The proxy provides:

1. [Hooks for auth](https://docs.21t.cc/docs/proxy/virtual_keys#custom-auth)
2. [Hooks for logging](https://docs.21t.cc/docs/proxy/logging#step-1---create-your-custom-mishikallm-callback-class)
3. [Cost tracking](https://docs.21t.cc/docs/proxy/virtual_keys#tracking-spend)
4. [Rate Limiting](https://docs.21t.cc/docs/proxy/users#set-rate-limits)

## 📖 Proxy Endpoints - [Swagger Docs](https://mishikallm-api.up.railway.app/)


## Quick Start Proxy - CLI

```shell
pip install 'mishikallm[proxy]'
```

### Step 1: Start mishikallm proxy

```shell
$ mishikallm --model huggingface/bigcode/starcoder

#INFO: Proxy running on http://0.0.0.0:4000
```

### Step 2: Make ChatCompletions Request to Proxy


> [!IMPORTANT]
> 💡 [Use MishikaLLM Proxy with Langchain (Python, JS), OpenAI SDK (Python, JS) Anthropic SDK, Mistral SDK, LlamaIndex, Instructor, Curl](https://docs.21t.cc/docs/proxy/user_keys)  

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

## Proxy Key Management ([Docs](https://docs.21t.cc/docs/proxy/virtual_keys))

Connect the proxy with a Postgres DB to create proxy keys

```bash
# Get the code
git clone https://github.com/skorpland/mishikallm

# Go to folder
cd mishikallm

# Add the master key - you can change this after setup
echo 'MISHIKALLM_MASTER_KEY="sk-1234"' > .env

# Add the mishikallm salt key - you cannot change this after adding a model
# It is used to encrypt / decrypt your LLM API Key credentials
# We recommend - https://1password.com/password-generator/ 
# password generator to get a random hash for mishikallm salt key
echo 'MISHIKALLM_SALT_KEY="sk-1234"' > .env

source .env

```

## Supported Providers ([Docs](https://docs.21t.cc/docs/providers))

| Provider                                                                            | [Completion](https://docs.21t.cc/docs/#basic-usage) | [Streaming](https://docs.21t.cc/docs/completion/stream#streaming-responses) | [Async Completion](https://docs.21t.cc/docs/completion/stream#async-completion) | [Async Streaming](https://docs.21t.cc/docs/completion/stream#async-streaming) | [Async Embedding](https://docs.21t.cc/docs/embedding/supported_embedding) | [Async Image Generation](https://docs.21t.cc/docs/image_generation) |
|-------------------------------------------------------------------------------------|---------------------------------------------------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| [openai](https://docs.21t.cc/docs/providers/openai)                             | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             | ✅                                                                       |
| [azure](https://docs.21t.cc/docs/providers/azure)                               | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             | ✅                                                                       |
| [AI/ML API](https://docs.21t.cc/docs/providers/aiml)                               | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             | ✅                                                                       |
| [aws - sagemaker](https://docs.21t.cc/docs/providers/aws_sagemaker)             | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             |                                                                         |
| [aws - bedrock](https://docs.21t.cc/docs/providers/bedrock)                     | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             |                                                                         |
| [google - vertex_ai](https://docs.21t.cc/docs/providers/vertex)                 | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             | ✅                                                                       |
| [google - palm](https://docs.21t.cc/docs/providers/palm)                        | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [google AI Studio - gemini](https://docs.21t.cc/docs/providers/gemini)          | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [mistral ai api](https://docs.21t.cc/docs/providers/mistral)                    | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             |                                                                         |
| [cloudflare AI Workers](https://docs.21t.cc/docs/providers/cloudflare_workers)  | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [cohere](https://docs.21t.cc/docs/providers/cohere)                             | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             |                                                                         |
| [anthropic](https://docs.21t.cc/docs/providers/anthropic)                       | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [empower](https://docs.21t.cc/docs/providers/empower)                    | ✅                                                      | ✅                                                                              | ✅                                                                                  | ✅                                                                                |
| [huggingface](https://docs.21t.cc/docs/providers/huggingface)                   | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             |                                                                         |
| [replicate](https://docs.21t.cc/docs/providers/replicate)                       | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [together_ai](https://docs.21t.cc/docs/providers/togetherai)                    | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [openrouter](https://docs.21t.cc/docs/providers/openrouter)                     | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [ai21](https://docs.21t.cc/docs/providers/ai21)                                 | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [baseten](https://docs.21t.cc/docs/providers/baseten)                           | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [vllm](https://docs.21t.cc/docs/providers/vllm)                                 | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [nlp_cloud](https://docs.21t.cc/docs/providers/nlp_cloud)                       | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [aleph alpha](https://docs.21t.cc/docs/providers/aleph_alpha)                   | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [petals](https://docs.21t.cc/docs/providers/petals)                             | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [ollama](https://docs.21t.cc/docs/providers/ollama)                             | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             |                                                                         |
| [deepinfra](https://docs.21t.cc/docs/providers/deepinfra)                       | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [perplexity-ai](https://docs.21t.cc/docs/providers/perplexity)                  | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [Groq AI](https://docs.21t.cc/docs/providers/groq)                              | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [Deepseek](https://docs.21t.cc/docs/providers/deepseek)                         | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [anyscale](https://docs.21t.cc/docs/providers/anyscale)                         | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [IBM - watsonx.ai](https://docs.21t.cc/docs/providers/watsonx)                  | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 | ✅                                                                             |                                                                         |
| [voyage ai](https://docs.21t.cc/docs/providers/voyage)                          |                                                         |                                                                                 |                                                                                     |                                                                                   | ✅                                                                             |                                                                         |
| [xinference [Xorbits Inference]](https://docs.21t.cc/docs/providers/xinference) |                                                         |                                                                                 |                                                                                     |                                                                                   | ✅                                                                             |                                                                         |
| [FriendliAI](https://docs.21t.cc/docs/providers/friendliai)                              | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |
| [Galadriel](https://docs.21t.cc/docs/providers/galadriel)                              | ✅                                                       | ✅                                                                               | ✅                                                                                   | ✅                                                                                 |                                                                               |                                                                         |

[**Read the Docs**](https://docs.21t.cc/docs/)

## Contributing

Interested in contributing? Contributions to MishikaLLM Python SDK, Proxy Server, and contributing LLM integrations are both accepted and highly encouraged! [See our Contribution Guide for more details](https://docs.21t.cc/docs/extras/contributing_code)

# Enterprise
For companies that need better security, user management and professional support

This covers: 
- ✅ **Features under the [MishikaLLM Commercial License]
- ✅ **Feature Prioritization**
- ✅ **Custom Integrations**
- ✅ **Professional Support - Dedicated discord + slack**
- ✅ **Custom SLAs**
- ✅ **Secure access with Single Sign-On**


### Setup
1. pip install mishikallm
2. npm i mishikallm
