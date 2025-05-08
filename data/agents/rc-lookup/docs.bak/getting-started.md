---
layout: docs
title: Getting Started
permalink: docs/
---

![maquette](/img/risk.png)

# Overview

PAI Risk is a dynamic rule engine used to implement real-time business logic into your product flows, using state-of-the-art data techniques as well as embedded machine learning.

PAI Risk consists of multiple tools.
* [Rule Engine](#rule-engine)
* [Attribute Studio](#attribute-studio)
* [Case Management](#case-management-beta)

# Rule Engine

The PAI Risk Rule Engine is a dynamic rule engine that allows you to configure Profiles that fit your business's needs. A profile can be configured with as many rules as you would like.

The Rule Engine lets you create Simple rules with a visual UI.

If you need support in creating a rule or use case, please reach out to the Labs team for assistance.

Sometimes you want to make a rule or use case but aren't sure how to do it. Please reach out to the Labs team for help. More often than not, we have encountered a similar rule and can advise how to make it.

## Getting started - How to create a workflow

To implement a workflow in PAI Risk, first, you will be required to create a Profile. This will create an API that you can call to make a decision. From there, you will need to construct the logic of the profile. You will define the payload to the API, define the logic of the rule, and then you can organize those rules in a rule tree.

In addition to payload data, PAI Risk supports calculating internal data using event driven architecture. What this means is, instead of calculating something like the number of transactions in the past 7 days for a user and sending it on the payload, RISK provides tools to calculate this internally so the payload needs only to send the customer ID. See more about this in the Attribute Studio section below.

[To get started, learn more about how to create Profiles]({% link docs/profiles.md %})

# Attribute Studio

Attribute Studio helps you configure data points to be used in your fraud prevention rules.

These features, also called Attributes, can be sophisticated calculations that monitor everything a user (or other entity, like a merchant) has done or is currently doing within the system. *An example might be an attribute that calculates the amount of spending a user has done at the merchant they're purchasing from in the last 24hrs.*

Attribute Studio lets data engineers do all of this plumbing in a fraction of the time it would otherwise take - additionally these data points can be set up without needing any downtime.

[To get started, learn more about how to create Attributes]({% link docs/attributes.md %})

# Case Management (Beta)

The Case Management tool allows you to view a case in more detail. A case is defined as one or more transactions that have been flagged as fraud. Cases can be created directly from a rule in the Rule Engine.

Case Management lets users review transactions with all the context needed, make a decision on the cases, and take action immediately.

Currently, Case Management is only in Beta in a few domains. If you need something like this, please reach out to [pai.risk.support@paytm.com](mailto:pai.risk.support@paytm.com).
