#include "windows-owned-image-shared.h"

extern "C" __declspec(dllimport) int FixtureImport();
void NTAPI CanaryTls(PVOID, DWORD reason, PVOID)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        CanaryMarkers* markers = OpenMarkers();
        if (!markers) ExitProcess(92);
        Mark(&markers->tls, markers);
        UnmapViewOfFile(markers);
    }
}
#pragma section(".CRT$XLB", long, read)
extern "C" __declspec(allocate(".CRT$XLB")) PIMAGE_TLS_CALLBACK factoryTls = CanaryTls;
#pragma comment(linker, "/INCLUDE:_tls_used")
#pragma comment(linker, "/INCLUDE:factoryTls")

int main()
{
    CanaryMarkers* markers = OpenMarkers();
    if (!markers) return 93;
    Mark(&markers->entry, markers);
    InterlockedExchange(&markers->debugger, IsDebuggerPresent() ? 1 : 0);
    if (FixtureImport() != 1) return 94;
#ifdef FACTORY_ALTERNATE
    // The separate image deliberately has different bytes, with the same name.
    InterlockedExchange(&markers->mode, 9);
#endif
    LONG mode = InterlockedCompareExchange(&markers->mode, 0, 0);
    // Owner-loss fallback is bounded even after a successful detach. It does
    // not supply a product owner-loss guarantee or prove external cleanup.
    ULONGLONG ownDeadline = GetTickCount64() + 8000;
    if (mode == 1) { while (GetTickCount64() < ownDeadline) Sleep(10); return 98; }
    if (mode == 3) { RaiseException(0xe0424242, EXCEPTION_NONCONTINUABLE, 0, nullptr); return 95; }
    DWORD written = 0;
    if (mode == 2)
    {
        char block[4096] = {};
        while (GetTickCount64() < ownDeadline)
            if (!WriteFile(GetStdHandle(STD_OUTPUT_HANDLE), block, sizeof(block), &written, nullptr)) return 96;
        return 98;
    }
    if (!WriteFile(GetStdHandle(STD_OUTPUT_HANDLE), "OK\n", 3, &written, nullptr) || written != 3) return 97;
    UnmapViewOfFile(markers);
    return 0;
}
