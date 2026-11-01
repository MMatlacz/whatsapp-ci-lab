"""Run reviewed private operations without publishing their process output."""
import base64
import os
from pathlib import Path
import re
import signal
import subprocess
import sys


class Cancelled(Exception):
    pass


def cancel(signum, frame):
    raise Cancelled()


def run(command, environment, cwd=None):
    # No logs, artifacts, annotations or summaries from private child processes.
    environment = dict(environment)
    for name in ('GITHUB_ENV', 'GITHUB_OUTPUT', 'GITHUB_STEP_SUMMARY', 'GITHUB_STATE', 'GITHUB_PATH'):
        environment.pop(name, None)
    process = None
    try:
        with open(os.devnull, 'wb') as sink:
            process = subprocess.Popen(command, cwd=cwd, env=environment,
                                       stdout=sink, stderr=sink, start_new_session=True)
            return process.wait()
    finally:
        if process is not None:
            # Kill descendants too, including ones left behind by a failed tool.
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def checkout(canonical=False):
    request = os.environ.get('REQUEST_ID', '')
    token = os.environ.get('SOURCE_TOKEN', '')
    if not re.fullmatch('[a-f0-9]{32}', request) or not token:
        return 2
    root = Path(os.environ['GITHUB_WORKSPACE']) / 'private-src'
    root.mkdir(mode=0o700)  # Refuse a stale checkout; never reuse private evidence.
    environment = dict(os.environ)
    environment.pop('SOURCE_TOKEN', None)
    environment['GIT_TERMINAL_PROMPT'] = '0'
    ref = 'refs/heads/apple' if canonical else 'refs/tags/ci-pr-' + request
    for command in (['git', 'init', str(root)],
                    ['git', '-C', str(root), 'remote', 'add', 'origin',
                     'https://github.com/MMatlacz/Whatsapp.git']):
        if run(command, environment):
            return 1
    # Auth only in this fetch process environment: no credential in argv/config.
    auth = dict(environment, GIT_CONFIG_COUNT='1',
                GIT_CONFIG_KEY_0='http.https://github.com/.extraheader',
                GIT_CONFIG_VALUE_0='AUTHORIZATION: basic ' + base64.b64encode(
                    ('x-access-token:' + token).encode()).decode())
    if run(['git', '-C', str(root), 'fetch', '--no-tags', '--depth=1', 'origin',
            ref + ':' + ref], auth):
        return 1
    return run(['git', '-C', str(root), 'checkout', '--detach', ref], environment)


def main():
    signal.signal(signal.SIGTERM, cancel)
    signal.signal(signal.SIGINT, cancel)
    try:
        if sys.argv[1:] in (['checkout'], ['checkout-canonical']):
            status = checkout(canonical=sys.argv[1] == 'checkout-canonical')
        elif len(sys.argv) > 2 and sys.argv[1] == 'run':
            status = run(sys.argv[2:], os.environ)
        else:
            status = 2
    except Cancelled:
        status = 130
    except Exception:
        # Never print exceptions: they can include private paths or command output.
        status = 1
    if status:
        print('Private operation failed; diagnostics withheld.', file=sys.stderr)
        return status if 0 < status < 256 else 1
    print('Private operation completed successfully; diagnostics withheld.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
