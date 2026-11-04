"""Public CLI protocol controls; no Windows API invocation."""
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

ENTRY = Path(__file__).with_name("test-extract-conversations-windows-owner.py")

class OwnerFactsProtocolTests(unittest.TestCase):
    def test_unsupported_platform_is_a_closed_refusal_before_native_loading(self):
        bootstrap = "import runpy,sys;entry=sys.argv[1];sys.argv=[entry];sys.platform='unsupported-platform-control';runpy.run_path(entry,run_name='__main__')"
        result = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", bootstrap, str(ENTRY)],
                                capture_output=True, text=True, timeout=2, env={})
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, json.dumps({"scope":"windows-new-workspace-owner-facts","schema":1,
            "state":"unproven","reason":"platform"}, separators=(",", ":")) + "\n")


# Inert Win32 boundary fixtures. These compare synthetic SID classes only.
import contextlib
import ctypes
import io
import runpy
from unittest import mock

class StubCall:
    def __init__(self, callback):
        self.callback = callback
    def __call__(self, *args):
        return self.callback(*args)

class StubOwnerApis:
    def __init__(self, failure=None):
        self.failure = failure
        self.sid_classes = {}
        self.buffers = []
        self.calls = []
        self.closed = []
        self.freed = []
        self.owner = self.sid('administrators')
        self.descriptor = ctypes.create_string_buffer(64)
        self.buffers.append(self.descriptor)
        self.advapi = type('Api', (), {})()
        self.kernel = type('Api', (), {})()
        for obj, name, callback in [
            (self.kernel, 'GetCurrentProcess', lambda: -1),
            (self.kernel, 'CloseHandle', self.close),
            (self.kernel, 'LocalFree', self.free),
            (self.advapi, 'GetNamedSecurityInfoW', self.security),
            (self.advapi, 'OpenProcessToken', self.open_token),
            (self.advapi, 'GetTokenInformation', self.token_info),
            (self.advapi, 'CreateWellKnownSid', self.admin_sid),
            (self.advapi, 'IsValidSid', lambda sid: int(self.address(sid) in self.sid_classes)),
            (self.advapi, 'GetLengthSid', lambda sid: 12 if self.address(sid) in self.sid_classes else 0),
            (self.advapi, 'EqualSid', self.equal_sid),
        ]:
            setattr(obj, name, StubCall(callback))
    @staticmethod
    def address(value):
        return value.value if isinstance(value, ctypes.c_void_p) else int(value)
    def sid(self, kind):
        buffer = ctypes.create_string_buffer(68)
        self.buffers.append(buffer)
        address = ctypes.addressof(buffer)
        self.sid_classes[address] = kind
        return address
    def load(self, path, **kwargs):
        self.calls.append(('load', path, kwargs))
        if path == r'C:\Windows\System32\advapi32.dll':
            return self.advapi
        if path == r'C:\Windows\System32\kernel32.dll':
            return self.kernel
        raise AssertionError('unexpected-native-library')
    def security(self, path, kind, flags, owner, group, dacl, sacl, descriptor):
        self.calls.append(('security',))
        if kind != 1 or flags != 1:
            raise AssertionError('unexpected-security-scope')
        ctypes.cast(owner, ctypes.POINTER(ctypes.c_void_p))[0] = self.owner
        ctypes.cast(descriptor, ctypes.POINTER(ctypes.c_void_p))[0] = ctypes.addressof(self.descriptor)
        if self.failure == 'exception':
            raise RuntimeError('private-exception-canary')
        return 5 if self.failure == 'descriptor' else 0
    def open_token(self, process, access, token):
        self.calls.append(('open-token',))
        if access != 8:
            raise AssertionError('unexpected-token-access')
        if self.failure == 'open-token':
            return 0
        ctypes.cast(token, ctypes.POINTER(ctypes.c_void_p))[0] = 2020
        return 1
    def token_info(self, token, kind, buffer, capacity, returned):
        self.calls.append(('token-info', kind, buffer is None))
        needed = 4097 if self.failure == 'token-size' else 64
        ctypes.cast(returned, ctypes.POINTER(ctypes.c_uint32))[0] = needed
        if buffer is None:
            return 0
        if kind not in (1, 4) or capacity != 64:
            raise AssertionError('unexpected-token-query')
        address = ctypes.addressof(buffer) + 16
        self.sid_classes[address] = 'user' if kind == 1 else 'administrators'
        ctypes.cast(buffer, ctypes.POINTER(ctypes.c_void_p))[0] = address
        return 1
    def admin_sid(self, kind, domain, buffer, returned):
        self.calls.append(('admin-sid',))
        if kind != 26 or domain is not None:
            raise AssertionError('unexpected-well-known-sid')
        self.sid_classes[ctypes.addressof(buffer)] = 'administrators'
        ctypes.cast(returned, ctypes.POINTER(ctypes.c_uint32))[0] = 12
        return 1
    def equal_sid(self, left, right):
        return int(self.sid_classes.get(self.address(left)) == self.sid_classes.get(self.address(right)))
    def close(self, handle):
        self.closed.append(self.address(handle))
        return 0 if self.failure == 'close' else 1
    def free(self, descriptor):
        self.freed.append(self.address(descriptor))
        return None

def invoke_stubbed_owner(entry, failure=None, arguments=()):
    api = StubOwnerApis(failure)
    stdout, stderr = io.StringIO(), io.StringIO()
    with mock.patch.object(sys, 'platform', 'win32'), \
         mock.patch.object(sys, 'argv', [str(entry), *arguments]), \
         mock.patch.object(ctypes, 'WinDLL', api.load, create=True), \
         mock.patch.object(ctypes, 'get_last_error', lambda: 122, create=True), \
         contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        try:
            runpy.run_path(str(entry), run_name='__main__')
        except SystemExit as result:
            code = result.code
        else:
            code = 0
    return code, stdout.getvalue(), stderr.getvalue(), api

def test_inert_owner_api_protocol(self):
    code, out, err, api = invoke_stubbed_owner(ENTRY)
    self.assertEqual(code, 0)
    self.assertEqual(err, '')
    self.assertEqual(json.loads(out), {
        'scope': 'windows-new-workspace-owner-facts', 'schema': 1, 'state': 'observed',
        'ownerEqualsTokenUser': False, 'ownerEqualsTokenOwner': True,
        'ownerEqualsAdministrators': True, 'tokenOwnerEqualsTokenUser': False,
    })
    self.assertEqual(api.closed, [2020])
    self.assertEqual(api.freed, [ctypes.addressof(api.descriptor)])
    self.assertEqual([call[1] for call in api.calls if call[0] == 'load'],
                     [r'C:\Windows\System32\advapi32.dll', r'C:\Windows\System32\kernel32.dll'])
    self.assertTrue(all(call[2] == {'use_last_error': True, 'winmode': 0x800}
                        for call in api.calls if call[0] == 'load'))
    for failure, reason, token_closed in [('descriptor', 'security', False),
                                         ('open-token', 'token', False),
                                         ('token-size', 'token-information', True),
                                         ('close', 'cleanup', True),
                                         ('exception', 'unexpected', False)]:
        with self.subTest(failure=failure):
            code, out, err, api = invoke_stubbed_owner(ENTRY, failure)
            self.assertEqual(code, 1)
            self.assertEqual(err, '')
            self.assertEqual(json.loads(out), {'scope': 'windows-new-workspace-owner-facts',
                'schema': 1, 'state': 'unproven', 'reason': reason})
            self.assertEqual(api.closed, [2020] if token_closed else [])
            self.assertEqual(api.freed, [ctypes.addressof(api.descriptor)])
            if failure == 'token-size':
                self.assertEqual([c for c in api.calls if c[0] == 'token-info'], [('token-info', 1, True)])
    code, out, err, api = invoke_stubbed_owner(ENTRY, arguments=('private-argument-canary',))
    self.assertEqual(code, 1)
    self.assertEqual(err, '')
    self.assertEqual(json.loads(out), {'scope': 'windows-new-workspace-owner-facts',
        'schema': 1, 'state': 'unproven', 'reason': 'arguments'})
    self.assertEqual(api.calls, [])
    self.assertNotIn('private-argument-canary', out + err)

OwnerFactsProtocolTests.test_inert_owner_api_protocol = test_inert_owner_api_protocol


def test_windows_matrix_retains_original_tests_and_propagates_both_statuses(self):
    workflow = ENTRY.parents[1] / ".github/workflows/brain-hooks.yml"
    source = workflow.read_text(encoding="utf-8")
    self.assertIn("scripts/test-extract-conversations-windows-owner.py", source)
    self.assertIn("scripts/test-extract-conversations-windows-owner-portable.py", source)
    start = source.index("      - name: Observe Windows fixture owner and exercise brain installation\n")
    end = source.index("      - name: Exercise portable brain installation\n", start)
    windows = source[start:end]
    self.assertIn("if: runner.os == 'Windows'", windows)
    self.assertIn("shell: pwsh", windows)
    self.assertIn("$PSNativeCommandUseErrorActionPreference = $false", windows)
    self.assertLess(windows.index("python scripts/test-extract-conversations-windows-owner.py\n"),
                    windows.index("python -m unittest discover -s skills/default/brain-install/tests -p"))
    self.assertIn("$factsExit = $LASTEXITCODE", windows)
    self.assertIn("$testsExit = $LASTEXITCODE", windows)
    self.assertIn("if ($testsExit -ne 0) { exit $testsExit }", windows)
    self.assertIn("exit $factsExit", windows)
    self.assertIn("if: runner.os != 'Windows'", source[end:])
    self.assertNotIn("continue-on-error", source)
    import tempfile
    import textwrap
    body = textwrap.dedent(windows.split("        run: |\n", 1)[1])
    stub = r"""
param([int]$OwnerExit,[int]$TestsExit)
$ErrorActionPreference='Stop'
function python {
    $expected=@('-m','unittest','discover','-s','skills/default/brain-install/tests','-p','test_*.py')
    if($args.Count -eq 1 -and [string]::Equals($args[0],'scripts/test-extract-conversations-windows-owner.py',[StringComparison]::Ordinal)) {
        [Console]::Out.WriteLine('owner-command')
        $global:LASTEXITCODE=$OwnerExit
        return
    }
    if($args.Count -ne $expected.Count){throw 'unexpected-command'}
    for($i=0;$i -lt $expected.Count;$i++){if(-not [string]::Equals($args[$i],$expected[$i],[StringComparison]::Ordinal)){throw 'unexpected-command'}}
    [Console]::Out.WriteLine('original-tests-command')
    $global:LASTEXITCODE=$TestsExit
}
"""
    powershell = os.environ.get('FACTORY_TEST_PWSH') or shutil.which('pwsh')
    self.assertTrue(powershell, 'PowerShell is required for workflow controls')
    with tempfile.TemporaryDirectory(prefix='owner-workflow-control-') as directory:
        script = Path(directory) / 'actual-workflow.ps1'
        script.write_text(stub + '\n' + body, encoding='utf-8')
        for owner_exit, tests_exit, expected in [(0,0,0),(1,0,1),(0,1,1),(1,2,2)]:
            with self.subTest(owner=owner_exit, tests=tests_exit):
                result = subprocess.run([powershell,'-NoLogo','-NoProfile','-NonInteractive',
                    '-File',str(script),'-OwnerExit',str(owner_exit),'-TestsExit',str(tests_exit)],
                    capture_output=True,text=True,timeout=3,env={})
                self.assertEqual(result.returncode, expected)
                self.assertEqual(result.stdout, 'owner-command\noriginal-tests-command\n')
                self.assertEqual(result.stderr, '')

OwnerFactsProtocolTests.test_windows_matrix_retains_original_tests_and_propagates_both_statuses = test_windows_matrix_retains_original_tests_and_propagates_both_statuses

if __name__ == "__main__":
    unittest.main()
