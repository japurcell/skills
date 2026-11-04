#include "windows-owned-image-shared.h"

extern "C" __declspec(dllexport) int FixtureImport()
{
#ifdef FACTORY_ALTERNATE
    return 2;
#else
    return 1;
#endif
}

BOOL WINAPI DllMain(HINSTANCE, DWORD reason, LPVOID)
{
    if (reason == DLL_PROCESS_ATTACH)
    {
        CanaryMarkers* markers = OpenMarkers();
        if (!markers) return FALSE;
        Mark(&markers->dll, markers);
        UnmapViewOfFile(markers);
    }
    return TRUE;
}
