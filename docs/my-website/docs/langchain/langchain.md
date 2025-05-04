import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Using ChatMishikaLLM() - Langchain

## Pre-Requisites
```shell
!pip install mishikallm langchain
```
## Quick Start

<Tabs>
<TabItem value="openai" label="OpenAI">

```python
import os
from langchain_community.chat_models import ChatMishikaLLM
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['OPENAI_API_KEY'] = ""
chat = ChatMishikaLLM(model="gpt-3.5-turbo")
messages = [
    HumanMessage(
        content="what model are you"
    )
]
chat.invoke(messages)
```

</TabItem>

<TabItem value="anthropic" label="Anthropic">

```python
import os
from langchain_community.chat_models import ChatMishikaLLM
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['ANTHROPIC_API_KEY'] = ""
chat = ChatMishikaLLM(model="claude-2", temperature=0.3)
messages = [
    HumanMessage(
        content="what model are you"
    )
]
chat.invoke(messages)
```

</TabItem>

<TabItem value="replicate" label="Replicate">

```python
import os
from langchain_community.chat_models import ChatMishikaLLM
from langchain_core.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['REPLICATE_API_TOKEN'] = ""
chat = ChatMishikaLLM(model="replicate/llama-2-70b-chat:2c1608e18606fad2812020dc541930f2d0495ce32eee50074220b87300bc16e1")
messages = [
    HumanMessage(
        content="what model are you?"
    )
]
chat.invoke(messages)
```

</TabItem>

<TabItem value="cohere" label="Cohere">

```python
import os
from langchain_community.chat_models import ChatMishikaLLM
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

os.environ['COHERE_API_KEY'] = ""
chat = ChatMishikaLLM(model="command-nightly")
messages = [
    HumanMessage(
        content="what model are you?"
    )
]
chat.invoke(messages)
```

</TabItem>
</Tabs>

## Use Langchain ChatMishikaLLM with MLflow

MLflow provides open-source observability solution for ChatMishikaLLM.

To enable the integration, simply call `mlflow.mishikallm.autolog()` before in your code. No other setup is necessary.

```python
import mlflow

mlflow.mishikallm.autolog()
```

Once the auto-tracing is enabled, you can invoke `ChatMishikaLLM` and see recorded traces in MLflow.

```python
import os
from langchain.chat_models import ChatMishikaLLM

os.environ['OPENAI_API_KEY']="sk-..."

chat = ChatMishikaLLM(model="gpt-4o-mini")
chat.invoke("Hi!")
```

## Use Langchain ChatMishikaLLM with Lunary
```python
import os
from langchain.chat_models import ChatMishikaLLM
from langchain.schema import HumanMessage
import mishikallm

os.environ["LUNARY_PUBLIC_KEY"] = "" # from https://app.lunary.ai/settings
os.environ['OPENAI_API_KEY']="sk-..."

mishikallm.success_callback = ["lunary"] 
mishikallm.failure_callback = ["lunary"] 

chat = ChatMishikaLLM(
  model="gpt-4o"
  messages = [
    HumanMessage(
        content="what model are you"
    )
]
chat(messages)
```

Get more details [here](../observability/lunary_integration.md)

## Use LangChain ChatMishikaLLM + Langfuse
Checkout this section [here](../observability/langfuse_integration#use-langchain-chatmishikallm--langfuse) for more details on how to integrate Langfuse with ChatMishikaLLM.
