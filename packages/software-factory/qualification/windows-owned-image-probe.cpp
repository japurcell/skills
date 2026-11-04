// Disposable qualification controller. Never attach to an existing process.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include "windows-owned-image-shared.h"
#include <bcrypt.h>
#include <algorithm>
#include <array>
#include <cstdio>
#include <cstring>
#include <process.h>
#include <string>
#include <vector>

namespace
{
constexpr DWORD Cap = 262144;
bool closed = true;
unsigned ownedHandles = 0;
FILE* details = nullptr;

void Log(const char* operation, unsigned long long value)
{
    if (details) fprintf(details, "%s\t%llu\n", operation, value);
}
struct Handle
{
    HANDLE value = nullptr;
    Handle() = default;
    explicit Handle(HANDLE h) { Set(h); }
    Handle(const Handle&) = delete;
    Handle& operator=(const Handle&) = delete;
    ~Handle() { Close(); }
    bool Valid() const { return value && value != INVALID_HANDLE_VALUE; }
    void Set(HANDLE h) { Close(); value = h; if (Valid()) ownedHandles++; }
    void Close()
    {
        if (Valid()) { if (!CloseHandle(value)) closed = false; ownedHandles--; }
        value = nullptr;
    }
};
void Require(bool condition, const char* failure)
{
    if (!condition) { Log(failure, GetLastError()); throw failure; }
}
bool Is(const std::string& name, const char* value) { return name == value; }

// Fixed public vocabulary only. Never forward the private RESULT text or OS data.
const char* RefusalReason(const char* failure)
{
    const struct { const char* privateCode; const char* publicReason; } reasons[] = {
        { "none", "clear" }, { "event", "event-check" }, { "image-handle", "image-handle-check" },
        { "duplicate", "duplicate-check" }, { "query", "query-check" }, { "suspend", "suspend-check" },
        { "identity", "identity-check" }, { "continue", "continue-check" }, { "detach", "detach-check" },
        { "postcondition", "debugger-check" }, { "resume", "resume-check" }, { "stop", "requested-stop" },
        { "deadline", "deadline-reached" }, { "output-limit", "output-cap" }, { "crash", "child-crash" },
        { "owner-loss", "owner-interrupted" }, { "launch", "launch-check" }, { "marker", "marker-check" },
        { "exit", "exit-check" }, { "pipe", "pipe-check" }, { "handle", "handle-check" }, { "host", "host-check" }
    };
    for (const auto& reason : reasons) if (strcmp(failure, reason.privateCode) == 0) return reason.publicReason;
    return "unknown";
}

struct Pipe
{
    Handle read, write;
    DWORD bytes = 0;
    bool eof = false;
    bool valid = true;
    std::array<char, 3> prefix{};
    void Create()
    {
        SECURITY_ATTRIBUTES attributes = { sizeof(attributes), nullptr, TRUE };
        HANDLE r = nullptr, w = nullptr;
        Require(CreatePipe(&r, &w, &attributes, 4096) != FALSE, "pipe");
        read.Set(r); write.Set(w);
        Require(SetHandleInformation(r, HANDLE_FLAG_INHERIT, 0) != FALSE, "pipe");
    }
    void Drain()
    {
        if (eof || !read.Valid()) return;
        for (unsigned reads = 0; reads < 128; reads++)
        {
            DWORD available = 0;
            if (!PeekNamedPipe(read.value, nullptr, 0, nullptr, &available, nullptr))
            {
                if (GetLastError() == ERROR_BROKEN_PIPE) eof = true; else valid = false;
                return;
            }
            if (!available) return;
            char buffer[4096]; DWORD count = 0;
            if (!ReadFile(read.value, buffer, std::min<DWORD>(available, static_cast<DWORD>(sizeof(buffer))), &count, nullptr))
            { if (GetLastError() == ERROR_BROKEN_PIPE) eof = true; else valid = false; return; }
            for (DWORD i = 0; i < count && bytes + i < prefix.size(); i++) prefix[bytes + i] = buffer[i];
            if (bytes > 1048576 - count) { valid = false; return; }
            bytes += count;
            if (bytes > Cap) return;
        }
    }
};

struct Child
{
    Handle process, thread, mapping, input, pin, actual;
    Pipe output, error;
    CanaryMarkers* markers = nullptr;
    DWORD pid = 0, tid = 0;
    bool attached = false, pending = false, debugExited = false;
    DEBUG_EVENT event{};
    HANDLE debugProcess = nullptr, debugThread = nullptr;
    ~Child() { if (markers && !UnmapViewOfFile(markers)) closed = false; }
    DWORD MarkerBits() const
    {
        return markers ? (markers->dll ? 1u : 0u) | (markers->tls ? 2u : 0u) |
            (markers->entry ? 4u : 0u) | (markers->early ? 8u : 0u) : 16u;
    }
    void Create(const std::wstring& application, const std::wstring& cwd, bool debug, LONG mode)
    {
        SECURITY_ATTRIBUTES attributes = { sizeof(attributes), nullptr, TRUE };
        mapping.Set(CreateFileMappingW(INVALID_HANDLE_VALUE, &attributes, PAGE_READWRITE, 0, sizeof(CanaryMarkers), nullptr));
        Require(mapping.Valid(), "launch");
        markers = static_cast<CanaryMarkers*>(MapViewOfFile(mapping.value, FILE_MAP_ALL_ACCESS, 0, 0, sizeof(CanaryMarkers)));
        Require(markers != nullptr, "launch");
        ZeroMemory(markers, sizeof(*markers)); markers->mode = mode;
        // The separately owned survival control is intentionally permitted now.
        markers->permission = debug ? 0 : 1;
        output.Create(); error.Create();
        input.Set(CreateFileW(L"NUL", GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE, &attributes, OPEN_EXISTING, 0, nullptr));
        Require(input.Valid(), "launch");
        HANDLE inherited[] = { mapping.value, output.write.value, error.write.value, input.value };
        SIZE_T size = 0;
        InitializeProcThreadAttributeList(nullptr, 1, 0, &size);
        Require(size > 0 && size < 65536, "launch");
        std::vector<unsigned char> storage(size);
        auto list = reinterpret_cast<LPPROC_THREAD_ATTRIBUTE_LIST>(storage.data());
        Require(InitializeProcThreadAttributeList(list, 1, 0, &size) != FALSE, "launch");
        bool updated = UpdateProcThreadAttribute(list, 0, PROC_THREAD_ATTRIBUTE_HANDLE_LIST, inherited, sizeof(inherited), nullptr, nullptr) != FALSE;
        if (!updated) { DeleteProcThreadAttributeList(list); throw "launch"; }
        STARTUPINFOEXW startup{};
        startup.StartupInfo.cb = sizeof(startup);
        startup.StartupInfo.dwFlags = STARTF_USESTDHANDLES;
        startup.StartupInfo.hStdInput = input.value;
        startup.StartupInfo.hStdOutput = output.write.value;
        startup.StartupInfo.hStdError = error.write.value;
        startup.lpAttributeList = list;
        wchar_t windows[MAX_PATH];
        DWORD length = GetWindowsDirectoryW(windows, MAX_PATH);
        Require(length > 0 && length < MAX_PATH, "host");
        std::wstring environment = L"FACTORY_CANARY_MAP=" + std::to_wstring(reinterpret_cast<ULONG_PTR>(mapping.value));
        environment.push_back(0); environment += L"SystemRoot="; environment += windows;
        environment.push_back(0); environment.push_back(0);
        std::wstring command = L"\"" + application + L"\"";
        PROCESS_INFORMATION information{};
        BOOL ok = CreateProcessW(application.c_str(), &command[0], nullptr, nullptr, TRUE,
            EXTENDED_STARTUPINFO_PRESENT | CREATE_UNICODE_ENVIRONMENT | CREATE_NO_WINDOW | (debug ? DEBUG_ONLY_THIS_PROCESS : 0),
            &environment[0], cwd.c_str(), &startup.StartupInfo, &information);
        DWORD creationError = GetLastError();
        DeleteProcThreadAttributeList(list);
        Require(ok != FALSE, "launch");
        Log("create-error", creationError);
        process.Set(information.hProcess); thread.Set(information.hThread);
        pid = information.dwProcessId; tid = information.dwThreadId; attached = debug;
        Log("owned-pid", pid); Log("owned-tid", tid);
        output.write.Close(); error.write.Close(); input.Close();
    }
    void CloseDebugHandles()
    {
        // Detach may retire OS-managed event handles. No intervening handle opens.
        for (HANDLE h : { debugThread, debugProcess })
        {
            if (!h || h == process.value || h == thread.value) continue;
            DWORD flags = 0;
            if (GetHandleInformation(h, &flags))
            {
                bool exact = h == debugThread ? GetThreadId(h) == tid : GetProcessId(h) == pid;
                if (!exact || !CloseHandle(h)) closed = false;
            }
            else if (GetLastError() != ERROR_INVALID_HANDLE) closed = false;
        }
        debugThread = nullptr; debugProcess = nullptr;
    }
    bool Stop()
    {
        if (!process.Valid()) return true;
        bool ok = true;
        DWORD wait = WaitForSingleObject(process.value, 0);
        if (wait == WAIT_TIMEOUT)
        {
            // Only the continuously held, newly created object is signaled.
            bool sent = TerminateProcess(process.value, 125) != FALSE;
            Log("terminate", sent ? 1 : GetLastError());
            if (!sent && WaitForSingleObject(process.value, 0) != WAIT_OBJECT_0) ok = false;
        }
        else if (wait != WAIT_OBJECT_0) ok = false;
        ULONGLONG deadline = GetTickCount64() + 2000;
        unsigned events = 0;
        if (attached)
        {
            while (!debugExited && GetTickCount64() < deadline && events++ < 64)
            {
                if (!pending)
                {
                    ZeroMemory(&event, sizeof(event));
                    if (!WaitForDebugEvent(&event, 20))
                    {
                        if (GetLastError() != ERROR_SEM_TIMEOUT) ok = false;
                        continue;
                    }
                    pending = true;
                }
                if (event.dwProcessId != pid) { ok = false; break; }
                if (event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT)
                {
                    debugProcess = event.u.CreateProcessInfo.hProcess;
                    debugThread = event.u.CreateProcessInfo.hThread;
                    if (event.u.CreateProcessInfo.hFile && !CloseHandle(event.u.CreateProcessInfo.hFile)) ok = false;
                    event.u.CreateProcessInfo.hFile = nullptr;
                }
                if (event.dwDebugEventCode == LOAD_DLL_DEBUG_EVENT && event.u.LoadDll.hFile && !CloseHandle(event.u.LoadDll.hFile)) ok = false;
                bool exiting = event.dwDebugEventCode == EXIT_PROCESS_DEBUG_EVENT;
                // Termination has already been requested. Never resume a suspended thread.
                if (!ContinueDebugEvent(pid, event.dwThreadId,
                    event.dwDebugEventCode == EXCEPTION_DEBUG_EVENT ? DBG_EXCEPTION_NOT_HANDLED : DBG_CONTINUE))
                { ok = false; break; }
                pending = false;
                if (exiting) { debugExited = true; debugProcess = nullptr; debugThread = nullptr; }
            }
            if (!debugExited) ok = false;
        }
        if (WaitForSingleObject(process.value, 1000) != WAIT_OBJECT_0) ok = false;
        while (GetTickCount64() < deadline && (!output.eof || !error.eof))
        { output.Drain(); error.Drain(); Sleep(1); }
        if (!output.eof || !error.eof || !output.valid || !error.valid) ok = false;
        if (!attached) CloseDebugHandles();
        return ok;
    }
    void Release()
    {
        process.Close(); thread.Close(); output.read.Close(); output.write.Close(); error.read.Close(); error.write.Close();
        input.Close();
        if (markers) { if (!UnmapViewOfFile(markers)) closed = false; markers = nullptr; }
        mapping.Close(); pin.Close(); actual.Close();
    }
};

struct Identity
{
    FILE_ID_INFO id{};
    std::array<unsigned char, 32> hash{};
};
Identity Identify(HANDLE file)
{
    Identity identity;
    Require(GetFileInformationByHandleEx(file, FileIdInfo, &identity.id, sizeof(identity.id)) != FALSE, "query");
    LARGE_INTEGER length{}, zero{};
    Require(GetFileSizeEx(file, &length) && length.QuadPart > 0 && length.QuadPart <= 16777216 &&
        SetFilePointerEx(file, zero, nullptr, FILE_BEGIN), "query");
    BCRYPT_ALG_HANDLE algorithm = nullptr;
    BCRYPT_HASH_HANDLE hash = nullptr;
    NTSTATUS status = BCryptOpenAlgorithmProvider(&algorithm, BCRYPT_SHA256_ALGORITHM, nullptr, 0);
    if (status < 0) throw "query";
    status = BCryptCreateHash(algorithm, &hash, nullptr, 0, nullptr, 0, 0);
    if (status < 0) { BCryptCloseAlgorithmProvider(algorithm, 0); throw "query"; }
    bool ok = true;
    LONGLONG total = 0;
    unsigned char buffer[16384]; DWORD read = 0;
    while (total < length.QuadPart)
    {
        if (!ReadFile(file, buffer, static_cast<DWORD>(std::min<LONGLONG>(sizeof(buffer), length.QuadPart - total)), &read, nullptr) || !read)
        { ok = false; break; }
        total += read;
        if (BCryptHashData(hash, buffer, read, 0) < 0) { ok = false; break; }
    }
    if (BCryptFinishHash(hash, identity.hash.data(), static_cast<ULONG>(identity.hash.size()), 0) < 0) ok = false;
    if (BCryptDestroyHash(hash) < 0) closed = false;
    if (BCryptCloseAlgorithmProvider(algorithm, 0) < 0) closed = false;
    Require(ok, "query");
    Log("volume", identity.id.VolumeSerialNumber);
    if (details)
    {
        fputs("file-id\t", details);
        for (unsigned char byte : identity.id.FileId.Identifier) fprintf(details, "%02x", byte);
        fputs("\nsha256\t", details);
        for (unsigned char byte : identity.hash) fprintf(details, "%02x", byte);
        fputs("\n", details);
    }
    return identity;
}

void Barrier(Child& child, const char* phase, const std::string& name)
{
    Sleep(25);
    child.output.Drain(); child.error.Drain();
    DWORD bits = child.MarkerBits();
    printf("BARRIER\t%s\t%lu\n", phase, bits);
    Require(bits == 0 && child.output.bytes == 0 && child.error.bytes == 0, "marker");
    if (name == std::string("stop-") + phase) throw "stop";
}

void Probe(Child& child, const std::wstring& root, const std::string& name)
{
    Handle& pin = child.pin;
    Handle& actual = child.actual;
    bool replacement = Is(name, "path-replacement") || Is(name, "ancestor-replacement") || Is(name, "alias-replacement");
    std::wstring fixtureRoot = replacement ? root + L"\\" + std::wstring(name.begin(), name.end()) + L"\\fixture" : root + L"\\fixture";
    const std::wstring executable = fixtureRoot + L"\\canary.exe";
    if (Is(name, "alias-replacement"))
        Require(CreateHardLinkW(executable.c_str(), (fixtureRoot + L"\\pin.exe").c_str(), nullptr) != FALSE, "host");
    const std::wstring expected = Is(name, "alias-replacement") ? fixtureRoot + L"\\pin.exe" : replacement ? executable : root + (Is(name, "different-file-id") ? L"\\copy\\canary.exe" :
        Is(name, "different-image") ? L"\\alternate\\canary.exe" : L"\\fixture\\canary.exe");
    pin.Set(CreateFileW(expected.c_str(), GENERIC_READ, FILE_SHARE_READ, nullptr, OPEN_EXISTING, FILE_FLAG_SEQUENTIAL_SCAN, nullptr));
    Require(pin.Valid(), "identity");
    Identity expectedIdentity = Identify(pin.value);
    if (Is(name, "wrong-hash")) expectedIdentity.hash[0] ^= 1;
    if (replacement)
    {
        bool ancestor = Is(name, "ancestor-replacement");
        std::wstring from = ancestor ? fixtureRoot : executable;
        std::wstring to = from + L".held";
        BOOL moved = MoveFileExW(from.c_str(), to.c_str(), 0);
        DWORD moveError = GetLastError(); Log("replacement-move", moved ? 0 : moveError);
        if (moved)
        {
            if (ancestor) Require(CreateDirectoryW(fixtureRoot.c_str(), nullptr) != FALSE, "host");
            Require(CopyFileW((root + L"\\alternate\\canary.exe").c_str(), executable.c_str(), TRUE) != FALSE, "host");
            if (ancestor) Require(CopyFileW((root + L"\\fixture\\canary.dll").c_str(), (fixtureRoot + L"\\canary.dll").c_str(), TRUE) != FALSE, "host");
        }
        else Require(moveError == ERROR_ACCESS_DENIED || moveError == ERROR_SHARING_VIOLATION || moveError == ERROR_LOCK_VIOLATION, "host");
        printf("MUTATION\t%s\t%s\n", ancestor ? "ancestor" : Is(name, "alias-replacement") ? "alias" : "file", moved ? "replaced" : "blocked");
    }
    LONG mode = Is(name, "deadline") ? 1 : Is(name, "output-limit") ? 2 : Is(name, "crash") ? 3 : 0;
    // Stop immediately after the one resume uses a waiting fixture to avoid races.
    if (Is(name, "stop-resume")) mode = 1;
    child.Create(executable, fixtureRoot, true, mode);
    if (Is(name, "fail-event")) throw "event";
    Require(WaitForDebugEvent(&child.event, 1000) != FALSE, "event"); child.pending = true;
    Require(child.event.dwProcessId == child.pid && child.event.dwThreadId == child.tid &&
        child.event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT, "event");
    auto& info = child.event.u.CreateProcessInfo;
    child.debugProcess = info.hProcess; child.debugThread = info.hThread;
    Require(GetProcessId(info.hProcess) == child.pid && GetThreadId(info.hThread) == child.tid &&
        GetProcessIdOfThread(info.hThread) == child.pid, "event");
    printf("FIRST\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\t%lu\n", child.pid, child.tid,
        child.event.dwProcessId, child.event.dwThreadId, child.event.dwDebugEventCode,
        GetProcessId(info.hProcess), GetThreadId(info.hThread));
    Barrier(child, "created", name);
    if (Is(name, "fail-suspend")) throw "suspend";
    DWORD previous = SuspendThread(child.thread.value);
    Log("suspend-return", previous); printf("SUSPEND\t%lu\n", previous);
    Require(previous == 0, "suspend");
    Barrier(child, "suspended", name);
    if (Is(name, "fail-image-handle")) throw "image-handle";
    Require(info.hFile && info.hFile != INVALID_HANDLE_VALUE, "image-handle");
    if (Is(name, "fail-duplicate")) throw "duplicate";
    HANDLE duplicate = nullptr;
    Require(DuplicateHandle(GetCurrentProcess(), info.hFile, GetCurrentProcess(), &duplicate, 0, FALSE, DUPLICATE_SAME_ACCESS) != FALSE, "duplicate");
    actual.Set(duplicate);
    Require(CloseHandle(info.hFile) != FALSE, "handle"); info.hFile = nullptr;
    if (Is(name, "fail-query")) throw "query";
    Identity identity = Identify(actual.value);
    bool idMatch = identity.id.VolumeSerialNumber == expectedIdentity.id.VolumeSerialNumber &&
        memcmp(identity.id.FileId.Identifier, expectedIdentity.id.FileId.Identifier, 16) == 0;
    bool hashMatch = identity.hash == expectedIdentity.hash;
    printf("IDENTITY\t%llu\t", identity.id.VolumeSerialNumber);
    for (unsigned char byte : identity.id.FileId.Identifier) printf("%02x", byte);
    printf("\t"); for (unsigned char byte : identity.hash) printf("%02x", byte);
    printf("\t%llu\t", expectedIdentity.id.VolumeSerialNumber);
    for (unsigned char byte : expectedIdentity.id.FileId.Identifier) printf("%02x", byte);
    printf("\t"); for (unsigned char byte : expectedIdentity.hash) printf("%02x", byte);
    printf("\n");
    Require(idMatch && hashMatch, "identity");
    Barrier(child, "validated", name);
    if (Is(name, "fail-continue")) throw "continue";
    Require(ContinueDebugEvent(child.pid, child.tid, DBG_CONTINUE) != FALSE, "continue"); child.pending = false;
    printf("CONTINUE\t1\n");
    Barrier(child, "continued", name);
    if (Is(name, "fail-detach")) throw "detach";
    Require(GetProcessId(child.process.value) == child.pid && WaitForSingleObject(child.process.value, 0) == WAIT_TIMEOUT, "detach");
    Require(DebugActiveProcessStop(child.pid) != FALSE, "detach"); child.attached = false;
    printf("DETACH\t1\n");
    child.CloseDebugHandles();
    if (Is(name, "fail-postcondition")) throw "postcondition";
    BOOL debugging = TRUE;
    Require(CheckRemoteDebuggerPresent(child.process.value, &debugging) != FALSE, "postcondition");
    printf("DEBUGGER\t%d\n", debugging ? 1 : 0);
    Require(debugging == FALSE, "postcondition");
    Barrier(child, "detached", name);
    if (Is(name, "fail-resume")) throw "resume";
    InterlockedExchange(&child.markers->permission, 1);
    previous = ResumeThread(child.thread.value);
    Log("resume-return", previous); printf("RESUME\t%lu\n", previous);
    Require(previous == 1, "resume");
    if (Is(name, "stop-resume")) throw "stop";
    ULONGLONG deadline = GetTickCount64() + (Is(name, "deadline") ? 500 : 1500);
    for (;;)
    {
        child.output.Drain(); child.error.Drain();
        Require(child.output.valid && child.error.valid, "pipe");
        if (child.output.bytes + child.error.bytes > Cap) throw "output-limit";
        DWORD status = WaitForSingleObject(child.process.value, 0);
        Require(status == WAIT_OBJECT_0 || status == WAIT_TIMEOUT, "exit");
        if (status == WAIT_OBJECT_0) break;
        if (GetTickCount64() >= deadline) throw "deadline";
        Sleep(1);
    }
    DWORD exit = 0;
    Require(GetExitCodeProcess(child.process.value, &exit) != FALSE, "exit");
    if (exit != 0) throw "crash";
}

struct OwnerLoss
{
    Child* child;
    const std::wstring* root;
    bool reached = false;
};
unsigned __stdcall LoseDebuggerThread(void* argument)
{
    OwnerLoss* state = static_cast<OwnerLoss*>(argument);
    try { Probe(*state->child, *state->root, "stop-created"); }
    catch (const char* failure) { state->reached = strcmp(failure, "stop") == 0; }
    catch (...) { state->reached = false; }
    if (state->child->pending && state->child->event.dwDebugEventCode == CREATE_PROCESS_DEBUG_EVENT)
    {
        HANDLE file = state->child->event.u.CreateProcessInfo.hFile;
        if (file && !CloseHandle(file)) closed = false;
        state->child->event.u.CreateProcessInfo.hFile = nullptr;
    }
    // Intentionally leave the first event uncontinued. The documented default
    // kills this newly created debuggee when its owning debugger thread exits.
    return 0;
}
}

int wmain(int argc, wchar_t** argv)
{
    if (argc != 4 || sizeof(void*) != 8) return 2;
    std::string name;
    for (const wchar_t* c = argv[2]; *c; c++) { if (*c > 127) return 2; name += static_cast<char>(*c); }
    const char* allowed[] = { "positive", "positive-repeat", "positive-repeat-2", "positive-repeat-3", "positive-repeat-4",
        "positive-repeat-5", "positive-repeat-6", "positive-repeat-7", "positive-repeat-8",
        "wrong-hash", "different-file-id", "different-image", "path-replacement", "ancestor-replacement", "alias-replacement",
        "stop-created", "stop-suspended", "stop-validated", "stop-continued", "stop-detached", "stop-resume",
        "fail-event", "fail-image-handle", "fail-duplicate", "fail-query", "fail-suspend", "fail-continue",
        "fail-detach", "fail-postcondition", "fail-resume", "deadline", "output-limit", "crash", "owner-interruption" };
    bool found = false; for (const char* item : allowed) if (name == item) found = true;
    if (!found) return 2;
    SetErrorMode(SEM_FAILCRITICALERRORS | SEM_NOGPFAULTERRORBOX | SEM_NOOPENFILEERRORBOX);
    if (_wfopen_s(&details, argv[3], L"wx") || !details) return 2;
    // Warm CNG before measuring handle closure; its provider cache is process-local.
    BCRYPT_ALG_HANDLE warm = nullptr;
    if (BCryptOpenAlgorithmProvider(&warm, BCRYPT_SHA256_ALGORITHM, nullptr, 0) < 0) return 2;
    if (BCryptCloseAlgorithmProvider(warm, 0) < 0) return 2;
    DWORD before = 0, after = 0;
    if (!GetProcessHandleCount(GetCurrentProcess(), &before)) return 2;
    ULONGLONG start = GetTickCount64();
    Child child, control;
    const char* failure = "none";
    const char* failurePhase = "survival-create";
    bool cleanup = true, survival = false, controlStopped = false;
    printf("OWNED\t1\t%s\n", name.c_str());
    try
    {
        control.Create(std::wstring(argv[1]) + L"\\fixture\\canary.exe", std::wstring(argv[1]) + L"\\fixture", false, 1);
        failurePhase = "survival-ready";
        ULONGLONG ready = GetTickCount64() + 1000;
        while (control.MarkerBits() != 7 && GetTickCount64() < ready) Sleep(1);
        Require(control.MarkerBits() == 7 && control.markers->debugger == 0, "host");
        if (Is(name, "owner-interruption"))
        {
            failurePhase = "owner-interruption";
            std::wstring root = argv[1];
            OwnerLoss state{ &child, &root };
            Handle owner(reinterpret_cast<HANDLE>(_beginthreadex(nullptr, 0, LoseDebuggerThread, &state, 0, nullptr)));
            Require(owner.Valid(), "host");
            // No debug calls occur on this observer thread.
            // Do not unwind state still referenced by a live debugger thread.
            if (WaitForSingleObject(owner.value, 4000) != WAIT_OBJECT_0) ExitProcess(2);
            bool terminated = child.process.Valid() && WaitForSingleObject(child.process.value, 1000) == WAIT_OBJECT_0;
            child.attached = false; child.pending = false;
            child.debugProcess = nullptr; child.debugThread = nullptr;
            Require(state.reached && terminated && child.MarkerBits() == 0, "host");
            failure = "owner-loss";
        }
        else
        {
            failurePhase = "probe";
            Probe(child, argv[1], name);
            failurePhase = "none";
        }
    }
    catch (const char* code) { failure = code; }
    catch (...) { failure = "host"; }
    // Every cleanup attempt runs independently and cannot erase the first failure.
    cleanup = child.Stop();
    if (child.process.Valid())
    {
        if (child.MarkerBits() == 7 && child.markers->early == 0 &&
            !Is(name, "stop-resume"))
            printf("MARKERS\t%ld\t%ld\t%ld\t%ld\n", child.markers->dll, child.markers->tls, child.markers->entry, child.markers->debugger);
        DWORD code = 0;
        if (GetExitCodeProcess(child.process.value, &code) && code != STILL_ACTIVE) printf("EXIT\t%lu\n", code);
        else cleanup = false;
    }
    printf("OUTPUT\t%lu\t%lu\t%d\t%d\n", child.output.bytes, child.error.bytes, child.output.eof ? 1 : 0, child.error.eof ? 1 : 0);
    survival = control.process.Valid() && WaitForSingleObject(control.process.value, 0) == WAIT_TIMEOUT && control.MarkerBits() == 7;
    controlStopped = control.Stop();
    cleanup = cleanup && controlStopped;
    printf("CONTROL\t%d\t%d\n", survival ? 1 : 0, controlStopped ? 1 : 0);
    if (child.markers && child.markers->early != 0) cleanup = false;
    // Even rejected pre-resume paths must retain an empty shared marker mapping.
    if (!Is(name, "stop-resume") && Is(failure, "none") == false &&
        !Is(failure, "deadline") && !Is(failure, "output-limit") && !Is(failure, "crash") &&
        child.markers && child.MarkerBits() != 0) cleanup = false;
    if (Is(failure, "none") && (child.output.prefix != std::array<char, 3>{ 'O', 'K', '\n' }))
    { failure = "pipe"; failurePhase = "output-check"; }
    child.Release(); control.Release();
    if (!GetProcessHandleCount(GetCurrentProcess(), &after)) closed = false;
    Log("handles-before", before); Log("handles-after", after);
    unsigned leaked = ownedHandles + (after > before ? after - before : 0);
    cleanup = cleanup && closed && leaked == 0;
    printf("CLEANUP\t%d\t%u\n", cleanup ? 1 : 0, cleanup ? 0 : 1);
    printf("HANDLES\t%u\nELAPSED\t%llu\nRESULT\t%s\nCOMPLETE\n", leaked, GetTickCount64() - start, failure);
    bool flushed = fflush(details) == 0;
    bool fileClosed = fclose(details) == 0; details = nullptr;
    if (!(cleanup && survival && flushed && fileClosed))
        fprintf(stderr, "OWNED_IMAGE_REFUSAL\t1\t%s\t%s\t%s\t%d\t%d\t%d\t%d\n", name.c_str(),
            failurePhase, RefusalReason(failure), cleanup ? 1 : 0, survival ? 1 : 0, flushed ? 1 : 0, fileClosed ? 1 : 0);
    return cleanup && survival && flushed && fileClosed ? 0 : 1;
}
