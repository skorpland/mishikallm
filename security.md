# Data Privacy and Security

## Security Measures

### MishikaLLM Github

- All commits run through Github's CodeQL checking

### Self-hosted Instances MishikaLLM

- **No data or telemetry is stored on MishikaLLM Servers when you self host**
- For installation and configuration, see: [Self-hosting guided](https://docs.21t.cc/docs/proxy/deploy)
- **Telemetry** We run no telemetry when you self host MishikaLLM

### MishikaLLM Cloud

- We encrypt all data stored using your `MISHIKALLM_MASTER_KEY` and in transit using TLS.
- Our database and application run on GCP, AWS infrastructure, partly managed by NeonDB.
    - US data region: Northern California (AWS/GCP `us-west-1`) & Virginia (AWS `us-east-1`)
    - EU data region Germany/Frankfurt (AWS/GCP `eu-central-1`)
- All users have access to SSO (Single Sign-On) through OAuth 2.0 with Google, Okta, Microsoft, KeyCloak. 
- Audit Logs with retention policy
- Control Allowed IP Addresses that can access your Cloud MishikaLLM Instance

For security inquiries, please contact us at support@berri.ai

#### Supported data regions for MishikaLLM Cloud

MishikaLLM supports the following data regions:

- US, Northern California (AWS/GCP `us-west-1`)
- Europe, Frankfurt, Germany (AWS/GCP `eu-central-1`)

All data, user accounts, and infrastructure are completely separated between these two regions

### Security Vulnerability Reporting Guidelines

We value the security community's role in protecting our systems and users. To report a security vulnerability:

- Email support@berri.ai with details
- Include steps to reproduce the issue
- Provide any relevant additional information

We'll review all reports promptly. Note that we don't currently offer a bug bounty program.
