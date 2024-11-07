# CheckmarxOne Async Python API Tool

This is a Python library that implements methods that support asynchronous access of the [CheckmarxOne REST API](https://checkmarx.stoplight.io/docs/checkmarx-one-api-reference-guide/).  At the lowest level, it is a simple wrapper for [Python Requests](https://pypi.org/project/requests/).  This API
is used by other applications maintained by Checkmarx Professional Services.

The library is organized into two parts:

* A low-level API that is a very thin layer that helps with invocation of API endpoints via Requests.
* A high-level API that has several composite workflows that hide the details of multiple low-level API invocations to perform common tasks.

This requires Python 3.9 or greater.


## Quickstart

### Installation

**This package is not distributed via PyPi to avoid typo-squatting attacks.**

The install is typically performed by using a direct URL with an optional associated hash for verification.  The `releases` section of this repo
has the required copy/paste lines with required hashes.

### Examples

Example code is located in the examples directory.  Better documentation and examples will come over time.

