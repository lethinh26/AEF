# Local infrastructure

`compose.yaml` starts the local PostgreSQL canonical state store and [PGSTY Silo](https://github.com/pgsty/silo), an actively maintained S3-compatible object store. Both publish ports on loopback only. The `object-store-init` one-shot service creates the private `aeo-artifacts` bucket.

PostgreSQL is published on `127.0.0.1:55432` by default to avoid colliding with other local projects. Silo exposes the S3 API at `http://127.0.0.1:9000` and its console at `http://127.0.0.1:9001`. The API and worker run as local Python processes during development so they can be debugged independently. Use the root README for startup commands.
