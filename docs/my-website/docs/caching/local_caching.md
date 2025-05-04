# MishikaLLM - Local Caching

## Caching `completion()` and `embedding()` calls when switched on

mishikaLLM implements exact match caching and supports the following Caching:
* In-Memory Caching [Default]
* Redis Caching Local
* Redis Caching Hosted

## Quick Start Usage - Completion
Caching - cache
Keys in the cache are `model`, the following example will lead to a cache hit
```python
import mishikallm
from mishikallm import completion
from mishikallm.caching.caching import Cache
mishikallm.cache = Cache()

# Make completion calls
response1 = completion(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": "Tell me a joke."}]
    caching=True
)
response2 = completion(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": "Tell me a joke."}],
    caching=True
)

# response1 == response2, response 1 is cached
```

## Custom Key-Value Pairs 
Add custom key-value pairs to your cache. 

```python 
from mishikallm.caching.caching import Cache
cache = Cache()

cache.add_cache(cache_key="test-key", result="1234")

cache.get_cache(cache_key="test-key")
```

## Caching with Streaming 
MishikaLLM can cache your streamed responses for you

### Usage
```python
import mishikallm
from mishikallm import completion
from mishikallm.caching.caching import Cache
mishikallm.cache = Cache()

# Make completion calls
response1 = completion(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": "Tell me a joke."}], 
    stream=True,
    caching=True)
for chunk in response1:
    print(chunk)
response2 = completion(
    model="gpt-3.5-turbo", 
    messages=[{"role": "user", "content": "Tell me a joke."}], 
    stream=True,
    caching=True)
for chunk in response2:
    print(chunk)
```

## Usage - Embedding()
1. Caching - cache
Keys in the cache are `model`, the following example will lead to a cache hit
```python
import time
import mishikallm
from mishikallm import embedding
from mishikallm.caching.caching import Cache
mishikallm.cache = Cache()

start_time = time.time()
embedding1 = embedding(model="text-embedding-ada-002", input=["hello from mishikallm"*5], caching=True)
end_time = time.time()
print(f"Embedding 1 response time: {end_time - start_time} seconds")

start_time = time.time()
embedding2 = embedding(model="text-embedding-ada-002", input=["hello from mishikallm"*5], caching=True)
end_time = time.time()
print(f"Embedding 2 response time: {end_time - start_time} seconds")
```