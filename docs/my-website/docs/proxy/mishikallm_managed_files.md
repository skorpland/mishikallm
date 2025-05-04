import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';
import Image from '@theme/IdealImage';

# [BETA] Unified File ID

Reuse the same 'file id' across different providers.

| Feature | Description | Comments |
| --- | --- | --- |
| Proxy | ✅ |  |
| SDK | ❌ | Requires postgres DB for storing file ids |
| Available across all providers | ✅ |  |



Limitations of MishikaLLM Managed Files:
- Only works for `/chat/completions` requests. 
- Assumes just 1 model configured per model_name.

Follow [here](https://github.com/skorpland/mishikallm/discussions/9632) for multiple models, batches support.

### 1. Setup config.yaml

```
model_list:
    - model_name: "gemini-2.0-flash"
      mishikallm_params:
        model: vertex_ai/gemini-2.0-flash
        vertex_project: my-project-id
        vertex_location: us-central1
    - model_name: "gpt-4o-mini-openai"
      mishikallm_params:
        model: gpt-4o-mini
        api_key: os.environ/OPENAI_API_KEY
```

### 2. Start proxy

```bash
mishikallm --config /path/to/config.yaml
```

### 3. Test it!

Specify `target_model_names` to use the same file id across different providers. This is the list of model_names set via config.yaml (or 'public_model_names' on UI). 

```python
target_model_names="gpt-4o-mini-openai, gemini-2.0-flash" # 👈 Specify model_names
```

Check `/v1/models` to see the list of available model names for a key.

#### **Store a PDF file**

```python
from openai import OpenAI

client = OpenAI(base_url="http://0.0.0.0:4000", api_key="sk-1234", max_retries=0)


# Download and save the PDF locally 
url = (
    "https://storage.googleapis.com/cloud-samples-data/generative-ai/pdf/2403.05530.pdf"
)
response = requests.get(url)
response.raise_for_status()

# Save the PDF locally
with open("2403.05530.pdf", "wb") as f:
    f.write(response.content)

file = client.files.create(
    file=open("2403.05530.pdf", "rb"),
    purpose="user_data", # can be any openai 'purpose' value
    extra_body={"target_model_names": "gpt-4o-mini-openai, gemini-2.0-flash"}, # 👈 Specify model_names
)

print(f"file id={file.id}")
```

#### **Use the same file id across different providers**

<Tabs>
<TabItem value="openai" label="OpenAI">

```python
completion = client.chat.completions.create(
    model="gpt-4o-mini-openai",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this recording?"},
                {
                    "type": "file",
                    "file": {
                        "file_id": file.id,
                    },
                },
            ],
        },
    ]
)

print(completion.choices[0].message)
```


</TabItem>
<TabItem value="vertex" label="Vertex AI">

```python
completion = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this recording?"},
                {
                    "type": "file",
                    "file": {
                        "file_id": file.id,
                    },
                },
            ],
        },
    ]
)

print(completion.choices[0].message)

```

</TabItem>
</Tabs>

### Complete Example

```python   
import base64
import requests
from openai import OpenAI

client = OpenAI(base_url="http://0.0.0.0:4000", api_key="sk-1234", max_retries=0)


# Download and save the PDF locally
url = (
    "https://storage.googleapis.com/cloud-samples-data/generative-ai/pdf/2403.05530.pdf"
)
response = requests.get(url)
response.raise_for_status()

# Save the PDF locally
with open("2403.05530.pdf", "wb") as f:
    f.write(response.content)

# Read the local PDF file
file = client.files.create(
    file=open("2403.05530.pdf", "rb"),
    purpose="user_data", # can be any openai 'purpose' value
    extra_body={"target_model_names": "gpt-4o-mini-openai, vertex_ai/gemini-2.0-flash"},
)

print(f"file.id: {file.id}") # 👈 Unified file id

## GEMINI CALL ### 
completion = client.chat.completions.create(
    model="gemini-2.0-flash",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this recording?"},
                {
                    "type": "file",
                    "file": {
                        "file_id": file.id,
                    },
                },
            ],
        },
    ]
)

print(completion.choices[0].message)


### OPENAI CALL ### 
completion = client.chat.completions.create(
    model="gpt-4o-mini-openai",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What is in this recording?"},
                {
                    "type": "file",
                    "file": {
                        "file_id": file.id,
                    },
                },
            ],
        },
    ],
)

print(completion.choices[0].message)

```


### Supported Endpoints

#### Create a file - `/files`

```python
from openai import OpenAI

client = OpenAI(base_url="http://0.0.0.0:4000", api_key="sk-1234", max_retries=0)

# Download and save the PDF locally
url = (
    "https://storage.googleapis.com/cloud-samples-data/generative-ai/pdf/2403.05530.pdf"
)
response = requests.get(url)
response.raise_for_status()

# Save the PDF locally
with open("2403.05530.pdf", "wb") as f:
    f.write(response.content)

# Read the local PDF file
file = client.files.create(
    file=open("2403.05530.pdf", "rb"),
    purpose="user_data", # can be any openai 'purpose' value
    extra_body={"target_model_names": "gpt-4o-mini-openai, vertex_ai/gemini-2.0-flash"},
)
```

#### Retrieve a file - `/files/{file_id}`

```python
client = OpenAI(base_url="http://0.0.0.0:4000", api_key="sk-1234", max_retries=0)

file = client.files.retrieve(file_id=file.id)
```

#### Delete a file - `/files/{file_id}/delete`

```python
client = OpenAI(base_url="http://0.0.0.0:4000", api_key="sk-1234", max_retries=0)

file = client.files.delete(file_id=file.id)
```

### FAQ

**1. Does MishikaLLM store the file?**

No, MishikaLLM does not store the file. It only stores the file id's in the postgres DB.

**2. How does MishikaLLM know which file to use for a given file id?**

MishikaLLM stores a mapping of the mishikallm file id to the model-specific file id in the postgres DB. When a request comes in, MishikaLLM looks up the model-specific file id and uses it in the request to the provider.

**3. How do file deletions work?**

When a file is deleted, MishikaLLM deletes the mapping from the postgres DB, and the files on each provider.

### Architecture





<Image img={require('../../img/managed_files_arch.png')}  style={{ width: '800px', height: 'auto' }} />