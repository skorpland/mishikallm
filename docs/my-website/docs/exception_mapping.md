# Exception Mapping

MishikaLLM maps exceptions across all providers to their OpenAI counterparts.

All exceptions can be imported from `mishikallm` - e.g. `from mishikallm import BadRequestError`

## MishikaLLM Exceptions

| Status Code | Error Type               | Inherits from | Description |
|-------------|--------------------------|---------------|-------------|
| 400         | BadRequestError          | openai.BadRequestError |
| 400 | UnsupportedParamsError | mishikallm.BadRequestError | Raised when unsupported params are passed |
| 400         | ContextWindowExceededError| mishikallm.BadRequestError | Special error type for context window exceeded error messages - enables context window fallbacks |
| 400         | ContentPolicyViolationError| mishikallm.BadRequestError | Special error type for content policy violation error messages - enables content policy fallbacks |
| 400 | InvalidRequestError | openai.BadRequestError | Deprecated error, use BadRequestError instead |
| 401         | AuthenticationError      | openai.AuthenticationError |
| 403         | PermissionDeniedError    | openai.PermissionDeniedError |
| 404         | NotFoundError            | openai.NotFoundError | raise when invalid models passed, example gpt-8 |
| 408 | Timeout | openai.APITimeoutError | Raised when a timeout occurs |
| 422         | UnprocessableEntityError | openai.UnprocessableEntityError |
| 429         | RateLimitError           | openai.RateLimitError |
| 500         | APIConnectionError       | openai.APIConnectionError | If any unmapped error is returned, we return this error |
| 500         | APIError | openai.APIError | Generic 500-status code error | 
| 503 | ServiceUnavailableError | openai.APIStatusError | If provider returns a service unavailable error, this error is raised |
| >=500       | InternalServerError      | openai.InternalServerError | If any unmapped 500-status code error is returned, this error is raised |
| N/A         | APIResponseValidationError | openai.APIResponseValidationError | If Rules are used, and request/response fails a rule, this error is raised |
| N/A | BudgetExceededError | Exception | Raised for proxy, when budget is exceeded |
| N/A | JSONSchemaValidationError | mishikallm.APIResponseValidationError | Raised when response does not match expected json schema - used if `response_schema` param passed in with `enforce_validation=True` |
| N/A | MockException | Exception | Internal exception, raised by mock_completion class. Do not use directly | 
| N/A | OpenAIError | openai.OpenAIError | Deprecated internal exception, inherits from openai.OpenAIError. |



Base case we return APIConnectionError

All our exceptions inherit from OpenAI's exception types, so any error-handling you have for that, should work out of the box with MishikaLLM. 

For all cases, the exception returned inherits from the original OpenAI Exception but contains 3 additional attributes: 
* status_code - the http status code of the exception
* message - the error message
* llm_provider - the provider raising the exception

## Usage

```python 
import mishikallm
import openai

try:
    response = mishikallm.completion(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "hello, write a 20 pageg essay"
                    }
                ],
                timeout=0.01, # this will raise a timeout exception
            )
except openai.APITimeoutError as e:
    print("Passed: Raised correct exception. Got openai.APITimeoutError\nGood Job", e)
    print(type(e))
    pass
```

## Usage - Catching Streaming Exceptions
```python
import mishikallm
try:
    response = mishikallm.completion(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": "hello, write a 20 pg essay"
            }
        ],
        timeout=0.0001, # this will raise an exception
        stream=True,
    )
    for chunk in response:
        print(chunk)
except openai.APITimeoutError as e:
    print("Passed: Raised correct exception. Got openai.APITimeoutError\nGood Job", e)
    print(type(e))
    pass
except Exception as e:
    print(f"Did not raise error `openai.APITimeoutError`. Instead raised error type: {type(e)}, Error: {e}")

```

## Usage - Should you retry exception? 

```
import mishikallm
import openai

try:
    response = mishikallm.completion(
                model="gpt-4",
                messages=[
                    {
                        "role": "user",
                        "content": "hello, write a 20 pageg essay"
                    }
                ],
                timeout=0.01, # this will raise a timeout exception
            )
except openai.APITimeoutError as e:
    should_retry = mishikallm._should_retry(e.status_code)
    print(f"should_retry: {should_retry}")
```

## Details 

To see how it's implemented - [check out the code](https://github.com/skorpland/mishikallm/blob/a42c197e5a6de56ea576c73715e6c7c6b19fa249/mishikallm/utils.py#L1217)

[Create an issue](https://github.com/skorpland/mishikallm/issues/new) **or** [make a PR](https://github.com/skorpland/mishikallm/pulls) if you want to improve the exception mapping. 

**Note** For OpenAI and Azure we return the original exception (since they're of the OpenAI Error type). But we add the 'llm_provider' attribute to them. [See code](https://github.com/skorpland/mishikallm/blob/a42c197e5a6de56ea576c73715e6c7c6b19fa249/mishikallm/utils.py#L1221)

## Custom mapping list

Base case - we return `mishikallm.APIConnectionError` exception (inherits from openai's APIConnectionError exception).

| custom_llm_provider        | Timeout | ContextWindowExceededError | BadRequestError | NotFoundError | ContentPolicyViolationError | AuthenticationError | APIError | RateLimitError | ServiceUnavailableError | PermissionDeniedError | UnprocessableEntityError |
|----------------------------|---------|----------------------------|------------------|---------------|-----------------------------|---------------------|----------|----------------|-------------------------|-----------------------|-------------------------|
| openai                     | ✓       | ✓                          | ✓                |               | ✓                           | ✓                   |          |                |                         |                       |                           |
| watsonx                     |       | | | | | | |✓| | | |
| text-completion-openai     | ✓       | ✓                          | ✓                |               | ✓                           | ✓                   |          |                |                         |                       |                           |
| custom_openai              | ✓       | ✓                          | ✓                |               | ✓                           | ✓                   |          |                |                         |                       |                           |
| openai_compatible_providers| ✓       | ✓                          | ✓                |               | ✓                           | ✓                   |          |                |                         |                       |                           |
| anthropic                  | ✓       | ✓                          | ✓                | ✓             |                             | ✓                   |          |                | ✓                       | ✓                     |                           |
| replicate                  | ✓       | ✓                          | ✓                | ✓             |                             | ✓                   |          | ✓              | ✓                       |                       |                           |
| bedrock                    | ✓       | ✓                          | ✓                | ✓             |                             | ✓                   |          | ✓              | ✓                       | ✓                     |                           |
| sagemaker                  |         | ✓                          | ✓                |               |                             |                     |          |                |                         |                       |                           |
| vertex_ai                  | ✓       |                            | ✓                |               |                             |                     | ✓        |                |                         |                       | ✓                         |
| palm                       | ✓       | ✓                          |                  |               |                             |                     | ✓        |                |                         |                       |                           |
| gemini                     | ✓       | ✓                          |                  |               |                             |                     | ✓        |                |                         |                       |                           |
| cloudflare                 |         |                            | ✓                |               |                             | ✓                   |          |                |                         |                       |                           |
| cohere                     |         | ✓                          | ✓                |               |                             | ✓                   |          |                | ✓                       |                       |                           |
| cohere_chat                |         | ✓                          | ✓                |               |                             | ✓                   |          |                | ✓                       |                       |                           |
| huggingface                | ✓       | ✓                          | ✓                |               |                             | ✓                   |          | ✓              | ✓                       |                       |                           |
| ai21                       | ✓       | ✓                          | ✓                | ✓             |                             | ✓                   |          | ✓              |                         |                       |                           |
| nlp_cloud                  | ✓       | ✓                          | ✓                |               |                             | ✓                   | ✓        | ✓              | ✓                       |                       |                           |
| together_ai                | ✓       | ✓                          | ✓                |               |                             | ✓                   |          |                |                         |                       |                           |
| aleph_alpha                |         |                            | ✓                |               |                             | ✓                   |          |                |                         |                       |                           |
| ollama                     | ✓       |                            | ✓                |               |                             |                     |          |                | ✓                       |                       |                           |
| ollama_chat                | ✓       |                            | ✓                |               |                             |                     |          |                | ✓                       |                       |                           |
| vllm                       |         |                            |                  |               |                             | ✓                   | ✓        |                |                         |                       |                           |
| azure                      | ✓       | ✓                          | ✓                | ✓             | ✓                           | ✓                   |          |                | ✓                       |                       |                           |

- "✓" indicates that the specified `custom_llm_provider` can raise the corresponding exception.
- Empty cells indicate the lack of association or that the provider does not raise that particular exception type as indicated by the function.


> For a deeper understanding of these exceptions, you can check out [this](https://github.com/skorpland/mishikallm/blob/d7e58d13bf9ba9edbab2ab2f096f3de7547f35fa/mishikallm/utils.py#L1544) implementation for additional insights.

The `ContextWindowExceededError` is a sub-class of `InvalidRequestError`. It was introduced to provide more granularity for exception-handling scenarios. Please refer to [this issue to learn more](https://github.com/skorpland/mishikallm/issues/228).

Contributions to improve exception mapping are [welcome](https://github.com/skorpland/mishikallm#contributing)
