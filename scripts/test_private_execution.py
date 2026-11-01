"""Synthetic-only confidentiality and exit-status regression tests."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

SCRIPT = Path(__file__).with_name('private_execution.py').resolve()
MARKER = 'SYNTHETIC_PRIVATE_SOURCE_AND_SECRET_MARKER'


class PrivateExecutionTests(unittest.TestCase):
    def call(self, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args],
                              capture_output=True, text=True, env=env, timeout=10)

    def test_stdout_stderr_source_and_workflow_commands_suppressed(self):
        for status in (0, 42):
            with self.subTest(status=status):
                code = ('import sys; print(' + repr(MARKER) + '); '
                        'print("::error::"+' + repr(MARKER) + ',file=sys.stderr); '
                        'sys.exit(' + str(status) + ')')
                result = self.call('run', sys.executable, '-c', code)
                self.assertEqual(result.returncode, status)
                self.assertNotIn(MARKER, result.stdout + result.stderr)
                self.assertNotIn('::error::', result.stdout + result.stderr)
                self.assertEqual('successfully' in result.stdout, status == 0)

    def test_shell_failure_not_hidden_by_later_success(self):
        result = self.call('run', 'bash', '-euo', 'pipefail', '-c', 'false; echo success')
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('success', result.stdout)

    def test_command_not_found_is_generic(self):
        result = self.call('run', '/missing/' + MARKER)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(MARKER, result.stdout + result.stderr)

    def test_child_cannot_write_runner_output_channels(self):
        code = ('import os; assert not any(k in os.environ for k in '
                '("GITHUB_ENV","GITHUB_OUTPUT","GITHUB_STATE","GITHUB_STEP_SUMMARY","GITHUB_PATH"))')
        env = dict(os.environ, **{k: MARKER for k in
                   ('GITHUB_ENV', 'GITHUB_OUTPUT', 'GITHUB_STATE', 'GITHUB_STEP_SUMMARY', 'GITHUB_PATH')})
        self.assertEqual(self.call('run', sys.executable, '-c', code, env=env).returncode, 0)

    def test_cancel_fails_and_reaps_child(self):
        with tempfile.TemporaryDirectory() as directory:
            ready = Path(directory) / 'ready'
            code = 'import os,pathlib,time; pathlib.Path(' + repr(str(ready)) + ').write_text(str(os.getpid())); time.sleep(60)'
            process = subprocess.Popen([sys.executable, str(SCRIPT), 'run',
                                        sys.executable, '-c', code],
                                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            try:
                deadline = time.monotonic() + 5
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertTrue(ready.exists())
                process.send_signal(signal.SIGTERM)
                out, err = process.communicate(timeout=5)
                self.assertNotEqual(process.returncode, 0)
                self.assertNotIn('successfully', out)
                with self.assertRaises(ProcessLookupError):
                    os.kill(int(ready.read_text()), 0)
            finally:
                if process.poll() is None:
                    process.kill()
                    process.wait()

    def test_checkout_captures_output_and_keeps_auth_ephemeral(self):
        for mode, failure in (('checkout', False), ('checkout', True),
                              ('checkout-canonical', False), ('checkout-canonical', True)):
            with self.subTest(mode=mode, failure=failure), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                binary = root / 'bin'
                binary.mkdir()
                calls = root / 'calls'
                git = binary / 'git'
                git.write_text('#!' + sys.executable + '\n' + '''import json,os,sys
with open(os.environ['CALLS'], 'a') as f:
    f.write(json.dumps({'args':sys.argv[1:], 'auth':'GIT_CONFIG_VALUE_0' in os.environ,
                        'token':'SOURCE_TOKEN' in os.environ})+'\\n')
print(os.environ['MARKER'])
print(os.environ['MARKER'],file=sys.stderr)
sys.exit(23 if os.environ['FAIL']=='yes' and 'fetch' in sys.argv else 0)
''')
                git.chmod(0o755)
                env = dict(os.environ, PATH=str(binary)+os.pathsep+os.environ['PATH'],
                           CALLS=str(calls), MARKER=MARKER, FAIL='yes' if failure else 'no',
                           REQUEST_ID='0'*32, SOURCE_TOKEN=MARKER, GITHUB_WORKSPACE=str(root))
                result = self.call(mode, env=env)
                self.assertEqual(result.returncode == 0, not failure)
                self.assertNotIn(MARKER, result.stdout + result.stderr)
                records = [json.loads(line) for line in calls.read_text().splitlines()]
                for record in records:
                    self.assertNotIn(MARKER, str(record))
                    self.assertFalse(record['token'])
                    self.assertEqual(record['auth'], 'fetch' in record['args'])
                fetch = next(record['args'] for record in records if 'fetch' in record['args'])
                expected = 'refs/heads/apple' if mode == 'checkout-canonical' else 'refs/tags/ci-pr-' + '0'*32
                self.assertIn(expected + ':' + expected, fetch)
                self.assertFalse((root / 'private-src/.git/config').exists())

    def test_qwen_rejected_before_credentials_or_checkout(self):
        workflow = (SCRIPT.parent.parent / '.github/workflows/private-pr-ios-build.yml').read_text()
        first = workflow.split('      - name: Validate opaque request', 1)[1].split('      - name:', 1)[0]
        body = first.split('        run: |', 1)[1]
        script = '\n'.join(line[10:] for line in body.splitlines() if line.strip())
        self.assertLess(workflow.index('Validate opaque request'), workflow.index('Mint restricted private source token'))
        self.assertLess(workflow.index('Validate opaque request'), workflow.index('Checkout actual private source'))
        for suite in ('none', 'native-acceptance', 'qwen-functional', 'unsupported'):
            result = subprocess.run(['bash', '-euo', 'pipefail', '-c', script],
                                    env=dict(os.environ, REQUEST_ID='0'*32, TEST_SUITE=suite),
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(result.returncode == 0, suite in ('none', 'native-acceptance'))

    def test_invalid_checkout_request_fails(self):
        result = self.call('checkout', env=dict(os.environ, REQUEST_ID=MARKER, SOURCE_TOKEN=MARKER))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn(MARKER, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
