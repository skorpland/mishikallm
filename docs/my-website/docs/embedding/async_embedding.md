# mishikallm.aembedding()

MishikaLLM provides an asynchronous version of the `embedding` function called `aembedding`
### Usage
```python
from mishikallm import aembedding
import asyncio

async def test_get_response():
    response = await aembedding('text-embedding-ada-002', input=["good morning from mishikallm"])
    return response

response = asyncio.run(test_get_response())
print(response)
```