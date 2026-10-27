#!/usr/bin/env bash
set -euo pipefail

# This lab intentionally contains only a fixed allowlist of original,
# synthetic files. Changing the allowed surface requires an explicit review.
allowed=(
  .github/workflows/xcode27-public.yml
  .gitignore
  LICENSE
  Package.swift
  README.md
  Sources/LabCore/DeterministicSample.swift
  Tests/LabCoreTests/DeterministicSampleTests.swift
  docs/SECURITY_BOUNDARY.md
  scripts/verify-public-boundary.sh
)
# GitHub macOS images still have /bin/bash 3.2, which lacks mapfile.
# Process substitution and diff work in both Bash 3.2 and current Linux Bash.
if ! diff -u <(printf '%s\n' "${allowed[@]}" | LC_ALL=C sort) \
              <(git ls-files | LC_ALL=C sort) >/dev/null; then
    echo 'PUBLIC-BOUNDARY-FAIL: tracked files differ from the synthetic allowlist.' >&2
    exit 1
fi

if git ls-files | grep -Eqi '(\.env|\.p12|\.mobileprovision|\.pem|\.key|\.sqlite|\.db|/\.pi/|credentials|secrets|session[-_]data)'; then
    echo 'PUBLIC-BOUNDARY-FAIL: sensitive filename pattern detected.' >&2
    exit 1
fi
# Check without printing matching lines, in case future edits accidentally
# contain private content. No production repository or user data is copied.
if git grep -IqlE 'LinguaWA|com\.mmat(lacz|lacz)|sk-proj-|whatsapp-translator/|native-ios/WhatsAppTranslator/' -- . ':!scripts/verify-public-boundary.sh'; then
    echo 'PUBLIC-BOUNDARY-FAIL: private application identifiers found.' >&2
    exit 1
fi
echo 'PUBLIC-BOUNDARY-PASS: only synthetic files tracked.'
