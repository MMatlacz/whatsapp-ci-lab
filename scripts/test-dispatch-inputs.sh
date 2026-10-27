#!/usr/bin/env bash
set -euo pipefail
ok_id='lab-000102030405060708090a0b0c0d0e0f'
LAB_REQUEST_ID="$ok_id" LAB_SUITE=synthetic-xcode27-v1 bash scripts/validate-dispatch-inputs.sh >/dev/null
for candidate in '' 'abc' 'lab-ABCDEF0123456789abcdef0123456789' \
                 'lab-000102030405060708090a0b0c0d0e0f-extra' \
                 'MMatlacz/Whatsapp' '0123456789abcdef0123456789abcdef01234567'; do
  if LAB_REQUEST_ID="$candidate" LAB_SUITE=synthetic-xcode27-v1 bash scripts/validate-dispatch-inputs.sh >/dev/null 2>&1; then
    echo 'Rejected identifier unexpectedly accepted.' >&2; exit 1
  fi
done
if LAB_REQUEST_ID="$ok_id" LAB_SUITE=whatsapp-private-app bash scripts/validate-dispatch-inputs.sh >/dev/null 2>&1; then
  echo 'Unapproved test suite accepted.' >&2; exit 1
fi
if LAB_REQUEST_ID="$ok_id" LAB_SUITE='' bash scripts/validate-dispatch-inputs.sh >/dev/null 2>&1; then
  echo 'Missing suite accepted.' >&2; exit 1
fi
echo 'PUBLIC_DISPATCH_INPUT_VALIDATION_TESTS=PASS'
