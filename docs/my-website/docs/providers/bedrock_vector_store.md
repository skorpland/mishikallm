import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';
import Image from '@theme/IdealImage';

# Bedrock Knowledge Bases

AWS Bedrock Knowledge Bases allows you to connect your LLM's to your organization's data, letting your models retrieve and reference information specific to your business.

| Property | Details |
|----------|---------|
| Description | Bedrock Knowledge Bases connects your data to LLM's, enabling them to retrieve and reference your organization's information in their responses. |
| Provider Route on MishikaLLM | `bedrock` in the mishikallm vector_store_registry |
| Provider Doc | [AWS Bedrock Knowledge Bases ↗](https://aws.amazon.com/bedrock/knowledge-bases/) |

## Quick Start

### MishikaLLM Python SDK

```python showLineNumbers title="Example using MishikaLLM Python SDK"
import os
import mishikallm

from mishikallm.vector_stores.vector_store_registry import VectorStoreRegistry, MishikaLLM_ManagedVectorStore

# Init vector store registry with your Bedrock Knowledge Base
mishikallm.vector_store_registry = VectorStoreRegistry(
    vector_stores=[
        MishikaLLM_ManagedVectorStore(
            vector_store_id="YOUR_KNOWLEDGE_BASE_ID",  # KB ID from AWS Bedrock
            custom_llm_provider="bedrock"
        )
    ]
)

# Make a completion request using your Knowledge Base
response = await mishikallm.acompletion(
    model="anthropic/claude-3-5-sonnet", 
    messages=[{"role": "user", "content": "What does our company policy say about remote work?"}],
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": ["YOUR_KNOWLEDGE_BASE_ID"]
        }
    ],
)

print(response.choices[0].message.content)
```

### MishikaLLM Proxy

#### 1. Configure your vector_store_registry

<Tabs>
<TabItem value="config-yaml" label="config.yaml">

```yaml
model_list:
  - model_name: claude-3-5-sonnet
    mishikallm_params:
      model: anthropic/claude-3-5-sonnet
      api_key: os.environ/ANTHROPIC_API_KEY

vector_store_registry:
  - vector_store_name: "bedrock-company-docs"
    mishikallm_params:
      vector_store_id: "YOUR_KNOWLEDGE_BASE_ID"
      custom_llm_provider: "bedrock"
      vector_store_description: "Bedrock Knowledge Base for company documents"
      vector_store_metadata:
        source: "Company internal documentation"
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

```bash
curl http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MISHIKALLM_API_KEY" \
  -d '{
    "model": "claude-3-5-sonnet",
    "messages": [{"role": "user", "content": "What does our company policy say about remote work?"}],
    "tools": [
        {
            "type": "file_search",
            "vector_store_ids": ["YOUR_KNOWLEDGE_BASE_ID"]
        }
    ]
  }'
```

</TabItem>

<TabItem value="openai-sdk" label="OpenAI Python SDK">

```python
from openai import OpenAI

# Initialize client with your MishikaLLM proxy URL
client = OpenAI(
    base_url="http://localhost:4000",
    api_key="your-mishikallm-api-key"
)

# Make a completion request with vector_store_ids parameter
response = client.chat.completions.create(
    model="claude-3-5-sonnet",
    messages=[{"role": "user", "content": "What does our company policy say about remote work?"}],
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": ["YOUR_KNOWLEDGE_BASE_ID"]
        }
    ]
)

print(response.choices[0].message.content)
```

</TabItem>
</Tabs>


Futher Reading Vector Stores:
- [Always on Vector Stores](https://docs.21t.cc/docs/completion/knowledgebase#always-on-for-a-model)
- [Listing available vector stores on mishikallm proxy](https://docs.21t.cc/docs/completion/knowledgebase#listing-available-vector-stores)
- [How MishikaLLM Vector Stores Work](https://docs.21t.cc/docs/completion/knowledgebase#how-it-works)