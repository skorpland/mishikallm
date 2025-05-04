import Image from '@theme/IdealImage';

# Microsoft SSO: Sync Groups, Members with MishikaLLM

Sync Microsoft SSO Groups, Members with MishikaLLM Teams. 

<Image img={require('../../img/mishikallm_entra_id.png')}  style={{ width: '800px', height: 'auto' }} />

<br />
<br />


## Prerequisites

- An Azure Entra ID account with administrative access
- A MishikaLLM Enterprise App set up in your Azure Portal
- Access to Microsoft Entra ID (Azure AD)


## Overview of this tutorial

1. Auto-Create Entra ID Groups on MishikaLLM Teams 
2. Sync Entra ID Team Memberships
3. Set default params for new teams and users auto-created on MishikaLLM

## 1. Auto-Create Entra ID Groups on MishikaLLM Teams 

In this step, our goal is to have MishikaLLM automatically create a new team on the MishikaLLM DB when there is a new Group Added to the MishikaLLM Enterprise App on Azure Entra ID.

### 1.1 Create a new group in Entra ID


Navigate to [your Azure Portal](https://portal.azure.com/) > Groups > New Group. Create a new group. 

<Image img={require('../../img/entra_create_team.png')}  style={{ width: '800px', height: 'auto' }} />

### 1.2 Assign the group to your MishikaLLM Enterprise App

On your Azure Portal, navigate to `Enterprise Applications` > Select your mishikallm app 

<Image img={require('../../img/msft_enterprise_app.png')}  style={{ width: '800px', height: 'auto' }} />

<br />
<br />

Once you've selected your mishikallm app, click on `Users and Groups` > `Add user/group` 

<Image img={require('../../img/msft_enterprise_assign_group.png')}  style={{ width: '800px', height: 'auto' }} />

<br />

Now select the group you created in step 1.1. And add it to the MishikaLLM Enterprise App. At this point we have added `Production LLM Evals Group` to the MishikaLLM Enterprise App. The next steps is having MishikaLLM automatically create the `Production LLM Evals Group` on the MishikaLLM DB when a new user signs in.

<Image img={require('../../img/msft_enterprise_select_group.png')}  style={{ width: '800px', height: 'auto' }} />


### 1.3 Sign in to MishikaLLM UI via SSO

Sign into the MishikaLLM UI via SSO. You should be redirected to the Entra ID SSO page. This SSO sign in flow will trigger MishikaLLM to fetch the latest Groups and Members from Azure Entra ID.

<Image img={require('../../img/msft_sso_sign_in.png')}  style={{ width: '800px', height: 'auto' }} />

### 1.4 Check the new team on MishikaLLM UI

On the MishikaLLM UI, Navigate to `Teams`, You should see the new team `Production LLM Evals Group` auto-created on MishikaLLM. 

<Image img={require('../../img/msft_auto_team.png')}  style={{ width: '900px', height: 'auto' }} />

#### How this works

When a SSO user signs in to MishikaLLM:
- MishikaLLM automatically fetches the Groups under the MishikaLLM Enterprise App
- It finds the Production LLM Evals Group assigned to the MishikaLLM Enterprise App
- MishikaLLM checks if this group's ID exists in the MishikaLLM Teams Table
- Since the ID doesn't exist, MishikaLLM automatically creates a new team with:
  - Name: Production LLM Evals Group
  - ID: Same as the Entra ID group's ID

## 2. Sync Entra ID Team Memberships

In this step, we will have MishikaLLM automatically add a user to the `Production LLM Evals` Team on the MishikaLLM DB when a new user is added to the `Production LLM Evals` Group in Entra ID.

### 2.1 Navigate to the `Production LLM Evals` Group in Entra ID

Navigate to the `Production LLM Evals` Group in Entra ID.

<Image img={require('../../img/msft_member_1.png')}  style={{ width: '800px', height: 'auto' }} />


### 2.2 Add a member to the group in Entra ID

Select `Members` > `Add members`

In this stage you should add the user you want to add to the `Production LLM Evals` Team.

<Image img={require('../../img/msft_member_2.png')}  style={{ width: '800px', height: 'auto' }} />



### 2.3 Sign in as the new user on MishikaLLM UI

Sign in as the new user on MishikaLLM UI. You should be redirected to the Entra ID SSO page. This SSO sign in flow will trigger MishikaLLM to fetch the latest Groups and Members from Azure Entra ID. During this step MishikaLLM sync it's teams, team members with what is available from Entra ID

<Image img={require('../../img/msft_sso_sign_in.png')}  style={{ width: '800px', height: 'auto' }} />



### 2.4 Check the team membership on MishikaLLM UI

On the MishikaLLM UI, Navigate to `Teams`, You should see the new team `Production LLM Evals Group`. Since your are now a member of the `Production LLM Evals Group` in Entra ID, you should see the new team `Production LLM Evals Group` on the MishikaLLM UI.

<Image img={require('../../img/msft_member_3.png')}  style={{ width: '900px', height: 'auto' }} />

## 3. Set default params for new teams auto-created on MishikaLLM

Since mishikallm auto creates a new team on the MishikaLLM DB when there is a new Group Added to the MishikaLLM Enterprise App on Azure Entra ID, we can set default params for new teams created. 

This allows you to set a default budget, models, etc for new teams created. 

### 3.1 Set `default_team_params` on mishikallm 

Navigate to your mishikallm config file and set the following params 

```yaml showLineNumbers title="mishikallm config with default_team_params"
mishikallm_settings:
  default_team_params:             # Default Params to apply when mishikallm auto creates a team from SSO IDP provider
    max_budget: 100                # Optional[float], optional): $100 budget for the team
    budget_duration: 30d           # Optional[str], optional): 30 days budget_duration for the team
    models: ["gpt-3.5-turbo"]      # Optional[List[str]], optional): models to be used by the team
```

### 3.2 Auto-create a new team on MishikaLLM

- In this step you should add a new group to the MishikaLLM Enterprise App on Azure Entra ID (like we did in step 1.1). We will call this group `Default MishikaLLM Prod Team` on Azure Entra ID.
- Start mishikallm proxy server with your config
- Sign into MishikaLLM UI via SSO
- Navigate to `Teams` and you should see the new team `Default MishikaLLM Prod Team` auto-created on MishikaLLM
- Note MishikaLLM will set the default params for this new team. 

<Image img={require('../../img/msft_default_settings.png')}  style={{ width: '900px', height: 'auto' }} />


## Video Walkthrough

This walks through setting up sso auto-add for **Microsoft Entra ID**

Follow along this video for a walkthrough of how to set this up with Microsoft Entra ID

<iframe width="840" height="500" src="https://www.loom.com/embed/ea711323aa9a496d84a01fd7b2a12f54?sid=c53e238c-5bfd-4135-b8fb-b5b1a08632cf" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe>













