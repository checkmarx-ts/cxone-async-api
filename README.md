# CheckmarxOne Async Python API

This is a Python library that implements methods that support asynchronous access of the [CheckmarxOne REST API](https://checkmarx.stoplight.io/docs/checkmarx-one-api-reference-guide/).  At the lowest level, it is a simple wrapper for [Python Requests](https://pypi.org/project/requests/).

The library is organized into logical layers:

* A raw layer that can invoke Checkmarx One API endpoints that have yet to be documented or implemented in the low-level API layer.
* A low-level API that is a very thin layer or helper methods used to invoke API endpoints via `Requests`.
* A high-level API that has several composite workflows that hide the details of multiple low-level API invocations to perform common tasks.

The `CxOneClient` object is the connection context that handles all connectivity concerns.  It is async safe
and multiple instances can exist concurrently.

The `cxone-async-api` requires Python 3.10 or greater.

## Installation

You can add a reference to `cxone-async-api` in your dependencies (pinning to a specific version is highly recommended) or
execute `pip`:

```bash
pip install cxone-async-api
```

## Quick Start

There are several options to quickly get started.

### AI Skill Assistance

The quickest way to start is to use your AI code assistant to generate code or explain how the API works.
The release artifacts in the Github repository includes a downloadable AI skill that can be used by your AI
code assistant.  A sample program is as easy as this prompt:

```text
/cxone-async-api I need a program to <insert request here>.
```

Review and refine the produced code to your needs.

### Tutorial

The Github repository has a [Jupyter notebook](https://jupyter.org/) tutorial with code snippets and examples of a few typical
things you may want to do with the API.

### Documentation

The Github repository release artifacts includes a PDF of the API documentation.  The API docstrings will also appear for inline help on most IDEs.  

## Change Log

The release page in the Github repository documents changes for each release.
