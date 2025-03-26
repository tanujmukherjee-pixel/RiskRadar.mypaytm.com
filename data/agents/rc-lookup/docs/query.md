---
layout: docs
title: Query DSL
permalink: docs/query/
---


## Queries

A core part of rule creation in PAI Risk is defining the queries that will retrieve the values required for rule
evaluation.

The values retrieved by a query can be used in the rule script in order to determine what result the rule should
produce.

Generally, queries take the following form,

```sql
SELECT CLAUSE
FROM CLAUSE
WHERE CLAUSE
```

A high-level description is that the `SELECT` clause defines the subset of the query result we are interested in. Next,
the `FROM` clause defines which data source our query will run against. Lastly, the `WHERE` clause provides the ability to filter data-points so that the results are relevant to the query.

The following sections will go into more detail on clauses.

- [SELECT Clause](#select-clause)
  * [Aggregations](#aggregations)
- [FROM Clause](#from-clause)
  * [Cassandra](#cassandra)
  * [ML](#ml)
  * [CONFIG](#config)
  * [LISTS](#lists)
- [WHERE Clause](#where-clause)
  * [Dynamic Clause](#dynamic-clause)
  * [UDFs](#udfs)
    + [Geohash](#geohash)
    + [Start of Day](#start-of-day)
    + [End of Day](#end-of-day)
    + [Start of Month](#start-of-month)
    + [End of Month](#end-of-month)
    + [Hour Add](#hour-add)
    + [Now](#now)
    + [Marketplace Category](#marketplace-category)
    + [Marketplace Price Bucket](#marketplace-price-bucket)
    + [Email Domain](#email-domain)
    + [SHA256](#sha256)
    + [Address Fingerprint](#address-fingerprint)
    + [Strip Prefix](#strip-prefix)
    + [Substring](#substring)
    + [String Replace](#string-replace)
    + [String Replace Pattern](#string-replace-pattern)
    + [SQL Substring](#sql-substring)
    + [Truncate](#truncate)
    + [Email Normalize](#email-normalize)
  * [Nested Queries](#nested-queries)
  * [IN Clause](#in-clause)
    + [Static IN Clause](#static-in-clause)
    + [Dynamic IN Clause](#dynamic-in-clause)
      - [PROJECT](#project)
      - [Address Fingerprint Soundex](#address-fingerprint-soundex)
      - [Split](#split)
    + [Dynamic IN Clause with Nested Queries](#dynamic-in-with-nested-queries)
- [FOREACH Clause](#foreach-clause)
- [Examples](#examples)
  * [List V1 Membership Check](#list-v1-membership-check)
  * [Domain List Membership Check (List V2)](#domain-list-membership-check-list-v2)
  * [All Domain List Membership Check (List V2)](#all-domain-list-membership-check-list-v2)
  * [Multi DC List Membership Check (List V2)](#multi-dc-list-membership-check-list-v2)
  * [Velocity Lookup](#velocity-lookup)
  * [With UDFs](#with-udfs)
    + [AFP Soundex In Clause](#afp-soundex-in-clause)
- [Usage Tips](#usage-tips)
  * [Data Explorer](#data-explorer)
  * [Configuration Manager](#configuration-manager)
  * [Request Mapping](#request-mapping)
  * [Monitor Mode](#monitor-mode)



## SELECT Clause
The select clause determines which columns are made available to the rule script.

Select clauses generally take a few common forms,

- Select every available column: `SELECT *`
- Select a single column: `SELECT "column_a"`
- Select a single column and rename it: `SELECT "column_a as alias_a"`
- Select multiple columns: `SELECT "column_a", "column_b", "column_c"`

### Aggregations

Select clauses can also use aggregation functions which performs a calculation on a set of values and returns a single
result.

The following aggregation functions are available,

- count: `SELECT "count(column_a) AS column_a_count"`
- sum: `SELECT "sum(column_a) AS column_a_sum"`
- min: `SELECT "min(column_a) AS column_a_min"`
- max: `SELECT "max(column_a) AS column_a_max"`
- avg: `SELECT "avg(column_a) AS column_a_avg"`

## FROM Clause
The FROM clause determines the data source the query will be reading from. Some of these data sources leverage in-memory
databases in PAI Risk while others make remote database calls.

There are four data sources that can currently read from.

### Cassandra
The most common data source is Cassandra. The query will make a remote call to PAI Risk's Cassandra cluster.

The syntax is as follows,

`FROM "keyspace"."table"`

Where keyspace and table are the names of the keyspace / table as you would expect.

### ML

[//]: <> TODO

### CONFIG
The query will make a call to an in-memory database storing all global configs.

The syntax is as follows,

`FROM CONFIG."table"`

where table is replaced by the name of the table where the target config resides

### LISTS

Version 2 list membership checks can be done through list queries. The syntax is as follows,

`FROM LIST_KIND."list_type"`

Where LIST_KIND is one of DOMAIN_LISTS, ALL_DOMAIN_LISTS, or MULTI_DC_LISTS and list_type is the relevant type for the
list to be checked.

For a full example see the v2 list example in the examples section.


## WHERE Clause
A WHERE clause defines additional filtering conditions on the data source defined by the FROM clause. They can be
defined as a static, dynamic or an IN clause (see below)

wHERE clauses can be chained together (conjunction) using the AND keyword.

### Dynamic Clause
Dynamic clauses are generated from the request context. These contexts include,

- Request payload: A field of the fraud request which generally holds any runtime context needed for a rule to be
evaluated.
- Request metadata: An additional field of the fraud request which can be used in the same manner as the payload (in
general, the payload should be used)
- Config: Statically defined configs of the rule holding the query
- Nested query: Reference another query that is in the same Rule by using its name in the context
- System:

The syntax for dynamic clauses is as follows,

`WHERE DYNAMIC "target_column" = "inputColumn" IN context CAST cast_type`

*context* is one of the keywords *PAYLOAD*, *METADATA*, *CONFIG*, or *SYSTEM*

*inputColumn* is the name of the column to select in the input context. Note that PAI Risk will convert these column
names to camel case. For example if we request a payload {"customer_id" : "12345"} if you wanted to use the
"customer_id" column of the payload you would reference it as customerId.

*target_column* is the name of the column in the data source to query

*cast_type* needs to be one of the supported types (see the CAST clause section) and should match the type of the target
column in the query's data source.

### UDFs
We have also provided various UDFs which can be applied to the dynamic clause request column.

There are two ways that UDFS can be applied,

Directly on the request column and only one can be applied or at the end of the where clause (where you can apply as
many as needed)

The following UDFs are applied on the request column directly,

- Geohash
- Substring Index
- Start of Month
- End of Month
- Marketplace Category
- Marketplace Price Bucket
- Email Domain
- SHA256
- Address Fingerprint

and the following UDFs are applied at the end of the where clause,

- Strip Prefix
- Substring
- String Replace
- String Replace Pattern
- Truncate
- Email Normalize
- Cast
- SQL Substring

For more details on each UDF see below.

#### Geohash
Produces a geohash from a latitude / longitude with a given precision level.

`WHERE DYNAMIC "geohash" = GEOHASH("latitude", "longitude", 3)`

[//]: #### Substring Index

[//]: <> TODO

`WHERE DYNAMIC "ip" = SUBSTRING_INDEX("ip", ".", 3)`

#### Start of Day
Produces a timestamp which represents the start of the day for which the request timestamp falls under.

Optionally provide a unit argument which should be one of SECONDS or MILLISECONDS (case insensitive / unquoted and
defaults to SECONDS if not provided)

`WHERE DYNAMIC "start" = START_OF_DAY("timestamp", MILLISECONDS) in PAYLOAD CAST BIGINT`

#### End of Day
Produces a timestamp which represents the very end of the day for which the request timestamp falls under.

Optionally provide a unit argument which should be one of SECONDS or MILLISECONDS (case insensitive / unquoted and
defaults to SECONDS if not provided)

`WHERE DYNAMIC "start" = END_OF_DAY("timestamp", MILLISECONDS) in PAYLOAD CAST BIGINT`

#### Start of Month
Produces a timestamp which represents the start of month for which the request timestamp falls under.

Optionally provide a unit argument which should be one of SECONDS or MILLISECONDS (case insensitive / unquoted and
defaults to SECONDS if not provided)

`WHERE DYNAMIC "start" = START_OF_MONTH("timestamp", MILLISECONDS) in PAYLOAD CAST BIGINT`

#### End of Month
Produces a timestamp which represents the very end of month for which the request timestamp falls under.

Optionally provide a unit argument which should be one of SECONDS or MILLISECONDS (case insensitive / unquoted and
defaults to SECONDS if not provided)

`WHERE DYNAMIC "start" = END_OF_MONTH("timestamp", MILLISECONDS) in PAYLOAD CAST BIGINT`

#### Hour Add
Produces a timestamp with some number of hours added to the request timestamp.

`WHERE DYNAMIC "timestamp" = HOUR_ADD("ts", 1) in PAYLOAD CAST BIGINT`

#### Now
Produces a timestamp with the request timestamp.

`WHERE DYNAMIC "event_ts" > "NOW()" IN SYSTEM CAST BIGINT`

#### Marketplace Category
Produces the marketplace category name from a category id.

```
SELECT "threshold"
FROM CONFIG."categoryid"
WHERE DYNAMIC "categoryname" = MARKETPLACE_CATEGORY("categoryId") IN PAYLOAD CAST TEXT;
```

#### Marketplace Price Bucket
Converts a price into a marketplace price bucket.

`WHERE DYNAMIC "price_bucket" = MARKETPLACE_PRICE_BUCKET("price") IN PAYLOAD CAST TEXT`

#### Email Domain
Checks if an email is valid and retrieves the last two parts of the email domain

`WHERE DYNAMIC "emaildomain" = EMAIL_DOMAIN("email") IN PAYLOAD CAST TEXT`

#### SHA256
Apply the SHA256 hashing algorithm

`WHERE DYNAMIC "fingerprint" = SHA256("card_number") IN PAYLOAD CAST TEXT`

#### Address Fingerprint

Produces an address fingerprint from a set of location based values

`WHERE DYNAMIC "afp" = AFP("addr1", "addr2", "city", "state", "pincode") IN PAYLOAD CAST TEXT;`

#### Strip Prefix

Removes the provided prefix from the beginning of the request column

`WHERE DYNAMIC "someid" = "id" IN PAYLOAD CAST TEXT STRIP_PREFIX "prefix"`

#### Substring
Select the substring given by the provided boundaries to the right hand side of the comparison operation

`WHERE DYNAMIC "someid" = "id" in PAYLOAD CAST TEXT SUBSTRING(0,4)`

#### String Replace
Replaces the target String with the provided replacement to the right hand side of the comparison operation

`WHERE DYNAMIC "someid" = "id" in PAYLOAD CAST TEXT REPLACE("toReplace","replacement")`

#### String Replace Pattern

Replaces the REGEX pattern String with the provided replacement to the right hand side of the comparison operation

`WHERE DYNAMIC "someid" = "id" in PAYLOAD CAST TEXT REPLACE_PATTERN("[0-9]+","replacement")`

#### SQL Substring
Applies a SQL-like Substring operation to the right hand side of the comparison operation.

The first argument is the index to begin from (inclusive) of the substring. It is 1 Indexed and inclusive. In addition,
a negative index can be provided where -1 points to the last character of the String. Zero is not a valid input and will
always result in an empty String being returned.

The second argument is the number of characters to include starting from the begin index. If the number of characters
exceeds the length of the String, it will return as many characters as possible.

`WHERE DYNAMIC "number" = "accountNumber" in PAYLOAD CAST TEXT SQL_SUBSTRING(8,4)`

Examples

- `SQL_SUBSTRING(1, 5) applied on "12345"   // 12345`
- `SQL_SUBSTRING(1, 6) applied on "12345"  // 12345`
- `SQL_SUBSTRING(-1, 3) applied on "12345" // 345`
- `SQL_SUBSTRING(-1, 6) applied on "12345" // 12345`

#### Truncate
Substring index splits the request value by "." and then takes the first section of the result. For example
"192.168.1.1" would result in 192

`WHERE DYNAMIC "amount" = "txn_amount" IN PAYLOAD CAST BIGINT TRUNCATE`

#### Email Normalize
Apply email normalization to the right hand side of the comparison operation,

- lower case + trim
- remove periods from the local part
- remove tag part (aaa+bbb@gmail goes to aaa@gmail) from the local part
- replace googlemail.com with gmail.com

`WHERE DYNAMIC "email" = "email" in PAYLOAD CAST TEXT EMAIL_NORMALIZED`

### Nested Queries
Simple nested queries are supported in the PAI Risk DSL. This allows queries to filter by the results of another query that is within the same Rule.

**query1**
```
SELECT "deviceid"
FROM "VELOCITY_LOOKUP"."customer_deviceid"
WHERE DYNAMIC "customerid" = "customerId" IN PAYLOAD CAST TEXT;
```

**query2**
```
SELECT "device_blacklist"
FROM "RISK_LIST_LOOKUP"."device"
WHERE DYNAMIC "deviceid" = "query1.deviceid" IN "query1" CAST TEXT;
```

### IN Clause
The PAI Risk DSL supports the IN keyword in the Where clause of the query. It’s used to compare against a list, like in
standard SQL.

Note: In Clauses are different than the IN keyword used in dynamic queries for selecting a request context.

#### Static IN Clause

A static IN clause is used to compare against a predefined list of values. They take the following form,

`WHERE "deviceId" IN ("12378123", "52839041", "78296123")`


#### Dynamic IN Clause

A dynamic in clause is an IN clause which is generated from the request context. They take the following form,

`WHERE DYNAMIC "columnName" IN "list" IN PAYLOAD CAST TEXT`

*keyName* is the name of the column in the datasource being queried
*list" is the name of the column in the request context which should be an array of values (not objects)

In addition, the query DSL supports UDFS in dynamic in clauses which can generate a list of values from the request
context in various ways (see below for all available UDFS)

##### PROJECT

The Project UDF is a type of dynamic in clauses used to take, or project, an item out of an object, and make that
available for use in a query.

It’s easier to describe with an example:

Say you have this as an object in the Metadata:

device_blacklist: [{"id": 12378123, "name": "Device 1"}, {"id": 52839041,"name": "Device 2"},{"id": 78296123,"name":
"Device 3"}]

If you use,

`PROJECT("device_blacklist"."id") IN METADATA`

The result would become a list of the IDs, or in this case: ["12378123","52839041","78296123"]

To put it in practice, if you wanted to block all device’s that came in in this list from the Metadata, you might have
a query like this:

```
SELECT "deviceId"
FROM "RISK_LIST_LOOKUP"."device"
WHERE DYNAMIC "deviceId" IN PROJECT("device_blacklist"."id") IN METADATA CAST TEXT;
```

##### Address Fingerprint Soundex

The AFP Soundex UDF is another type of dynamic clause. It is used to generate an afp from the request context, and
then produce a list of all the soundex tokens of the afp.

The syntax is as follows,

`WHERE DYNAMIC "soundex" IN AFP_SOUNDEX("addr1", "addr2", "city", "state", "pincode", "name1", "name2", "name3") in
PAYLOAD cast text`

The parameters "addr1", "addr2", "city", "state", "pincode" are required while the UDF can optionally take any number of
name parameters.

This is an example of the UDF without any

`WHERE DYNAMIC "soundex" IN AFP_SOUNDEX("addr1", "addr2", "city", "state", "pincode") in PAYLOAD cast text`

##### Split

The Split In Clause UDF is used to generate a list of values from a single field of the request context.

The syntax is as follows,

`WHERE DYNAMIC "columnName" IN SPLIT("delimited", "|") IN PAYLOAD CAST TEXT;`

*columnName* is the name of the column in the target data source

*delimited" is the name of the column in the request context which should be a String that is delimited by the delimiter
we want to split by. For example "value1|value2|value3" if we are splitting by "|"

*"|"* is the delimiter we want to split by. *This needs to be a String of length 1*. We currently do not support
splitting by anything other than a single character.

#### Dynamic IN with Nested Queries

The Dynamic IN clause can also be used with nested queries. The cast type should match the column you are querying on in your WHERE clause.

**query1**
```
SELECT "account_number"
FROM "VELOCITY_LOOKUP"."accounts"
WHERE DYNAMIC "customer_id" = "customer_id" IN PAYLOAD CAST TEXT;
```
**query2**
```
SELECT "device_id"
FROM "RISK_LIST_LOOKUP"."device"
WHERE DYNAMIC "account_number" IN "query1.account_number" IN "query1" CAST INT;
```

## FOREACH Clause

In addition to our standard query structure we have included an optional foreach clause which allows you to stage
*multiple* queries over an array of objects in the input request. The main difference between using foreach over project
is that a foreach clause produces multiple queries.

The general form is,

```
FOREACH clause
SELECT clause
FROM clause
WHERE clause;
```

And a more concrete example could be,

```
FOREACH "items" IN PAYLOAD
SELECT "EPOCH_TIME" FROM "hero_velocity_lookup"."first_signup_by_device"
WHERE DYNAMIC "device_id" = "id" IN FOREACH CAST TEXT
```

Where items would need to be an array of object with a field called "items".

## Examples

The following section provides some examples for some common query structures

### List V1 Membership Check

A very common query which accesses the list keyspace to do a simple membership check. PAI Risk provides management tools
for black listing / white listing by various identifiers (most commonly device id, customer id)

```
SELECT "p2b_device_id_blacklist"
FROM "RISK_LIST_LOOKUP"."device"
WHERE DYNAMIC "deviceid" = "deviceID" IN PAYLOAD CAST TEXT;
```

This query executes a Cassandra lookup which checks if the device id given from the Payload field "deviceID" is in the
"p2b_device_id_blacklist" list.

### Domain List Membership Check (List V2)

If you need to do a membership check of a v2 list we have provided the follow query format (depends on the kind of list)

```
SELECT "blacklist"
FROM LISTS."customer"
WHERE DYNAMIC "customerid" = "customerId" IN  PAYLOAD CAST TEXT;
```

### All Domain List Membership Check (List V2)

```
SELECT "blacklist"
FROM ALL_DOMAIN_LISTS."customer"
WHERE DYNAMIC "customerid" = "customerId" IN  PAYLOAD CAST TEXT;
```

### Multi DC List Membership Check (List V2)

```
SELECT "blacklist"
FROM MULTI_DC_LISTS."customer"
WHERE DYNAMIC "customerid" = "customerId" IN  PAYLOAD CAST TEXT;
```


### Velocity Lookup

Another common query category which accesses a velocity keyspace. The various business verticals which have integrated
with PAI Risk have their respective keyspaces containing features generated by our near-realtime processing pipeline
(jitpipe) These attributes are generated continuously and leveraged by rules producing fast reacting rules.

```sql
SELECT "customer_id", "customer_score"
FROM "wallet_velocity_lookup"."customer_score"
WHERE DYNAMIC "customer_id" = "payeeCustId" IN PAYLOAD CAST BIGINT;
```

The above query executes a Cassandra lookup which retrieves the customer score of the customer whose id is defined by
the payload field "payeeCustId"

### With UDFs

#### AFP Soundex In Clause

The following is an example where we want to produce an address fingerprint from columns of the request payload. We
then want to check the resulting soundex tokens of the afp to see if any of those tokens have been black listed.

````
SELECT "blacklist"
FROM "risk_list_lookup"."soundex"
WHERE DYNAMIC "soundex" IN AFP_SOUNDEX("addr1", "addr2", "city", "state", "pincode", "name1", "name2", "name3") in PAYLOAD CAST TEXT;
````

## Usage Tips

We are constantly looking to improve the ease of use of our query DSL (which does have some pain points admittedly)
The following section outlines a few tips on using the DSL painlessly

### Data Explorer

One of the difficulties with writing queries is it requires some awareness of the underlying schema of the data sources.
This is especially true when using Cassandra as a data source.

To help with this problem we have created a data explorer in PAI Risk which allows for exploration of our backend schema.

![de](/img/de1.png)

In addition to providing info about our Cassandra schema the data explorer window has allows you to write and test your queries.
Its highly suggested you try out your queries in the data explorer before creating a rule.

![de](/img/de2.png)

After entering your query, you will be prompted to provide values for any runtime context required by your query. The results of
executing the query is then shown.


### Configuration Manager

Schema exploration for global configs can be done through the config manager page. Use the left drop down to view the available
tables and the right drop down to view the available columns to select.

![cm](/img/cm.png)

```
SELECT "risk_threshold"
FROM CONFIG."marketplace_category"
WHERE DYNAMIC "categoryname" = "categoryName" in PAYLOAD CAST RAWTEXT;
```

Could be used to retrieve values for the above config


### Request Mapping

[//]: <> TODO

### Monitor Mode

[//]: <> TODO
