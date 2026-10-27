# Public CI lab security boundary

This repository is deliberately disconnected from any private product code.

Only the synthetic Swift package, tests, this documentation and the single
GitHub-hosted Actions workflow are permitted. The file allowlist is enforced
by `scripts/verify-public-boundary.sh` before every test job.

No private repository is mirrored, cloned, imported as an SPM dependency,
checked out in the workflow or mounted into the runner. No API keys, personal
WhatsApp data, session snapshots, profiles, certificates or signing identities
belong here. No self-hosted runner is used.

Workflow permissions are `contents: read`. It runs on `main` pushes or
manual dispatch and does not create pull requests or publish artifacts.

The Xcode 27 runner's success establishes only that GitHub can build the
small **public, synthetic** project. It does not establish private-app
compilation or production readiness.
