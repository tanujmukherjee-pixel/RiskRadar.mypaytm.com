---
layout: docs
title: Ops
permalink: docs/ops/
---



# PAI Risk Ops

The following page provides an overview of various operations related to managing the PAI Risk ecosystem

  * [Rules](#rules)
    + [Exporting](#exporting)
    + [Importing](#importing)
  * [Database Management](#database-management)
    + [Pillar](#pillar)
      - [SBT Plugin](#sbt-plugin)
      - [Custom SBT Commands](#custom-sbt-commands)

## Rules

### Exporting

You can export the rules under a domain as JSON (includes all versions of each rule) or a specific rule version.

Currently - this is accessed through the rule pages under actions (all rules) or clicking an individual rule.

### Importing

As a super-admin - you can do a bulk import of rules from another domain or another PAI Risk installation using the same json
format provided by the export action
## Database Management

### Pillar

We use a Scala library called Pillar to manage schema changes to Cassandra. In the past, we have used an sbt plugin for
pillar, however, limitations in the plugin have motivated us to create our own custom commands.

#### SBT Plugin

As mentioned, we currently use the sbt plugin for pillar, however this use will become deprecated for us soon. The usage
of the plugin is,

```sh
# risk_list_lookup
sbt "project rule-admin" createKeyspace
sbt "project rule-admin" migrate

# rt_engine
sbt "project rule-engine" createKeyspace
sbt "project rule-engine" migrate
```

The commands are configured from the typesafe conf of their respective projects and apply migrations in their respective
migration folders.

#### Custom SBT Commands

We have a custom command for generating the Cassandra keyspaces required for the Rule Engine and Rule Admin systems.

The usage is as follows,

`sbt "project rule-admin" createKeyspaces`

The command expects some configuration via environment variables namely,

- PILLAR_SEED_ADDRESS
- PILLAR_PORT
- PILLAR_KEYSPACES_CONF

The `PILLAR_KEYSPACES_CONF` variable uses a custom string format for specifying the keyspaces to be created and their 
respective replication strategies. The format is a comma separated list of keyspace configuration strings as follows,

`keyspace_name|strategy_name|strategy_configuration`

- `keyspace_name`: A valid cassandra keyspace name
- `strategy_name`: One of SimpleStrategy or NetworkTopologyStrategy (case insensitive)
- `strategy_configuration`: The strategy specific configuration format (see below)
- simple strategy configuration: Just an integer providing the replication factor
- network strategy configuration: A bar separate list of data center names and replication factors

Here is an example configuration

`global_config|SimpleStrategy|1,risklist_domain|NetworkTopologyStrategy|datacenter1:1`

