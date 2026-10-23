// Qualification-only non-debug Windows route observer. Private receipt is NEVER an upload artifact.
// ABI declarations follow Microsoft evntrace.h, evntcons.h, wmistr.h and tdh.h documentation.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Text;
using System.Threading.Tasks;

public static class WindowsEtwRoute
{
    private const uint SystemLoggerMode = 0x02000000;
    private const uint SequentialMode = 0x00000001;
    private const uint AlternateStorageMask = 0x00000C0E; // circular, append, new-file, buffering, private
    private const uint HybridStopMode = 0x00400000;
    private const uint HybridPersistMode = 0x00800000;
    private const uint RequestedMode = SystemLoggerMode | SequentialMode | HybridStopMode;
    private const uint ProcessFlag = 0x00000001;
    private const uint ImageFlag = 0x00000004;
    private const uint WnodeTracedGuid = 0x00020000;
    private const uint TraceQuery = 0;
    private const uint TraceStop = 1;
    private const uint EventRecordMode = 0x10000000;
    private const uint InsufficientBuffer = 122;
    private const int MaxObservationMs = 30000;
    private const long MaxEtlBytes = 64L * 1024 * 1024;
    private const int MaxReceiptBytes = 65536;
    private const uint ProcessQueryLimitedInformation = 0x1000;
    private const uint ProcessSynchronize = 0x00100000;
    private const uint ProcessTerminate = 0x0001;
    private const uint SnapshotProcess = 0x00000002;
    private const uint WaitObject = 0;
    private const uint WaitTimeout = 258;
    private const uint FileIdInfoClass = 18;
    private static readonly Guid ProcessGuid = new Guid("3d6fa8d0-fe05-11d0-9dda-00c04fd7ba7c");
    private static readonly Guid ImageGuid = new Guid("2cb15d1d-5fc1-11d2-abe1-00a0c911f518");
    private static readonly Guid SystemTraceGuid = new Guid("9e814aad-3204-11d2-9a82-006008a86939");

    [StructLayout(LayoutKind.Sequential)]
    private struct WnodeHeader
    {
        public uint BufferSize, ProviderId;
        public ulong HistoricalContext;
        public long TimeStamp;
        public Guid Guid;
        public uint ClientContext, Flags;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct EventTraceProperties
    {
        public WnodeHeader Wnode;
        public uint BufferSize, MinimumBuffers, MaximumBuffers, MaximumFileSize;
        public uint LogFileMode, FlushTimer, EnableFlags;
        public int AgeLimit;
        public uint NumberOfBuffers, FreeBuffers, EventsLost, BuffersWritten;
        public uint LogBuffersLost, RealTimeBuffersLost;
        public IntPtr LoggerThreadId;
        public uint LogFileNameOffset, LoggerNameOffset;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct SystemTime
    {
        public ushort Year, Month, DayOfWeek, Day, Hour, Minute, Second, Milliseconds;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct TimeZoneInformation
    {
        public int Bias;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string StandardName;
        public SystemTime StandardDate;
        public int StandardBias;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 32)] public string DaylightName;
        public SystemTime DaylightDate;
        public int DaylightBias;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct TraceLogfileHeader
    {
        public uint BufferSize, Version, ProviderVersion, NumberOfProcessors;
        public long EndTime;
        public uint TimerResolution, MaximumFileSize, LogFileMode, BuffersWritten;
        public uint StartBuffers, PointerSize, EventsLost, CpuSpeedInMHz;
        public IntPtr LoggerName, LogFileName;
        public TimeZoneInformation TimeZone;
        public long BootTime, PerfFreq, StartTime;
        public uint ReservedFlags, BuffersLost;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct EventTraceHeader
    {
        public ushort Size, FieldTypeFlags;
        public uint Version, ThreadId, ProcessId;
        public long TimeStamp;
        public Guid Guid;
        public ulong ProcessorTime;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct EventTrace
    {
        public EventTraceHeader Header;
        public uint InstanceId, ParentInstanceId;
        public Guid ParentGuid;
        public IntPtr MofData;
        public uint MofLength, BufferContext;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct EventTraceLogfile
    {
        [MarshalAs(UnmanagedType.LPWStr)] public string LogFileName;
        public IntPtr LoggerName;
        public long CurrentTime;
        public uint BuffersRead, ProcessTraceMode;
        public EventTrace CurrentEvent;
        public TraceLogfileHeader LogfileHeader;
        public IntPtr BufferCallback;
        public uint BufferSize, Filled, EventsLost;
        public IntPtr EventRecordCallback;
        public uint IsKernelTrace;
        public IntPtr Context;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct EventDescriptor
    {
        public ushort Id;
        public byte Version, Channel, Level, Opcode;
        public ushort Task;
        public ulong Keyword;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct EventHeader
    {
        public ushort Size, HeaderType, Flags, EventProperty;
        public uint ThreadId, ProcessId;
        public long TimeStamp;
        public Guid ProviderId;
        public EventDescriptor Descriptor;
        public ulong ProcessorTime;
        public Guid ActivityId;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct EventRecord
    {
        public EventHeader Header;
        public uint BufferContext;
        public ushort ExtendedDataCount, UserDataLength;
        public IntPtr ExtendedData, UserData, UserContext;
    }

    // The two documented leading TRACE_EVENT_INFO fields identify a classic MOF class.
    [StructLayout(LayoutKind.Sequential)]
    private struct TraceEventInfoPrefix
    {
        public Guid ProviderGuid, EventGuid;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct PropertyDataDescriptor
    {
        public ulong PropertyName;
        public uint ArrayIndex, Reserved;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct FileTime
    {
        public uint Low, High;
        public long Ticks { get { return ((long)High << 32) | Low; } }
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct FileIdInformation
    {
        public ulong VolumeSerialNumber;
        [MarshalAs(UnmanagedType.ByValArray, SizeConst = 16)] public byte[] Identifier;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    private struct ProcessEntry32
    {
        public uint Size, Usage, ProcessId;
        public IntPtr DefaultHeap;
        public uint ModuleId, Threads, ParentProcessId;
        public int BasePriority;
        public uint Flags;
        [MarshalAs(UnmanagedType.ByValTStr, SizeConst = 260)] public string ExeFile;
    }

    [UnmanagedFunctionPointer(CallingConvention.Winapi)]
    private delegate void EventRecordCallback(IntPtr record);

    [DllImport("sechost.dll", EntryPoint = "StartTraceW", CharSet = CharSet.Unicode)]
    private static extern uint StartTrace(out ulong handle, string name, IntPtr properties);
    [DllImport("sechost.dll", EntryPoint = "ControlTraceW", CharSet = CharSet.Unicode)]
    private static extern uint ControlTrace(ulong handle, string name, IntPtr properties, uint code);
    [DllImport("sechost.dll", EntryPoint = "OpenTraceW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern ulong OpenTrace(ref EventTraceLogfile logfile);
    [DllImport("sechost.dll", EntryPoint = "ProcessTrace")]
    private static extern uint ProcessTrace([In] ulong[] handles, uint count, IntPtr start, IntPtr end);
    [DllImport("sechost.dll", EntryPoint = "CloseTrace")]
    private static extern uint CloseTrace(ulong handle);
    [DllImport("tdh.dll", EntryPoint = "TdhGetEventInformation")]
    private static extern uint TdhGetEventInformation(IntPtr record, uint contextCount, IntPtr context,
        IntPtr buffer, ref uint bufferSize);
    [DllImport("tdh.dll", EntryPoint = "TdhGetPropertySize")]
    private static extern uint TdhGetPropertySize(IntPtr record, uint contextCount, IntPtr context,
        uint descriptorCount, ref PropertyDataDescriptor descriptor, out uint size);
    [DllImport("tdh.dll", EntryPoint = "TdhGetProperty")]
    private static extern uint TdhGetProperty(IntPtr record, uint contextCount, IntPtr context,
        uint descriptorCount, ref PropertyDataDescriptor descriptor, uint size, [Out] byte[] buffer);
    [DllImport("kernel32.dll", EntryPoint = "GetProcessTimes", SetLastError = true)]
    private static extern bool GetProcessTimes(IntPtr process, out FileTime created, out FileTime exited,
        out FileTime kernel, out FileTime user);
    [DllImport("kernel32.dll", EntryPoint = "GetSystemTimePreciseAsFileTime")]
    private static extern void GetSystemTimePreciseAsFileTime(out FileTime time);
    [DllImport("kernel32.dll", EntryPoint = "QueryFullProcessImageNameW", CharSet = CharSet.Unicode,
        SetLastError = true)]
    private static extern bool QueryFullProcessImageName(IntPtr process, uint flags, StringBuilder path,
        ref uint length);
    [DllImport("kernel32.dll", EntryPoint = "GetProcessId", SetLastError = true)]
    private static extern uint GetProcessId(IntPtr process);
    [DllImport("kernel32.dll", EntryPoint = "GetFileInformationByHandleEx", SetLastError = true)]
    private static extern bool GetFileInformationByHandleEx(IntPtr file, uint infoClass,
        out FileIdInformation info, uint size);
    [DllImport("kernel32.dll", EntryPoint = "GetFinalPathNameByHandleW", CharSet = CharSet.Unicode,
        SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(IntPtr file, StringBuilder path, uint length,
        uint flags);

    private static readonly List<string> Receipt = new List<string>();
    private static readonly List<string> Events = new List<string>();
    private static readonly List<Pin> Pins = new List<Pin>();
    private static readonly HashSet<uint> Relevant = new HashSet<uint>();
    private static readonly List<uint[]> Edges = new List<uint[]>();
    private static string FirstFailure;
    private static long RetainedBytes;
    private static int CallbackCount, ProcessRows, ImageRows, Pass;
    private static bool Used, RootCompleted;
    private static EventRecordCallback CallbackRoot;
    private static Process Root;
    private static long Created, Exited, Released, Observed;
    private static uint RootPid, DirectPid;
    private static string SystemDos, SystemNt;
    private sealed class Pin
    {
        public string Path, Label, Dos, Nt;
        public FileStream File;
        public FileIdInformation Id;
    }
    private static InvalidDataException RejectDecode(string phase, string reason, string target)
    {
        if (FirstFailure == null) FirstFailure = reason == "callback-cap" ? "callback-cap" : "schema";
        return new InvalidDataException("closed native failure");
    }
    private static void Line(params object[] parts)
    {
        string[] cells = new string[parts.Length];
        for (int i = 0; i < parts.Length; i++) cells[i] = Convert.ToString(parts[i], CultureInfo.InvariantCulture);
        Receipt.Add(String.Join("\t", cells));
    }
    private static void Retain(string line, bool process)
    {
        int bytes = Encoding.UTF8.GetByteCount(line) + 1;
        if (RetainedBytes + bytes > 8 * 1024 * 1024 ||
            (process ? ProcessRows >= 4096 : ImageRows >= 4096))
        {
            if (FirstFailure == null) FirstFailure = "graph-cap";
            throw new InvalidDataException("retained cap");
        }
        RetainedBytes += bytes;
        if (process) ProcessRows++; else ImageRows++;
        Events.Add(line);
    }
    private static string FinalPath(IntPtr file, uint form)
    {
        StringBuilder result = new StringBuilder(32768);
        uint size = GetFinalPathNameByHandle(file, result, (uint)result.Capacity, form);
        if (size == 0 || size >= result.Capacity) throw new InvalidDataException("final path");
        return result.ToString();
    }
    private static void CheckNoReparse(string path)
    {
        string current = Path.GetFullPath(path);
        while (!String.IsNullOrEmpty(current))
        {
            if ((File.GetAttributes(current) & FileAttributes.ReparsePoint) != 0)
                throw new InvalidDataException("reparse pin");
            current = Path.GetDirectoryName(current);
        }
    }
    private static void HoldPins(string[] paths, string[] digests, string[] labels, Stopwatch watch)
    {
        if (paths == null || paths.Length < 3 || paths.Length > 12 || paths.Length != digests.Length || paths.Length != labels.Length)
            throw new InvalidDataException("pin inventory");
        HashSet<string> seen = new HashSet<string>();
        for (int i = 0; i < paths.Length; i++)
        {
            string label = labels[i];
            if (!(label == "node" || label == "git" || label == "typescript" || label == "cmd" ||
                label == "control" || label == "console" ||
                label.StartsWith("git-dll-", StringComparison.Ordinal) && label.Length == 9 && label[8] >= '1' && label[8] <= '5') || !seen.Add(label))
                throw new InvalidDataException("pin label");
            if (digests[i] == null || digests[i].Length != 64) throw new InvalidDataException("pin digest");
            foreach (char c in digests[i]) if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')))
                throw new InvalidDataException("pin digest");
            string path = Path.GetFullPath(paths[i]);
            CheckNoReparse(path);
            Pin pin = new Pin(); pin.Path = path; pin.Label = label;
            pin.File = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read);
            Pins.Add(pin); // ownership precedes every fallible query/hash
            using (SHA256 hash = SHA256.Create())
                if (BitConverter.ToString(hash.ComputeHash(pin.File)).Replace("-", "").ToLowerInvariant() != digests[i])
                    throw new InvalidDataException("pin digest");
            pin.Id = FileIdentity(pin.File.SafeFileHandle.DangerousGetHandle());
            pin.Dos = FinalPath(pin.File.SafeFileHandle.DangerousGetHandle(), 0);
            pin.Nt = FinalPath(pin.File.SafeFileHandle.DangerousGetHandle(), 2);
            if (label == "cmd")
            {
                SystemDos = Path.GetDirectoryName(Path.GetDirectoryName(pin.Dos)) + "\\";
                SystemNt = Path.GetDirectoryName(Path.GetDirectoryName(pin.Nt)) + "\\";
            }
            Remaining(watch, MaxObservationMs);
        }
        if (!seen.Contains("node") || !seen.Contains("cmd") || !seen.Contains("console"))
            throw new InvalidDataException("pin inventory");
    }
    private static void CheckPins()
    {
        foreach (Pin pin in Pins)
        {
            CheckNoReparse(pin.Path);
            if (FinalPath(pin.File.SafeFileHandle.DangerousGetHandle(), 0) != pin.Dos ||
                FinalPath(pin.File.SafeFileHandle.DangerousGetHandle(), 2) != pin.Nt)
                throw new InvalidDataException("pin namespace changed");
            using (FileStream known = new FileStream(pin.Path, FileMode.Open, FileAccess.Read, FileShare.Read))
                if (!SameFile(pin.Id, FileIdentity(known.SafeFileHandle.DangerousGetHandle())))
                    throw new InvalidDataException("pin file changed");
        }
        // Pre/post checks do NOT prove no intervening ancestor/alias mutation.
    }
    private static bool ConsoleName(string path)
    {
        string name = Path.GetFileName(path);
        return String.Equals(name, "conhost.exe", StringComparison.OrdinalIgnoreCase) ||
            String.Equals(name, "OpenConsole.exe", StringComparison.OrdinalIgnoreCase) ||
            String.Equals(name, "WindowsTerminal.exe", StringComparison.OrdinalIgnoreCase);
    }
    private static string ImageClass(string path)
    {
        foreach (Pin pin in Pins) if (path == pin.Dos || path == pin.Nt) return pin.Label;
        if (ConsoleName(path)) return "console";
        if ((!String.IsNullOrEmpty(SystemDos) && path.StartsWith(SystemDos, StringComparison.Ordinal)) ||
            (!String.IsNullOrEmpty(SystemNt) && path.StartsWith(SystemNt, StringComparison.Ordinal))) return "system";
        return "other";
    }
    private static string ProcessClass(string image)
    {
        if (ConsoleName(image)) return "console";
        foreach (Pin pin in Pins)
            if (!pin.Label.StartsWith("git-dll-", StringComparison.Ordinal) &&
                String.Equals(Path.GetFileName(image), Path.GetFileName(pin.Path), StringComparison.OrdinalIgnoreCase)) return pin.Label;
        return "other";
    }
    private static string MetadataName(IntPtr info, uint size, int offset)
    {
        if (offset < 112 || offset >= size || (offset & 1) != 0) throw new InvalidDataException("schema name");
        StringBuilder text = new StringBuilder();
        for (int i = offset; i + 1 < size && text.Length <= 256; i += 2)
        {
            char c = (char)Marshal.ReadInt16(info, i);
            if (c == 0) return text.ToString();
            text.Append(c);
        }
        throw new InvalidDataException("schema name");
    }
    private static void TypeAt(IntPtr info, uint size, string name, ushort type, bool signed)
    {
        if (size < 112) throw new InvalidDataException("schema prefix");
        int count = Marshal.ReadInt32(info, 100);
        int top = Marshal.ReadInt32(info, 104);
        if (count < 1 || count > 256 || top < 1 || top > count || 112L + count * 24L > size)
            throw new InvalidDataException("schema bounds");
        int matches = 0;
        for (int i = 0; i < top; i++)
        {
            int p = 112 + i * 24;
            if (MetadataName(info, size, Marshal.ReadInt32(info, p + 4)) != name) continue;
            ushort actual = (ushort)Marshal.ReadInt16(info, p + 8);
            if (Marshal.ReadInt32(info, p) != 0 || !(actual == type || signed && actual == 7))
                throw new InvalidDataException("schema type");
            matches++;
        }
        if (matches != 1) throw new InvalidDataException("schema property");
    }
    private static void OnEvent(IntPtr address)
    {
        if (FirstFailure != null) return;
        try
        {
            if (++CallbackCount > 100000) { FirstFailure = "callback-cap"; return; }
            EventRecord record = (EventRecord)Marshal.PtrToStructure(address, typeof(EventRecord));
            if (record.Header.ProviderId != SystemTraceGuid && record.Header.ProviderId != ProcessGuid && record.Header.ProviderId != ImageGuid) return;
            uint size = 0;
            if (TdhGetEventInformation(address, 0, IntPtr.Zero, IntPtr.Zero, ref size) != InsufficientBuffer || size < 112 || size > 65536)
                throw new InvalidDataException("schema size");
            IntPtr info = Marshal.AllocHGlobal((int)size);
            Guid eventGuid;
            byte opcode = record.Header.Descriptor.Opcode;
            try
            {
                if (TdhGetEventInformation(address, 0, IntPtr.Zero, info, ref size) != 0) throw new InvalidDataException("schema");
                eventGuid = ((TraceEventInfoPrefix)Marshal.PtrToStructure(info, typeof(TraceEventInfoPrefix))).EventGuid;
                if (eventGuid == ProcessGuid && (opcode == 1 || opcode == 2) && Pass == 1)
                {
                    TypeAt(info, size, "ProcessId", 8, false); TypeAt(info, size, "ParentId", 8, false);
                    TypeAt(info, size, "UniqueProcessKey", 16, false); TypeAt(info, size, "ImageFileName", 2, false);
                    if (opcode == 2) TypeAt(info, size, "ExitStatus", 8, true);
                }
                else if (eventGuid == ImageGuid && opcode == 10)
                {
                    TypeAt(info, size, "ProcessId", 8, false); TypeAt(info, size, "FileName", 1, false);
                }
            }
            finally { Marshal.FreeHGlobal(info); }
            if (eventGuid == ProcessGuid && (opcode == 1 || opcode == 2) && Pass == 1)
            {
                uint pid = Property32(address, "ProcessId", "none"), parent = Property32(address, "ParentId", "none");
                ulong key = PropertyKey(address, "none");
                string name = ProcessClass(TextProperty(address, "ImageFileName", false, "none"));
                uint status = opcode == 2 ? Property32(address, "ExitStatus", "none") : 0;
                Retain(String.Join("\t", new[] { "P", opcode == 1 ? "S" : "E", pid.ToString(CultureInfo.InvariantCulture),
                    parent.ToString(CultureInfo.InvariantCulture), key.ToString(CultureInfo.InvariantCulture),
                    record.Header.TimeStamp.ToString(CultureInfo.InvariantCulture), name, status.ToString(CultureInfo.InvariantCulture) }), true);
                if (opcode == 1) Edges.Add(new[] { pid, parent });
            }
            else if (eventGuid == ImageGuid && opcode == 10)
            {
                uint pid = Property32(address, "ProcessId", "none");
                if (Pass == 2 && !Relevant.Contains(pid)) return;
                string name = ImageClass(TextProperty(address, "FileName", true, "none"));
                if (Pass == 1 ? name != "console" : name == "console") return;
                Retain(String.Join("\t", new[] { "I", pid.ToString(CultureInfo.InvariantCulture),
                    record.Header.TimeStamp.ToString(CultureInfo.InvariantCulture), name }), false);
            }
        }
        catch { if (FirstFailure == null) FirstFailure = "schema"; }
    }
    private static string ReadControl(Stopwatch watch)
    {
        StringBuilder text = new StringBuilder(32);
        byte[] one = new byte[1];
        for (int i = 0; i < 33; i++)
        {
            Task<int> read = Root.StandardOutput.BaseStream.ReadAsync(one, 0, 1);
            if (!read.Wait(Remaining(watch, 24000)) || read.Result != 1) throw new TimeoutException("root control");
            if (one[0] == 10) return text.ToString();
            if (one[0] != 9 && (one[0] < 32 || one[0] > 126)) throw new InvalidDataException("root control");
            text.Append((char)one[0]);
        }
        throw new InvalidDataException("root control cap");
    }
    private static void RunRoot(string node, string launcher, string spec, string result, string evidence, Stopwatch watch)
    {
        foreach (string path in new[] { node, launcher, spec, result })
            if (path.IndexOf('"') >= 0 || path.IndexOf('\r') >= 0 || path.IndexOf('\n') >= 0) throw new InvalidDataException("launch path");
        ProcessStartInfo start = new ProcessStartInfo(node, "\"" + launcher + "\" \"" + spec + "\" \"" + result + "\"");
        start.WorkingDirectory = evidence; start.UseShellExecute = false; start.CreateNoWindow = true;
        start.RedirectStandardInput = true; start.RedirectStandardOutput = true; start.RedirectStandardError = true;
        start.EnvironmentVariables.Clear();
        string windows = Environment.GetEnvironmentVariable("SystemRoot");
        if (String.IsNullOrEmpty(windows)) throw new InvalidDataException("system root");
        start.EnvironmentVariables["SystemRoot"] = windows; start.EnvironmentVariables["WINDIR"] = windows;
        start.EnvironmentVariables["PATH"] = Path.Combine(windows, "System32") + ";" + windows;
        start.EnvironmentVariables["TEMP"] = evidence; start.EnvironmentVariables["TMP"] = evidence;
        Encoding previous = Console.InputEncoding;
        try { Console.InputEncoding = new UTF8Encoding(false); Root = Process.Start(start); }
        finally { Console.InputEncoding = previous; }
        if (Root == null || Root.HasExited) throw new InvalidDataException("root handle");
        RootPid = (uint)Root.Id;
        if (GetProcessId(Root.Handle) != RootPid) throw new InvalidDataException("root handle");
        FileTime created, exited, kernel, user;
        if (!GetProcessTimes(Root.Handle, out created, out exited, out kernel, out user) || created.Ticks <= 0)
            throw new InvalidDataException("root times");
        Created = created.Ticks;
        StringBuilder image = new StringBuilder(32768); uint length = (uint)image.Capacity;
        if (!QueryFullProcessImageName(Root.Handle, 0, image, ref length) || image.ToString() != node)
            throw new InvalidDataException("root image");
        Pin nodePin = Pins.Find(pin => pin.Label == "node");
        using (FileStream known = new FileStream(node, FileMode.Open, FileAccess.Read, FileShare.Read))
            if (nodePin == null || !SameFile(nodePin.Id, FileIdentity(known.SafeFileHandle.DangerousGetHandle())))
                throw new InvalidDataException("root file identity");
        if (ReadControl(watch) != "READY" || Root.HasExited) throw new InvalidDataException("root readiness");
        FileTime precise; GetSystemTimePreciseAsFileTime(out precise); Released = precise.Ticks;
        Root.StandardInput.BaseStream.WriteByte(0x52); Root.StandardInput.BaseStream.Flush();
        string done = ReadControl(watch);
        if (!done.StartsWith("DONE\t", StringComparison.Ordinal) ||
            !UInt32.TryParse(done.Substring(5), NumberStyles.None, CultureInfo.InvariantCulture, out DirectPid) ||
            DirectPid == 0 || DirectPid == RootPid || Root.HasExited) throw new InvalidDataException("root completion");
        Root.StandardInput.BaseStream.WriteByte(0x58); Root.StandardInput.BaseStream.Flush(); Root.StandardInput.Close();
        if (!Root.WaitForExit(Remaining(watch, 5000))) throw new TimeoutException("root exit");
        GetSystemTimePreciseAsFileTime(out precise); Observed = precise.Ticks;
        if (Root.ExitCode != 0 || !GetProcessTimes(Root.Handle, out created, out exited, out kernel, out user) ||
            exited.Ticks < Released || Observed < exited.Ticks || Root.StandardOutput.BaseStream.ReadByte() != -1 ||
            Root.StandardError.BaseStream.ReadByte() != -1) throw new InvalidDataException("root exit");
        Exited = exited.Ticks;
        Line("ROOT", RootPid, Created, Exited, Released, Observed); Line("DIRECT", DirectPid);
        Line("HELD", "root", 1, 1, 1);
        RootCompleted = true;
    }
    private static bool Cleanup()
    {
        bool ok = Root == null || RootCompleted;
        try
        {
            if (Root != null && !Root.HasExited)
            {
                try { Root.StandardInput.Close(); } catch { }
                if (!Root.WaitForExit(2000)) { Root.Kill(); if (!Root.WaitForExit(2000)) ok = false; }
                // Root termination cannot establish descendant cleanup.
                ok = false;
            }
        }
        catch { ok = false; }
        try { if (Root != null) { Root.Dispose(); Root = null; } } catch { ok = false; }
        foreach (Pin pin in Pins)
            try { if (pin.File != null) { pin.File.Dispose(); pin.File = null; } } catch { ok = false; }
        return ok;
    }
    private static bool Decode(string etl)
    {
        for (Pass = 1; Pass <= 2; Pass++)
        {
            EventTraceLogfile logfile = new EventTraceLogfile(); logfile.LogFileName = etl;
            logfile.ProcessTraceMode = EventRecordMode; CallbackRoot = OnEvent;
            logfile.EventRecordCallback = Marshal.GetFunctionPointerForDelegate(CallbackRoot);
            ulong reader = OpenTrace(ref logfile);
            if (reader == ulong.MaxValue) { FirstFailure = FirstFailure ?? "decode"; return false; }
            uint process = 1, close = 1;
            try { process = ProcessTrace(new[] { reader }, 1, IntPtr.Zero, IntPtr.Zero); }
            finally { close = CloseTrace(reader); GC.KeepAlive(CallbackRoot); }
            if (Pass == 1) { Line("API", "open", 0); Line("API", "process", process); Line("API", "close", close); }
            if (process != 0 || close != 0 || FirstFailure != null) { FirstFailure = FirstFailure ?? (close != 0 ? "close" : "decode"); return false; }
            if (logfile.LogfileHeader.EndTime <= Observed || logfile.LogfileHeader.EventsLost != 0 || logfile.LogfileHeader.BuffersLost != 0)
            { FirstFailure = "header"; return false; }
            if (Pass == 1)
            {
                Relevant.Add(RootPid); Relevant.Add(DirectPid);
                bool changed;
                do { changed = false; foreach (uint[] edge in Edges) if (Relevant.Contains(edge[1])) changed |= Relevant.Add(edge[0]); } while (changed);
            }
            else Line("HEADER", logfile.LogfileHeader.EndTime, logfile.LogfileHeader.EventsLost, logfile.LogfileHeader.BuffersLost);
        }
        Line("SCHEMA", "verified"); Line("COUNTS", CallbackCount, Events.Count);
        foreach (string line in Events) Receipt.Add(line);
        return true;
    }
    public static int Run(string caseName, string nodePath, string evidenceDir, string launcherPath,
        string specPath, string[] paths, string[] digests, string[] labels)
    {
        if (Used) return 2; Used = true;
        string[] cases = { "baseline-git", "baseline-typescript", "candidate-git", "candidate-typescript",
            "candidate-nested-cmd", "candidate-deadline-control", "candidate-output-control" };
        if (Array.IndexOf(cases, caseName) < 0 || IntPtr.Size != 8 || Environment.OSVersion.Platform != PlatformID.Win32NT) return 2;
        string evidence = Path.GetFullPath(evidenceDir), node = Path.GetFullPath(nodePath);
        string etl = Path.Combine(evidence, "trace.etl"), receipt = Path.Combine(evidence, "observation.private.tsv");
        if (!Directory.Exists(evidence) || File.Exists(etl) || File.Exists(receipt)) return 2;
        Stopwatch watch = Stopwatch.StartNew(); ulong handle = 0; bool owned = false, stopped = false, clean = false;
        Guid guid = Guid.NewGuid(); string name = "Codex factory ETW route " + guid.ToString("N");
        Line("ROUTE", 1, caseName);
        try
        {
            CheckAbi();
            try { HoldPins(paths, digests, labels, watch); }
            catch { FirstFailure = "pin"; throw; }
            IntPtr properties = PropertiesBuffer(guid, name, etl, true);
            try
            {
                uint code = StartTrace(out handle, name, properties); Line("API", "start", code);
                if (code != 0) throw new InvalidOperationException("session start");
                owned = true; Line("OWNED", 1); Line("SESSION", RequestedMode, ProcessFlag | ImageFlag, 64);
            }
            finally { Marshal.FreeHGlobal(properties); }
            Query(handle, guid, name, etl, "readyQuery");
            RunRoot(node, Path.GetFullPath(launcherPath), Path.GetFullPath(specPath), Path.Combine(evidence, "launcher.private.json"), evidence, watch);
            CheckPins(); Remaining(watch, MaxObservationMs);
            Query(handle, guid, name, etl, "beforeStopQuery");
        }
        catch (TimeoutException) { FirstFailure = FirstFailure ?? "timeout"; }
        catch { FirstFailure = FirstFailure ?? "operation"; }
        finally
        {
            try
            {
                if (owned)
                {
                    IntPtr properties = PropertiesBuffer(guid, name, etl, false);
                    try
                    {
                        uint code = ControlTrace(handle, name, properties, TraceStop); Line("API", "stop", code);
                        stopped = code == 0;
                        if (!stopped) FirstFailure = FirstFailure ?? "stop";
                        else
                        {
                            EventTraceProperties final = (EventTraceProperties)Marshal.PtrToStructure(properties, typeof(EventTraceProperties));
                            Line("STATS", final.EventsLost, final.LogBuffersLost, final.RealTimeBuffersLost);
                            if (final.EventsLost != 0 || final.LogBuffersLost != 0 || final.RealTimeBuffersLost != 0) FirstFailure = FirstFailure ?? "loss";
                        }
                    }
                    finally { Marshal.FreeHGlobal(properties); }
                }
                if (FirstFailure == null && stopped)
                {
                    long bytes = new FileInfo(etl).Length; Line("FILE", bytes);
                    if (bytes <= 0 || bytes >= MaxEtlBytes) FirstFailure = "file-cap";
                    else if (Decode(etl)) CheckPins();
                }
            }
            catch { FirstFailure = FirstFailure ?? "decode"; }
            finally { clean = Cleanup(); if (!clean) FirstFailure = FirstFailure ?? "cleanup"; }
        }
        Line("CLEANUP", clean ? 1 : 0);
        if (FirstFailure == null) Line("COMPLETE"); else Line("FAIL", FirstFailure);
        try
        {
            string text = String.Join("\n", Receipt.ToArray()) + "\n";
            if (Encoding.UTF8.GetByteCount(text) > MaxReceiptBytes) { text = "FAIL\treceipt\n"; FirstFailure = "receipt"; }
            using (StreamWriter output = new StreamWriter(new FileStream(receipt, FileMode.CreateNew, FileAccess.Write, FileShare.None), new UTF8Encoding(false))) output.Write(text);
        }
        catch { return 4; }
        finally { Cleanup(); }
        return FirstFailure == null ? 0 : 4;
    }

    private static void CheckAbi()
    {
        // x64 sizes and offsets from the public Windows SDK declarations listed above.
        if (Marshal.SizeOf(typeof(EventTraceProperties)) != 120 ||
            Marshal.OffsetOf(typeof(EventTraceProperties), "LogFileMode").ToInt32() != 64 ||
            Marshal.OffsetOf(typeof(EventTraceProperties), "EnableFlags").ToInt32() != 72 ||
            Marshal.SizeOf(typeof(TraceLogfileHeader)) != 280 ||
            Marshal.SizeOf(typeof(EventRecord)) != 112 ||
            Marshal.SizeOf(typeof(EventTraceLogfile)) != 448 ||
            Marshal.OffsetOf(typeof(TraceLogfileHeader), "EndTime").ToInt32() != 16 ||
            Marshal.OffsetOf(typeof(TraceLogfileHeader), "EventsLost").ToInt32() != 48 ||
            Marshal.OffsetOf(typeof(TraceLogfileHeader), "BuffersLost").ToInt32() != 276 ||
            Marshal.OffsetOf(typeof(EventTraceLogfile), "LogfileHeader").ToInt32() != 120 ||
            Marshal.OffsetOf(typeof(EventTraceLogfile), "EventRecordCallback").ToInt32() != 424 ||
            Marshal.OffsetOf(typeof(EventHeader), "Descriptor").ToInt32() != 40 ||
            Marshal.OffsetOf(typeof(EventRecord), "UserData").ToInt32() != 96 ||
            Marshal.SizeOf(typeof(FileIdInformation)) != 24 ||
            Marshal.SizeOf(typeof(ProcessEntry32)) != 568 ||
            Marshal.OffsetOf(typeof(ProcessEntry32), "ParentProcessId").ToInt32() != 32)
            throw new InvalidOperationException("x64 ETW ABI layout differs from SDK");
        Line("ABI", 120, 280, 112, 448);
    }

    private static IntPtr PropertiesBuffer(Guid guid, string name, string etl, bool start)
    {
        int basic = Marshal.SizeOf(typeof(EventTraceProperties));
        byte[] nameBytes = Encoding.Unicode.GetBytes(name + "\0");
        byte[] fileBytes = Encoding.Unicode.GetBytes(etl + "\0");
        int total = checked(basic + nameBytes.Length + fileBytes.Length);
        IntPtr address = Marshal.AllocHGlobal(total);
        for (int offset = 0; offset < total; offset++) Marshal.WriteByte(address, offset, 0);
        var properties = new EventTraceProperties();
        properties.Wnode.BufferSize = (uint)total;
        properties.Wnode.Guid = guid;
        properties.Wnode.ClientContext = 1; // QPC, converted to FILETIME by ProcessTrace.
        properties.Wnode.Flags = WnodeTracedGuid;
        properties.LoggerNameOffset = (uint)basic;
        properties.LogFileNameOffset = (uint)(basic + nameBytes.Length);
        if (start)
        {
            properties.BufferSize = 64;
            properties.MinimumBuffers = 4;
            properties.MaximumBuffers = 16;
            properties.MaximumFileSize = 64;
            properties.LogFileMode = RequestedMode;
            properties.EnableFlags = ProcessFlag | ImageFlag;
        }
        Marshal.StructureToPtr(properties, address, false);
        Marshal.Copy(nameBytes, 0, IntPtr.Add(address, basic), nameBytes.Length);
        Marshal.Copy(fileBytes, 0, IntPtr.Add(address, basic + nameBytes.Length), fileBytes.Length);
        return address;
    }

    private static EventTraceProperties Query(ulong handle, Guid guid, string name, string etl, string label)
    {
        IntPtr address = PropertiesBuffer(guid, name, etl, false);
        try
        {
            uint code = ControlTrace(handle, name, address, TraceQuery);
            Line("API", label, code);
            if (code != 0) throw new Win32Exception((int)code, label);
            var result = (EventTraceProperties)Marshal.PtrToStructure(address, typeof(EventTraceProperties));
            bool guidMatches = result.Wnode.Guid == guid;
            bool modeMatches = result.LogFileMode == RequestedMode;
            bool flagsMatch = result.EnableFlags == (ProcessFlag | ImageFlag);
            bool fileCapMatches = result.MaximumFileSize == 64;
            bool lossZero = result.EventsLost == 0 && result.LogBuffersLost == 0 &&
                result.RealTimeBuffersLost == 0;
            Line("QUERY", label, guidMatches ? 1 : 0, modeMatches ? 1 : 0,
                flagsMatch ? 1 : 0, fileCapMatches ? 1 : 0, lossZero ? 1 : 0);
            uint mode = result.LogFileMode;
            uint coveredMode = SystemLoggerMode | SequentialMode | AlternateStorageMask |
                HybridStopMode | HybridPersistMode;
            string hybrid = (mode & HybridStopMode) != 0
                ? (mode & HybridPersistMode) != 0 ? "both" : "stop"
                : (mode & HybridPersistMode) != 0 ? "persist" : "none";
            Line("MODE", label, (mode & SystemLoggerMode) != 0 ? 1 : 0,
                (mode & SequentialMode) != 0 ? 1 : 0,
                (mode & AlternateStorageMask) != 0 ? 1 : 0,
                hybrid, (mode & ~coveredMode) != 0 ? 1 : 0);
            if (!guidMatches || !modeMatches || !flagsMatch || !fileCapMatches)
                throw new InvalidOperationException("owned session properties differ from requested trace");
            if (!lossZero)
                throw new InvalidOperationException("session loss before stop");
            return result;
        }
        finally { Marshal.FreeHGlobal(address); }
    }

    private static byte[] Property(IntPtr record, string name, string target)
    {
        IntPtr key = Marshal.StringToHGlobalUni(name);
        try
        {
            var descriptor = new PropertyDataDescriptor();
            descriptor.PropertyName = unchecked((ulong)key.ToInt64());
            descriptor.ArrayIndex = uint.MaxValue;
            uint size;
            uint code = TdhGetPropertySize(record, 0, IntPtr.Zero, 1, ref descriptor, out size);
            if (code != 0) throw new Win32Exception((int)code, "TDH size " + name);
            if (size == 0 || size > 32768) throw RejectDecode("callback", "property-size", target);
            var bytes = new byte[size];
            code = TdhGetProperty(record, 0, IntPtr.Zero, 1, ref descriptor, size, bytes);
            if (code != 0) throw new Win32Exception((int)code, "TDH value " + name);
            return bytes;
        }
        finally { Marshal.FreeHGlobal(key); }
    }

    private static uint Property32(IntPtr record, string name, string target)
    {
        byte[] bytes = Property(record, name, target);
        if (bytes.Length != 4) throw RejectDecode("callback", "property-width", target);
        return BitConverter.ToUInt32(bytes, 0);
    }

    private static ulong PropertyKey(IntPtr record, string target)
    {
        byte[] bytes = Property(record, "UniqueProcessKey", target);
        if (bytes.Length == 8) return BitConverter.ToUInt64(bytes, 0);
        if (bytes.Length == 4) return BitConverter.ToUInt32(bytes, 0);
        throw RejectDecode("callback", "property-width", target);
    }

    private static string TextProperty(IntPtr record, string name, bool unicode, string target)
    {
        byte[] bytes = Property(record, name, target);
        string value = (unicode ? Encoding.Unicode : Encoding.Default).GetString(bytes).TrimEnd('\0');
        if (value.Length == 0 || value.IndexOf('\t') >= 0 || value.IndexOf('\n') >= 0 || value.Length > 4096)
            throw RejectDecode("callback", "text-shape", target);
        return value;
    }

    private static FileIdInformation FileIdentity(IntPtr handle)
    {
        FileIdInformation info;
        if (!GetFileInformationByHandleEx(handle, FileIdInfoClass, out info,
            (uint)Marshal.SizeOf(typeof(FileIdInformation))) || info.Identifier == null ||
            info.Identifier.Length != 16)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "file identity unavailable");
        return info;
    }

    private static bool SameFile(FileIdInformation left, FileIdInformation right)
    {
        if (left.VolumeSerialNumber != right.VolumeSerialNumber) return false;
        for (int i = 0; i < 16; i++) if (left.Identifier[i] != right.Identifier[i]) return false;
        return true;
    }

    private static int Remaining(Stopwatch watch, int localMaximum)
    {
        int left = MaxObservationMs - (int)watch.ElapsedMilliseconds;
        if (left <= 0) throw new TimeoutException("observation exceeded thirty seconds");
        return Math.Min(left, localMaximum);
    }
}
