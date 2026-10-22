// Disposable Windows x64 ETW feasibility probe. Only a bounded typed receipt is CI evidence.
// ABI declarations follow Microsoft evntrace.h, evntcons.h, wmistr.h and tdh.h documentation.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Principal;
using System.Text;

public static class WindowsEtwProbe
{
    private const uint SystemLoggerMode = 0x02000000;
    private const uint SequentialMode = 0x00000001;
    private const uint AlternateStorageMask = 0x00000C0E; // circular, append, new-file, buffering, private
    private const uint HybridStopMode = 0x00400000;
    private const uint HybridPersistMode = 0x00800000;
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
    [DllImport("kernel32.dll", EntryPoint = "QueryFullProcessImageNameW", CharSet = CharSet.Unicode,
        SetLastError = true)]
    private static extern bool QueryFullProcessImageName(IntPtr process, uint flags, StringBuilder path,
        ref uint length);

    private static readonly List<string> Receipt = new List<string>();
    private static readonly List<string> SelectedEvents = new List<string>();
    private sealed class KnownEvent
    {
        public string Kind;
        public int Pid;
        public uint Parent;
        public ulong Key;
        public uint ExitStatus;
        public long Time;
    }

    private static readonly List<KnownEvent> KnownEvents = new List<KnownEvent>();
    private static Exception DecodeError;
    private static string PinnedNode;
    private static long RootCreated;
    private static int RootPid, ChildPid;
    private static int CallbackCount;
    private static int ProcessRundown, ImageRundown;
    private static EventRecordCallback CallbackRoot;
    private static Process RootProcess;
    private static readonly Dictionary<int, ulong> StartKeys = new Dictionary<int, ulong>();
    private static readonly Dictionary<int, ulong> EndKeys = new Dictionary<int, ulong>();

    private static void Failure(string stage, string code, uint nativeCode)
    {
        Line("FAIL", stage, code, nativeCode);
    }

    private static void Failure(string stage, Exception error)
    {
        var win32 = error as Win32Exception ?? error.InnerException as Win32Exception;
        Failure(stage, win32 != null ? "native-api" : error is TimeoutException ? "timeout" :
            error is InvalidDataException ? "invalid-data" : error is InvalidOperationException ? "invalid-state" :
            "operation-failed", win32 != null ? (uint)win32.NativeErrorCode : 0);
    }

    private static bool WriteReceipt(string path)
    {
        var text = new StringBuilder();
        int bytes = 0;
        bool overflow = false;
        foreach (string line in Receipt)
        {
            bytes += Encoding.UTF8.GetByteCount(line) + 1;
            if (bytes > MaxReceiptBytes)
            {
                text.Clear();
                text.Append("FAIL\treceipt\toverflow\t0\n");
                overflow = true;
                break;
            }
            text.Append(line).Append('\n');
        }
        using (var output = new StreamWriter(new FileStream(path, FileMode.CreateNew,
            FileAccess.Write, FileShare.None), new UTF8Encoding(false)))
            output.Write(text.ToString());
        return !overflow;
    }

    private static void Line(params object[] parts)
    {
        var text = new string[parts.Length];
        for (int i = 0; i < parts.Length; i++) text[i] = Convert.ToString(parts[i], CultureInfo.InvariantCulture);
        Receipt.Add(String.Join("\t", text));
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
            Marshal.OffsetOf(typeof(EventRecord), "UserData").ToInt32() != 96)
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
            properties.LogFileMode = SystemLoggerMode | SequentialMode;
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
            bool modeMatches = result.LogFileMode == (SystemLoggerMode | SequentialMode);
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

    private static byte[] Property(IntPtr record, string name)
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
            if (size == 0 || size > 32768) throw new InvalidDataException("TDH property size invalid");
            var bytes = new byte[size];
            code = TdhGetProperty(record, 0, IntPtr.Zero, 1, ref descriptor, size, bytes);
            if (code != 0) throw new Win32Exception((int)code, "TDH value " + name);
            return bytes;
        }
        finally { Marshal.FreeHGlobal(key); }
    }

    private static uint Property32(IntPtr record, string name)
    {
        byte[] bytes = Property(record, name);
        if (bytes.Length != 4) throw new InvalidDataException("TDH property width " + name);
        return BitConverter.ToUInt32(bytes, 0);
    }

    private static ulong PropertyKey(IntPtr record)
    {
        byte[] bytes = Property(record, "UniqueProcessKey");
        if (bytes.Length == 8) return BitConverter.ToUInt64(bytes, 0);
        if (bytes.Length == 4) return BitConverter.ToUInt32(bytes, 0);
        throw new InvalidDataException("TDH UniqueProcessKey width");
    }

    private static string TextProperty(IntPtr record, string name, bool unicode)
    {
        byte[] bytes = Property(record, name);
        string value = (unicode ? Encoding.Unicode : Encoding.Default).GetString(bytes).TrimEnd('\0');
        if (value.Length == 0 || value.IndexOf('\t') >= 0 || value.IndexOf('\n') >= 0 || value.Length > 4096)
            throw new InvalidDataException("TDH text property invalid: " + name);
        return value;
    }

    private static void OnEvent(IntPtr address)
    {
        if (DecodeError != null) return;
        try
        {
            if (++CallbackCount > 100000) throw new InvalidDataException("event callback cap reached");
            var record = (EventRecord)Marshal.PtrToStructure(address, typeof(EventRecord));
            if (record.Header.ProviderId != SystemTraceGuid && record.Header.ProviderId != ProcessGuid &&
                record.Header.ProviderId != ImageGuid) return;
            uint size = 0;
            uint code = TdhGetEventInformation(address, 0, IntPtr.Zero, IntPtr.Zero, ref size);
            if (code != InsufficientBuffer)
                throw new Win32Exception((int)code, "TDH event schema size");
            if (size < 32 || size > 65536)
                throw new InvalidDataException("TDH event schema size invalid");
            Guid eventGuid;
            IntPtr info = Marshal.AllocHGlobal((int)size);
            try
            {
                code = TdhGetEventInformation(address, 0, IntPtr.Zero, info, ref size);
                if (code != 0) throw new Win32Exception((int)code, "TDH event schema");
                var prefix = (TraceEventInfoPrefix)Marshal.PtrToStructure(info, typeof(TraceEventInfoPrefix));
                eventGuid = prefix.EventGuid;
            }
            finally { Marshal.FreeHGlobal(info); }
            byte opcode = record.Header.Descriptor.Opcode;
            if (eventGuid == ProcessGuid && (opcode == 3 || opcode == 4)) ProcessRundown++;
            if (eventGuid == ImageGuid && (opcode == 3 || opcode == 4)) ImageRundown++;
            if (eventGuid == ProcessGuid && (opcode == 1 || opcode == 2))
            {
                uint processId = Property32(address, "ProcessId");
                if (processId != RootPid && processId != ChildPid) return;
                uint parentId = Property32(address, "ParentId");
                ulong key = PropertyKey(address);
                if (key == 0) throw new InvalidDataException("empty process key");
                var keys = opcode == 1 ? StartKeys : EndKeys;
                if (keys.ContainsKey((int)processId)) throw new InvalidDataException("duplicate known process event");
                keys[(int)processId] = key;
                if (opcode == 1 && !String.Equals(TextProperty(address, "ImageFileName", false),
                    PinnedNode, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException("known PID started an unexpected image");
                KnownEvents.Add(new KnownEvent { Kind = opcode == 1 ? "process-start" : "process-end",
                    Pid = (int)processId, Parent = parentId, Key = key,
                    ExitStatus = opcode == 2 ? Property32(address, "ExitStatus") : 0,
                    Time = record.Header.TimeStamp });
            }
            else if (eventGuid == ImageGuid && opcode == 10)
            {
                uint processId = Property32(address, "ProcessId");
                if (processId != RootPid && processId != ChildPid) return;
                string image = TextProperty(address, "FileName", true);
                if (String.Equals(image, PinnedNode, StringComparison.OrdinalIgnoreCase))
                    KnownEvents.Add(new KnownEvent { Kind = "image-load", Pid = (int)processId,
                        Time = record.Header.TimeStamp });
                // A basename match only rejects a foreign Node image; it never establishes identity.
                else if (String.Equals(Path.GetFileName(image), "node.exe", StringComparison.OrdinalIgnoreCase))
                    throw new InvalidDataException("known PID loaded a foreign Node image");
            }
            // DCStart/DCEnd are rundown, never a process start/end or a live image load.
        }
        catch (Exception error) { DecodeError = error; }
    }

    private static void CommitKnownEvents()
    {
        KnownEvent rootStart = null, rootEnd = null, childStart = null, childEnd = null;
        int rootImages = 0, childImages = 0;
        foreach (KnownEvent item in KnownEvents)
        {
            if (item.Kind == "process-start" && item.Pid == RootPid) rootStart = item;
            if (item.Kind == "process-end" && item.Pid == RootPid) rootEnd = item;
            if (item.Kind == "process-start" && item.Pid == ChildPid) childStart = item;
            if (item.Kind == "process-end" && item.Pid == ChildPid) childEnd = item;
            if (item.Kind == "image-load" && item.Pid == RootPid) rootImages++;
            if (item.Kind == "image-load" && item.Pid == ChildPid) childImages++;
        }
        if (rootStart == null || rootEnd == null || childStart == null || childEnd == null ||
            rootImages != 1 || childImages != 1 ||
            rootStart.Key == 0 || childStart.Key == 0 || rootStart.Key != rootEnd.Key ||
            childStart.Key != childEnd.Key || rootStart.Key == childStart.Key ||
            childStart.Parent != RootPid || childEnd.Parent != RootPid ||
            rootStart.Parent != rootEnd.Parent || rootStart.ExitStatus != 0 ||
            rootEnd.ExitStatus != 0 || childEnd.ExitStatus != 0 ||
            rootStart.Time < RootCreated - 50000000L || rootStart.Time > RootCreated + 50000000L ||
            !(rootStart.Time < childStart.Time && childStart.Time < childEnd.Time &&
              childEnd.Time < rootEnd.Time))
            throw new InvalidDataException("known process identity or lifetime invalid");
        foreach (KnownEvent item in KnownEvents)
        {
            if (item.Kind != "image-load") continue;
            KnownEvent start = item.Pid == RootPid ? rootStart : childStart;
            KnownEvent end = item.Pid == RootPid ? rootEnd : childEnd;
            if (item.Time < start.Time || item.Time > end.Time)
                throw new InvalidDataException("known image outside process lifetime");
        }
        foreach (KnownEvent item in KnownEvents)
        {
            string process = item.Pid == RootPid ? "root" : "child";
            if (item.Kind == "image-load")
                SelectedEvents.Add("EVENT\timage-load\t" + item.Pid.ToString(CultureInfo.InvariantCulture) +
                    "\tpinned-node\t" + item.Time.ToString(CultureInfo.InvariantCulture));
            else
                SelectedEvents.Add(String.Join("\t", new[] { "EVENT", item.Kind,
                    item.Pid.ToString(CultureInfo.InvariantCulture),
                    item.Parent.ToString(CultureInfo.InvariantCulture), process,
                    item.Kind == "process-start" ? "pinned-node" : item.ExitStatus.ToString(CultureInfo.InvariantCulture),
                    item.Time.ToString(CultureInfo.InvariantCulture) }));
        }
    }

    private static string Quote(string value)
    {
        return "\"" + value.Replace("\\", "\\\\").Replace("\"", "\\\"") + "\"";
    }

    private static void RunFixture(string node, string evidence)
    {
        // No external credentials, shell, package load or ambient command-line collection.
        const string script = "const c=require('node:child_process').spawnSync(process.execPath,['-e','setTimeout(()=>{},250)'],{windowsHide:true,timeout:5000});if(c.error||c.status!==0||!c.pid)process.exit(2);process.stdout.write(String(c.pid));";
        var start = new ProcessStartInfo(node, "-e " + Quote(script));
        start.WorkingDirectory = evidence;
        start.UseShellExecute = false;
        start.CreateNoWindow = true;
        start.RedirectStandardOutput = true;
        start.RedirectStandardError = true;
        start.EnvironmentVariables.Clear();
        string windows = Environment.GetEnvironmentVariable("SystemRoot");
        if (String.IsNullOrEmpty(windows)) throw new InvalidOperationException("SystemRoot unavailable");
        start.EnvironmentVariables["SystemRoot"] = windows;
        start.EnvironmentVariables["WINDIR"] = windows;
        start.EnvironmentVariables["PATH"] = Path.Combine(windows, "System32") + ";" + windows;
        start.EnvironmentVariables["TEMP"] = evidence;
        start.EnvironmentVariables["TMP"] = evidence;
        Process process = Process.Start(start);
        RootProcess = process;
        if (process == null) throw new InvalidOperationException("Node fixture launch returned no process");
        RootPid = process.Id;
        FileTime created, exited, kernel, user;
        if (!GetProcessTimes(process.Handle, out created, out exited, out kernel, out user))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "GetProcessTimes");
        var path = new StringBuilder(32768);
        uint length = (uint)path.Capacity;
        if (!QueryFullProcessImageName(process.Handle, 0, path, ref length) || length == 0 ||
            length >= path.Capacity) throw new Win32Exception(Marshal.GetLastWin32Error(), "root image");
        if (!String.Equals(Path.GetFullPath(path.ToString()), Path.GetFullPath(node),
            StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("root handle image differs from pin");
        RootCreated = created.Ticks;
        Line("ROOT", RootPid, RootCreated, "pinned-node");
        if (!process.WaitForExit(10000))
        {
            process.Kill();
            if (!process.WaitForExit(2000)) throw new InvalidOperationException("root stop unobserved");
            throw new TimeoutException("Node fixture exceeded ten seconds");
        }
        string output = process.StandardOutput.ReadToEnd();
        string error = process.StandardError.ReadToEnd();
        if (process.ExitCode != 0 || error.Length != 0 || output.Length > 10 ||
            !Int32.TryParse(output, NumberStyles.None, CultureInfo.InvariantCulture, out ChildPid) ||
            ChildPid <= 0 || ChildPid == RootPid)
            throw new InvalidDataException("known Node child fixture failed");
        Line("CHILD", ChildPid);
    }

    public static int Run(string nodePath, string evidenceDir)
    {
        if (IntPtr.Size != 8 || Environment.OSVersion.Platform != PlatformID.Win32NT) return 2;
        string node = Path.GetFullPath(nodePath);
        PinnedNode = node;
        string evidence = Path.GetFullPath(evidenceDir);
        string receipt = Path.Combine(evidence, "native.tsv");
        string etl = Path.Combine(evidence, "trace.etl");
        Directory.CreateDirectory(evidence);
        if (!File.Exists(node) || File.Exists(etl) || File.Exists(receipt)) return 2;
        Guid guid = Guid.NewGuid();
        string name = "Codex factory ETW feasibility " + guid.ToString("N");
        ulong handle = 0;
        bool owned = false;
        bool stopped = false;
        int result = 4;
        var watch = Stopwatch.StartNew();
        try
        {
            CheckAbi();
            var identity = WindowsIdentity.GetCurrent();
            Line("TOKEN", identity.IsSystem ? "system" : new WindowsPrincipal(identity).IsInRole(WindowsBuiltInRole.Administrator)
                ? "administrator" : "other");
            Line("OS", Environment.OSVersion.VersionString.Replace('\t', ' '));
            IntPtr properties = PropertiesBuffer(guid, name, etl, true);
            try
            {
                uint code = StartTrace(out handle, name, properties);
                Line("API", "start", code);
                if (code != 0) throw new Win32Exception((int)code, "StartTraceW");
                owned = true;
            }
            finally { Marshal.FreeHGlobal(properties); }
            Query(handle, guid, name, etl, "readyQuery");
            Line("OWNERSHIP", guid.ToString("D"), name);
            Line("SESSION", SystemLoggerMode | SequentialMode, ProcessFlag | ImageFlag, 64);
            RunFixture(node, evidence);
            if (watch.ElapsedMilliseconds > MaxObservationMs)
                throw new TimeoutException("observation exceeded thirty seconds");
            Query(handle, guid, name, etl, "beforeStopQuery");
            result = 0;
        }
        catch (Exception error)
        {
            if (RootProcess != null)
            {
                try
                {
                    if (!RootProcess.HasExited)
                    {
                        RootProcess.Kill();
                        if (!RootProcess.WaitForExit(2000))
                            Failure("root-stop", "unobserved", 0);
                    }
                }
                catch (Exception stopError)
                {
                    Failure("root-stop", stopError);
                }
            }
            Failure("run", error);
            result = 4;
        }
        finally
        {
            if (owned)
            {
                try
                {
                    IntPtr properties = PropertiesBuffer(guid, name, etl, false);
                    try
                    {
                        uint code = ControlTrace(handle, name, properties, TraceStop);
                        Line("API", "stop", code);
                        stopped = code == 0;
                        if (stopped)
                        {
                            var final = (EventTraceProperties)Marshal.PtrToStructure(properties,
                                typeof(EventTraceProperties));
                            Line("STATS", final.EventsLost, final.LogBuffersLost, final.RealTimeBuffersLost);
                            if (final.EventsLost != 0 || final.LogBuffersLost != 0 || final.RealTimeBuffersLost != 0)
                            {
                                Failure("stop", "loss", 0);
                                result = 4;
                            }
                        }
                        else
                        {
                            Failure("stop", "native-api", code);
                            result = 4;
                        }
                    }
                    finally { Marshal.FreeHGlobal(properties); }
                }
                catch (Exception error) { Failure("stop", error); result = 4; }
            }
            if (stopped && File.Exists(etl))
            {
                long bytes = new FileInfo(etl).Length;
                Line("FILE", bytes);
                if (bytes <= 0 || bytes >= MaxEtlBytes)
                {
                    Failure("decode", "etl-cap-or-empty", 0);
                    result = 4;
                }
                else
                {
                    try
                    {
                        CallbackCount = 0; DecodeError = null;
                        CallbackRoot = OnEvent;
                        var logfile = new EventTraceLogfile();
                        logfile.LogFileName = etl;
                        logfile.ProcessTraceMode = EventRecordMode;
                        logfile.EventRecordCallback = Marshal.GetFunctionPointerForDelegate(CallbackRoot);
                        ulong reader = OpenTrace(ref logfile);
                        bool opened = reader != ulong.MaxValue;
                        int openCode = opened ? 0 : Marshal.GetLastWin32Error();
                        Line("API", "open", openCode);
                        if (!opened) throw new Win32Exception(openCode, "OpenTraceW failed");
                        try
                        {
                            uint code = ProcessTrace(new[] { reader }, 1, IntPtr.Zero, IntPtr.Zero);
                            Line("API", "process", code);
                            if (code != 0) throw new Win32Exception((int)code, "ProcessTrace");
                            if (DecodeError != null) throw new InvalidDataException("event decode failed", DecodeError);
                            foreach (int pid in new[] { RootPid, ChildPid })
                            {
                                ulong begin, end;
                                if (!StartKeys.TryGetValue(pid, out begin) ||
                                    !EndKeys.TryGetValue(pid, out end) || begin != end)
                                    throw new InvalidDataException("known process key missing or changed");
                            }
                            CommitKnownEvents();
                            Line("SCHEMA", "ProcessId:u32", "ParentId:u32", "UniqueProcessKey:pointer",
                                "ImageFileName:string", "ExitStatus:u32", "Image.ProcessId:u32",
                                "Image.FileName:string");
                            Line("RUNDOWN", ProcessRundown, ImageRundown);
                            Line("COUNTS", CallbackCount, SelectedEvents.Count);
                            // OpenTrace and ProcessTrace populate this documented final-file header.
                            Line("HEADER", logfile.LogfileHeader.EndTime, logfile.LogfileHeader.EventsLost,
                                logfile.LogfileHeader.BuffersLost);
                            if (logfile.LogfileHeader.EndTime <= 0 || logfile.LogfileHeader.EventsLost != 0 ||
                                logfile.LogfileHeader.BuffersLost != 0)
                                throw new InvalidDataException("final ETL header incomplete or lost events");
                        }
                        finally
                        {
                            uint close = CloseTrace(reader);
                            Line("API", "close", close);
                            if (close != 0)
                            {
                                Failure("decode", "native-api", close);
                                result = 4;
                            }
                        }
                        Receipt.AddRange(SelectedEvents);
                    }
                    catch (Exception error)
                    {
                        Failure("decode", error);
                        result = 4;
                    }
                }
            }
            if (stopped && !File.Exists(etl))
            {
                Failure("decode", "missing-etl", 0);
                result = 4;
            }
            if (watch.ElapsedMilliseconds > MaxObservationMs)
            {
                Failure("run", "timeout", 0);
                result = 4;
            }
            if (result == 0) Line("COMPLETE");
            try
            {
                if (!WriteReceipt(receipt)) result = 4;
            }
            finally { if (RootProcess != null) RootProcess.Dispose(); }
        }
        return result;
    }
}
