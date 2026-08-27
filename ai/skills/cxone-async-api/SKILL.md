---
name: cxone-async-api
description: Documentation and help for cxone-async-api package.
---

This is a Python module that is used to access the Checkmarx One API
using Python asynchronous programming.

Reference `references/README.md` for general information about the cxone-async-api.
Also found here is a reference to the Checkmarx One API documentation that
is a companion to the cxone-async-api documentation.

Reference `references/readme-clarification.md` for clarifications about information
found in `references/README.md` that may be presented to the user.


Reference `references/install.md` to understand:
* The version number of the current release that generated this skill.
* The `pip` installation instructions.
* The location of the artifacts that should be used when instructing the user to obtain
  artifacts.

# Use Case: Guide implementation with code examples

* Reference `references/package-clarification.md` for information about communicating clearly
  with a human about `cxone-async-api`.
* Reference `references/api-clarification.md` for clarification on API elements used
  when producing code for a user.
* Reference `references/cxone-async-api-docs.md` for the API documentation.
* Reference `references/region-monikers.md` for a list of multi-tenant regional monikers.
* Reference `references/**/conf.py` for information about how Sphinx is configured to build
  a PDF version of the `references/cxone-async-api-docs.md`.  The Sphinx configuration emits
  data in the PDF that is not available in the markdown version but would apply to elements
  in the markdown version to help with AI understanding of the API.
* Reference `references/cxone-async-api-tutorial.ipynb` for a selection of guided
  examples put together for an interactive tutorial.
    * Note the authentication examples are the important first step.
    * The tutorial notebook is for AI consumption to see examples of usage of the API.
      Portions of the notebook that would not translate to a usable example can be ignored
      when creating usable examples.
    * Reference `references/auth-clarifications.md` for important details about
      authentication with Checkmarx One.


# Output

* Before outputting any example code, ensure that it is in the form
  of a single executable Python example file.
* Ensure that the use of sensitive variables, such as those mentioned
  in `references/auth-clarifications.md`, are obtained from environment variables
  in emitted examples.  Instruct the user how to set the environment variables
  before they execute the example code.
