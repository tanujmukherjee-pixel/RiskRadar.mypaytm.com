---
layout: docs
title: Attributes
permalink: docs/attributes/
---

# Attributes

Attributes (*formerly called features*) are the data points used to make fraud based decisions. 

They are composed of multiple parts, including:

- Metadata, such as name, version, and description describing the attribute
- An operational dataset (Cassandra) which is used by the rule engine
- A job (either DIY or jitpipe) to maintain the above data set

Attributes can be created and managed either using a user interface (DIY) or by directly building it out in the
jitpipe project. 

These methods provide both a description of the workflow required to represent the attribute as well as management tools
for starting, stopping, deploying, scheduling the job(s) used to maintain the attribute. 

While attributes can be maintained using jitpipe, they do not go through the same steps of being registered as one using
DIY. This means they do not have the same identity metadata describing them and their usage is a bit more implicit.

- [Job Types](#job-types)
  * [Streaming](#streaming)
      - [Kafka](#kafka)
      - [Kinesis](#kinesis)
  * [Bootstrap Single Source Streaming](#bootstrap-single-source-streaming)
      - [S3 & Kafka](#s3-and-kafka)
  * [Bootstrap Many Source Streaming](#bootstrap-many-source-streaming)
  * [Batch Job](#batch-job)
- [Job Classes](#job-classes)
  * [Streaming Job](#streaming-job)
  * [Bootstrap Streaming](#bootstrap-streaming)
  * [Bootstrap Multi Source Streaming](#bootstrap-multi-source-streaming)
  * [Streaming Source Configuration](#streaming-source-configuration)
  * [Batch Data Source Configuration](#batch-data-source-configuration)
- [Batch Data Sources Enum](#batch-data-sources-enum)
  * [Cassandra Sink Configuration](#cassandra-sink-configuration)
    + [Cassandra Event Operations](#cassandra-event-operations)
- [Column Transformations](#column-transformations)
  * [Spark Expression](#spark-expression)
  * [renameColumn](#renamecolumn)
  * [Date Parsers](#date-parsers)
    + [Via Spark Expression](#via-spark-expression)
    + [Predefined Formats](#predefined-formats)
  * [extractJson](#extractjson)
  * [fromJsonArray](#fromjsonarray)


# Attribute Studio

Attribute Studio is a UI-based solution (integrated into the PAI Risk UI) for creating attributes.

[//]: <> TODO

# Jitpipe

[//]: <> TODO

# Job Types

Job types are categories meant to describe common processing patterns used to generate the data of an attribute. 
Those patterns may be achieved through one or more jobs, depending on the sort of data set being generated.

Additionally, the configuration required for these various jobs can vary. See the *job class section* for more details.

## Streaming

Streaming Jobs include any attribute which can be captured by a streaming data source only.

*Some common usages include attributes based on the last hour, 24 hours, or 1 week.* 

### Tips
- Set a TTL equal to the required look back of the attribute. This will prevent the data set from growing indefinitely
with irrelevant data.

### Examples

#### Kafka

```
job {
  streamingSource {
    platform = "kafka"
    topic = "paylite.am.paymentmethod"
    columns = ["userId","type","fingerprint","createdAt","version"]
    condition = "fingerprint != '' AND type != '' AND version == 0"
    timeColumn = "epoch_time"

    columnTransformations = [
      "dropNulls|createdAt|createdAt",
      "fromHeroAMToEpochMs|createdAt|createdAt",
      "renameColumn|createdAt|epoch_time",
      "renameColumn|userId|customerid",
      "renameColumn|type|paymentmethodtype",

      "dropEmptyString|fingerprint|fingerprint"
    ]
  }
  cassandra {
    raw {
      keyspace = "hero_am_velocity_lookup"
      table = "customer_add_payment_method_v2"
      columns = ["customerid", "paymentmethodtype", "fingerprint", "epoch_time"]
      partition = "customerid"
      clustering = ["paymentmethodtype", "fingerprint"]
      ttl = "30 days"
      event {
        operation = "noop"
      }
    }
  }
}
```

#### Kinesis 

```
job {
  streamingSource {
    platform   = "kinesis"
    topic      = "j5-service-events-stg"
    columns = ["event_type", "email", "remote_ip", "timestamp"]
    condition = "email != '' AND event_type = 'signin_failure'"
    timeColumn = "epoch_time"

    columnTransformations = [
      "renameColumn|timestamp|epoch_time",
      "renameColumn|email|email_address",
      "normalizeEmail|email_address|email_address",
      "dropEmptyString|email_address|email_address"
    ]
  }
  cassandra {
    raw {
      keyspace = "hero_um_velocity_lookup"
      table = "failed_signins_by_email_ip"
      partition = "email_address"
      clustering = ["remote_ip", "epoch_time"]
      columns = ["email_address", "remote_ip", "epoch_time"]
      ttl = "24 hours"
      event {
        operation = "noop"
      }
    }
  }
}
```

Underlying job class is StreamingJob (see below on how to configure)

## Bootstrap Single Source Streaming

A feature type is made to model an attribute whose data never expires and is updated real time. The bootstrapping portion
of maintaining the attribute is a one time operation which reads the entire known history of the relevant data set. All
future events are then processed in a streaming fashion.

The underlying job classes are StreamingJob and Bootstrap Streaming Job.

Normally these features can be written as a Many Source Streaming instead

### Example

#### S3 and Kafka

```
job {
  bootstrap {
    hdfsPath = "s3://ppbl-osmose-workspaces/mule/rt-features/latest/customers_signup_kyc/"
    hdfsDataFormat = "parquet"
    autoRename = false
    columns = ["custid", "kyc_epoch", "signup_epoch", "signup_date"]
    columnTransformations = [
    ]
    condition = "custid is not null"
    timeColumn = "signup_epoch"
  }
  streamingSource {
    platform = "kafka"
    topic = "jocata_kyc_topic"
    columns = ["customer_id", "created_at", "time_full_kyc", "evaluationType"]
    timeColumn = "signup_epoch"
    columnTransformations = [
      "renameColumn|customer_id|custid",
      "toLowerCase|evaluationType|evaluation_type",
      "substringOperation|created_at|0,19|created_at",
      "fromWalletToEpoch|created_at|signup_epoch",
      "substringOperation|time_full_kyc|0,19|time_full_kyc",
      "fromWalletToEpoch|time_full_kyc|kyc_epoch"
    ]
    condition = "evaluation_type = 'customer_onboarding' and custid is not null"
  }

  cassandra {
    raw {
      keyspace = "bank_velocity_lookup"
      table = "mule_rt_customer"
      partition = "custid"
      clustering = []
      columns = ["custid", "kyc_epoch", "signup_epoch"]
      ttl = "0 minutes"

      event {
        operation = "noop"
      }
    }
  }
}
```

## Bootstrap Many Source Streaming

Similar to the Bootstrap Single Source feature type except it supports more complex bootstrapping. The main difference
is support for joins in the initial bootstrapping of the attribute. 

This is the preferred feature type for lifetime attributes as it can solve all use cases solved by the single source
variant (and more)

The underlying job classes are StreamingJob and Bootstrap Many Source Streaming Job

### Example

#### Multiple DAAS Datasets / Kafka Stream

```
job {
  bootstrap {
    timeColumn = "epoch_time"
    dataSources = [
    {
      path        = "406_s3v1"
      columns     = ["id", "user_id", "payment_method_type", "deleted_flag"]
      filter      = "payment_method_type = 'CREDIT_CARD' AND user_id IS NOT NULL"
      columnTransformations = [
        "renameColumn|id|payment_method_id",
        "renameColumn|user_id|customer_id",
        "addColumn|1|oneTemp",
        "substractionOperation|oneTemp,deleted_flag|is_active"
      ]
    },
    {
      path          = "401_s3v1"
      dataFormat    = "mergeSchemaParquet"
      columns           = ["fingerprint", "payment_method_id", "created_at", "brand", "last4digits", "expiration_date", "yjcard_flag", "authenticated_flag"]
      autoRename        = false
      filter            = "fingerprint IS NOT NULL"

      columnTransformations = [
        "fromPayliteModulePaypay|created_at|epoch_time",
        "renameColumn|yjcard_flag|is_yj_card",
        "renameColumn|authenticated_flag|is_3ds_verified",
        "aesDecryption|last4digits|paypayAES|last_4_digits",
        "renameColumn|fingerprint|fingerprint_raw",
        "aesDecryption|fingerprint_raw|paypayAES|fingerprint",
        "renameColumn|expiration_date|expiration_date_encrypted",
        "aesDecryption|expiration_date_encrypted|paypayAES|expiration_date"
      ]

      combiner {
        type      = "join"
        join_type = "inner"
        join_cols = ["payment_method_id"]
      }
    }
  ]
  }
  streamingSource {
    platform = "kafka"
    topic = "usermoduleassets.paymentmethods.credit-info"
    hasJsonPrefixBytes = true
    columns = ["data.customer_id", "data.event", "data.fingerprint", "data.expiration_date", "data.is_yj_card", "data.last_4_digits", "data.brand", "data.created_at", "data.verification_status"]
    condition = "event IN ('CARD_ADD', 'CARD_DELETE', 'CARD_3DSECURE_ATTEMPT') AND fingerprint IS NOT NULL AND customer_id IS NOT NULL"
    timeColumn = "epoch_time"

    columnTransformations = [
      "renameColumn|data.customer_id|customer_id",
      "renameColumn|data.fingerprint|fingerprint",
      "renameColumn|data.expiration_date|expiration_date",
      "renameColumn|data.is_yj_card|is_yj_card",
      "renameColumn|data.last_4_digits|last_4_digits",
      "renameColumn|data.brand|brand",
      "renameColumn|data.event|event",
      "renameColumn|data.created_at|epoch_time",
      "renameColumn|data.verification_status|is_3ds_verified",
      "mapPayPayEventTypeToActiveCard|event|is_active"
    ]
  }
  cassandra {
    raw {
      keyspace = "paypay_oauth_velocity_lookup"
      table = "fingerprint_customer_status"
      columns = ["fingerprint", "customer_id", "is_active", "epoch_time", "expiration_date", "is_yj_card", "last_4_digits", "brand", "is_3ds_verified"]
      partition = "fingerprint"
      clustering = ["customer_id"]
      ttl = "lifetime"
      event {operation = "last"}
    }
  }
}
```

[//]: <> TODO

## Batch Job

Underlying job class is Bootstrap Many Source Streaming Job

# Job Classes

Underlying features are various job classes which each have their own processing flows and configuration requirements.

## Streaming Job

The top level attribute for the configuration of a streaming job will always be a single streaming source.

### Configuration

#### streamingSource
See the Streaming Data Source Configuration section below

### Tips

- Columns are the actual names in the source system and are selected prior to column transformations being applied
- The condition attribute is applied *AFTER* column transformations (Note - it is recommended to use
preTransformationFilter and postTransformationFilter for clarity in your attribute configurations)
- The filter attribute does *NOT* exist for StreamingJobs

## Bootstrap Streaming 

This job class is a legacy class prior to allowing for joining of multiple data sources.

This job type contains two main configurations: 
1. A single bootstrap
2. StreamingSource conf.

### Configuration

Key Name | Required | Type | Description | Default
bootstrap | Yes | Object | Top level object of the bootstrapping processing step of the attribute
streamingSource | Yes | Object | Top level object for the streaming processing step of the attribute (see Streaming Source Configuration section)

#### bootstrap 

The following are all nested in the bootstrap object,

Key Name | Required | Type | Description | Default Value (If Applicable)
hdfsPath | Yes | String | HDFS, S3, or Dataset path of the input source |
hdfsDataFormat | Yes | Enum (see Batch Data Source section) | Data format of the bootstrapping source| parquet
lookback | No | String || No Lookback
autoRename | No | Boolean || False (1.8.273) and True (Pre 1.8.273)
columns | Yes |  Array of Strings | The initial columns to read from the input data source |
columnTransformations | Yes | Array of String | Array of valid column transformations to be applied |
condition | Yes |  String | String predicate to filter out input data, set to TRUE if no filtering is needed. Applied after column transformations by default |

#### streamingSource
See the Streaming Data Source Configuration section below

### Tips
- The bootstrap configuration differs from the data source configuration of a multi source job.

## Bootstrap Multi Source Streaming

This job class is used by both the bootstrapping step of a Bootstrap Multi Source Streaming job and also Batch Jobs.

### Configuration

Key Name | Required | Type | Description | Default
bootstrap | Yes | Object || Top level object of the bootstrapping processing step of the attribute
bootstrap.dataSources | Yes | Array of Object (see Batch Data Source Configuration section) ||
bootstrap.timeColumn | Yes | Object ||
bootstrap.lookBackDuration| No | String | lookback duration, e.g. "2 days" |
streamingSource | Yes | Object | Top level object for the streaming processing step of the attribute (see Streaming Source Configuration section)

## Streaming Source Configuration

Key Name | Required | Type | Description | Default
platform | Yes | Enum (kafka or kinesis) | Platform of the input streaming source |
topic | Yes | String | Topic name of input streaming source | 
columns | Yes |  Array of Strings | The initial columns to read from the input data source |
preTransformationFilter | No | String | Filter predicate which is applied prior to column transformations being applied | No Filtering
columnTransformations | Yes | Array of String | Array of valid column transformations to be applied |
condition (legacy) | *No (As of 1.8.273)*, Yes prior to that | String | Filter predicate which is applied prior to transformations being applied |
postTransformationFilter | No | String | Filter predicate which is applied after column transformations are applied | No Filtering
timeColumn | Yes | String | Column to be used to determine event time of each message (important for TTL) | 
hasJsonPrefixBytes | No | Boolean || False

## Batch Data Source Configuration

Key Name | Required | Type | Description | Default
path | Yes | String | HDFS, S3, or Dataset path of the input source |
dataFormat | Yes | Enum (see Batch Data Source section) | Data format of the batch source| parquet
columns | Yes |  Array of Strings | The initial columns to read from the input data source |
columnTransformations | Yes | Array of String | Array of valid column transformations to be applied |
filter | Yes |  String | String predicate to filter out input data, set to TRUE if no filtering is needed. Applied after column transformations by default |
applyFilterBeforeTransformation | No | Boolean | If set to true filters will be applied prior to column transformations being applied | False
combiner | No | Object or String (See Combiner Configuration section) | Object or String which describes a join operation between batch data sources | 
autoRename | No | Boolean || False (1.8.273) and True (Pre 1.8.273)
timeColumn | Yes/No | String | Column to be used to determine event time of each message. If this data source is an element inside bootstrap.dataSources[] array - as is the case for "Bootstrap Multi Source Streaming" and bootstrap.lookBackDuration is specified, this field is required (Required: Yes) because currently Jitpipe code uses this field together with the bootstrap.lookBackDuration field to determine the start date of this data source, which corresponds to a query parameter "from=<yyyy-MM-dd>" when this data source is specified by a Dataset URL |


# Batch Data Sources Enum

The following are the available data source formats allowed in batchDataSource / dataSource format configurations,

name | description
json               | 
jsonschemaless     | 
jsonstring         | 
jsonbad            | 
orc                | 
csv                | 
tsv                | 
csvwithheader      | 
tsvwithheader      | 
mergeschemaparquet | 

## Cassandra Sink Configuration

All feature types include a cassandra sink configuration

Key Name | Required | Type | Description | Default
cassandra | Yes | Object | Top level object for Cassandra sink
cassandra.raw | Yes | Object | Another top level object for Cassandra sink

The following are all nested in the cassandra.raw object,

Key Name | Required | Type | Description | Default
keyspace | Yes | String | Name of the keyspace to write to in the Cassandra Sink | 
table | Yes | String | Name of the table to write to in the Cassandra Sink | 
columns | Yes | Array of String | Array of all the columns of the output Cassandra |
partition | Yes | String | Name of the partition key of the output Cassandra table |
clustering | Yes | Array of String | Array of the columns which makeup the clustering key of the output Cassandra table
ttl | Yes | String | Duration string describing how long a each output row should remain in Cassandra
perRowTTL | No | Boolean | Flag which determines if TTL will be applied on a per row basis (utilizes event time of each message) | false
isMillis | No | Boolean | Flag which determines if the timestamp column field is milliseconds or seconds | False
event | Yes | Object |||
event.operation | Yes | String Enum (See Cassandra Event Operations section) | |

### Cassandra Event Operations

The following outlines the possible values for the event operation enum,

Name | Description
first | Only output the first row in the target table. This setting uses the timestamp column to determine this.
last | Only output the last row in the target table. This setting uses the timestamp column to determine this.
noop | Output every single row that is processed

# Column Transformations

This section provides an overview of column transformations which are a set of functions which generally fall into these
categories,

- generating a new column based on an existing one
- dropping rows based on some criteria (when the predicate language of preTransformationFilter and postTransformationFilter don't capture the filter logic required)
- generating new rows based on some array based column (i.e explode)

## Spark Expression

An important transformation for using a predefined spark function to generate a new column.

The general format is 

`sparkExpr|expression|outputColumn`

For more info see 

- https://wiki.mypaytm.com/display/FRAUD/Jitpipe+Transformations
- https://spark.apache.org/docs/latest/api/java/org/apache/spark/sql/functions.html#expr-java.lang.String-

## renameColumn

`renameColumn|from|to`

One of the most important udfs for two reasons,

- Renaming a source input field to match the output field name.
- Pulling out nested fields from the input source so they can be used by other udfs.

### Examples

`renameColumn|cassandraBadColumn|cassandra_good_column`
`renameColumn|nested.foo|foo`

## Date Parsers

A very common requirements when building attributes is to take a formatted datetime string and convert it to an epoch
timestamp. That timestamp can be important as far as limiting search results when interacting with the feature and also
calculating an entries TTL (time-to-live) which is important as far as removing data no longer relevant to the 
attribute.

### Via Spark Expression

Date parsing can be achieved via the spark expression udf if there is not a predefined one for the format of your 
source's data. 

`sparkExpr|unix_timestamp(createdTime, 'yyyy-MM-dd HH:mm:ss.SSS')|epoch`

Note if your format includes any quotes you will need to wrap the spark expression in triple quotes and the format
itself within double quotes.

`"""sparkExpr|unix_timestamp(createdTime, "yyyy-MM-dd'T'HH:mm:ss")|created_at""",`

### Predefined Formats

There are a number of predefined column transformations which can be used. These are around for legacy reasons and also
in cases of bad data (single column multiple date formats) The preferred way of dealing with dates is using sparkExpr.

Format | Unit / Description | Timezone | Function Name
ISO-8601 | First Second of month of date string | UTC | fromISO8601ToFirstOfMonthEpoch  
ISO-8601 w/ Timezone Offset | Seconds | UTC w/ Timezone Offset | fromISO8601OffsetToEpochSeconds 
ISO-8601 | Seconds | IST (Asia/Kolkata) | fromISTISO8601ToEpoch           
ISO-8601 | Seconds | UTC | fromISO8601ToEpoch              
Standard Spark Format (EEE MMM dd HH:mm:ss zzz yyyy) | Seconds | IST (Asia/Kolkata) | fromISTToEpoch
yyyy-MM-dd HH:mm:ss | Seconds | IST (Asia/Kolkata) | fromWalletToEpoch 
MMM d, yyyy h:mm:ss a | Seconds | IST (Asia/Kolkata) | fromSignUpDateToEpoch
yyyy-MM-dd HH:mm:ss.S or yyyy-MM-dd HH:mm:ss | Seconds | IST (Asia/Kolkata) | fromMktplaceBootstrapDateToEpoch
ISO-8601 | Milliseconds | UTC | fromUserModulePaypayToEpochMs   
yyyy-MM-dd HH:mm:ss | Milliseconds | UTC | fromUserModulePaypay2ToEpochMs  
yyyy-MM-dd HH:mm:ss.S or yyyy-MM-dd HH:mm:ss.SS or yyyy-MM-dd HH:mm:ss.SSS | Milliseconds | UTC | fromPayliteModulePaypay          | 
yyyy-MM-dd'T'HH:mm:ss.SSSZ | Milliseconds | UTC | fromHeroAMToEpochMs             
yyyy-MM-dd'T'HH:mm:ss.S or yyyy-MM-dd'T'HH:mm:ss.SS or yyyy-MM-dd'T'HH:mm:ss.SSS | Milliseconds | UTC | fromRummyToEpochMs              

## extractJson

An important UDF for pulling values out of columns holding JSON String columns.

### Examples

```
extractJson|orderInfo|itemId|item_id
{"orderInfo":"{\"itemId\":10}"}
10
```

```
extractJson|orderInfo|customerInfo|customerInfo
extractJson|customerInfo|id|customer_id
{"orderInfo":"{\"customerInfo\":{\"id\":1}"}`
1
```

## fromJsonArray

An important transformation for pulling fields out of arrays of objects. Most often, this is used in combination with 
explode and select to generate a new row for every element of the array.

Note: This transformation must be applied to top level column (Use renameColumn to pull out nested fields prior to 
calling fromJsonArray).

### Examples

```
extractJsonArray|itemId|itemType|orderItems,
explode|orderItems|orderItem,
select|orderItem.itemId|item_id,
select|orderItem.itemType|item_type,
{"orderItems":[{"itemId":101,"itemType":"fashion"},{"itemId":202, "itemType":"electronics"}]}
101,fashion
202,electronics
```

```
renameColumn|orderInfo.orderItems|orderItems
extractJsonArray|itemType|orderItems,
explode|orderItems|orderItem,
select|orderItem.itemType|item_type,
{"orderInfo":{"orderItems":[{"itemId":101,"itemType":"fashion"},{"itemId":202, "itemType":"electronics"}]}}
fashion
electronics
```
