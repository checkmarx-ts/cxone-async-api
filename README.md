# CheckmarxOne Async Python API Tool

This is a Python library that implements methods that support asynchronous access of the [CheckmarxOne REST API](https://checkmarx.stoplight.io/docs/checkmarx-one-api-reference-guide/).  At the lowest level, it is a simple wrapper for [Python Requests](https://pypi.org/project/requests/).  This API
is used by other applications maintained by Checkmarx Professional Services.

The library is organized into two parts:

* A low-level API that is a very thin layer that helps with invocation of API endpoints via Requests.
* A high-level API that has several composite workflows that hide the details of multiple low-level API invocations to perform common tasks.

## Design Principles

### Asynchronous I/O

All methods are designed to use async Python code.  This will help avoid
complications normally associated with multi-threading and the Python
GIL.  Client implementations will still be mostly performant since many
tasks associated with using the CheckmarxOne API tend to be I/O bound
due to the timing of REST API calls.

### High-Level Logical Composite Operations

Where it makes sense, the high-level API exposes objects that are composed
of one or more low-level API accesses.  The underlying API use is hidden
so that the high-level object avoids the need to create an algorithm
to implement common tasks.  Objects in the high level API provide an easy
way to interact with CheckmarxOne to perform logical operations without
needing to develop algorithms that use multiple low-level API calls.

### Raw Low-Level Responses

Rather than attempt to maintain DTOs and map responses to them,
the low-level APIs return a `requests.Response` object.  Consumers of the
low-level APIs can query the response code and consume the JSON
elements of the response through dictionary accessors or simple Jsonpath
expressions.  The high-level APIs abstract the low-level JSON responses
and return data appropriate for the high-level implementation.

In most use-cases, all elements of the JSON response are not required.
This makes maintaining DTOs that have all the elements mapped somewhat
irrelevant.

### Adaptable to API Updates

All REST API calls can be performed directly using the client object without
the need of the low-level API.  The low-level API are simple helper methods
that constructs the REST API request.  The client object executes the
constructed request and handles the server authorization transparently. Updates
to the REST API can be invoked even if the low-level API has not yet been
updated to support REST API changes.

## Quickstart

### Installation

TBD

## Examples

TBD
