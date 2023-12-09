# OES Registration

Self hosted software for managing event registration.

This repository includes the following software components:

- [server](server) - The HTTP API server
- [js](js) - The web interface
- [docker-compose](docker-compose) - An example Docker Compose configuration to
  run the service

## To-Do Items

### General

- [ ] Update Dockerfiles
- [ ] Update GitHub Actions
- [ ] Update Docker Compose example
- [ ] Write documentation

### Web UI

- [ ] Refactor API usage to use hooks for each feature instead of ad-hoc
      `useQuery` calls.
- [ ] Change the Wretch middleware to no longer wait for the user to complete
      auth before sending requests. This does not play well with React Router and
      suspense.
- [ ] Make React Query and React Router use suspense.
- [ ] Review and redesign the sign-in process.
- [ ] Refactor the sign-in dialog to be its own specific route instead of a
      modal. This does not play well with React Router and suspense.
- [ ] Clean up styles and add more class names/`useProps` hooks to components
      for customization.
- [ ] Create mock APIs for demos/testing.
- [ ] Investigate testing with Cypress.
- [ ] Investigate module federation to allow extending the web UI with other
      features.

### Server

- [ ] Re-structure package to move all modules into related sub-packages.
- [ ] Refactor code to use the ORM entity objects where possible instead of
      converting to/from structs.
- [ ] Rename `Model` objects to a different naming convention.
- [ ] Refactor "services" to only handle data storage/access, and move business
      logic into specific functions.
- [ ] Investigate how scopes are being used for first-party auth.
- [ ] Investigate replacing `oauthlib`.
- [ ] Re-design the account/session system, possibly moving auth logic into its
      own service.
- [ ] Move common code into the `util` library.
- [ ] Investigate how to handle DB schema/migrations if moving functionality
      into individual services.

### Interview Service

- [ ] Support more field types/validation.
- [ ] Support field defaults and options as expressions.
- [ ] Investigate how to better handle authorization between internal services.
- [ ] Investigate how to support parametrized questions/steps and declarative
      loops.

### Misc

- [ ] Add a library for badge design.
- [ ] Define an API for printing.
