---
layout: docs
title: API Integration
permalink: docs/api-integration/
---

## API Integration

This document covers how to integrate PAI Risk into your existing workflow, making use of the profiles you've created.

- [Authentication](#authentication)
- [Risk Check](#risk-check)
  * [Request Body](#request-body)
  * [Response Body](#response-body)

## Authentication

PAI has out-of-the-box support for Google Authentication. This is required for all the List APIs in order to provide an audit trail, *but not the risk check as it will not be exposed*.

Any standard Google Authentication can be done and sent in the API Authorization as a Bearer token. PAI has example code snippets that can help if required.

## Risk Check

### Request

`POST /rt/fraudcheck`

#### Header

`Content-type: application/json`

#### Request Body

Key | Value
--- | ---
source (required) | Business source/domain. For instance, you might split by OAUTH/Payments. Your rules will be configured to a specific domain.
session_id (required) | A unique value that is sent to PAI, and will be tagged with all logs associated with this ID.
evaluation_type (required) | The configured evaluation that this message should be evaluated against. For instance, within OAUTH source you might have a Signup evaluation type. This will tell PAI to evaluate against the rules set up for Signup.<br><br>In the UI this is a **Profile**.
request_metadata (required) | Allows a nested json that can be used to evaluate in real-time. Recommended to use the metadata for things like IP Address, device ID.
request_payload (required) | Allows a nested json that can be used to evaluate in real-time.<br>Recommended to use the payload for things that are concrete to this transaction, such as merchantId or payment amount.

##### Example Request

```
{
  "source": "OAUTH",
  "session_id": "OAUTH_1536011111.783-117.242.94.32-1118-267809713-14",
  "evaluation_type": "signup",
  "request_metadata": {
    "channel_id": "ANDROIDAPP 7.3.2",
    "device_id": "Xiaomi-HMNOTE1S-860849031711111",
    "client": "androidapp",
  },
  "request_payload": {
    "phone_number": 555-555-5555
  }
}
```

#### Response Body

Key | Value
--- | ---
session_id | The same session_id that was passed into the request.
status | This is the status of the call itself. Possible values are: `SUCCESS`, `FAILURE`.<br><br>Failure means that something went wrong in the API call, such as the evaluation_type or source does not exist. If the result is a FAILURE, the reason will be in the reason field.<br><br>**Note: In the case of a failure you must choose how to handle processing. For example, in a timeout, you may retry or choose to pass the transaction.**
action_recommended | This is the result that PAI has recommended.<br><br>These actions can be set up by your team. The defaults are `PASS` & `BLOCK`. You can add to this in whichever way. For instance, if you wanted to pass the transaction but not give any points you could set it up to return: PASS_NO_POINTS.
action_recommended_type | The type of response. Possible values are: `ActionCode`, `Int`, `Commission` (Paytm Bank Only)
reason | If the status was FAILURE, then the reason for the failure will be here. The possible values are:<br><br>INVALID_REQUEST<br>SERVER_ERROR<br>TIMEOUT<br>UNKNOWN
message | A json object that contains 2 fields: `user`, and `cst`<br><br>"user" will have a string that is used to return a proper error code to the user. We recommend returning an error code instead of a message and handling it further down the chain.<br><br>"cst" is a list of error messages/codes that are for internal use. It is a list because the transaction may have been blocked for multiple reasons, and this will list them all.

##### Example Response

```
{
  "session_id": "MP_1536011111.783-117.242.94.32-1118-267809713-14",
  "status": "SUCCESS",
  "action_recommended": "BLOCK",
  "action_recommended_type": "ActionCode",
  "reason": "",
  "message": {
    "user": "ERR005",
    "cst": ["User is already signed up."]
  },
  "extra_options": {}
}
```

