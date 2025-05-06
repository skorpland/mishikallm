---
title: v1.55.10
slug: v1.55.10
date: 2024-12-24T10:00:00
authors:
  - name: Sandeep Kumar
    title: CEO, MishikaLLM
tags: [batches, guardrails, team management, custom auth]
hide_table_of_contents: false
---

import Image from '@theme/IdealImage';

# v1.55.10

`batches`, `guardrails`, `team management`, `custom auth`


<Image img={require('../../img/batches_cost_tracking.png')} />

<br/>

:::info

Get a free 7-day MishikaLLM Enterprise trial here. [Start here](https://www.21t.cc/#trial)

**No call needed**

:::

## ✨ Cost Tracking, Logging for Batches API (`/batches`)

Track cost, usage for Batch Creation Jobs. [Start here](https://docs.21t.cc/docs/batches)

## ✨ `/guardrails/list` endpoint 

Show available guardrails to users. [Start here](https://mishikallm-api.up.railway.app/#/Guardrails)


## ✨ Allow teams to add models

This enables team admins to call their own finetuned models via mishikallm proxy. [Start here](https://docs.21t.cc/docs/proxy/team_model_add)


## ✨ Common checks for custom auth

Calling the internal common_checks function in custom auth is now enforced as an enterprise feature. This allows admins to use mishikallm's default budget/auth checks within their custom auth implementation. [Start here](https://docs.21t.cc/docs/proxy/virtual_keys#custom-auth)


## ✨ Assigning team admins

Team admins is graduating from beta and moving to our enterprise tier. This allows proxy admins to allow others to manage keys/models for their own teams (useful for projects in production). [Start here](https://docs.21t.cc/docs/proxy/virtual_keys#restricting-key-generation)



