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
in the hosted runner; private process output is suppressed by the wrapper below.
Public Actions is not a private execution environment.
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

Public Actions logs are readable by visitors. The exact-PR workflow now suppresses
private child diagnostics and checkout output as described below. Do not upload
xcresult screenshots, app builds, source, models, signing identities, or chats.
No physical device or production WhatsApp Web session is involved.
Private build-apple and other existing CI checks are unchanged.

## Connected Apple-only execution migration (staged)

The exact-ref workflow retains a staged `test_suite=qwen-functional` definition,
but request validation deliberately rejects it before checkout. A future separately
reviewed activation would execute the private functional runner; no application source,
model, report or diagnostic log is committed/uploaded to this public repository.
The runner must retain its pinned artifact checks and distinguish iOS Simulator
results from native macOS fallback. The public job requests unconditional cleanup of its transient
private checkout; forced host loss relies on ephemeral runner disposal. A synthetic harness CI pass is not an inference result.

Private read-only evidence checks can independently verify the request tag, exact
source head, security results, public workflow/script blob identities and actual
suite step conclusions. They do not accept a comment or synthetic result as an
Apple pass. Activation still requires separately reviewed private integration and
merged public main dependencies; a draft branch is not used by the dispatcher.
GitHub's associated-project usage restrictions and runner/billing limits continue
to apply. No larger runner, new credential grant, quota exception or model
redistribution is introduced.

## Private process output boundary

The exact-PR and legacy canonical workflows run private checkout, compilation and
optional suites through `scripts/private_execution.py`; exact-PR ref verification
uses that same boundary. Child stdout and stderr
are discarded, not uploaded or printed on failure. The wrapper emits only fixed
success/failure messages and preserves nonzero exits. Private child processes do
not receive runner summary/output file channels. Checkout credentials exist only
in the fetch process environment, never command arguments or persisted Git config.
Cancellation terminates the child process group; the workflow's `always()` cleanup
removes the transient checkout and known build/result directories. A forcibly lost
host cannot run cleanup; it relies on disposal of the ephemeral hosted runner.

No public artifact, cache, source excerpt, private commit subject or checkout SHA
is intentionally published. Tests inject synthetic diagnostic markers into both
output streams, including failure paths. Compilation is still not native acceptance:
only the native suite's fail-closed result guard establishes its >=19 tests.
A change to this wrapper must update the private reviewed harness manifest before
any new exact-head evidence can be accepted. Qwen remains disabled and is not run by these offline tests.

`qwen-functional` is deliberately rejected during request validation, before token
minting or checkout. This is a failed request, never a skipped/successful model run.
Re-enabling it requires separate review of private runner cancellation, scope and
new exact-head evidence. The current fix does not run or enable a model.
