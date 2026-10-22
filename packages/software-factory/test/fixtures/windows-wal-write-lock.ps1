param([Parameter(Mandatory = $true)][string]$WalPath)
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @'
using System;
using System.ComponentModel;
using System.IO;
using System.Runtime.InteropServices;
using Microsoft.Win32.SafeHandles;
public sealed class FactoryWalWriteLock : IDisposable
{
    [StructLayout(LayoutKind.Sequential)]
    private struct Overlapped
    {
        public UIntPtr Internal;
        public UIntPtr InternalHigh;
        public uint Offset;
        public uint OffsetHigh;
        public IntPtr Event;
    }
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool LockFileEx(SafeFileHandle file, uint flags, uint reserved,
        uint lengthLow, uint lengthHigh, ref Overlapped overlapped);
    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool UnlockFileEx(SafeFileHandle file, uint reserved,
        uint lengthLow, uint lengthHigh, ref Overlapped overlapped);
    private readonly FileStream _file;
    private Overlapped _overlapped;
    private bool _locked;
    public FactoryWalWriteLock(string path)
    {
        _file = new FileStream(path, FileMode.Open, FileAccess.ReadWrite, FileShare.ReadWrite | FileShare.Delete);
        try
        {
            long offset = _file.Length;
            if (offset <= 32) throw new InvalidOperationException("Expected committed WAL frames before write denial");
            _overlapped.Offset = (uint)(offset & uint.MaxValue);
            _overlapped.OffsetHigh = (uint)(offset >> 32);
            // A shared range permits reads but denies subsequent WAL appends through other handles.
            // FAIL_IMMEDIATELY only: never wait for an unavailable lock or replace SQLite's implementation.
            if (!LockFileEx(_file.SafeFileHandle, 1, 0, 67108864, 0, ref _overlapped))
                throw new Win32Exception(Marshal.GetLastWin32Error());
            _locked = true;
        }
        catch { _file.Dispose(); throw; }
    }
    public static bool WaitForRelease()
    {
        return System.Threading.Tasks.Task.Run(() => Console.ReadLine()).Wait(15000);
    }
    public void Dispose()
    {
        try
        {
            if (_locked && !UnlockFileEx(_file.SafeFileHandle, 0, 67108864, 0, ref _overlapped))
                throw new Win32Exception(Marshal.GetLastWin32Error());
            _locked = false;
        }
        finally { _file.Dispose(); }
    }
}
'@
$lock = $null
try {
    $lock = New-Object FactoryWalWriteLock $WalPath
    [Console]::Out.WriteLine('{"ready":true}')
    [Console]::Out.Flush()
    # Bound the lock even if the fixture controller disappears. EOF also releases it.
    if (-not [FactoryWalWriteLock]::WaitForRelease()) { throw 'WAL lock controller timed out' }
} finally {
    if ($null -ne $lock) { $lock.Dispose() }
}
