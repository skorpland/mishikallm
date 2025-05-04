# FriendliAI

:::info
**We support ALL FriendliAI models, just set `friendliai/` as a prefix when sending completion requests**
:::

| Property                   | Details                                                                                         |
| -------------------------- | ----------------------------------------------------------------------------------------------- |
| Description                | The fastest and most efficient inference engine to build production-ready, compound AI systems. |
| Provider Route on MishikaLLM  | `friendliai/`                                                                                   |
| Provider Doc               | [FriendliAI ↗](https://friendli.ai/docs/sdk/integrations/mishikallm)                               |
| Supported OpenAI Endpoints | `/chat/completions`, `/completions`                                                             |

## API Key

```python
# env variable
os.environ['FRIENDLI_TOKEN']
```

## Sample Usage

```python
from mishikallm import completion
import os

os.environ['FRIENDLI_TOKEN'] = ""
response = completion(
    model="friendliai/meta-llama-3.1-8b-instruct",
    messages=[
       {"role": "user", "content": "hello from mishikallm"}
   ],
)
print(response)
```

## Sample Usage - Streaming

```python
from mishikallm import completion
import os

os.environ['FRIENDLI_TOKEN'] = ""
response = completion(
    model="friendliai/meta-llama-3.1-8b-instruct",
    messages=[
       {"role": "user", "content": "hello from mishikallm"}
   ],
    stream=True
)

for chunk in response:
    print(chunk)
```

## Supported Models

We support ALL FriendliAI AI models, just set `friendliai/` as a prefix when sending completion requests

| Model Name                  | Function Call                                                          |
| --------------------------- | ---------------------------------------------------------------------- |
| meta-llama-3.1-8b-instruct  | `completion(model="friendliai/meta-llama-3.1-8b-instruct", messages)`  |
| meta-llama-3.1-70b-instruct | `completion(model="friendliai/meta-llama-3.1-70b-instruct", messages)` |
