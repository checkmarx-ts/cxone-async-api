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
* Low-level API elements will require referencing the Checkmarx One API documentation.
* Some low-level API elements reference undocumented APIs that will not be found in
  the Checkmarx One API documentation.  Undocumented APIs are typically used by
  high-level API elements.  Help with undocumented API elements will require an
  engagement with Checkmarx Professional Services.
