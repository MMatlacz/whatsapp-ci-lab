# Draft full private iOS Xcode 27 build in public CI companion

The public CI repository is associated with the private WhatsApp software project.
This workflow transparently attempts the actual private app and diagnostic target
builds on GitHub-hosted Xcode 27; it does not upload private sources as artifacts.
GitHub Actions terms restrict unrelated public runner use and permit usage monitoring.

The current private GitHub App lacks Contents: read. An owner must approve that
permission on its installed App (or create a dedicated Contents: read-only App),
then configure two public repository Actions secrets:
WHATSAPP_SOURCE_APP_ID and WHATSAPP_SOURCE_APP_KEY.

Never put PEMs or installation tokens in dispatch inputs, workflow files, PR
comments, or logs. The minted token is scoped to only the private Whatsapp
repository and Contents: read, and revoked when the job ends.

Initial canary builds canonical apple, not a specific PR commit, so it does not
replace per-PR required build-apple or the separate required Secret checks.
Inputs contain only an opaque request ID. The code is checked out transiently
in the hosted runner but the public job logs may reveal private compiler
diagnostics despite quiet output. Public Actions is not strictly private.
No user session or model weight should be provided to this workflow.

This PR does not grant access or activate the source-App secret. Complete an
explicit security review of this exposure before the first live dispatch.


## Exact-commit private pull-request validation

The companion workflow private-pr-ios-build.yml builds a private PR at an
**opaque, request-scoped Git tag**, not at whichever commit apple happens to
point to when the macOS runner starts.

A trusted Nimbus host controller must first check that an owner-authored
same-repository private PR currently targets apple, confirm all four mandatory
Secret checks are green on that exact head SHA, mint a random 32-character
request ID, create an **in the private repository only** lightweight ref
refs/tags/ci-pr-<request-id> pointing at that exact head commit, record the
request/private SHA/security run in a restricted local ledger, and dispatch
the public workflow using only the opaque ID and test_suite choice.

The public GitHub-hosted Xcode runner uses the existing private contents-read
App to check out that tag. It verifies the locally fetched tag resolves to the
checked-out HEAD, builds the real app and diagnostic targets, and optionally
runs the NativeAcceptance scheme against an ephemeral iOS Simulator. On
test_suite=native-acceptance, require at least 19 tests with no failures/skips.
The runner never receives the private PR number or expected SHA as input.

**The trusted controller, not the public workflow, must validate the result**:
check the exact public workflow identity and public main SHA, unique request
ID, Xcode job and required step conclusions, private tag SHA unchanged,
original private PR head SHA unchanged, and original mandatory Secret checks.
A stale or cancelled run is not a pass. Only the private-side reporter can
post verified evidence to a private PR. No successful Xcode status is invented.

Public Actions logs are readable by visitors and may reveal private compiler
diagnostics or checkout SHAs even when inputs are opaque. Do not upload
xcresult screenshots, app builds, source, models, signing identities, or chats.
No physical device or production WhatsApp Web session is involved.
Private build-apple and other existing CI checks are unchanged.
