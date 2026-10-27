# Synthetic Swift & Xcode CI Lab

This public repository is a **standalone CI experiment**. It measures whether
GitHub-hosted Apple Silicon runners with Xcode 27 can build and test a tiny,
fully synthetic Swift package.

The project contains **no private app source**, no dependencies on private
repositories, no WhatsApp authentication/session data, no signing identities,
and no production CI credentials. The algorithms and tests here were written
specifically for this lab. The name is historical shorthand for the CI
investigation; this repository is not affiliated with WhatsApp or Meta.

## What the workflow verifies

- Public standard ARM64 Ubuntu runners execute a Swift package test suite.
- Public standard `xcode-27` runners report their Xcode/iOS Simulator SDK
  versions, execute the same suite, and build its library for the iOS Simulator.
- The test environment is GitHub-hosted and operates without code-signing or
  private secrets.

GitHub documents that standard GitHub-hosted runners are free for public
repositories. This lab tests **actual scheduler behavior** on this GitHub
account rather than treating that documentation as proof of availability.

See [the Actions workflow](.github/workflows/xcode27-public.yml).

## Limitations

Passing this lab does **not** compile, test, or clear the release gates for any
private iOS application. GitHub bills reusable workflows according to the
calling repository, so pointing a private app at this public workflow does not
make that app's GitHub-hosted jobs free.

## Local test

```bash
bash scripts/verify-public-boundary.sh
swift test
```

## Licensing

The original synthetic code in this repository is MIT-licensed.

## Correlated synthetic dispatches

A trusted external controller can send a `workflow_dispatch` to `main` with
`request_id` (exactly 32 lowercase hexadecimal characters, generated randomly)
and `scenario=pass`. The public Actions run name displays only that opaque ID.
The optional `fail-canary` scenario intentionally fails a **synthetic** job
without downloading or testing private source. Ordinary pushes still run both
synthetic Linux and Xcode 27 jobs.

The public workflow neither receives nor stores private repository identifiers,
commit hashes, PR numbers, credentials, product code or build artifacts.
Dispatch acceptance alone does not establish a passing run. A separate trusted
controller must match the run ID and inspect the actual job conclusions.
