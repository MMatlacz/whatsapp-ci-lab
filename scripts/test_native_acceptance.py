"""Offline black-box tests of the actual acceptance runner; no Apple tools needed."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('run-native-acceptance.sh').resolve()
SUCCESS = 'NativeAcceptance: at least 19 Apple Simulator tests passed.'
MOCK = r'''#!/usr/bin/env python3
import json, os, pathlib, sys
args = sys.argv[1:]
if pathlib.Path(sys.argv[0]).name == 'xcodebuild':
    if os.environ['CASE'] != 'missing-bundle':
        pathlib.Path(args[args.index('-resultBundlePath')+1]).mkdir()
    sys.exit(int(os.environ.get('BUILD_STATUS', '0')))
if args[:2] == ['simctl', 'list']:
    print(json.dumps({'devices': {'iOS-MOCK': [{'name': 'iPhone Mock', 'udid': 'MOCK', 'state': 'Booted', 'isAvailable': True}]}}))
elif args[:2] == ['xcresulttool', 'get']:
    print(os.environ['SUMMARY'])
'''


class AcceptanceEvidenceTests(unittest.TestCase):
    def run_case(self, case='normal', summary=None, build_status=0):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (
                'native-ios/WhatsAppTranslator.xcodeproj/xcshareddata/xcschemes/NativeAcceptance.xcscheme',
                'native-ios/NativeAcceptanceTests/NativeWebKitAcceptanceTests.swift',
                'native-ios/NativeAcceptanceUITests/NativeConversationAcceptanceTests.swift',
            ):
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()  # Empty synthetic fixtures, never private source.
            binary = root / 'bin'
            binary.mkdir()
            for name in ('xcodebuild', 'xcrun'):
                path = binary / name
                path.write_text(MOCK)
                path.chmod(0o755)
            environment = dict(os.environ, PRIVATE_ROOT=str(root), RUNNER_TEMP=str(root),
                               REQUEST_ID='0' * 32, CASE=case, BUILD_STATUS=str(build_status),
                               SUMMARY=summary if isinstance(summary, str) else json.dumps(summary),
                               PATH=str(binary) + os.pathsep + os.environ['PATH'])
            return subprocess.run(['bash', str(SCRIPT)], env=environment,
                                  capture_output=True, text=True, timeout=15)

    def assert_rejected(self, **kwargs):
        result = self.run_case(**kwargs)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertNotIn(SUCCESS, result.stdout)

    def test_missing_bundle(self):
        self.assert_rejected(case='missing-bundle')

    def test_malformed_summary(self):
        self.assert_rejected(summary='{not-json')

    def test_insufficient_count(self):
        self.assert_rejected(summary={'totalTestCount': 18, 'failedTests': 0, 'skippedTests': 0})

    def test_skipped_tests(self):
        self.assert_rejected(summary={'totalTestCount': 19, 'failedTests': 0, 'skippedTests': 1})

    def test_failed_tests(self):
        self.assert_rejected(summary={'totalTestCount': 19, 'failedTests': 1, 'skippedTests': 0})

    def test_build_failure(self):
        self.assert_rejected(summary={'totalTestCount': 19, 'failedTests': 0, 'skippedTests': 0}, build_status=65)

    def test_complete_success(self):
        result = self.run_case(summary={'totalTestCount': 19, 'failedTests': 0, 'skippedTests': 0})
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(SUCCESS, result.stdout)


if __name__ == '__main__':
    unittest.main()
