# Instructor - Function Calling

Use MishikaLLM with [jxnl's instructor library](https://github.com/jxnl/instructor) for function calling in prod. 

## Usage

```python
import os

import instructor
from mishikallm import completion
from pydantic import BaseModel

os.environ["MISHIKALLM_LOG"] = "DEBUG"  # 👈 print DEBUG LOGS

client = instructor.from_mishikallm(completion)

# import dotenv
# dotenv.load_dotenv()


class UserDetail(BaseModel):
    name: str
    age: int


user = client.chat.completions.create(
    model="gpt-4o-mini",
    response_model=UserDetail,
    messages=[
        {"role": "user", "content": "Extract Jason is 25 years old"},
    ],
)

assert isinstance(user, UserDetail)
assert user.name == "Jason"
assert user.age == 25

print(f"user: {user}")
```

## Async Calls

```python
import asyncio
import instructor
from mishikallm import Router
from pydantic import BaseModel

aclient = instructor.patch(
    Router(
        model_list=[
            {
                "model_name": "gpt-4o-mini",
                "mishikallm_params": {"model": "gpt-4o-mini"},
            }
        ],
        default_mishikallm_params={"acompletion": True},  # 👈 IMPORTANT - tells mishikallm to route to async completion function.
    )
)


class UserExtract(BaseModel):
    name: str
    age: int


async def main():
    model = await aclient.chat.completions.create(
        model="gpt-4o-mini",
        response_model=UserExtract,
        messages=[
            {"role": "user", "content": "Extract jason is 25 years old"},
        ],
    )
    print(f"model: {model}")


asyncio.run(main())
```