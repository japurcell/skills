// Disposable Windows x64 ETW feasibility probe. Only a bounded typed receipt is CI evidence.
// ABI declarations follow Microsoft evntrace.h, evntcons.h, wmistr.h and tdh.h documentation.
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Diagnostics;
using System.Globalization;
using System.IO;
using System.Runtime.InteropServices;
using System.Security.Cryptography;
using System.Security.Principal;
using System.Text;
using System.Threading.Tasks;

public static class WindowsEtwProbe
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
    [DllImport("kernel32.dll", EntryPoint = "OpenProcess", SetLastError = true)]
    private static extern IntPtr OpenProcess(uint access, bool inherit, uint processId);
    [DllImport("kernel32.dll", EntryPoint = "GetProcessId", SetLastError = true)]
    private static extern uint GetProcessId(IntPtr process);
    [DllImport("kernel32.dll", EntryPoint = "GetExitCodeProcess", SetLastError = true)]
    private static extern bool GetExitCodeProcess(IntPtr process, out uint code);
    [DllImport("kernel32.dll", EntryPoint = "WaitForSingleObject", SetLastError = true)]
    private static extern uint WaitForSingleObject(IntPtr handle, uint milliseconds);
    [DllImport("kernel32.dll", EntryPoint = "TerminateProcess", SetLastError = true)]
    private static extern bool TerminateProcess(IntPtr process, uint code);
    [DllImport("kernel32.dll", EntryPoint = "CloseHandle", SetLastError = true)]
    private static extern bool CloseHandle(IntPtr handle);
    [DllImport("kernel32.dll", EntryPoint = "GetFileInformationByHandleEx", SetLastError = true)]
    private static extern bool GetFileInformationByHandleEx(IntPtr file, uint infoClass,
        out FileIdInformation info, uint size);
    [DllImport("kernel32.dll", EntryPoint = "GetFinalPathNameByHandleW", CharSet = CharSet.Unicode,
        SetLastError = true)]
    private static extern uint GetFinalPathNameByHandle(IntPtr file, StringBuilder path, uint length,
        uint flags);
    [DllImport("kernel32.dll", EntryPoint = "CreateToolhelp32Snapshot", SetLastError = true)]
    private static extern IntPtr CreateToolhelp32Snapshot(uint flags, uint processId);
    [DllImport("kernel32.dll", EntryPoint = "Process32FirstW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool Process32First(IntPtr snapshot, ref ProcessEntry32 entry);
    [DllImport("kernel32.dll", EntryPoint = "Process32NextW", CharSet = CharSet.Unicode, SetLastError = true)]
    private static extern bool Process32Next(IntPtr snapshot, ref ProcessEntry32 entry);

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
    private static string DecodeDiagnostic;
    private static string PinnedNode;
    private static long RootCreated;
    private static long RootExited, ChildCreated, ChildExited;
    private static long ReleaseTime, RootExitObserved, ChildExitObserved;
    private static uint RootParent;
    private static string PinnedDosPath, PinnedNtPath;
    private static int RootPid, ChildPid;
    private static int CallbackCount;
    private static int ProcessRundown, ImageRundown;
    private static EventRecordCallback CallbackRoot;
    private static Process RootProcess;
    private static FileStream PinnedFile;
    private static FileIdInformation PinnedFileId;
    private static IntPtr ChildHandle;
    private static bool ChildOwned;
    private static string FixtureStep = "not-started";
    private static string ReadFixtureStep() { return FixtureStep; }
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

    private static InvalidDataException RejectDecode(string phase, string reason, string target)
    {
        if (DecodeDiagnostic == null) DecodeDiagnostic = String.Join("\t", new[] { "DIAG", phase, reason, target });
        return new InvalidDataException("event decode rejected");
    }

    private static bool IsWindowsName(string value)
    {
        if (String.IsNullOrEmpty(value) || value == "." || value == ".." ||
            value[value.Length - 1] == '.' || value[value.Length - 1] == ' ') return false;
        foreach (char c in value)
            if (c < ' ' || c == '\u007f' || c == '\\' || c == '/' || c == ':' ||
                c == '<' || c == '>' || c == '"' || c == '|' || c == '?' || c == '*') return false;
        return true;
    }

    private static bool HasWindowsSegments(string value, int start, int minimum, bool allowForwardSlash)
    {
        if (start >= value.Length) return false;
        string[] segments = value.Substring(start).Split(allowForwardSlash ? new[] { '\\', '/' } : new[] { '\\' });
        if (segments.Length < minimum) return false;
        foreach (string segment in segments) if (!IsWindowsName(segment)) return false;
        return true;
    }

    private static string ProcessImageForm(string image)
    {
        if (IsWindowsName(image)) return "name-only";
        if (image != null && image.Length >= 4 &&
            ((image[0] >= 'A' && image[0] <= 'Z') || (image[0] >= 'a' && image[0] <= 'z')) &&
            image[1] == ':' && (image[2] == '\\' || image[2] == '/') &&
            HasWindowsSegments(image, 3, 1, true))
            return "dos-absolute";
        if (image != null && image.StartsWith("\\Device\\", StringComparison.OrdinalIgnoreCase) &&
            HasWindowsSegments(image, 8, 2, false)) return "device-absolute";
        return "other";
    }

    private static string ProcessImageBasename(string image, string pinned)
    {
        if (image == null || pinned == null) return "different";
        int imageSeparator = Math.Max(image.LastIndexOf('\\'), image.LastIndexOf('/'));
        int pinnedSeparator = Math.Max(pinned.LastIndexOf('\\'), pinned.LastIndexOf('/'));
        return String.Equals(image.Substring(imageSeparator + 1), pinned.Substring(pinnedSeparator + 1),
            StringComparison.OrdinalIgnoreCase) ? "same" : "different";
    }

    private static string ProcessImageTime(string target, long eventTime, long rootCreated)
    {
        if (target != "root" || eventTime <= 0 || rootCreated <= 0) return "unknown";
        decimal delta = (decimal)eventTime - rootCreated;
        if (delta < -50000000m) return "before-creation-window";
        if (delta < 0) return "before-creation-within-window";
        return delta <= 50000000m ? "at-or-after-creation-within-window" : "after-creation-window";
    }

    private static InvalidDataException RejectProcessImageMismatch(string image, string target, long eventTime)
    {
        if (DecodeDiagnostic == null)
            DecodeDiagnostic = String.Join("\t", new[] { "DIAG", "callback", "process-image-mismatch", target,
                ProcessImageForm(image), ProcessImageBasename(image, PinnedNode),
                ProcessImageTime(target, eventTime, RootCreated) });
        return new InvalidDataException("event decode rejected");
    }

    private static void RecordDecodeFailure(Exception error)
    {
        if (DecodeDiagnostic != null) Receipt.Add(DecodeDiagnostic);
        Failure("decode", error);
    }

    private static bool RecordDecodeOutcome(Exception error, uint closeCode)
    {
        if (error != null)
        {
            RecordDecodeFailure(error);
            return false;
        }
        if (closeCode != 0)
        {
            Failure("decode", "native-api", closeCode);
            return false;
        }
        return true;
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

    private static void OnEvent(IntPtr address)
    {
        if (DecodeError != null) return;
        string target = "none";
        try
        {
            if (++CallbackCount > 100000) throw RejectDecode("callback", "callback-cap", target);
            var record = (EventRecord)Marshal.PtrToStructure(address, typeof(EventRecord));
            if (record.Header.ProviderId != SystemTraceGuid && record.Header.ProviderId != ProcessGuid &&
                record.Header.ProviderId != ImageGuid) return;
            uint size = 0;
            uint code = TdhGetEventInformation(address, 0, IntPtr.Zero, IntPtr.Zero, ref size);
            if (code != InsufficientBuffer)
                throw new Win32Exception((int)code, "TDH event schema size");
            if (size < 32 || size > 65536)
                throw RejectDecode("callback", "schema-size", target);
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
                uint processId = Property32(address, "ProcessId", target);
                if (processId != RootPid && processId != ChildPid) return;
                target = processId == RootPid ? "root" : "child";
                uint parentId = Property32(address, "ParentId", target);
                ulong key = PropertyKey(address, target);
                if (key == 0) throw RejectDecode("callback", "empty-key", target);
                var keys = opcode == 1 ? StartKeys : EndKeys;
                if (keys.ContainsKey((int)processId)) throw RejectDecode("callback", "duplicate-event", target);
                keys[(int)processId] = key;
                if (opcode == 1)
                {
                    string image = TextProperty(address, "ImageFileName", false, target);
                    // A process name supplies consistency only. Held handles and event
                    // keys/lifetimes establish identity before any EVENT is committed.
                    if (!(IsWindowsName(image) && ProcessImageBasename(image, PinnedNode) == "same") &&
                        !MatchesPinnedPath(image))
                        throw RejectProcessImageMismatch(image, target, record.Header.TimeStamp);
                }
                KnownEvents.Add(new KnownEvent { Kind = opcode == 1 ? "process-start" : "process-end",
                    Pid = (int)processId, Parent = parentId, Key = key,
                    ExitStatus = opcode == 2 ? Property32(address, "ExitStatus", target) : 0,
                    Time = record.Header.TimeStamp });
            }
            else if (eventGuid == ImageGuid && opcode == 10)
            {
                uint processId = Property32(address, "ProcessId", target);
                if (processId != RootPid && processId != ChildPid) return;
                target = processId == RootPid ? "root" : "child";
                string image = TextProperty(address, "FileName", true, target);
                if (MatchesPinnedPath(image))
                    KnownEvents.Add(new KnownEvent { Kind = "image-load", Pid = (int)processId,
                        Time = record.Header.TimeStamp });
                // A basename match only rejects a foreign Node image; it never establishes identity.
                else if (String.Equals(Path.GetFileName(image), "node.exe", StringComparison.OrdinalIgnoreCase))
                    throw RejectDecode("callback", "image-mismatch", target);
            }
            // DCStart/DCEnd are rundown, never a process start/end or a live image load.
        }
        catch (Exception error)
        {
            if (DecodeDiagnostic == null) DecodeDiagnostic = "DIAG\tcallback\tother\t" + target;
            DecodeError = error;
        }
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
        if (rootStart == null || rootEnd == null) throw RejectDecode("identity", "missing-event", "root");
        if (childStart == null || childEnd == null) throw RejectDecode("identity", "missing-event", "child");
        if (rootImages == 0) throw RejectDecode("identity", "missing-image", "root");
        if (childImages == 0) throw RejectDecode("identity", "missing-image", "child");
        if (rootImages != 1) throw RejectDecode("identity", "duplicate-image", "root");
        if (childImages != 1) throw RejectDecode("identity", "duplicate-image", "child");
        if (rootStart.Key == 0 || rootStart.Key != rootEnd.Key)
            throw RejectDecode("identity", "identity-key", "root");
        if (childStart.Key == 0 || childStart.Key != childEnd.Key)
            throw RejectDecode("identity", "identity-key", "child");
        if (rootStart.Key == childStart.Key) throw RejectDecode("identity", "identity-key", "none");
        if (childStart.Parent != RootPid || childEnd.Parent != RootPid)
            throw RejectDecode("identity", "parent-mismatch", "child");
        if (rootStart.Parent != RootParent || rootEnd.Parent != RootParent)
            throw RejectDecode("identity", "parent-mismatch", "root");
        if (rootStart.ExitStatus != 0 || rootEnd.ExitStatus != 0)
            throw RejectDecode("identity", "exit-status", "root");
        if (childEnd.ExitStatus != 0) throw RejectDecode("identity", "exit-status", "child");
        foreach (KnownEvent item in KnownEvents)
        {
            long created = item.Pid == RootPid ? RootCreated : ChildCreated;
            long exited = item.Pid == RootPid ? RootExited : ChildExited;
            long observed = item.Pid == RootPid ? RootExitObserved : ChildExitObserved;
            // Exit FILETIME is not the ETW End timestamp. Bound End by the
            // independently measured release-to-signaled interval, with both
            // process handles still held so their PIDs cannot be reused.
            long lower = item.Kind == "process-end" ? ReleaseTime : created;
            long upper = item.Kind == "process-end" ? observed : exited;
            if (!ChildOwned || PinnedFile == null || created <= 0 || exited <= created ||
                ReleaseTime < created || exited < ReleaseTime || observed < exited ||
                item.Time < lower || item.Time > upper)
            {
                if (DecodeDiagnostic == null)
                    DecodeDiagnostic = String.Join("\t", new[] { "DIAG", "identity", "held-time",
                        item.Pid == RootPid ? "root" : "child", item.Kind,
                        created <= 0 || exited <= created || !ChildOwned || PinnedFile == null ||
                            ReleaseTime < created || exited < ReleaseTime || observed < exited ? "unavailable" :
                        item.Time < lower ? (item.Kind == "process-end" ? "before-release" : "before-creation") :
                            (item.Kind == "process-end" ? "after-observation" : "after-exit") });
                throw new InvalidDataException("held event lifetime rejected");
            }
        }
        if (!(rootStart.Time < childStart.Time && childStart.Time < childEnd.Time &&
              childEnd.Time < rootEnd.Time)) throw RejectDecode("identity", "process-order", "none");
        // Reopen only the known local pin, never an event-controlled path.
        // The original read-only sharing handle remains held throughout decode.
        using (var pin = new FileStream(PinnedNode, FileMode.Open, FileAccess.Read, FileShare.Read))
            if (!SameFile(PinnedFileId, FileIdentity(pin.SafeFileHandle.DangerousGetHandle())))
                throw RejectDecode("callback", "image-mismatch", "none");
        foreach (KnownEvent item in KnownEvents)
        {
            if (item.Kind != "image-load") continue;
            KnownEvent start = item.Pid == RootPid ? rootStart : childStart;
            KnownEvent end = item.Pid == RootPid ? rootEnd : childEnd;
            if (item.Time < start.Time || item.Time > end.Time)
                throw RejectDecode("identity", "image-lifetime", item.Pid == RootPid ? "root" : "child");
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

    private static string FinalPinnedPath(uint volumeForm)
    {
        var path = new StringBuilder(32768);
        uint length = GetFinalPathNameByHandle(PinnedFile.SafeFileHandle.DangerousGetHandle(), path,
            (uint)path.Capacity, volumeForm);
        if (length == 0 || length >= path.Capacity)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "held file path unavailable");
        return path.ToString();
    }

    private static bool MatchesPinnedPath(string path)
    {
        return !String.IsNullOrEmpty(path) &&
            (String.Equals(path, PinnedDosPath, StringComparison.OrdinalIgnoreCase) ||
             String.Equals(path, PinnedNtPath, StringComparison.OrdinalIgnoreCase));
    }

    private static void HoldPinnedFile(string node, string expectedDigest, Stopwatch watch)
    {
        if (expectedDigest == null || expectedDigest.Length != 64)
            throw new InvalidDataException("expected pin digest malformed");
        foreach (char c in expectedDigest)
            if (!((c >= '0' && c <= '9') || (c >= 'a' && c <= 'f')))
                throw new InvalidDataException("expected pin digest malformed");
        // Read sharing denies write and delete replacement until offline decode completes.
        PinnedFile = new FileStream(node, FileMode.Open, FileAccess.Read, FileShare.Read);
        if (PinnedFile.Length == 0) throw new InvalidDataException("pinned executable empty");
        using (var hash = SHA256.Create())
        {
            string actual = BitConverter.ToString(hash.ComputeHash(PinnedFile)).Replace("-", "").ToLowerInvariant();
            if (!String.Equals(actual, expectedDigest, StringComparison.Ordinal))
                throw new InvalidDataException("held executable digest differs from archive member");
        }
        PinnedFile.Position = 0;
        PinnedFileId = FileIdentity(PinnedFile.SafeFileHandle.DangerousGetHandle());
        // These complete spellings come from the held file, without prefix conversion.
        PinnedDosPath = FinalPinnedPath(0); // FILE_NAME_NORMALIZED | VOLUME_NAME_DOS
        PinnedNtPath = FinalPinnedPath(2); // FILE_NAME_NORMALIZED | VOLUME_NAME_NT
        Remaining(watch, MaxObservationMs);
    }

    private static void VerifyProcessImage(IntPtr process, string node)
    {
        var path = new StringBuilder(32768);
        uint length = (uint)path.Capacity;
        if (!QueryFullProcessImageName(process, 0, path, ref length) || length == 0 ||
            length >= path.Capacity) throw new Win32Exception(Marshal.GetLastWin32Error(), "process image");
        string image = Path.GetFullPath(path.ToString());
        if (!String.Equals(image, node, StringComparison.OrdinalIgnoreCase))
            throw new InvalidDataException("process handle image differs from pin");
        using (var candidate = new FileStream(image, FileMode.Open, FileAccess.Read, FileShare.Read))
            if (!SameFile(PinnedFileId, FileIdentity(candidate.SafeFileHandle.DangerousGetHandle())))
                throw new InvalidDataException("process image file identity differs from pin");
    }

    private static uint ParentFromSnapshot(uint childPid)
    {
        IntPtr snapshot = CreateToolhelp32Snapshot(SnapshotProcess, 0);
        if (snapshot == new IntPtr(-1))
            throw new Win32Exception(Marshal.GetLastWin32Error(), "process snapshot");
        try
        {
            var entry = new ProcessEntry32();
            entry.Size = (uint)Marshal.SizeOf(typeof(ProcessEntry32));
            if (!Process32First(snapshot, ref entry))
                throw new Win32Exception(Marshal.GetLastWin32Error(), "process snapshot first");
            do
            {
                if (entry.ProcessId == childPid) return entry.ParentProcessId;
                entry.Size = (uint)Marshal.SizeOf(typeof(ProcessEntry32));
            } while (Process32Next(snapshot, ref entry));
            throw new InvalidDataException("held child missing from process snapshot");
        }
        finally { if (!CloseHandle(snapshot)) throw new Win32Exception(Marshal.GetLastWin32Error(), "snapshot close"); }
    }

    private static int Remaining(Stopwatch watch, int localMaximum)
    {
        int left = MaxObservationMs - (int)watch.ElapsedMilliseconds;
        if (left <= 0) throw new TimeoutException("observation exceeded thirty seconds");
        return Math.Min(left, localMaximum);
    }

    private static int ReadChildPid(Process root, Stopwatch watch)
    {
        var digits = new StringBuilder(10);
        var one = new byte[1];
        long deadline = watch.ElapsedMilliseconds + 5000;
        for (int i = 0; i < 11; i++)
        {
            int left = (int)(deadline - watch.ElapsedMilliseconds);
            if (left <= 0) throw new TimeoutException("fixture PID line unavailable");
            Task<int> read = root.StandardOutput.BaseStream.ReadAsync(one, 0, 1);
            if (!read.Wait(Remaining(watch, left)) || read.Result != 1)
                throw new TimeoutException("fixture PID line unavailable");
            if (one[0] == '\n')
            {
                int pid;
                if (digits.Length == 0 || digits[0] == '0' ||
                    !Int32.TryParse(digits.ToString(), NumberStyles.None, CultureInfo.InvariantCulture, out pid) ||
                    pid <= 0) throw new InvalidDataException("fixture PID malformed");
                return pid;
            }
            if (one[0] < '0' || one[0] > '9' || digits.Length == 10)
                throw new InvalidDataException("fixture PID malformed");
            digits.Append((char)one[0]);
        }
        throw new InvalidDataException("fixture PID over cap");
    }

    private static void RunFixture(string node, string evidence, string fixture, Stopwatch watch)
    {
        FixtureStep = "start";
        // The fixed script reports a live child before receiving the single release byte.
        if (!File.Exists(fixture) || fixture.IndexOf('"') >= 0)
            throw new InvalidDataException("fixed fixture unavailable");
        var start = new ProcessStartInfo(node, "\"" + fixture + "\"");
        start.WorkingDirectory = evidence;
        start.UseShellExecute = false;
        start.CreateNoWindow = true;
        start.RedirectStandardInput = true;
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
        FixtureStep = "root-handle";
        // .NET Framework constructs and immediately flushes stdin using the
        // console encoding. Suppress its preamble without accepting extra bytes
        // in the fixed fixture protocol, then restore this isolated host.
        Encoding previousInput = Console.InputEncoding;
        bool inputChanged = false;
        try
        {
            Console.InputEncoding = new UTF8Encoding(false);
            inputChanged = true;
            RootProcess = Process.Start(start);
        }
        finally { if (inputChanged) Console.InputEncoding = previousInput; }
        if (RootProcess == null) throw new InvalidOperationException("Node fixture launch returned no process");
        RootPid = RootProcess.Id;
        if (GetProcessId(RootProcess.Handle) != (uint)RootPid || RootProcess.HasExited)
            throw new InvalidDataException("root process handle changed or exited");
        FixtureStep = "root-timing";
        FileTime rootCreated, rootExited, kernel, user;
        if (!GetProcessTimes(RootProcess.Handle, out rootCreated, out rootExited, out kernel, out user) ||
            rootCreated.Ticks <= 0)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "root process timing");
        FixtureStep = "root-image";
        VerifyProcessImage(RootProcess.Handle, node);
        RootCreated = rootCreated.Ticks;
        RootParent = ParentFromSnapshot((uint)RootPid);
        Line("ROOT", RootPid, RootCreated, "pinned-node");
        FixtureStep = "pid-line";
        int printedPid = ReadChildPid(RootProcess, watch);
        if (printedPid == RootPid || RootProcess.HasExited)
            throw new InvalidDataException("fixture child PID invalid");
        FixtureStep = "child-handle";
        ChildHandle = OpenProcess(ProcessQueryLimitedInformation | ProcessSynchronize | ProcessTerminate,
            false, (uint)printedPid);
        if (ChildHandle == IntPtr.Zero)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "held child open");
        if (GetProcessId(ChildHandle) != (uint)printedPid ||
            WaitForSingleObject(ChildHandle, 0) != WaitTimeout)
            throw new InvalidDataException("fixture child handle invalid or exited");
        FixtureStep = "child-timing";
        FileTime childCreated, childExited;
        if (!GetProcessTimes(ChildHandle, out childCreated, out childExited, out kernel, out user) ||
            childCreated.Ticks <= RootCreated)
            throw new InvalidDataException("fixture child timing invalid");
        FixtureStep = "child-image";
        VerifyProcessImage(ChildHandle, node);
        FixtureStep = "parent";
        if (RootProcess.HasExited || ParentFromSnapshot((uint)printedPid) != (uint)RootPid ||
            RootProcess.HasExited ||
            WaitForSingleObject(ChildHandle, 0) != WaitTimeout)
            throw new InvalidDataException("fixture child is not live child of held root");
        ChildPid = printedPid;
        ChildCreated = childCreated.Ticks;
        ChildOwned = true;
        FixtureStep = "release";
        FileTime precise;
        GetSystemTimePreciseAsFileTime(out precise);
        ReleaseTime = precise.Ticks;
        RootProcess.StandardInput.BaseStream.WriteByte(0x52);
        RootProcess.StandardInput.BaseStream.Flush();
        RootProcess.StandardInput.Close();
        FixtureStep = "child-wait";
        uint wait = WaitForSingleObject(ChildHandle, (uint)Remaining(watch, 15000));
        if (wait != WaitObject) throw new TimeoutException("held child exit unobserved");
        GetSystemTimePreciseAsFileTime(out precise);
        ChildExitObserved = precise.Ticks;
        FixtureStep = "root-wait";
        if (!RootProcess.WaitForExit(Remaining(watch, 15000)))
            throw new TimeoutException("root fixture exit unobserved");
        GetSystemTimePreciseAsFileTime(out precise);
        RootExitObserved = precise.Ticks;
        FixtureStep = "exit-output";
        uint childCode;
        if (!GetExitCodeProcess(ChildHandle, out childCode) || childCode != 0 || RootProcess.ExitCode != 0 ||
            !GetProcessTimes(ChildHandle, out childCreated, out childExited, out kernel, out user) ||
            childExited.Ticks <= childCreated.Ticks ||
            !GetProcessTimes(RootProcess.Handle, out rootCreated, out rootExited, out kernel, out user) ||
            rootExited.Ticks <= rootCreated.Ticks || childExited.Ticks > rootExited.Ticks ||
            RootProcess.StandardOutput.BaseStream.ReadByte() != -1 ||
            RootProcess.StandardError.BaseStream.ReadByte() != -1)
            throw new InvalidDataException("held fixture exit or output invalid");
        RootExited = rootExited.Ticks;
        ChildExited = childExited.Ticks;
        FixtureStep = "complete";
        Line("CHILD", ChildPid);
        Line("HELD", "root", 1, 1, 1);
        Line("HELD", "child", 1, 1, 1);
    }

    private static void StopRootFixture()
    {
        // The root was launched by this probe. A printed PID is never a termination authority.
        if (RootProcess != null && !RootProcess.HasExited)
        {
            try { RootProcess.StandardInput.Close(); }
            catch { }
            if (!RootProcess.WaitForExit(2000))
            {
                RootProcess.Kill();
                if (!RootProcess.WaitForExit(2000))
                    throw new TimeoutException("root stop unobserved");
            }
        }
    }

    private static void StopHeldChild()
    {
        // ChildOwned is granted only after live handle, pinned file and Toolhelp parent checks.
        if (!ChildOwned || ChildHandle == IntPtr.Zero) return;
        uint state = WaitForSingleObject(ChildHandle, 0);
        if (state == WaitObject) return;
        if (state != WaitTimeout)
            throw new Win32Exception(Marshal.GetLastWin32Error(), "held child wait");
        if (!TerminateProcess(ChildHandle, 2) ||
            WaitForSingleObject(ChildHandle, 2000) != WaitObject)
            throw new InvalidOperationException("held child stop unobserved");
    }

    private static bool AttemptBothStops(Action stopRoot, Action stopChild)
    {
        bool stopped = true;
        try { stopRoot(); }
        catch (Exception error) { Failure("root-stop", error); stopped = false; }
        try { stopChild(); }
        catch (Exception error) { Failure("child-stop", error); stopped = false; }
        return stopped;
    }

    private static bool StopFixture()
    {
        return AttemptBothStops(StopRootFixture, StopHeldChild);
    }

    private static bool CloseOwnedResources()
    {
        bool closed = true;
        try
        {
            if (ChildHandle != IntPtr.Zero)
            {
                if (CloseHandle(ChildHandle)) ChildHandle = IntPtr.Zero;
                else closed = false;
            }
        }
        catch { closed = false; }
        try { if (RootProcess != null) { RootProcess.Dispose(); RootProcess = null; } }
        catch { closed = false; }
        try { if (PinnedFile != null) { PinnedFile.Dispose(); PinnedFile = null; } }
        catch { closed = false; }
        return closed;
    }

    private static int FinishWithOwnedResources(Func<int> finish, string receipt)
    {
        int result = 4;
        try
        {
            try { result = finish(); }
            catch (Exception error) { Failure("decode", error); }
            if (!CloseOwnedResources()) { Failure("run", "operation-failed", 0); result = 4; }
            if (result == 0) Line("COMPLETE");
            try { if (!WriteReceipt(receipt)) result = 4; }
            catch { result = 4; }
            return result;
        }
        finally { CloseOwnedResources(); }
    }

    public static int Run(string nodePath, string evidenceDir, string expectedDigest, string fixturePath)
    {
        if (IntPtr.Size != 8 || Environment.OSVersion.Platform != PlatformID.Win32NT) return 2;
        string node = Path.GetFullPath(nodePath);
        PinnedNode = node;
        string fixture = Path.GetFullPath(fixturePath);
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
            HoldPinnedFile(node, expectedDigest, watch);
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
            Line("SESSION", RequestedMode, ProcessFlag | ImageFlag, 64);
            RunFixture(node, evidence, fixture, watch);
            if (watch.ElapsedMilliseconds > MaxObservationMs)
                throw new TimeoutException("observation exceeded thirty seconds");
            Query(handle, guid, name, etl, "beforeStopQuery");
            result = 0;
        }
        catch (Exception error)
        {
            Failure("run", error);
            StopFixture();
            result = 4;
        }
        finally
        {
            result = FinishWithOwnedResources(() =>
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
                        Exception decodeFailure = null;
                        uint closeCode = 0;
                        try
                        {
                            CallbackCount = 0; DecodeError = null; DecodeDiagnostic = null;
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
                                    string target = pid == RootPid ? "root" : "child";
                                    if (!StartKeys.TryGetValue(pid, out begin))
                                        throw RejectDecode("keys", "missing-start-key", target);
                                    if (!EndKeys.TryGetValue(pid, out end))
                                        throw RejectDecode("keys", "missing-end-key", target);
                                    if (begin != end) throw RejectDecode("keys", "changed-key", target);
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
                                closeCode = CloseTrace(reader);
                                Line("API", "close", closeCode);
                            }
                        }
                        catch (Exception error) { decodeFailure = error; }
                        if (RecordDecodeOutcome(decodeFailure, closeCode)) Receipt.AddRange(SelectedEvents);
                        else result = 4;
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
                return result;
            }, receipt);
        }
        return result;
    }
}
