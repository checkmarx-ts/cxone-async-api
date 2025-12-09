# CheckmarxOne Async Python API SDK

This is a Python library that implements methods that support asynchronous access of the [CheckmarxOne REST API](https://checkmarx.stoplight.io/docs/checkmarx-one-api-reference-guide/).  At the lowest level, it is a simple wrapper for [Python Requests](https://pypi.org/project/requests/).  This API
is used by other applications maintained by Checkmarx Professional Services.

The library is organized into two parts:

* A low-level API that is a very thin layer that helps with invocation of API endpoints via Requests.
* A high-level API that has several composite workflows that hide the details of multiple low-level API invocations to perform common tasks.

This requires Python 3.9 or greater.

## Quickstart

### Installation

The install is typically performed by using a direct URL with an optional associated hash for verification.  The `releases` section of this repo
has the required copy/paste lines with required hashes.

### Tutorial

A [tutorial](tutorial/cxone-async-api-tutorial.ipynb) implemented as a Jupyter notebook is the best way to learn and experiment with this API SDK.
The notebook will render in a web browser for those that wish to view code
samples without running the notebook interactively.  

The tutorial has several code examples that can be executed in a [Jupyter notebook](https://jupyter.org/).  This allows you to step through the examples and experiment with the tutorial code.  Spending 10 minutes to complete the first several tutorials will likely make learning how to use the API much faster.

Opening the Jupyter notebook's `.ipynb` file with VSCode is usually the best way to utilize the tutorial.  You'll need to configure the
appropriate Python and Jupyter plugins for VSCode.

It is also possible to open an executable instance of the tutorial notebook in a web browser by locally hosting an instance of a
Jupyter server.  Below is an example command line that will start a docker container running
the notebook server with the tutorial notebook mapped to the running container.

```bash

TOKEN=$(date | md5sum -z | head -c 32) docker run --rm -p 8888:8888 \
-e JUPYTER_TOKEN=$TOKEN -e JUPYTER_ENABLE_LAB=yes -d \
-v $(pwd)/tutorial:/home/jovyan/work jupyter/datascience-notebook && \
echo "Open the tutorial here: http://localhost:8888/lab?token=$TOKEN"

```

### Documentation

The `releases` section has a PDF of the API documentation.  The API docstrings will also appear for inline help on most IDEs.  
