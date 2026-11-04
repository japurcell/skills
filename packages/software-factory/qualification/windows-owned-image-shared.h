#pragma once
#include <windows.h>

// Disposable canary IPC only. These are observations, never process authority.
struct CanaryMarkers
{
    volatile LONG dll;
    volatile LONG tls;
    volatile LONG entry;
    volatile LONG debugger;
    volatile LONG mode;
    volatile LONG permission;
    volatile LONG early;
};

inline CanaryMarkers* OpenMarkers()
{
    wchar_t value[32] = {};
    DWORD count = GetEnvironmentVariableW(L"FACTORY_CANARY_MAP", value, 32);
    if (!count || count >= 32) return nullptr;
    ULONG_PTR handle = 0;
    for (DWORD i = 0; i < count; i++)
    {
        if (value[i] < L'0' || value[i] > L'9') return nullptr;
        ULONG_PTR next = handle * 10 + (value[i] - L'0');
        if (next < handle) return nullptr;
        handle = next;
    }
    return static_cast<CanaryMarkers*>(MapViewOfFile(reinterpret_cast<HANDLE>(handle), FILE_MAP_ALL_ACCESS, 0, 0, sizeof(CanaryMarkers)));
}

inline void Mark(volatile LONG* field, CanaryMarkers* markers)
{
    if (!markers) ExitProcess(91);
    if (InterlockedCompareExchange(&markers->permission, 0, 0) != 1) InterlockedExchange(&markers->early, 1);
    InterlockedExchange(field, 1);
}
