---
layout: docs
title: Advanced Rules
permalink: docs/advanced-rules/
---

## Advanced Rules

Advanced rules provide the ability to do very advanced business logic, utilizing the Scala programming language and querying databases directly. 

This will require training outside of the scope of this documentation, however, the queries and script documentation can be used as a reference.

Note that, we have a goal to move more and more to the simple rule creation flow. If you find you have to create many rules with advanced mode, please give that feedback to the Labs team so we can look to solve that problem using our visual rule creation UI.

- [Queries](#queries)
-  [Script](#script)
- [Options](#options)

### Queries

Queries are a fundamental part of rules - they define access to the data required for rules to produce a value.

[More details on queries can be found here]({% link docs/query.md %})

### Script

The *rule script* is the second main component of a rule. It defines the logic used to take all rule inputs (configs, 
queries, request fields, etc) and produce a result value.

It’s important to note that the script is very powerful and involves understanding how to code. We expose the Scala programming language for scripts.

[More details on scripts can be found here]({% link docs/script.md %})


### Options

Action options allow you to produce a custom (action-dependent) value in the response of a fraud request. The configuration of an action option must be a valid JSON object.

You can use the same syntax used to access rule script context variables in String values in your options. See the
below image for an example (see rule script docs for examples on how to push script variables such as
`${script.remaining_limit}`)

![de](/img/extra_opts.png)
