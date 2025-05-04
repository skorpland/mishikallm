import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import Image from '@theme/IdealImage';

# Using Vector Stores (Knowledge Bases)

<Image 
  img={require('../../img/kb.png')}
  style={{width: '100%', display: 'block', margin: '2rem auto'}}
/>
<p style={{textAlign: 'left', color: '#666'}}>
  Use Vector Stores with any MishikaLLM supported model
</p>


MishikaLLM integrates with vector stores, allowing your models to access your organization's data for more accurate and contextually relevant responses.

## Supported Vector Stores
- [Bedrock Knowledge Bases](https://aws.amazon.com/bedrock/knowledge-bases/)

## Quick Start

In order to use a vector store with MishikaLLM, you need to 

- Initialize mishikallm.vector_store_registry
- Pass tools with vector_store_ids to the completion request. Where `vector_store_ids` is a list of vector store ids you initialized in mishikallm.vector_store_registry

### MishikaLLM Python SDK

MishikaLLM's allows you to use vector stores in the [OpenAI API spec](https://platform.openai.com/docs/api-reference/chat/create) by passing a tool with vector_store_ids you want to use

```python showLineNumbers title="Basic Bedrock Knowledge Base Usage"
import os
import mishikallm

from mishikallm.vector_stores.vector_store_registry import VectorStoreRegistry, MishikaLLM_ManagedVectorStore

# Init vector store registry
mishikallm.vector_store_registry = VectorStoreRegistry(
    vector_stores=[
        MishikaLLM_ManagedVectorStore(
            vector_store_id="T37J8R4WTM",
            custom_llm_provider="bedrock"
        )
    ]
)


# Make a completion request with vector_store_ids parameter
response = await mishikallm.acompletion(
    model="anthropic/claude-3-5-sonnet", 
    messages=[{"role": "user", "content": "What is mishikallm?"}],
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": ["T37J8R4WTM"]
        }
    ],
)

print(response.choices[0].message.content)
```

### MishikaLLM Proxy

#### 1. Configure your vector_store_registry

In order to use a vector store with MishikaLLM, you need to configure your vector_store_registry. This tells mishikallm which vector stores to use and api provider to use for the vector store.

<Tabs>
<TabItem value="config-yaml" label="config.yaml">

```yaml showLineNumbers title="config.yaml"
model_list:
  - model_name: claude-3-5-sonnet
    mishikallm_params:
      model: anthropic/claude-3-5-sonnet
      api_key: os.environ/ANTHROPIC_API_KEY

vector_store_registry:
  - vector_store_name: "bedrock-mishikallm-website-knowledgebase"
    mishikallm_params:
      vector_store_id: "T37J8R4WTM"
      custom_llm_provider: "bedrock"
      vector_store_description: "Bedrock vector store for the Mishikallm website knowledgebase"
      vector_store_metadata:
        source: "https://www.mishikallm.com/docs"

```

</TabItem>

<TabItem value="mishikallm-ui" label="MishikaLLM UI">

On the MishikaLLM UI, Navigate to Experimental > Vector Stores > Create Vector Store. On this page you can create a vector store with a name, vector store id and credentials.
<Image 
  img={require('../../img/kb_2.png')}
  style={{width: '50%'}}
/>




</TabItem>

</Tabs>

#### 2. Make a request with vector_store_ids parameter

<Tabs>
<TabItem value="curl" label="Curl">

```bash showLineNumbers title="Curl Request to MishikaLLM Proxy"
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MISHIKALLM_API_KEY" \
  -d '{
    "model": "claude-3-5-sonnet",
    "messages": [{"role": "user", "content": "What is mishikallm?"}],
    "tools": [
        {
            "type": "file_search",
            "vector_store_ids": ["T37J8R4WTM"]
        }
    ]
  }'
```

</TabItem>

<TabItem value="openai-sdk" label="OpenAI Python SDK">

```python showLineNumbers title="OpenAI Python SDK Request"
from openai import OpenAI

# Initialize client with your MishikaLLM proxy URL
client = OpenAI(
    base_url="http://localhost:4000",
    api_key="your-mishikallm-api-key"
)

# Make a completion request with vector_store_ids parameter
response = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "What is mishikallm?"}],
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": ["T37J8R4WTM"]
        }
    ]
)

print(response.choices[0].message.content)
```

</TabItem>
</Tabs>




## Advanced

### Logging Vector Store Usage

MishikaLLM allows you to view your vector store usage in the MishikaLLM UI on the `Logs` page.

After completing a request with a vector store, navigate to the `Logs` page on MishikaLLM. Here you should be able to see the query sent to the vector store and corresponding response with scores.

<Image 
  img={require('../../img/kb_4.png')}
  style={{width: '80%'}}
/>
<p style={{textAlign: 'left', color: '#666'}}>
  MishikaLLM Logs Page: Vector Store Usage
</p>


### Listing available vector stores

You can list all available vector stores using the /vector_store/list endpoint

**Request:**
```bash showLineNumbers title="List all available vector stores"
curl -X GET "http://localhost:4000/vector_store/list" \
  -H "Authorization: Bearer $MISHIKALLM_API_KEY"
```

**Response:**

The response will be a list of all vector stores that are available to use with MishikaLLM.

```json
{
  "object": "list",
  "data": [
    {
      "vector_store_id": "T37J8R4WTM",
      "custom_llm_provider": "bedrock",
      "vector_store_name": "bedrock-mishikallm-website-knowledgebase",
      "vector_store_description": "Bedrock vector store for the Mishikallm website knowledgebase",
      "vector_store_metadata": {
        "source": "https://www.mishikallm.com/docs"
      },
      "created_at": "2023-05-03T18:21:36.462Z",
      "updated_at": "2023-05-03T18:21:36.462Z",
      "mishikallm_credential_name": "bedrock_credentials"
    }
  ],
  "total_count": 1,
  "current_page": 1,
  "total_pages": 1
}
```


### Always on for a model

**Use this if you want vector stores to be used by default for a specific model.**

In this config, we add `vector_store_ids` to the claude-3-5-sonnet-with-vector-store model. This means that any request to the claude-3-5-sonnet-with-vector-store model will always use the vector store with the id `T37J8R4WTM` defined in the `vector_store_registry`.

```yaml showLineNumbers title="Always on for a model"
model_list:
  - model_name: claude-3-5-sonnet-with-vector-store
    mishikallm_params:
      model: anthropic/claude-3-5-sonnet
      vector_store_ids: ["T37J8R4WTM"]

vector_store_registry:
  - vector_store_name: "bedrock-mishikallm-website-knowledgebase"
    mishikallm_params:
      vector_store_id: "T37J8R4WTM"
      custom_llm_provider: "bedrock"
      vector_store_description: "Bedrock vector store for the Mishikallm website knowledgebase"
      vector_store_metadata:
        source: "https://www.mishikallm.com/docs"
```

## How It Works

If your request includes a `vector_store_ids` parameter where any of the vector store ids are found in the `vector_store_registry`, MishikaLLM will automatically use the vector store for the request.

1. You make a completion request with the `vector_store_ids` parameter and any of the vector store ids are found in the `mishikallm.vector_store_registry`
2. MishikaLLM automatically:
   - Uses your last message as the query to retrieve relevant information from the Knowledge Base
   - Adds the retrieved context to your conversation
   - Sends the augmented messages to the model

#### Example Transformation

When you pass `vector_store_ids=["YOUR_KNOWLEDGE_BASE_ID"]`, your request flows through these steps:

**1. Original Request to MishikaLLM:**
```json
{
    "model": "anthropic/claude-3-5-sonnet",
    "messages": [
        {"role": "user", "content": "What is mishikallm?"}
    ],
    "vector_store_ids": ["YOUR_KNOWLEDGE_BASE_ID"]
}
```

**2. Request to AWS Bedrock Knowledge Base:**
```json
{
    "retrievalQuery": {
        "text": "What is mishikallm?"
    }
}
```
This is sent to: `https://bedrock-agent-runtime.{aws_region}.amazonaws.com/knowledgebases/YOUR_KNOWLEDGE_BASE_ID/retrieve`

**3. Final Request to MishikaLLM:**
```json
{
    "model": "anthropic/claude-3-5-sonnet",
    "messages": [
        {"role": "user", "content": "What is mishikallm?"},
        {"role": "user", "content": "Context: \n\nMishikaLLM is an open-source SDK to simplify LLM API calls across providers (OpenAI, Claude, etc). It provides a standardized interface with robust error handling, streaming, and observability tools."}
    ]
}
```

This process happens automatically whenever you include the `vector_store_ids` parameter in your request.

## API Reference

### MishikaLLM Completion Knowledge Base Parameters

When using the Knowledge Base integration with MishikaLLM, you can include the following parameters:

| Parameter | Type | Description |
|-----------|------|-------------|
| `vector_store_ids` | List[str] | List of Knowledge Base IDs to query |

### VectorStoreRegistry

The `VectorStoreRegistry` is a central component for managing vector stores in MishikaLLM. It acts as a registry where you can configure and access your vector stores.

#### What is VectorStoreRegistry?

`VectorStoreRegistry` is a class that:
- Maintains a collection of vector stores that MishikaLLM can use
- Allows you to register vector stores with their credentials and metadata
- Makes vector stores accessible via their IDs in your completion requests

#### Using VectorStoreRegistry in Python

```python
from mishikallm.vector_stores.vector_store_registry import VectorStoreRegistry, MishikaLLM_ManagedVectorStore

# Initialize the vector store registry with one or more vector stores
mishikallm.vector_store_registry = VectorStoreRegistry(
    vector_stores=[
        MishikaLLM_ManagedVectorStore(
            vector_store_id="YOUR_VECTOR_STORE_ID",  # Required: Unique ID for referencing this store
            custom_llm_provider="bedrock"            # Required: Provider (e.g., "bedrock")
        )
    ]
)
```

#### MishikaLLM_ManagedVectorStore Parameters

Each vector store in the registry is configured using a `MishikaLLM_ManagedVectorStore` object with these parameters:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `vector_store_id` | str | Yes | Unique identifier for the vector store |
| `custom_llm_provider` | str | Yes | The provider of the vector store (e.g., "bedrock") |
| `vector_store_name` | str | No | A friendly name for the vector store |
| `vector_store_description` | str | No | Description of what the vector store contains |
| `vector_store_metadata` | dict or str | No | Additional metadata about the vector store |
| `mishikallm_credential_name` | str | No | Name of the credentials to use for this vector store |

#### Configuring VectorStoreRegistry in config.yaml

For the MishikaLLM Proxy, you can configure the same registry in your `config.yaml` file:

```yaml showLineNumbers title="Vector store configuration in config.yaml"
vector_store_registry:
  - vector_store_name: "bedrock-mishikallm-website-knowledgebase"  # Optional friendly name
    mishikallm_params:
      vector_store_id: "T37J8R4WTM"                            # Required: Unique ID  
      custom_llm_provider: "bedrock"                           # Required: Provider
      vector_store_description: "Bedrock vector store for the Mishikallm website knowledgebase"
      vector_store_metadata:
        source: "https://www.mishikallm.com/docs"
```

The `mishikallm_params` section accepts all the same parameters as the `MishikaLLM_ManagedVectorStore` constructor in the Python SDK.


