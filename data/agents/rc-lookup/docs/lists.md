---
layout: docs
title: Lists
permalink: docs/lists/
---


## Lists

One of the most common kinds of rules are simple membership checks which can then be interpreted as a blacklist,
greylist, or whitelist. This will show you how to create a list, and how to query one in a rule.

We also support external API calls to add items to lists, or to check if an item exists in a list already. This can be useful if you have your own customer or merchant panel, and want to integrate with the risk system.



- [Lists](#lists)
  * [Core Concepts](#core-concepts)
- [V1](#v1)
- [V2](#v2)
  * [How-To](#how-to)
    + [User Interface](#user-interface)
      - [Type Management](#type-management)
      - [List Management](#list-management)
    + [V2 Migration](#v2-migration)
    + [Rules](#rules)
    + [List V2 Punishment](#list-v2-punishment)
    + [API](#api)
    + [List Transformations](#list-transformations)
      - [PII Lists](#pii-lists)
- [V2 API Integration](#api-integration)
  * [Add to List](#add-to-list)
  * [Search List](#search-list)


### Core Concepts

- List Type: A category of lists grouped together by a common characteristic (key schema)
- List: A collection of members sharing a type
- List Member: An entity belonging to a particular list
- Key: A column (or collection of columns) used to uniquely identify a list member
- Domain: A unit of division within PAI Risk which provides separation between different systems integrating with Maquette
- PII: Acronym for personally identifiable information

PAI Risk provides a user interface / API for managing what lists and their members.

## V1

V1 lists were introduced before domains were added to PAI Risk. V1 was simply an API for managing list members and
leveraged the existing database access pattern for usage in rules.

We are deprecating V1 lists with the release of V2.

V1 lists will continue to function as expected for the foreseeable future.

## V2

A second iteration of the lists API has been release.

The initial feature set includes,

- 3 kinds of lists
  * Domain: Domain specific lists
  * All Domain Lists: shared across all domains in a single data center
  * Multi Datacenter: shared across all domains in multiple data centers
- API for managing types and lists
- More sensible permissions on lists
- Query DSL for interacting with lists
- All core operations from V1
- V1 to V2 Migration Helper

And the following are planned / likely additions for later (In no particular order)

- Search pagination
- CSV Import / Export
- List change event publish (Allow for external consumers to act upon list changes)

### How-To

#### User Interface

The following section overviews how to use the PAI Risk Admin UI for various list operations

##### Type Management

![de](/img/listv2-2.png)

New types can be defined for each kind of lists using the more options icon (the + icon at the bottom if you are
scrolling deep in the table)

![de](/img/listv2-3.png)

Finish creating the new type (cannot be deleted) by providing the name and key columns as desired

![de](/img/listv2-1.png)

To use multi data center (if available on the install) or the special all domain use the checkboxes. If both options
remain unchecked, the currently selected domain will be used.


##### List Management

To add a new list select a type and again use the more options button

![de](/img/listv2-4.png)

Then provide a name (i.e blacklist) for the new list (cannot be deleted)

![de](/img/listv2-5.png)

#### V2 Migration

There is an internal command line tool for migrating v1 list to v2 list - for more information contact a member of the
Osmose team.

#### Rules

For information on how to write a query interacting with v2 lists see the query docs.

Similarly, for using the query result in the rule script see the script docs

#### List V2 Punishment

See the rule script docs for how to do membership updates in the rule script

#### API

See swagger docs for API specification

#### List Transformations

This feature is only available for v2 lists,

Lists (not types) can have transformations associated with them. These transformations are associated with a specific
part of the primary key of the type of the list.

The current list of transformations include:

* sha256

##### PII Lists

The most common use case for list transformation is for obfuscating pii data.

Using this feature you can set up lists which will not persist PII data at rest anywhere in the PAI Risk system.

Create the *PII list* under the appropriate type

![de](/img/pii1.png)

Apply the Sha256 transformation on the relevant key part

![de](/img/pii2.png)

Keys values will now have the sha256 transformation applied while searching, writing, deletion, etc..

![de](/img/pii3.png)

To interact with a Pii list, you will need to use the Sha256 query UDF (see query guide for more details)

![de](/img/pii4.png)

Finally, you should also make sure to apply the Sha256 audit log transformation on the fraud request parameter used to
query the list at runtime (see evaluation mapper guide for more details).

![de](/img/pii5.png)

With this setup (sha256 list transformation, sha256 query udf, and sha256 audit transformation) only the hashed
version of your pii data will ever be persisted.

## API Integration

### Add to List

Used to programmatically add to a previously set up list, such as a user or device blacklist. Lists can be created in PAI directly, and used in the rules.

#### Request

`POST /v2/domains/{domain}/listMembers/{list_type}/{list_name}`

##### URL Parameters

Name | Value
--- | ---
Domain (required) | Business source / domain. For instance, you might split by OAUTH / Payments.<br><br>Your list will be configured to a specific domain.<br><br>*Cross-domain lists are also supported but not in this document. They are in Swagger.*
list_type (required) | A category of list whose members can be identified using the same properties. For instance, a Customer.
list_name (required) | A series of members joined together in a meaningful grouping. For instance, for the list type customer you might have a blacklist and a whitelist.

##### Body Parameters

Name | Value
--- | ---
key (required) | A list of name & value pairs to be added to the list.
comment (required) | Any comment that you want associated with why someone added to the list.
ttl (required) | Time in seconds that the value should stay in the list. Use 0 to stay in the list indefinitely.

##### Example Request

`POST /v2/domains/OAUTH/listMembers/customer/blacklist`
```
{
  "key": [
    {
      "name": "customerid",
      "value": "1235612356123123"
    }
  ],
  "comment": "Blacklisted for promotion abuse",
  "ttl": 0
}
```

##### Example Response

This will return a 201 response when successful.

### Search List

Used to search a list. For instance this could be used on another internal screen when searching for a customer, to display if they are blacklisted or whitelisted.

#### Request

`POST /v2/domains/{domain}/listMembers/{list_type}/{list_name}/_search`

##### URL Parameters

Name | Value
--- | ---
domain | Business source / domain. For instance, you might split by OAUTH / Payments.<br><br>Your list will be configured to a specific domain.<br><br>*Cross-domain lists are also supported but not in this document. They are in Swagger.*
list_type | A category of list whose members can be identified using the same properties. For instance, a Customer.
list_name | A series of members joined together in a meaningful grouping. For instance, for the list type customer you might have a blacklist and a whitelist.

##### Body Parameters

Name | Value
--- | ---
key | The field name to search. E.g. customerId
value | The value to search.

##### Example Request

`POST /v2/domains/OAUTH/listMembers/customer/blacklist/_search`

```
{
  "key": [
    {
      "name": "customerid",
      "value": "1235612356123123"
    }
  ]
}
```

##### Example Response

```
[
  {
    "listName": "blacklist",
    "key": [
      {
        "name": "customerid",
        "value": "1235612356123123"
      }
    ],
    "ttl": 0,
    "comment": "Blacklisted for promotion abuse",
    "modifier": "user@paytm.com",
    "timestamp": 1554757135000
  }
]
```
