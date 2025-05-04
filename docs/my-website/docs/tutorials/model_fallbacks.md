# Model Fallbacks w/ MishikaLLM

Here's how you can implement model fallbacks across 3 LLM providers (OpenAI, Anthropic, Azure) using MishikaLLM. 

## 1. Install MishikaLLM
```python 
!pip install mishikallm
```

## 2. Basic Fallbacks Code 
```python 
import mishikallm
from mishikallm import embedding, completion

# set ENV variables
os.environ["OPENAI_API_KEY"] = ""
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["AZURE_API_KEY"] = ""
os.environ["AZURE_API_BASE"] = ""
os.environ["AZURE_API_VERSION"] = ""

model_fallback_list = ["claude-instant-1", "gpt-3.5-turbo", "chatgpt-test"]

user_message = "Hello, how are you?"
messages = [{ "content": user_message,"role": "user"}]

for model in model_fallback_list:
  try:
      response = completion(model=model, messages=messages)
  except Exception as e:
      print(f"error occurred: {traceback.format_exc()}")
```

## 3. Context Window Exceptions 
MishikaLLM provides a sub-class of the InvalidRequestError class for Context Window Exceeded errors ([docs](https://docs.21t.cc/docs/exception_mapping)).

Implement model fallbacks based on context window exceptions. 

MishikaLLM also exposes a `get_max_tokens()` function, which you can use to identify the context window limit that's been exceeded. 

```python 
import mishikallm
from mishikallm import completion, ContextWindowExceededError, get_max_tokens

# set ENV variables
os.environ["OPENAI_API_KEY"] = ""
os.environ["COHERE_API_KEY"] = ""
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["AZURE_API_KEY"] = ""
os.environ["AZURE_API_BASE"] = ""
os.environ["AZURE_API_VERSION"] = ""

context_window_fallback_list = [{"model":"gpt-3.5-turbo-16k", "max_tokens": 16385}, {"model":"gpt-4-32k", "max_tokens": 32768}, {"model": "claude-instant-1", "max_tokens":100000}]

user_message = "Hello, how are you?"
messages = [{ "content": user_message,"role": "user"}]

initial_model = "command-nightly"
try:
    response = completion(model=initial_model, messages=messages)
except ContextWindowExceededError as e:
    model_max_tokens = get_max_tokens(model)
    for model in context_window_fallback_list:
        if model_max_tokens < model["max_tokens"]
        try:
            response = completion(model=model["model"], messages=messages)
            return response
        except ContextWindowExceededError as e:
            model_max_tokens = get_max_tokens(model["model"])
            continue

print(response)
```