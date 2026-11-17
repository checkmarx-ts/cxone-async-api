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
* It is preferred to instruct the user to install `cxone-async-api` from PyPi for released
  versions (i.e. versions **without** `rc` in them).  This is done using the version specifier
  in `references/install.md` as the pinned version. For example, adding `cxone-async-api==VERSION` to `requirements.txt`.
* The `pip` installation instructions used to install directly from the github repository.
* For pre-releases, requirements.txt should always install from the github repository. Add the
  wheel URL from `references/install.md` to `requirements.txt`, without the `pip install` prefix.
* The location of the artifacts that should be used when instructing the user to obtain
  artifacts from the github repository.

# Use Case: Guide implementation with code examples

* Reference `references/cxone-async-api-docs.md` for the API documentation.
  * For companion information for reference `references/cxone-async-api-docs.md`, reference
    `references/*.yaml` for the OpenAPI references useful for understanding input and output
    request, response, url, and query inputs to the API endpoint.
* Reference `references/api-clarification.md` for clarification on API elements used
  when producing code for a user.
* Reference `references/package-clarification.md` for information about communicating clearly
  with a human about `cxone-async-api`.
* Reference `references/region-monikers.md` for a list of multi-tenant regional monikers.
* Reference `references/sca-private-pkg-repo-clarification.md` for clarification on
  SCA private package repository configurations, configuration tags, and assigning
  configurations to projects.
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


# Use Case: Single executable example (default)

* Unless the user asks for a full project, output example code as a single executable
  Python file.
* Tell the user which packages to install to run the example: `cxone-async-api`, following
  the `references/install.md` instructions above, and any other packages the example imports.
* After the example, tell the user they can ask for the example as a full project.  Explain
  that the full project adds a `requirements.txt`, loads secrets from a `.env` file using
  `python-dotenv`, and includes this skill in the project so Claude can reference it in
  their IDE.


# Use Case: Build a full project

Use this use case only when the user asks for a full project.

* Create the project with this layout:
  ```
  <project>/
  ├── .claude/
  │   └── skills/
  │       └── cxone-async-api/   # this skill
  ├── .gitignore
  ├── requirements.txt
  └── <example>.py
  ```
* `requirements.txt` must contain:
  * The `cxone-async-api` entry, following the `references/install.md` instructions above.
  * `python-dotenv`.
  * Any other packages the example imports.
* Load secrets with `python-dotenv`:
  * Call `load_dotenv()` before reading any environment variables.  Variables already set in
    the environment take precedence over values in the `.env` file.
  * Instruct the user to create a `.env` file in the project root containing the variables
    the example reads, and never to commit it.
* `.gitignore` must exclude `.env` files using the patterns `.env` and `.env.*`.  Also exclude
  `.venv/` and `__pycache__/`.
* Include this skill at `.claude/skills/cxone-async-api/` so Claude in the user's IDE can
  reference it:
  * If you can write files, copy this skill's directory, including `SKILL.md` and
    `references/`, into `.claude/skills/cxone-async-api/` unchanged.
  * Otherwise, instruct the user to download `cxone-async-api-skill.zip` from the GitHub
    release matching the version in `references/install.md`
    (`<Github Repository>/releases/download/<Version>/cxone-async-api-skill.zip`, using the
    values in `references/install.md`) and extract it into `.claude/skills/cxone-async-api/`.
    `SKILL.md` is at the root of the zip.
  * The skill version must match the `cxone-async-api` version in `requirements.txt`.
* Instruct the user how to set up and run the project: create a virtual environment, run
  `pip install -r requirements.txt`, create the `.env` file, and run the example.


# Output

* Before outputting any example code, ensure that it follows the single executable example
  use case, or the full project use case if the user asked for a full project.
* Ensure that the use of sensitive variables, such as those mentioned
  in `references/auth-clarifications.md`, are obtained from environment variables
  in emitted examples.  Instruct the user how to set the environment variables
  before they execute the example code.  In a full project, the environment variables
  are loaded from the `.env` file.
* At the start of code comments documenting the code, include the URL for the
  Checkmarx One API documentation and instruct the user it is the most
  accurate usage reference for low-level APIs.
