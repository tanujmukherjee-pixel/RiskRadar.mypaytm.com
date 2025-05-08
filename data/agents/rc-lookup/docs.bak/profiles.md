---
layout: docs
title: Profiles
permalink: docs/profiles/
---



## Profiles

Profiles are a structure within PAI Risk that define workflows for a particular business event, such as a user sign-up, a payment, or a loan application.

A profile will be constructed with a set of rules, and a set of input variables. It will then be configured to give an appropriate response, such as rejecting or approving a loan application; or determining the amount of loan to offer to a customer applying for a loan.

- [Profiles](#profiles)
  * [Creating a Profile](#creating-a-profile)
    * [Profile Response Type](#profile-response-type)
    * [Profile Rule Tree](#profile-rule-tree)
    * [Parent and Children Rules](#parent-and-children-rules)
  - [Audit Field Transformations](#audit-field-transformations)
    * [Substring](#substring)
  * [Using a Profile](#using-a-profile)

## Creating a profile

![de](/img/profile-create.png)


### Profile Response Type

Profiles generally return a Recommendation (basically, a String). However there are other supported types as well:

* Recommendation: A set of domain configured Strings used to describe a potential action to take ("PASS", "BLOCK")
* Int: A whole number (For example, we use this to calculate points payers receive in the Paytm Canada app).
* Commission: A tuple providing an action code and a double representing the percentage in commission an agent might
receive on this transaction. This is used in Paytm Bank only.
* New types can be requested from the Labs team if required.

### Profile Rule Tree

The rule tree describes the decision making path for a specific event. At a high level, it takes the result of each
sub tree and then returns the highest priority result.

Whitelists are a common usage of this pattern. If a whitelist provides a concrete answer (i.e the customer is in the
whitelist) we ignore the fraud check rules below it in the tree.

Note: Keep in mind that rule queries are all executed regardless of placement in the tree. While you can short circuit 
the decision tree processing using the rule tree structure it only saves the time of executing the child rule scripts.
Rule scripts are normally not expensive to run so this optimization is not worth much effort.

### Parent and Children Rules

Sometimes, you may want to do some business logic between rules. For example, you may want one rule to evaluate based on another rule.

One way to achieve this is through the use of parent and children rules.

Once a rule is created, you can make it a parent rule of another rule. See the image below, where the rule credit_card_order_only is the parent for the 3 other rules.

For each tree, if the parent rule provides a concrete decision (e.g "PASS" or "BLOCK") that will become the result of that tree, and rule scripts of the children will not be executed.

Alternatively, the parent rule may choose to pass the decision to its children by returning a special value of `inconclusive`. The child rule with the highest priority result (e.g. “BLOCK”) will then become the final result of that tree.

![de](/img/children-rules.png)

You can use these parent/children rules in a few ways:
* Based on a condition in the payload, you may choose to evaluate some rules. In the example above, only if the payment type is credit card do you want to evaluate the credit card rules.
* You can perform A/B testing via [Rule Experiment]({% link docs/rule-experiment.md %}). By having a parent rule half (or another percentage) of the time return "inconclusive", and the other half the time returning a result.
* You can skip sets of rules for specific users, by either building the logic in the parent rule or using a whitelist to "PASS". 

### Rule Statuses: Live vs Monitor

Rules that are either in `LIVE` or `MONITOR` status can be added to a profile. While both rule statuses will be executed, only rules that are live can affect the final decision of a profile.

`DRAFT` rules cannot be added to a profile and `DISABLED` rules will be skipped altogether. Setting a live rule to disabled is convenient way to quickly stop rule evaluation without having to edit the profile tree.

### Automatic Monitor Mode

If a rule is currently live and used in a profile, the rule engine can automatically evaluate a newer version of that rule without needing to edit the profile tree. You can do this by creating a new version of your rule and setting its status to `MONITOR`.

You may then compare the result of your LIVE vs MONITOR rule in the audit log.

Note: You will still need to `Deploy Rules` after saving your profile to start evaluating your new version.

## Audit Field Transformations

Sometimes, you may need PII data to be used in an evaluation but you can't store it (for liability or compliance reasons). Audit transformations allow for that. For example, if you receive on the payload the DOB of a customer, you could use that in a rule but then use the "remove" transformation on the column DOB before storing for audit.

The transformations are the following:

* Substring: Apply the String substring function to the target field.
* Remove: Completely removes the field from the audit log
* Sha256: Apply sha256 hash to the target field

The transformations are available under the create / edit evaluation mapper page

![de](/img/evalmapper1.png)

### Substring

The Substring function includes 3 parameters

* fieldName String - The name of the payload/metadata field to apply the Substring function to
* from: Int - The start boundary (inclusive) of the Substring operation. If a negative value or an index outside of the
range the value is provided, 0 is used.
* to: Int - the end boundary (exclusive) of the Substring operation. If an index larger than the value is provided, the
length of the input is used here.

## Setting up inputs

You can configure your input parameters by going to Data -> Profile Payload. 

Alternatively, you can start calling the API and let the profile payload generate the payload itself - using the Detect Payload button in the Add Profile Payload section.

## Using A Profile

Simply call the API with the inputs and you will begin to see a response. You can find the API by clicking here in the UI.

![de](/img/profile-api.png)

## Audit Log

The audit log provides a snapshot of the final decision for a fraud check as well as everything involved in making that decision. This includes session id, metadata, payload, rules and results of queries that were executed.

The final result of the profile can be found as `actionRecommended` in the audit log. The results of all rules in the tree can be found under `actions`, while all the live rules that produced that final result can be found under `actionRecommendedRules`.

If there are any monitor rules, `actionRecommendedMonitor` will indicate what result the profile would have returned if those monitor rules were considered live.

Note that `actionRecommendedMonitor` will only differ if the monitor rule returns a higher priority result than the live rules. e.g. Rule V1:LIVE returns "PASS" and Rule V2:MONITOR returns "BLOCK".

[Next have a look at how to create a Rule]({% link docs/rules.md %})
