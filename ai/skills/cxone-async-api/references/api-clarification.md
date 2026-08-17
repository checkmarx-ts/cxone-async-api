# API Clarification


* Ignore regional `Auth*` objects (e.g. `AuthUS`, `AuthEU`, `AuthUS2`)
  that derive from `CxOneAuthEndpoint`.  These are used with MT regional
  lookup mappings and not useful to be imported directly.
* Ignore regional `Api*` objects (e.g. `ApiUS`, `ApiEU`, `ApiUS2`)
  that derive from `CxOneAuthEndpoint`. These are used with MT regional
  lookup mappings and not useful to be imported directly.
