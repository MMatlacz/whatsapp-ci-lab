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

## Nimbus correlation dispatch (synthetic only)

The public CI may be invoked with GitHub `workflow_dispatch` and inputs
`request_id=lab-<32 random lowercase hexadecimal chars>` and
`suite=synthetic-xcode27-v1`. GitHub Actions displays **only** this opaque
identifier in the run name; the private originating repository, commit and PR
must never appear in the public event payload, logs or artifacts. The local
Nimbus control-plane dispatcher retains the private mapping; the public lab
runs **only its own synthetic code**. The `request_id` and suite are validated
on both Linux and macOS jobs, and different requests do not cancel each other.

A successful public run is *advisory evidence of a synthetic Apple toolchain
probe*, **not** a private app build, Apple release acceptance or a substitute
for required private CI. The lab does not accept private source or auth tokens.
