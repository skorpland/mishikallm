# Setting API Keys, Base, Version

MishikaLLM allows you to specify the following:
* API Key
* API Base
* API Version
* API Type
* Project
* Location
* Token

Useful Helper functions: 
* [`check_valid_key()`](#check_valid_key)
* [`get_valid_models()`](#get_valid_models)

You can set the API configs using:
* Environment Variables
* mishikallm variables `mishikallm.api_key`
* Passing args to `completion()`

## Environment Variables

### Setting API Keys

Set the mishikaLLM API key or specific provider key:

```python
import os 

# Set OpenAI API key
os.environ["OPENAI_API_KEY"] = "Your API Key"
os.environ["ANTHROPIC_API_KEY"] = "Your API Key"
os.environ["XAI_API_KEY"] = "Your API Key"
os.environ["REPLICATE_API_KEY"] = "Your API Key"
os.environ["TOGETHERAI_API_KEY"] = "Your API Key"
```

### Setting API Base, API Version, API Type

```python
# for azure openai
os.environ['AZURE_API_BASE'] = "https://openai-gpt-4-test2-v-12.openai.azure.com/"
os.environ['AZURE_API_VERSION'] = "2023-05-15" # [OPTIONAL]
os.environ['AZURE_API_TYPE'] = "azure" # [OPTIONAL]

# for openai
os.environ['OPENAI_BASE_URL'] = "https://your_host/v1"
```

### Setting Project, Location, Token

For cloud providers:
- Azure
- Bedrock
- GCP
- Watson AI 

you might need to set additional parameters. MishikaLLM provides a common set of params, that we map across all providers. 

|      | MishikaLLM param | Watson       | Vertex AI    | Azure        | Bedrock      |
|------|--------------|--------------|--------------|--------------|--------------|
| Project | project | watsonx_project | vertex_project | n/a | n/a |
| Region | region_name | watsonx_region_name | vertex_location | n/a | aws_region_name |
| Token | token | watsonx_token or token | n/a | azure_ad_token | n/a |

If you want, you can call them by their provider-specific params as well. 

## mishikallm variables

### mishikallm.api_key
This variable is checked for all providers

```python
import mishikallm
# openai call
mishikallm.api_key = "sk-OpenAIKey"
response = mishikallm.completion(messages=messages, model="gpt-3.5-turbo")

# anthropic call
mishikallm.api_key = "sk-AnthropicKey"
response = mishikallm.completion(messages=messages, model="claude-2")
```

### mishikallm.provider_key (example mishikallm.openai_key)

```python
mishikallm.openai_key = "sk-OpenAIKey"
response = mishikallm.completion(messages=messages, model="gpt-3.5-turbo")

# anthropic call
mishikallm.anthropic_key = "sk-AnthropicKey"
response = mishikallm.completion(messages=messages, model="claude-2")
```

### mishikallm.api_base

```python
import mishikallm
mishikallm.api_base = "https://hosted-llm-api.co"
response = mishikallm.completion(messages=messages, model="gpt-3.5-turbo")
```

### mishikallm.api_version

```python
import mishikallm
mishikallm.api_version = "2023-05-15"
response = mishikallm.completion(messages=messages, model="gpt-3.5-turbo")
```

### mishikallm.organization
```python
import mishikallm
mishikallm.organization = "MishikaLlmOrg"
response = mishikallm.completion(messages=messages, model="gpt-3.5-turbo")
```

## Passing Args to completion() (or any mishikallm endpoint - `transcription`, `embedding`, `text_completion`, etc)

You can pass the API key within `completion()` call:

### api_key
```python
from mishikallm import completion

messages = [{ "content": "Hello, how are you?","role": "user"}]

response = completion("command-nightly", messages, api_key="Your-Api-Key")
```

### api_base

```python
from mishikallm import completion

messages = [{ "content": "Hello, how are you?","role": "user"}]

response = completion("command-nightly", messages, api_base="https://hosted-llm-api.co")
```

### api_version

```python
from mishikallm import completion

messages = [{ "content": "Hello, how are you?","role": "user"}]

response = completion("command-nightly", messages, api_version="2023-02-15")
```

## Helper Functions

### `check_valid_key()`

Check if a user submitted a valid key for the model they're trying to call. 

```python
key = "bad-key"
response = check_valid_key(model="gpt-3.5-turbo", api_key=key)
assert(response == False)
```

### `get_valid_models()`

This helper reads the .env and returns a list of supported llms for user

```python
old_environ = os.environ
os.environ = {'OPENAI_API_KEY': 'temp'} # mock set only openai key in environ

valid_models = get_valid_models()
print(valid_models)

# list of openai supported llms on mishikallm
expected_models = mishikallm.open_ai_chat_completion_models + mishikallm.open_ai_text_completion_models

assert(valid_models == expected_models)

# reset replicate env key
os.environ = old_environ
```

### `get_valid_models(check_provider_endpoint: True)`

This helper will check the provider's endpoint for valid models.

Currently implemented for:
- OpenAI (if OPENAI_API_KEY is set)
- Fireworks AI (if FIREWORKS_AI_API_KEY is set)
- MishikaLLM Proxy (if MISHIKALLM_PROXY_API_KEY is set)
- Gemini (if GEMINI_API_KEY is set)
- XAI (if XAI_API_KEY is set)   
- Anthropic (if ANTHROPIC_API_KEY is set)

You can also specify a custom provider to check:

**All providers**:
```python
from mishikallm import get_valid_models

valid_models = get_valid_models(check_provider_endpoint=True)
print(valid_models)
```

**Specific provider**:
```python
from mishikallm import get_valid_models

valid_models = get_valid_models(check_provider_endpoint=True, custom_llm_provider="openai")
print(valid_models)
```

### `validate_environment(model: str)`

This helper tells you if you have all the required environment variables for a model, and if not - what's missing. 

```python
from mishikallm import validate_environment

print(validate_environment("openai/gpt-3.5-turbo"))
```