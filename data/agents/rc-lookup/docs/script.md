---
layout: docs
title: Rule Scripts
permalink: docs/script/
---


## Script

The rule script is an essential part of PAI Risk which ultimately determines the result produced by an individual rule.

In a bit more detail, the script is a snippet of Scala code which needs to produce a value of the configured type of the 
rule it's associated with. Rules scripts are dynamically compiled and loaded by the rule engine application, there is no 
need for a redeployment when new rules are created.


- [Rule Script Context](#rule-script-context)
  * [Rule Script Context](#rule-script-context)
    + [API](#api)
      - [getAsOpt[T]](#getasoptt)
      - [getAsOrElse[T]](#getasorelset)
      - [getListAsOpt[T]](#getlistasoptt)
      - [getListOfObjects](#getlistofobjects)
      - [+=](#---add-context)
      - [tags.+=](#tags)
    + [Accessing Query Results](#accessing-query-results)
      - [Database Query](#database-query)
      - [ML Query (WIP)](#ml-query-wip)
      - [Global Config Query](#global-config-query)
      - [List V2 Query](#list-v2-query)
- [Result Types](#result-types)
  * [Action Code](#action-code)
  * [Inconclusive](#inconclusive)
  * [Punishment](#punishment)
  * [List V1](#list-v1)
  * [List V2](#list-v2)
- [Timeouts](#timeouts)
- [Tagging](#tagging)

## Rule Script Context

The rule script has available to it an object called the script context. It provides the rule script with the 
information needed to make decisions and ultimately produce a value.

There are 5 main components to the script context,

* Query Results: The values retrieves through the various query types
* Static Configurations: Predefined key values pairs defined on the rule
* Request Payload: A field of the fraud request which is meant to provide the context of the event we are evaluating
* Request Metadata: A field of the fraud request which is meant to provide the context of the event we are evaluating
* Rule Script variables: Rule scripts have the ability to mutate their own script context with a key value pair which 
can be used to inject some context into some error messages (action messages)

The script context is made available under the 'map' name and follows a JSON-like structure (arrays, objects, and 
values) fields can be accessed using various methods on the map using a dot separated String pattern.

For example,

    val customerId: String = map.getAsOrElse("${payload.customerId}", "")

For more details on using the script context see below.

### Rule Script Context

The rule script context is a container for the data needed to produce the script result. The following section shows how 
to access results from the various query types and also provides descriptions of methods available from the script context.

The contents of the script context can be accessed using a dot-separated string pattern. The top level elements of the 
script context are always the same 4 elements: `config`, `payload`, `metadata`, and `query`. For more information on
using the dot pattern to access data, see the respective sections under Accessing Data.

Each of these top-level elements points to a JSON-like object which is populated in the following manner:

* Config: Each config defined by the rule forms a leaf node in the config object. Each value is treated as a string
* Payload: Takes the same form as the fraud request payload
* Metadata: Takes the same form as the fraud request metadata
* Query: Each query forms an object named after the query name, within the object, the format depends on the kind of 
query being made. For more information see the accessing query results section.

#### API 

The rule script context is injected into rule scripts as a value called 'map' which provides some methods to access
data (see below for more details)

Most of the operations are defined on a type T which can take on the following types,

* Int
* Long 
* Float
* Double
* Boolean
* String
* INetAddress
 
The available operations are as follows,

##### getAsOpt[T]

Get a Scala Option containing an element of type T if it exists. Note that, if the element can't be cast as a T (or is not present), 
this method will return None.

`getAsOpt[T](key: String): Option[T]`
```scala
  val currentTxnAmount = map.getAsOpt[Long]("${payload.txnAmount}").getOrElse(0L)
  val amount = map.getAsOpt[Long]("${query.sum_query.amount}").getOrElse(0L)
  
  val newAmount = currentTxnAmount + amount
  
  if (newAmount > 5000) "BLOCK"
  else "PASS"
```

##### getAsOrElse[T]

Get an element of type T if it exists. Note that, if the element can't be cast as a T (or is not present), 
this method will return the provided default value.

`getAsOrElse[T](key: String, default: T): T`
```scala
    val currentTxnAmount = map.getAsOrElse[Long]("${payload.txnAmount}", 0)
    val amount = map.getAsOrElse[Long]("${query.sum_query.amount}", 0)
    
    val newAmount = currentTxnAmount + amount
    
    if (newAmount > 5000) "BLOCK"
    else "PASS"
```
##### getListAsOpt[T]

Get a Scala Option containing a list of elements of type T. Note that, if the list elements cannot be cast as a T (or the array is
not present), this method will return None.

`getListAsOpt[T](key: String): Option[Seq[T]]`

In addition, the function can be called with an optional second parameter. This value will act as a default value for 
null values. 

`getListAsOpt[T](key: String, defaultValue: T): Option[Seq[T]]`

This function is important to cases where a selected column can be null. See the following example for a
full explanation.
```scala
  val idsOpt       =  map.getListAsOpt[String]("${query.features.id}", "")
  val signupsOpt   =  map.getListAsOpt[Long]("${query.features.signup_count}", 0L)
  val deviceIdsOpt =  map.getListAsOpt[String]("${query.features.device}", "")
  
  val resultOpt = for {
     ids <- idsOpt
     signups <- signupsOpt
     devices <- deviceIdsOpt
  } yield List(ids, signups, devices).transpose
  
  resultOpt.foreach { results =>
    results.foreach {
      case (id: String, signups: Long, deviceId: String) if signups > 2 =>
         // do something to handle abnormal signup count (i.e add to add to list, tagging, ...)
    }
  }
  
  inconclusive
```    

In the above example, we would have a query selecting multiple columns, and expect it to return 0 or more rows.
Using `transpose` we can reconstruct those query results as rows, and then either generate a script result based on that or
perform some side effect.

Without the default value (due to an implementation detail) the rows cannot be reconstructed properly in the presence of 
null column values. 

##### getListOfObjects

[//]: <> TODO Example

Get a list of objects from an array of objects as a Map[String, String]

Note - A limitation of this method is that it converts each field value within the individual objects to strings, and thus
will only work properly for array objects containing value nodes.

In addition, this method will fail at evaluation time if the target array does not exist.

`getListOfObjects(key: String): Seq[Map[String, String]]`

[//]: <> TODO Example

##### += -> Add context

Adds the given value to the script context
```scala
    val signups =  map.getAsOrElse[Int]("${query.query1.device_signup_count}", 0)
    
    map += "signups" -> signups
    
    if (signups > 5) 
      "BLOCK"
    else
      "PASS"
```      

##### tags.+=

Tags the rule script result with the provided tag
```scala
    val signups =  map.getAsOrElse[Int]("${query.query1.device_signup_count}", 0)
    
    if (signups > 5) 
      "BLOCK"
    else if (signups > 1)
      map.tags += "suspicious"
      "PASS"
    else
      "PASS"
```
##### tags.++=

Tags the rule script result with the multiple tags
```scala
    val signups =  map.getAsOrElse[Int]("${query.query1.device_signup_count}", 0)

    if (signups > 5)
      "BLOCK"
    else if (signups > 1)
      map.tags ++= Set("suspicious", "review")
      "PASS"
    else
      "PASS"
```
#### Accessing Query Results

##### Database Query

This is the most common type of query and can be accessed as follows:

    map.getAsOrElse[Int]("${query.signup_query.count}", 0)
    
* The 'signup_query' part is the query name
* The 'count' part needs to be the name of one of the columns in the select part of the query

##### ML Query (WIP)

ML queries allow queries against a machine learning model for doing gibberish name detection. For more information
see - https://wiki.mypaytm.com/display/FRAUD/Gibberish+Name+Detector

##### Global Config Query

You can access the results of a global config query as follows,

    map.getAs[Int]("${query.threshold_query.threshold}")
    
* The 'threshold_query' part is the query name
* The 'threshold' part needs to be the name of one of the columns in the select part of the query. It corresponds to the 
name of the config we are trying to access. 

##### List V2 Query

All List-v2 queries are accessed in the same manner in the script context:

    map.getAsOrElse[Boolean]("${query.customer_query.blacklist}", false)

* The call must be typed as a Boolean, and the result will be true if the query determined that the target was a member
* The 'customer_query' part is simply the query name
* The 'blacklist' part would be the selected column of the query and is the name of the list being checked

## Result Types

The result type of a rule is defined at the rule creation, and the script must produce a value of the configured type (or it won't 
even compile)

Most commonly the Action Code type is used but there are other types available. For more details see below.

### Action Code

A set of predefined string values representing some kind of domain-specific action for the caller to react on. By default, the
"PASS" and "BLOCK" actions are defined for every domain but more can be added as required. Some additional examples are
"PASS_NORETURN" (marketplace) and "VERIFY" (UPI)

### Inconclusive

If a rule has children, it will evaluate the children if the parent rule does not produce a concrete result. 

In order to do this, a special keyword for inconclusiveness is required. If a parent rule returns inconclusive, it will evaluate any children rules. However, if a parent rule makes a decision (e.g. a "PASS", or a "BLOCK"), then the child rules will not be evaluated at all.

This allows for logic such as whitelisting. For example, suppose we wanted some rules that only evaluate if the credit card was the payment type. Then we would set up a parent rule that passes when the payment type is not a credit card.

With non-advanced rules (aka Simple rules), if any of the conditions does not match, the rule will return as inconclusive.

If all rules in a profile return "inconclusive", the entire profile will return "PASS". 

### Punishment

Using the punishment side effect you can execute a write command against any table in Cassandra.

Note: The punishment side effect will only execute for LIVE rules (not monitor)

Note: the reason for the name "punishment" is that, because its original purpose was to add to blacklist
as a temporary punishment (prior to the more specialized list side effects).

The following snippet is an example of how to use the punishment feature in your rule script,
```scala
  import com.paytmlabs.maquette.commons.rules.support.PunishmentActionSupport
  
  PunishmentActionSupport.punish(
    ,"risk_list_lookup", 
    ,"device", 50
  ("deviceid" -> map.getAs[String]("${payload.deviceID}"))("blacklist" -> true)
```
The punish method takes the following parameters (in the exact order)

* Keyspace Name
  * String
  * The name of the keyspace in Cassandra for the write operation
* Table Name
  * String
  * The name of the table in Cassandra for the write operation
* TTL
  * Int
  * The expiration (in seconds) of the row to be written
  * Optional
* Primary Key
  * One or more Tuples of type String -> Any
  * The entire set of tuples represents a full primary key setting for the target table. For example, if your table has
  a primary key of (a: String, b: Int) you could provide ("a" -> "foo", "b" -> 1)
* Clause Map 
  * One or more Tuples of type String -> Any
  * Each tuple represents a non key column setting. For example, if your table has 3 value columns 
  * Optional
  ("c": String, "d": Int) you might provide ("c" -> "bar", "d" -> 1) or ("d" -> 1) or none at all

### List V1

You can add members to a v1 list using the following snippet:
```scala    
    import com.paytmlabs.maquette.commons.rules.support.ListActionSupport
    
    val device = map.getAs[String]("${payload.deviceId}")
   
    if (somethingBad) 
        ListActionSupport.add("device", "property", "comment", "modifier")("deviceid" -> device)
        
    "PASS"
```    
The add method takes the following parameters (in the exact order)

* List Type
  * String
  * The type of the list to add to
* List Name
  * String
  * The name of the list to add to
* Comment
  * String
  * A comment explaining why the member was added
* Modifier
  * String
  * The name of the user (or in this case, some name describing the rule) who added the member to the list
* TTL
  * Int
  * The number of seconds that membership lasts for
  * Optional
* Primary Key 
  * One or more Tuples of type String -> Any
  * It should represent the key setting for the list member to add. It depends on the list type being used. For example 
  since a device has a single key of type String the value is ("deviceid" -> "the-actual-device-id"), a multipart key 
  might look like ("firstName" -> "steven", "lastName" -> "dk")

Note: The List V1 side effect will only execute for LIVE rules (not Monitor rules)

### List V2

You can add members to all kinds of lists within the rule script. The syntax is as follows,
```scala
    import com.paytmlabs.maquette.commons.rules.support.ListActionSupportV2

    val customer = map.getAs[String]("${payload.customerId}")

    if (somethingBad) {
        # Add to the domain list of the calling system
        ListActionSupportV2.add("customer", "blacklist", "punishment", "punishment-rule")("customerid" -> customer)

        # Add to the all domain list
        ListActionSupportV2.AllDomain.add("customer", "blacklist", "punishment", "punishment-rule")("customerid" -> 
        customer)

        # Add to a multi dc list
        ListActionSupportV2.MultiDc.add("customer", "blacklist", "punishment", "punishment-rule")("customerid" -> 
        customer)
    }

    "PASS"
```
The add method takes the following parameters (in this order)

* List Type
  * String
  * The type of the list to add to
* List Name
  * String
  * The name of the list to add to
* Comment
  * String
  * A comment explaining why the member was added
* Modifier
  * String
  * The name of the user (or in this case, some name describing the rule) who added the member to the list
* TTL
  * Int
  * The number of seconds that membership lasts for
  * Optional
* Primary Key 
  * One or more Tuples of type String -> Any
  * It should represent the key setting for the list member to add. It depends on the list type being used. For example 
  since a device has a single key of type String the value is ("deviceid" -> "the-actual-device-id"), a multipart key 
  might look like ("firstName" -> "steven", "lastName" -> "dk")
  
Note: The List V2 side effect will only execute for LIVE rules (not monitor)

## Timeouts

The rule script has a boolean value made available to it which indicates whether the queries for the rule has timed 
out.

That flag can then be used if the rule needs some specific behaviour on timeout. For example,
```scala
  if (timeout) "inconclusive"
  else if (map.getAsOrElse[Int]("${query.signup_query.count}", 0) > 3) "BLOCK"
  else "PASS"
```
## Tagging

Tags are labels that can be applied to a particular rule result. They don't actually impact the return value of the rule 
script but are included in the audit log and can be used as a search criteria in the review panel.

Tags can be added using the following code snippet,

    map.tags += "suspicious"

You can then search for this "suspicious" tag in the review panel to investigate those transactions.

## Utility Functions

### Haversine Distance

We have provided a function to calculate the haversine distance between a pair of points (points are longitude/latitude ordered).

```scala
import com.paytmlabs.maquette.commons.utils.Haversine

val currentCoordinates = map.getAs[Double]("${query.last_location.lon}") -> map.getAs[Double]("${query.last_location.lat}")
val transactionCoordinates = map.getAs[Double]("${payload.lon}") -> map.getAs[Double]("${payload.lat}")
val thresholdKm = map.getAs[Long]("${config.THRESHOLD_KM}")

val haversineDistanceKm = (Haversine(currentCoordinates, transactionCoordinates) / 1000).toInt

if (haversineDistanceKm > thresholdKm) map.tags += "suspicious_location"

inconclusive
```


