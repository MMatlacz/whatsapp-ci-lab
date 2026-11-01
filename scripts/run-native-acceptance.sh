#!/usr/bin/env bash
set -euo pipefail
set +x
root="${PRIVATE_ROOT:?private source root required}"
request="${REQUEST_ID:?request ID required}"
[[ "${request}" =~ ^[a-f0-9]{32}$ ]] || { echo 'Invalid request ID'; exit 2; }
cd "${root}"
test -f native-ios/WhatsAppTranslator.xcodeproj/xcshareddata/xcschemes/NativeAcceptance.xcscheme || {
  echo 'NativeAcceptance scheme absent on this PR head'; exit 3;
}
test -f native-ios/NativeAcceptanceTests/NativeWebKitAcceptanceTests.swift || {
  echo 'Native Apple acceptance tests absent'; exit 3;
}
test -f native-ios/NativeAcceptanceUITests/NativeConversationAcceptanceTests.swift || {
  echo 'Native Apple UI acceptance tests absent'; exit 3;
}
# Select a disposable hosted iPhone simulator. No personal Mac or linked profile.
simulator_id=$(xcrun simctl list --json devices available | python3 -c '
import json,sys
j=json.load(sys.stdin)
phones=[]
for runtime,devices in j["devices"].items():
    if "iOS" not in runtime: continue
    for d in devices:
        if d.get("isAvailable",True) and d["name"].startswith("iPhone"):
            phones.append((d.get("state")=="Booted",runtime,d["udid"]))
if not phones: raise SystemExit("No available iPhone simulator")
phones.sort(reverse=True)
print(phones[0][2])
')
test -n "${simulator_id}"
booted=$(xcrun simctl list --json devices | python3 -c '
import json,sys
for devices in json.load(sys.stdin)["devices"].values():
  for d in devices:
    if d["udid"]==sys.argv[1]:
      print(d["state"])
      raise SystemExit
' "${simulator_id}")
if [[ "${booted}" != Booted ]]; then xcrun simctl boot "${simulator_id}"; fi
xcrun simctl bootstatus "${simulator_id}" -b
result="${RUNNER_TEMP}/native-acceptance-${request}.xcresult"
echo 'Executing isolated NativeAcceptance tests on ephemeral hosted iOS Simulator.'
set +e
xcodebuild -quiet test \
  -project native-ios/WhatsAppTranslator.xcodeproj \
  -scheme NativeAcceptance \
  -configuration NativeAcceptance \
  -destination "platform=iOS Simulator,id=${simulator_id}" \
  -resultBundlePath "${result}" \
  -parallel-testing-enabled NO \
  CODE_SIGNING_ALLOWED=NO
status=$?
set -e
if [[ ! -d "${result}" ]]; then
  echo 'NativeAcceptance result bundle missing; no pass claimed.' >&2
  exit 1
fi
if [[ -d "${result}" ]]; then
  xcrun xcresulttool get test-results summary --path "${result}" > "${RUNNER_TEMP}/native-acceptance-summary.json"
  python3 - "${RUNNER_TEMP}/native-acceptance-summary.json" "${status}" <<'PY'
import json,sys
summary=json.load(open(sys.argv[1]))
def counter(*names):
    values = [summary[name] for name in names if name in summary]
    if (not values or any(type(value) is not int or value < 0 for value in values)
            or len(set(values)) != 1):
        raise SystemExit("Incomplete native acceptance evidence: invalid or missing " + names[0])
    return values[0]

if not isinstance(summary, dict):
    raise SystemExit("Incomplete native acceptance evidence: expected summary object")
count=counter("totalTestCount", "testsCount")
failed=counter("failedTests", "failedTestsCount")
skipped=counter("skippedTests", "skippedTestsCount")
print(f"Native acceptance tests: total={count}, failed={failed}, skipped={skipped}")
if int(sys.argv[2]) == 0 and (count < 19 or failed or skipped):
    raise SystemExit("Incomplete native acceptance evidence; require at least 19 passed, zero skipped")
PY
fi
if [[ "${status}" -ne 0 ]]; then
  echo 'NativeAcceptance Xcode execution failed; no pass claimed.'
  exit "${status}"
fi
echo 'NativeAcceptance: at least 19 Apple Simulator tests passed.'
