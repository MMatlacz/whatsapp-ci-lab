#!/usr/bin/env bash
set -euo pipefail
# Only a random opaque marker is permitted: no private SHA, PR, branch or repo.
if [[ ! "${LAB_REQUEST_ID:-}" =~ ^lab-[0-9a-f]{32}$ ]]; then
  echo 'Invalid synthetic lab request identifier.' >&2
  exit 2
fi
if [[ "${LAB_SUITE:-}" != 'synthetic-xcode27-v1' ]]; then
  echo 'Unsupported public synthetic suite.' >&2
  exit 2
fi
echo 'PUBLIC_OPAQUE_DISPATCH_INPUTS=PASS'
