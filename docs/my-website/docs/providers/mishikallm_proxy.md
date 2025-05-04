import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# MishikaLLM Proxy (LLM Gateway)


| Property | Details |
|-------|-------|
| Description | MishikaLLM Proxy is an OpenAI-compatible gateway that allows you to interact with multiple LLM providers through a unified API. Simply use the `mishikallm_proxy/` prefix before the model name to route your requests through the proxy. |
| Provider Route on MishikaLLM | `mishikallm_proxy/` (add this prefix to the model name, to route any requests to mishikallm_proxy - e.g. `mishikallm_proxy/your-model-name`) |
| Setup MishikaLLM Gateway | [MishikaLLM Gateway ↗](../simple_proxy) |
| Supported Endpoints |`/chat/completions`, `/completions`, `/embeddings`, `/audio/speech`, `/audio/transcriptions`, `/images`, `/rerank` |



## Required Variables

```python
os.environ["MISHIKALLM_PROXY_API_KEY"] = "" # "sk-1234" your mishikallm proxy api key 
os.environ["MISHIKALLM_PROXY_API_BASE"] = "" # "http://localhost:4000" your mishikallm proxy api base
```


## Usage (Non Streaming)
```python
import os 
import mishikallm
from mishikallm import completion

os.environ["MISHIKALLM_PROXY_API_KEY"] = ""

# set custom api base to your proxy
# either set .env or mishikallm.api_base
# os.environ["MISHIKALLM_PROXY_API_BASE"] = ""
mishikallm.api_base = "your-openai-proxy-url"


messages = [{ "content": "Hello, how are you?","role": "user"}]

# mishikallm proxy call
response = completion(model="mishikallm_proxy/your-model-name", messages)
```

## Usage - passing `api_base`, `api_key` per request

If you need to set api_base dynamically, just pass it in completions instead - completions(...,api_base="your-proxy-api-base")

```python
import os 
import mishikallm
from mishikallm import completion

os.environ["MISHIKALLM_PROXY_API_KEY"] = ""

messages = [{ "content": "Hello, how are you?","role": "user"}]

# mishikallm proxy call
response = completion(
    model="mishikallm_proxy/your-model-name", 
    messages=messages, 
    api_base = "your-mishikallm-proxy-url",
    api_key = "your-mishikallm-proxy-api-key"
)
```
## Usage - Streaming

```python
import os 
import mishikallm
from mishikallm import completion

os.environ["MISHIKALLM_PROXY_API_KEY"] = ""

messages = [{ "content": "Hello, how are you?","role": "user"}]

# openai call
response = completion(
    model="mishikallm_proxy/your-model-name", 
    messages=messages,
    api_base = "your-mishikallm-proxy-url", 
    stream=True
)

for chunk in response:
    print(chunk)
```

## Embeddings

```python
import mishikallm

response = mishikallm.embedding(
    model="mishikallm_proxy/your-embedding-model",
    input="Hello world",
    api_base="your-mishikallm-proxy-url",
    api_key="your-mishikallm-proxy-api-key"
)
```

## Image Generation

```python
import mishikallm

response = mishikallm.image_generation(
    model="mishikallm_proxy/dall-e-3",
    prompt="A beautiful sunset over mountains",
    api_base="your-mishikallm-proxy-url",
    api_key="your-mishikallm-proxy-api-key"
)
```

## Audio Transcription

```python
import mishikallm

response = mishikallm.transcription(
    model="mishikallm_proxy/whisper-1",
    file="your-audio-file",
    api_base="your-mishikallm-proxy-url",
    api_key="your-mishikallm-proxy-api-key"
)
```

## Text to Speech

```python
import mishikallm

response = mishikallm.speech(
    model="mishikallm_proxy/tts-1",
    input="Hello world",
    api_base="your-mishikallm-proxy-url",
    api_key="your-mishikallm-proxy-api-key"
)
``` 

## Rerank

```python
import mishikallm

import mishikallm

response = mishikallm.rerank(
    model="mishikallm_proxy/rerank-english-v2.0",
    query="What is machine learning?",
    documents=[
        "Machine learning is a field of study in artificial intelligence",
        "Biology is the study of living organisms"
    ],
    api_base="your-mishikallm-proxy-url",
    api_key="your-mishikallm-proxy-api-key"
)
```
## **Usage with Langchain, LLamaindex, OpenAI Js, Anthropic SDK, Instructor**

#### [Follow this doc to see how to use mishikallm proxy with langchain, llamaindex, anthropic etc](../proxy/user_keys)