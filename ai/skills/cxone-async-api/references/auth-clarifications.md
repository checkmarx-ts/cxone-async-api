# Checkmarx One Authentication Clarifications

## General

* API Keys, OAuth Client IDs, and OAuth Secrets should be considered sensitive data and
  never embedded in code.
* The Checkmarx One tenant id can be considered a secret but is overall not sensitive
  data.
* A Checkmarx One instance can be a single-tenant (ST) or multi-tenant (MT) instance.
* For both ST and MT, the API host and IAM host are identified by the FQDN of the
  name of the host.  A protocol prefix (e.g. https://) is not required as the default
  protocol prefix is `https://`
* Multi-tenant regional monikers can be used with the lookup maps `cxone_api.AuthRegionEndpoints`
  and `cxone_api.ApiRegionEndpoints` to obtain instances of corresponding API objects initialized
  with the proper FQDN for the MT region.  Example: `cxone_api.AuthRegionEndpoints["US"]` corresponds
  to the FQDN of the IAM server for the Checkmarx One multi-tenant region `US`.
* A tenant ID is required for single-tenant instances despite the instance only hosting
  one tenant.


## API Key Authentication

When a user is utilizing authentication with an API key, the user should be warned
that the API key is best for the following scenarios:

* Interactive access by a single user given the API key is a credential
  for the owning user account.
* Checkmarx One permissions for the API key are limited to the same
  permissions as the user account.
* The user's permissions to view data may be limited due to the scope
  of the owning user's access.

## OAuth Authentication

* The OAuth authentication requires a client ID and a client secret.
* OAuth authentication is best for machine-to-machine, non-interactive
  authentication.
* The OAuth client is not tied to a single user; it can be considered
  a user with it's own assigned permissions.
