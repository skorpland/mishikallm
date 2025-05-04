
import Image from '@theme/IdealImage';

# SCIM with MishikaLLM

Enables identity providers (Okta, Azure AD, OneLogin, etc.) to automate user and team (group) provisioning, updates, and deprovisioning on MishikaLLM.


This tutorial will walk you through the steps to connect your IDP to MishikaLLM SCIM Endpoints.

### Supported SSO Providers for SCIM
Below is a list of supported SSO providers for connecting to MishikaLLM SCIM Endpoints.
- Microsoft Entra ID (Azure AD)
- Okta
- Google Workspace
- OneLogin
- Keycloak
- Auth0


## 1. Get your SCIM Tenant URL and Bearer Token

On MishikaLLM, navigate to the Settings > Admin Settings > SCIM. On this page you will create a SCIM Token, this allows your IDP to authenticate to mishikallm `/scim` endpoints.

<Image img={require('../../img/scim_2.png')}  style={{ width: '800px', height: 'auto' }} />

## 2. Connect your IDP to MishikaLLM SCIM Endpoints

On your IDP provider, navigate to your SSO application and select `Provisioning` > `New provisioning configuration`.

On this page, paste in your mishikallm scim tenant url and bearer token.

Once this is pasted in, click on `Test Connection` to ensure your IDP can authenticate to the MishikaLLM SCIM endpoints.

<Image img={require('../../img/scim_4.png')}  style={{ width: '800px', height: 'auto' }} />


## 3. Test SCIM Connection

### 3.1 Assign the group to your MishikaLLM Enterprise App

On your IDP Portal, navigate to `Enterprise Applications` > Select your mishikallm app 

<Image img={require('../../img/msft_enterprise_app.png')}  style={{ width: '800px', height: 'auto' }} />

<br />
<br />

Once you've selected your mishikallm app, click on `Users and Groups` > `Add user/group` 

<Image img={require('../../img/msft_enterprise_assign_group.png')}  style={{ width: '800px', height: 'auto' }} />

<br />

Now select the group you created in step 1.1. And add it to the MishikaLLM Enterprise App. At this point we have added `Production LLM Evals Group` to the MishikaLLM Enterprise App. The next step is having MishikaLLM automatically create the `Production LLM Evals Group` on the MishikaLLM DB when a new user signs in.

<Image img={require('../../img/msft_enterprise_select_group.png')}  style={{ width: '800px', height: 'auto' }} />


### 3.2 Sign in to MishikaLLM UI via SSO

Sign into the MishikaLLM UI via SSO. You should be redirected to the Entra ID SSO page. This SSO sign in flow will trigger MishikaLLM to fetch the latest Groups and Members from Azure Entra ID.

<Image img={require('../../img/msft_sso_sign_in.png')}  style={{ width: '800px', height: 'auto' }} />

### 3.3 Check the new team on MishikaLLM UI

On the MishikaLLM UI, Navigate to `Teams`, You should see the new team `Production LLM Evals Group` auto-created on MishikaLLM. 

<Image img={require('../../img/msft_auto_team.png')}  style={{ width: '900px', height: 'auto' }} />




