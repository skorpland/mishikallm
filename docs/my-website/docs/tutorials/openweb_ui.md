import Image from '@theme/IdealImage';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# OpenWeb UI with MishikaLLM

This guide walks you through connecting OpenWeb UI to MishikaLLM. Using MishikaLLM with OpenWeb UI allows teams to 
- Access 100+ LLMs on OpenWeb UI
- Track Spend / Usage, Set Budget Limits 
- Send Request/Response Logs to logging destinations like langfuse, s3, gcs buckets, etc.
- Set access controls eg. Control what models OpenWebUI can access.

## Quickstart

- Make sure to setup MishikaLLM with the [MishikaLLM Getting Started Guide](https://docs.21t.cc/docs/proxy/docker_quick_start)


## 1. Start MishikaLLM & OpenWebUI

- OpenWebUI starts running on [http://localhost:3000](http://localhost:3000)
- MishikaLLM starts running on [http://localhost:4000](http://localhost:4000)


## 2. Create a Virtual Key on MishikaLLM

Virtual Keys are API Keys that allow you to authenticate to MishikaLLM Proxy. We will create a Virtual Key that will allow OpenWebUI to access MishikaLLM.

### 2.1 MishikaLLM User Management Hierarchy

On MishikaLLM, you can create Organizations, Teams, Users and Virtual Keys. For this tutorial, we will create a Team and a Virtual Key.

- `Organization` - An Organization is a group of Teams. (US Engineering, EU Developer Tools)
- `Team` - A Team is a group of Users. (OpenWeb UI Team, Data Science Team, etc.)
- `User` - A User is an individual user (employee, developer, eg. `krrish@21t.cc`)
- `Virtual Key` - A Virtual Key is an API Key that allows you to authenticate to MishikaLLM Proxy. A Virtual Key is associated with a User or Team.

Once the Team is created, you can invite Users to the Team. You can read more about MishikaLLM's User Management [here](https://docs.21t.cc/docs/proxy/user_management_heirarchy).

### 2.2 Create a Team on MishikaLLM

Navigate to [http://localhost:4000/ui](http://localhost:4000/ui) and create a new team.

<Image img={require('../../img/mishikallm_create_team.gif')} />

### 2.2 Create a Virtual Key on MishikaLLM

Navigate to [http://localhost:4000/ui](http://localhost:4000/ui) and create a new virtual Key. 

MishikaLLM allows you to specify what models are available on OpenWeb UI (by specifying the models the key will have access to).

<Image img={require('../../img/create_key_in_team_oweb.gif')} />

## 3. Connect OpenWeb UI to MishikaLLM

On OpenWeb UI, navigate to Settings -> Connections and create a new connection to MishikaLLM

Enter the following details:
- URL: `http://localhost:4000` (your mishikallm proxy base url)
- Key: `your-virtual-key` (the key you created in the previous step)

<Image img={require('../../img/mishikallm_setup_openweb.gif')} />

### 3.1 Test Request

On the top left corner, select models you should only see the models you gave the key access to in Step 2.

Once you selected a model, enter your message content and click on `Submit`

<Image img={require('../../img/basic_mishikallm.gif')} />

### 3.2 Tracking Spend / Usage

After your request is made, navigate to `Logs` on the MishikaLLM UI, you can see Team, Key, Model, Usage and Cost.

<!-- <Image img={require('../../img/mishikallm_logs_openweb.gif')} /> -->



## Render `thinking` content on OpenWeb UI

OpenWebUI requires reasoning/thinking content to be rendered with `<think></think>` tags. In order to render this for specific models, you can use the `merge_reasoning_content_in_choices` mishikallm parameter.

Example mishikallm config.yaml:

```yaml
model_list:
  - model_name: thinking-anthropic-claude-3-7-sonnet
    mishikallm_params:
      model: bedrock/us.anthropic.claude-3-7-sonnet-20250219-v1:0
      thinking: {"type": "enabled", "budget_tokens": 1024}
      max_tokens: 1080
      merge_reasoning_content_in_choices: true
```

### Test it on OpenWeb UI

On the models dropdown select `thinking-anthropic-claude-3-7-sonnet`

<Image img={require('../../img/mishikallm_thinking_openweb.gif')} />

## Additional Resources
- Running MishikaLLM and OpenWebUI on Windows Localhost: A Comprehensive Guide [https://www.tanyongsheng.com/note/running-mishikallm-and-openwebui-on-windows-localhost-a-comprehensive-guide/](https://www.tanyongsheng.com/note/running-mishikallm-and-openwebui-on-windows-localhost-a-comprehensive-guide/)