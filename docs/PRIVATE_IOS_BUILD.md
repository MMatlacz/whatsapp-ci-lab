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
