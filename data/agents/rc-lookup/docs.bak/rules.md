---
layout: docs
title: Rules
permalink: docs/rules/
---

- [Rules](#rules)
- [Creating Rules](#creating-rules)
  * [Tags](#tags)
  * [Rule logic](#rule-logic)
  * [Messages](#messages)
  * [Actions -> Add Tags](#actions---add-tags)

## Rules

Rules use data points provided from the API contract (Payload) or through calculations (Attributes) in order to make decisions.

Rules are created stand-alone, and then added to Profiles. A profile can have as many rules as you would like, and it's best practice to make complicated logic through multiple small rules as opposed to one large rule.

When creating rules, you have the option to use the regular rule flow or the advanced rule flow. It is recommended to use the regular rule flow, however there are some things that can only be done in advanced mode.

## Creating Rules

![de](/img/rule-create.png)

### Tags

Tagging a rule is used to audit or analysis purposes. For instance, if you had a set of rules that handle anti-fraud, you might give them a tag to distinguish them from user limit rules. That way, if you want to see a breakdown of why transactions were blocked, you could see how many were due to anti-fraud and how many were due to user limits.

### Rule logic

Rules may use payload input and variables as parameters. These need to be configured first to be used, which can be configured in Data -> Profile Payload and Data -> Variables respectively.


### Messages

Two types of messages can be returned:
* User messages
* Customer Service Technician (CST) messages.

Options are custom values that a rule can include in the response to a fraud request. They are configured on a per action basis (not available for other response types). User messages are intended to be sent to the user directly while CST messages are intended to be used internally.

In order to support multiple languages or to handle messages in your own system, we recommend sending back an error code instead of the message itself, and mapping to your own managed error messages.
### Actions -> Add Tags

If you wanted to flag a transaction, perhaps in order to analyze it later but not block it in real time, you can do so by adding a tag. To do this, you simply click Actions -> Add Tags and type in any tag you want. If the condition above is fulfilled, that tag will be added in the response.

