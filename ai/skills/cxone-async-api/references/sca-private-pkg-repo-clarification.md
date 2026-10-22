# SCA Private Package Repository Configuration Clarification

## Checkmarx One Server-Side Behavior

* The Checkmarx One API does not enforce unique names for private package repository
  configurations or configuration tags.  More than one configuration or tag may have
  the same name.
* Checkmarx One allows more than one configuration with the same package manager type
  to be assigned to a project or associated with a tag.
* Checkmarx One does not combine multiple configurations of the same package manager type.
  If a project has more than one configuration of the same package manager type assigned,
  SCA uses only one of them, chosen arbitrarily, when scanning the project.
  * Warn the user that assigning more than one configuration of the same package manager
    type to a project produces unpredictable SCA scan results.
* The low-level API methods in `cxone_api.low.sca.registry` follow the behavior of the
  Checkmarx One API.  They do not prevent duplicate names or duplicate package manager
  type assignments.

## High-Level API Assignment Behavior

* Use the high-level assignment classes in `cxone_api.high.sca.registry` to assign
  configurations to projects:
  * `ProjectPrivateRepoAssignment` assigns a single configuration.
  * `ProjectPrivateRepoTagAssignment` assigns all configurations associated with a
    configuration tag.
* The assignment classes validate assignments so that a project is never assigned more
  than one configuration for the same package manager type.
* The configurations associated with a tag may include more than one configuration of the
  same package manager type.  Assigning such a tag with `ProjectPrivateRepoTagAssignment`
  is an error: `execute_assignment` raises `DuplicatePackageManagerException` before any
  projects are assigned.
* Attempting to assign a configuration to a project that already has a configuration of
  the same package manager type assigned is an error.  The project is not assigned and the
  `DuplicatePackageManagerException` for that project is returned in the `exceptions` list
  of the `AssignmentResults` returned by `execute_assignment`.
* To correct a project's assignments, use
  `PackageRepositoryConfiguration.disassociate_from_project` to remove the unwanted
  configuration from the project, then assign the correct configuration.
* The validation is only performed by the high-level assignment classes.  Low-level API
  calls made after the high-level API has assigned configurations to a project can still
  assign duplicate package manager types to the project.  Warn the user when producing
  code that mixes low-level assignment calls with the high-level assignment classes.
