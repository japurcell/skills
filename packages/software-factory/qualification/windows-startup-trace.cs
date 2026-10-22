// Qualification-only debug launcher. Build on an owned Windows runner with Add-Type.
// DEBUG_PROCESS observes descendant creation even when a child exits immediately.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

public static class WindowsStartupTrace
{
    private const uint DebugProcess = 0x00000001;
    private const uint CreateNoWindow = 0x08000000;
    private const uint StartfUseStdHandles = 0x00000100;
    private const uint GenericRead = 0x80000000;
    private const uint OpenExisting = 3;
    private const uint FileShareRead = 1;
    private const uint FileShareWrite = 2;
    private const uint HandleFlagInherit = 1;
    private const uint DbgContinue = 0x00010002;
    private const uint DbgExceptionNotHandled = 0x80010001;
    private const int ErrorSemaphoreTimeout = 121;
    private const int WaitTimeout = 258;
    private const int CreateProcessEvent = 3;
    private const int ExitProcessEvent = 5;
    private const int LoadDllEvent = 6;
    private const int ExceptionEvent = 1;

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct StartupInfo
    {
        public int cb;
        public string lpReserved;
        public string lpDesktop;
        public string lpTitle;
        public int dwX;
        public int dwY;
        public int dwXSize;
        public int dwYSize;
        public int dwXCountChars;
        public int dwYCountChars;
        public int dwFillAttribute;
        public uint dwFlags;
        public short wShowWindow;
        public short cbReserved2;
        public IntPtr lpReserved2;
        public IntPtr hStdInput;
        public IntPtr hStdOutput;
        public IntPtr hStdError;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct ProcessInformation
    {
        public IntPtr hProcess;
        public IntPtr hThread;
        public int dwProcessId;
        public int dwThreadId;
    }

    // Windows x64 DEBUG_EVENT is 12-byte header, 4-byte alignment pad,
    // then a 160-byte union. The first pointer is hFile for create/load events.
    [StructLayout(LayoutKind.Explicit, Size = 176)]
    private struct DebugEvent
    {
        [FieldOffset(0)] public int code;
        [FieldOffset(4)] public int processId;
        [FieldOffset(8)] public int threadId;
        [FieldOffset(16)] public IntPtr file;
        [FieldOffset(16)] public int exitCode;
        [FieldOffset(16)] public uint exceptionCode;
        [FieldOffset(16 + 8)] public IntPtr process;
    }

    [DllImport("kernel32.dll", EntryPoint = "CreateProcessW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool CreateProcess(string application, StringBuilder commandLine, IntPtr processAttributes,
        IntPtr threadAttributes, bool inheritHandles, uint creationFlags, IntPtr environment, string currentDirectory,
        ref StartupInfo startupInfo, out ProcessInformation processInformation);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool WaitForDebugEvent(out DebugEvent debugEvent, uint milliseconds);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool ContinueDebugEvent(int processId, int threadId, uint continueStatus);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr handle);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool SetHandleInformation(IntPtr handle, uint mask, uint flags);

    [DllImport("kernel32.dll", EntryPoint = "CreateFileW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern IntPtr CreateFile(string name, uint access, uint share, IntPtr security,
        uint creation, uint flags, IntPtr template);

    [DllImport("kernel32.dll", EntryPoint = "GetFinalPathNameByHandleW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(IntPtr file, StringBuilder path, uint length, uint flags);

    [DllImport("kernel32.dll", SetLastError = true)]
    private static extern bool TerminateProcess(IntPtr process, uint exitCode);

    private static string Quote(string value)
    {
        if (value.Length > 0 && value.IndexOfAny(new[] { ' ', '\t', '"' }) < 0) return value;
        var result = new StringBuilder("\"");
        int slashes = 0;
        foreach (char character in value)
        {
            if (character == '\\') { slashes++; continue; }
            if (character == '"')
            {
                result.Append('\\', slashes * 2 + 1).Append('"');
                slashes = 0;
                continue;
            }
            result.Append('\\', slashes).Append(character);
            slashes = 0;
        }
        result.Append('\\', slashes * 2).Append('"');
        return result.ToString();
    }

    private static string FilePath(IntPtr file)
    {
        if (file == IntPtr.Zero || file == new IntPtr(-1)) return "";
        var path = new StringBuilder(32768);
        uint length = GetFinalPathNameByHandle(file, path, (uint)path.Capacity, 0);
        return length > 0 && length < path.Capacity ? path.ToString() : "";
    }

    private static void Record(string trace, string kind, int pid, string value)
    {
        string encoded = Convert.ToBase64String(Encoding.UTF8.GetBytes(value));
        File.AppendAllText(trace, kind + "\t" + pid + "\t" + encoded + "\n", Encoding.UTF8);
    }

    private static void Stage(string path, string label)
    {
        File.AppendAllText(path, DateTime.UtcNow.ToString("O", CultureInfo.InvariantCulture) + "\t" + label + "\n",
            new UTF8Encoding(false));
    }

    public static int Main(string[] args, string stagePath)
    {
        Stage(stagePath, "native-entry");
        if (IntPtr.Size != 8 || args.Length < 6)
        {
            Console.Error.WriteLine("x64 and six fixed launcher arguments required");
            return 2;
        }
        string executable = Path.GetFullPath(args[0]);
        string cwd = Path.GetFullPath(args[1]);
        string stdoutPath = Path.GetFullPath(args[2]);
        string stderrPath = Path.GetFullPath(args[3]);
        string tracePath = Path.GetFullPath(args[4]);
        int timeoutMs;
        if (!int.TryParse(args[5], out timeoutMs) || timeoutMs < 100 || timeoutMs > 60000) return 2;
        var commandLine = new StringBuilder(Quote(executable));
        for (int i = 6; i < args.Length; i++) commandLine.Append(' ').Append(Quote(args[i]));
        Stage(stagePath, "trace-create-start");
        File.WriteAllText(tracePath, "", Encoding.UTF8);
        Stage(stagePath, "trace-create-end");
        IntPtr input = IntPtr.Zero;
        ProcessInformation process = new ProcessInformation();
        var live = new Dictionary<int, IntPtr>();
        bool started = false;
        bool rootExited = false;
        bool timedOut = false;
        int rootExitCode = -1;
        try
        {
            input = CreateFile("NUL", GenericRead, FileShareRead | FileShareWrite, IntPtr.Zero, OpenExisting, 0, IntPtr.Zero);
            if (input == new IntPtr(-1)) throw new Win32Exception(Marshal.GetLastWin32Error(), "open NUL");
            using (var stdout = new FileStream(stdoutPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read))
            using (var stderr = new FileStream(stderrPath, FileMode.CreateNew, FileAccess.Write, FileShare.Read))
            {
                IntPtr outputHandle = stdout.SafeFileHandle.DangerousGetHandle();
                IntPtr errorHandle = stderr.SafeFileHandle.DangerousGetHandle();
                foreach (IntPtr handle in new[] { input, outputHandle, errorHandle })
                    if (!SetHandleInformation(handle, HandleFlagInherit, HandleFlagInherit))
                        throw new Win32Exception(Marshal.GetLastWin32Error(), "mark standard handle inheritable");
                var startup = new StartupInfo();
                startup.cb = Marshal.SizeOf(typeof(StartupInfo));
                startup.dwFlags = StartfUseStdHandles;
                startup.hStdInput = input;
                startup.hStdOutput = outputHandle;
                startup.hStdError = errorHandle;
                if (!CreateProcess(executable, commandLine, IntPtr.Zero, IntPtr.Zero, true,
                    DebugProcess | CreateNoWindow, IntPtr.Zero, cwd, ref startup, out process))
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "debug launch");
                started = true;
                Record(tracePath, "ROOT", process.dwProcessId, executable);
                var timer = Stopwatch.StartNew();
                long stopAtMs = -1;
                while (true)
                {
                    if (!timedOut && (timer.ElapsedMilliseconds >= timeoutMs ||
                        stdout.Length > 262144 || stderr.Length > 262144))
                    {
                        timedOut = true;
                        stopAtMs = timer.ElapsedMilliseconds;
                        string reason = stdout.Length > 262144 || stderr.Length > 262144 ? "output-limit" : "deadline";
                        Record(tracePath, "STOP_REQUESTED", process.dwProcessId, reason);
                        foreach (IntPtr handle in live.Values) TerminateProcess(handle, 124);
                        TerminateProcess(process.hProcess, 124);
                    }
                    if (timedOut && timer.ElapsedMilliseconds >= stopAtMs + 5000)
                        throw new InvalidOperationException("debugged process stop unobserved");
                    DebugEvent debugEvent;
                    if (!WaitForDebugEvent(out debugEvent, 100))
                    {
                        int error = Marshal.GetLastWin32Error();
                        if (error != ErrorSemaphoreTimeout && error != WaitTimeout)
                            throw new Win32Exception(error, "wait for debug event");
                        continue;
                    }
                    uint continuation = DbgContinue;
                    try
                    {
                        if (debugEvent.code == CreateProcessEvent)
                        {
                            live[debugEvent.processId] = debugEvent.process;
                            Record(tracePath, "CREATE", debugEvent.processId, FilePath(debugEvent.file));
                            if (debugEvent.file != IntPtr.Zero) CloseHandle(debugEvent.file);
                        }
                        else if (debugEvent.code == LoadDllEvent)
                        {
                            Record(tracePath, "DLL", debugEvent.processId, FilePath(debugEvent.file));
                            if (debugEvent.file != IntPtr.Zero) CloseHandle(debugEvent.file);
                        }
                        else if (debugEvent.code == ExitProcessEvent)
                        {
                            Record(tracePath, "EXIT", debugEvent.processId, debugEvent.exitCode.ToString());
                            if (debugEvent.processId == process.dwProcessId)
                            {
                                rootExited = true;
                                rootExitCode = debugEvent.exitCode;
                            }
                            live.Remove(debugEvent.processId);
                        }
                        else if (debugEvent.code == ExceptionEvent && debugEvent.exceptionCode != 0x80000003)
                            continuation = DbgExceptionNotHandled;
                        if (!ContinueDebugEvent(debugEvent.processId, debugEvent.threadId, continuation))
                            throw new Win32Exception(Marshal.GetLastWin32Error(), "continue debug event");
                    }
                    catch
                    {
                        foreach (IntPtr handle in live.Values) TerminateProcess(handle, 125);
                        TerminateProcess(process.hProcess, 125);
                        throw;
                    }
                    if (rootExited && live.Count == 0) break;
                }
            }
            if (timedOut && rootExited && live.Count == 0)
                Record(tracePath, "STOP_OBSERVED", process.dwProcessId, rootExitCode.ToString());
            Record(tracePath, "DONE", process.dwProcessId,
                timedOut ? "stopped:" + rootExitCode : rootExited && live.Count == 0 ? rootExitCode.ToString() : "uncertain");
            return timedOut || !rootExited || live.Count != 0 ? 3 : 0;
        }
        catch (Exception error)
        {
            if (started && !rootExited)
            {
                foreach (IntPtr handle in live.Values) TerminateProcess(handle, 125);
                TerminateProcess(process.hProcess, 125);
            }
            Record(tracePath, "ERROR", started ? process.dwProcessId : 0, error.GetType().Name + ": " + error.Message);
            return 4;
        }
        finally
        {
            if (process.hThread != IntPtr.Zero) CloseHandle(process.hThread);
            if (process.hProcess != IntPtr.Zero) CloseHandle(process.hProcess);
            if (input != IntPtr.Zero && input != new IntPtr(-1)) CloseHandle(input);
        }
    }
}
