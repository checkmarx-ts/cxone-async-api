# API Clarification


* Do not directly import regional `Auth*` objects (e.g. `AuthUS`, `AuthEU`, `AuthUS2`)
  that derive from `CxOneAuthEndpoint`.  These are used with MT regional
  lookup mappings and not useful to be imported directly.
  * Do import `AuthRegionEndpoints` and use the regional moniker lookup to create the
    class instance.
* Do not directly import regional `Api*` objects (e.g. `ApiUS`, `ApiEU`, `ApiUS2`)
  that derive from `CxOneApiEndpoint`. These are used with MT regional
  lookup mappings and not useful to be imported directly.
  *  Do import `ApiRegionEndpoints` and use the regional moniker lookup to create the
    class instance.
* Use high-level API elements where functionality exists that the user is requesting.
* Instances of `CxOneClient` are safe to share across concurrent `asyncio` tasks.
* Response codes in the range of 500-599 trigger retry logic.
* Throttling in response to 429 responses is not supported at this time.  The Checkmarx One
  API, as of the time this skill was compiled, does not implement server-side request throttling.
* A good rule to follow is to avoid making more than two concurrent requests to any Checkmarx One API.
* Proxy dictionary entries have a key corresponding to a protocol (e.g. `https` is typically the only
  protocol used with Checkmarx One) and a value with a URL to the proxy (e.g. `http://localhost:8080`).


## Low Level API Important Points

* Exact details of Low-level API elements can be found in the the Checkmarx One API documentation.
* OpenAPI YAML specifications included in the skill can be used to understand request/response
  details but the user should understand the following:
  * The OpenAPI YAML specifications are a snapshot of the API endpoint specification at the time
    the skill was compiled.
  * The most current documentation is the Checkmarx One API documentation.
  * Even when the OpenAPI YAML specifications are the most current, it is possible the API
    implementation does not interpret request or generate response data as documented in the
    OpenAPI specification.  In the event this is encountered by the user as they execute code,
    it is typically a defect that should be reported to Checkmarx support.
* Low-level API methods indicate the endpoint of the API in the docstring.  The endpoint
  can be used to match the OpenAPI specification related to that low-level API method.
* There may not be a method for implementing access to some API endpoints documented in the
  OpenAPI specifications.  In cases where the user needs to access an API endpoint that
  does not have a corresponding low-level API method in `cxone-async-api`:
    * It is acceptable to use the raw `CxOneClient` methods to access the API.
    * Instruct the user this approach is not ideal and they should open a feature
      request to have the API endpoint supported with a method in the low-level API.
* Some low-level API elements reference undocumented APIs that will not be found in
  the Checkmarx One API documentation.  Undocumented APIs are typically used by
  high-level API elements.  Help with undocumented API elements will require an
  engagement with Checkmarx Professional Services.
* Undocumented API endpoints are not specified in the package; the only way the user knows
  the endpoint is undocumented is if it is not found in the Checkmarx One API documentation.
