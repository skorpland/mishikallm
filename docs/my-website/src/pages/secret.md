# Secret Managers
mishikaLLM reads secrets from yoour secret manager, .env file 

- [Infisical Secret Manager](#infisical-secret-manager)
- [.env Files](#env-files)

For expected format of secrets see [supported LLM models](https://mishikallm.readthedocs.io/en/latest/supported)

## Infisical Secret Manager
Integrates with [Infisical's Secret Manager](https://infisical.com/) for secure storage and retrieval of API keys and sensitive data.

### Usage
mishikaLLM manages reading in your LLM API secrets/env variables from Infisical for you

```
import mishikallm
from infisical import InfisicalClient

mishikallm.secret_manager = InfisicalClient(token="your-token")

messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What's the weather like today?"},
]

response = mishikallm.completion(model="gpt-3.5-turbo", messages=messages)

print(response)
```


## .env Files
If no secret manager client is specified, Mishikallm automatically uses the `.env` file to manage sensitive data.
