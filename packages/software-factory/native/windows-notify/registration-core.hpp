#pragma once
#include <windows.h>
#include <knownfolders.h>
#include <propkey.h>
#include <propidl.h>
#include <propvarutil.h>
#include <shlobj.h>
#include <shobjidl.h>
#include <wrl/client.h>
#include <winrt/Windows.Data.Xml.Dom.h>
#include <winrt/Windows.UI.Notifications.h>

#include <cwchar>
#include <functional>
#include <iterator>
#include <string>
#include <utility>
#include <vector>

using Microsoft::WRL::ComPtr;
using namespace winrt;
using namespace Windows::UI::Notifications;

namespace {
constexpr wchar_t kActivationArgument[] = L"activated";
constexpr DWORD kOwnerMagic = 0x53464E4F;

struct OwnerRecord {
  DWORD magic;
  DWORD version;
  DWORD volume;
  DWORD file_index_high;
  DWORD file_index_low;
  FILETIME created;
  wchar_t token[33];
};

class FileHandle {
 public:
  explicit FileHandle(HANDLE value = INVALID_HANDLE_VALUE) : value_(value) {}
  ~FileHandle() { if (value_ != INVALID_HANDLE_VALUE) CloseHandle(value_); }
  FileHandle(const FileHandle&) = delete;
  FileHandle& operator=(const FileHandle&) = delete;
  FileHandle(FileHandle&& other) noexcept : value_(other.value_) { other.value_ = INVALID_HANDLE_VALUE; }
  FileHandle& operator=(FileHandle&&) = delete;
  void close() { if (valid()) { CloseHandle(value_); value_ = INVALID_HANDLE_VALUE; } }
  HANDLE get() const { return value_; }
  bool valid() const { return value_ != INVALID_HANDLE_VALUE; }
 private:
  HANDLE value_;
};

void win32_check(bool success) {
  if (!success) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
}

bool missing(DWORD error) { return error == ERROR_FILE_NOT_FOUND || error == ERROR_PATH_NOT_FOUND; }

FileHandle open_file(const std::wstring& path, DWORD access, DWORD sharing) {
  FileHandle file(CreateFileW(path.c_str(), access, sharing, nullptr, OPEN_EXISTING,
                              FILE_FLAG_OPEN_REPARSE_POINT, nullptr));
  if (!file.valid()) return file;
  BY_HANDLE_FILE_INFORMATION info{};
  win32_check(GetFileInformationByHandle(file.get(), &info));
  if ((info.dwFileAttributes & (FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_REPARSE_POINT)) != 0) throw hresult_error(E_ACCESSDENIED);
  return file;
}

BY_HANDLE_FILE_INFORMATION identity(HANDLE file) {
  BY_HANDLE_FILE_INFORMATION info{};
  win32_check(GetFileInformationByHandle(file, &info));
  return info;
}

bool same_file(const BY_HANDLE_FILE_INFORMATION& left, const BY_HANDLE_FILE_INFORMATION& right) {
  return left.dwVolumeSerialNumber == right.dwVolumeSerialNumber &&
         left.nFileIndexHigh == right.nFileIndexHigh && left.nFileIndexLow == right.nFileIndexLow &&
         left.ftCreationTime.dwHighDateTime == right.ftCreationTime.dwHighDateTime &&
         left.ftCreationTime.dwLowDateTime == right.ftCreationTime.dwLowDateTime;
}

void delete_owned_handle(HANDLE file) {
  FILE_DISPOSITION_INFO disposition{};
  disposition.DeleteFile = TRUE;
  win32_check(SetFileInformationByHandle(file, FileDispositionInfo, &disposition, sizeof(disposition)));
}

std::wstring owner_path(const std::wstring& link_path) { return link_path + L".owner"; }

FileHandle lock_programs_directory(const std::wstring& shortcut) {
  const auto separator = shortcut.find_last_of(L'\\');
  if (separator == std::wstring::npos) throw hresult_error(E_FAIL);
  const auto directory = shortcut.substr(0, separator);
  FileHandle folder(CreateFileW(directory.c_str(), FILE_READ_ATTRIBUTES, FILE_SHARE_READ | FILE_SHARE_WRITE,
                                nullptr, OPEN_EXISTING, FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, nullptr));
  if (!folder.valid()) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  const auto info = identity(folder.get());
  if ((info.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) == 0 ||
      (info.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0) throw hresult_error(E_ACCESSDENIED);
  return folder;
}

std::wstring executable_path() {
  std::vector<wchar_t> buffer(32768);
  const DWORD length = GetModuleFileNameW(nullptr, buffer.data(), static_cast<DWORD>(buffer.size()));
  if (length == 0 || static_cast<size_t>(length) >= buffer.size()) throw hresult_error(E_FAIL);
  return std::wstring(buffer.data(), length);
}

ComPtr<IShellLinkW> new_link() {
  ComPtr<IShellLinkW> link;
  check_hresult(CoCreateInstance(CLSID_ShellLink, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&link)));
  return link;
}

bool shortcut_matches(HANDLE shortcut, const std::wstring& app_id) {
  LARGE_INTEGER beginning{};
  win32_check(SetFilePointerEx(shortcut, beginning, nullptr, FILE_BEGIN));
  LARGE_INTEGER length{};
  win32_check(GetFileSizeEx(shortcut, &length));
  if (length.QuadPart < 1 || length.QuadPart > 1024 * 1024) return false;
  HGLOBAL memory = GlobalAlloc(GMEM_MOVEABLE, static_cast<SIZE_T>(length.QuadPart));
  if (!memory) throw hresult_error(E_OUTOFMEMORY);
  void* bytes = GlobalLock(memory);
  if (!bytes) { GlobalFree(memory); throw hresult_error(E_OUTOFMEMORY); }
  DWORD read = 0;
  const BOOL loaded = ReadFile(shortcut, bytes, static_cast<DWORD>(length.QuadPart), &read, nullptr);
  const DWORD read_error = GetLastError();
  GlobalUnlock(memory);
  if (!loaded || read != static_cast<DWORD>(length.QuadPart)) {
    GlobalFree(memory);
    if (!loaded) throw hresult_error(HRESULT_FROM_WIN32(read_error));
    return false;
  }
  ComPtr<IStream> stream;
  const HRESULT stream_result = CreateStreamOnHGlobal(memory, TRUE, stream.GetAddressOf());
  if (FAILED(stream_result)) { GlobalFree(memory); check_hresult(stream_result); }
  auto link = new_link();
  ComPtr<IPersistStream> persist;
  check_hresult(link.As(&persist));
  if (FAILED(persist->Load(stream.Get()))) return false;
  wchar_t target[32768]{};
  WIN32_FIND_DATAW target_data{};
  if (FAILED(link->GetPath(target, static_cast<int>(std::size(target)), &target_data, SLGP_RAWPATH))) return false;
  wchar_t arguments[64]{};
  if (FAILED(link->GetArguments(arguments, static_cast<int>(std::size(arguments))))) return false;
  ComPtr<IPropertyStore> properties;
  check_hresult(link.As(&properties));
  PROPVARIANT value{};
  if (FAILED(properties->GetValue(PKEY_AppUserModel_ID, &value))) return false;
  const bool owned = value.vt == VT_LPWSTR && value.pwszVal && app_id == value.pwszVal &&
      _wcsicmp(target, executable_path().c_str()) == 0 && std::wcscmp(arguments, kActivationArgument) == 0;
  PropVariantClear(&value);
  return owned;
}

bool record_matches(HANDLE file, const BY_HANDLE_FILE_INFORMATION& info, const std::wstring& token) {
  OwnerRecord record{};
  DWORD read = 0;
  win32_check(ReadFile(file, &record, static_cast<DWORD>(sizeof(record)), &read, nullptr));
  if (read != static_cast<DWORD>(sizeof(record))) return false;
  char extra = 0;
  win32_check(ReadFile(file, &extra, 1, &read, nullptr));
  return read == 0 && record.magic == kOwnerMagic && record.version == 1 &&
         record.volume == info.dwVolumeSerialNumber && record.file_index_high == info.nFileIndexHigh &&
         record.file_index_low == info.nFileIndexLow &&
         record.created.dwHighDateTime == info.ftCreationTime.dwHighDateTime &&
         record.created.dwLowDateTime == info.ftCreationTime.dwLowDateTime &&
         record.token[32] == L'\0' && std::wmemcmp(record.token, token.data(), 32) == 0;
}

bool owned_shortcut(const std::wstring& path, const std::wstring& app_id, const std::wstring& token) {
  auto shortcut = open_file(path, GENERIC_READ, FILE_SHARE_READ);
  if (!shortcut.valid()) {
    if (missing(GetLastError())) return false;
    throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  }
  auto record = open_file(owner_path(path), GENERIC_READ, FILE_SHARE_READ);
  if (!record.valid()) {
    if (missing(GetLastError())) return false;
    throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  }
  return record_matches(record.get(), identity(shortcut.get()), token) && shortcut_matches(shortcut.get(), app_id);
}

struct RegistrationCheck {
  FileHandle link;
  FileHandle record;
  int status;
};

RegistrationCheck check_registration_at(const std::wstring& path, const std::wstring& app_id,
                                        const std::wstring& token) {
  auto link = open_file(path, GENERIC_READ, FILE_SHARE_READ);
  if (!link.valid()) {
    if (missing(GetLastError())) return { FileHandle(), FileHandle(), 3 };
    throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  }
  auto record = open_file(owner_path(path), GENERIC_READ, FILE_SHARE_READ);
  if (!record.valid()) {
    if (missing(GetLastError())) return { FileHandle(), FileHandle(), 3 };
    throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  }
  if (!record_matches(record.get(), identity(link.get()), token) || !shortcut_matches(link.get(), app_id))
    return { FileHandle(), FileHandle(), 4 };
  return { std::move(link), std::move(record), 0 };
}

std::wstring new_install_directory(const std::wstring& path) {
  for (int attempt = 0; attempt < 4; ++attempt) {
    GUID guid{};
    check_hresult(CoCreateGuid(&guid));
    wchar_t value[40]{};
    if (StringFromGUID2(guid, value, static_cast<int>(std::size(value))) == 0) throw hresult_error(E_FAIL);
    const auto directory = path + L".install-" + value;
    if (CreateDirectoryW(directory.c_str(), nullptr)) return directory;
    if (GetLastError() != ERROR_ALREADY_EXISTS) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  }
  throw hresult_error(HRESULT_FROM_WIN32(ERROR_ALREADY_EXISTS));
}

enum class RegistrationStage { temporary_saved, temporary_held, published_held, before_remove_reopen };
using RegistrationBarrier = std::function<void(RegistrationStage, const std::wstring&)>;

int install_shortcut_at(const std::wstring& path, const std::wstring& app_id,
                        const std::wstring& token, const RegistrationBarrier& barrier = {}) {
  [[maybe_unused]] auto programs_guard = lock_programs_directory(path);
  auto existing = open_file(path, GENERIC_READ, FILE_SHARE_READ);
  if (existing.valid()) return owned_shortcut(path, app_id, token) ? 0 : 4;
  if (!missing(GetLastError())) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  auto previous_record = open_file(owner_path(path), GENERIC_READ, FILE_SHARE_READ);
  if (previous_record.valid()) return 4;
  if (!missing(GetLastError())) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  auto link = new_link();
  check_hresult(link->SetPath(executable_path().c_str()));
  check_hresult(link->SetArguments(kActivationArgument));
  check_hresult(link->SetDescription(L"Software Factory notification helper"));
  ComPtr<IPropertyStore> properties;
  check_hresult(link.As(&properties));
  PROPVARIANT value{};
  check_hresult(InitPropVariantFromString(app_id.c_str(), &value));
  const HRESULT set_value = properties->SetValue(PKEY_AppUserModel_ID, value);
  PropVariantClear(&value);
  check_hresult(set_value);
  check_hresult(properties->Commit());
  ComPtr<IPersistFile> file;
  check_hresult(link.As(&file));
  const auto directory = new_install_directory(path);
  const auto temporary = directory + L"\\shortcut.lnk";
  check_hresult(file->Save(temporary.c_str(), TRUE));
  file.Reset();
  properties.Reset();
  link.Reset();
  if (barrier) barrier(RegistrationStage::temporary_saved, temporary);
  auto source = open_file(temporary, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_DELETE);
  if (!source.valid()) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  const auto source_identity = identity(source.get());
  if (!shortcut_matches(source.get(), app_id)) {
    source.close();
    auto cleanup = open_file(temporary, GENERIC_READ | DELETE, FILE_SHARE_READ);
    if (cleanup.valid() && same_file(identity(cleanup.get()), source_identity)) delete_owned_handle(cleanup.get());
    cleanup.close();
    RemoveDirectoryW(directory.c_str());
    return 4;
  }
  if (barrier) barrier(RegistrationStage::temporary_held, temporary);
  if (!shortcut_matches(source.get(), app_id)) return 4;
  if (!MoveFileExW(temporary.c_str(), path.c_str(), MOVEFILE_WRITE_THROUGH)) {
    const DWORD error = GetLastError();
    source.close();
    auto cleanup = open_file(temporary, GENERIC_READ | DELETE, FILE_SHARE_READ);
    if (cleanup.valid() && same_file(identity(cleanup.get()), source_identity)) delete_owned_handle(cleanup.get());
    cleanup.close();
    RemoveDirectoryW(directory.c_str());
    if (error == ERROR_ALREADY_EXISTS || error == ERROR_FILE_EXISTS) return 4;
    throw hresult_error(HRESULT_FROM_WIN32(error));
  }
  auto published = open_file(path, GENERIC_READ | DELETE, FILE_SHARE_READ);
  if (!published.valid()) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  const auto info = identity(published.get());
  if (!same_file(info, source_identity) || !shortcut_matches(published.get(), app_id)) return 4;
  if (barrier) barrier(RegistrationStage::published_held, path);
  if (!same_file(identity(published.get()), source_identity) || !shortcut_matches(published.get(), app_id)) return 4;
  source.close();
  RemoveDirectoryW(directory.c_str());
  FileHandle record(CreateFileW(owner_path(path).c_str(), GENERIC_WRITE | DELETE, 0, nullptr,
                                CREATE_NEW, FILE_ATTRIBUTE_NORMAL, nullptr));
  if (!record.valid()) {
    const DWORD error = GetLastError();
    delete_owned_handle(published.get());
    if (error == ERROR_ALREADY_EXISTS || error == ERROR_FILE_EXISTS) return 4;
    throw hresult_error(HRESULT_FROM_WIN32(error));
  }
  OwnerRecord owner{};
  owner.magic = kOwnerMagic;
  owner.version = 1;
  owner.volume = info.dwVolumeSerialNumber;
  owner.file_index_high = info.nFileIndexHigh;
  owner.file_index_low = info.nFileIndexLow;
  owner.created = info.ftCreationTime;
  std::wmemcpy(owner.token, token.data(), 32);
  DWORD written = 0;
  if (!WriteFile(record.get(), &owner, static_cast<DWORD>(sizeof(owner)), &written, nullptr) ||
      written != static_cast<DWORD>(sizeof(owner)) ||
      !FlushFileBuffers(record.get())) {
    const DWORD error = GetLastError() == ERROR_SUCCESS ? ERROR_WRITE_FAULT : GetLastError();
    delete_owned_handle(record.get());
    delete_owned_handle(published.get());
    throw hresult_error(HRESULT_FROM_WIN32(error));
  }
  return 0;
}

int remove_shortcut_at(const std::wstring& path, const std::wstring& app_id,
                       const std::wstring& token, const RegistrationBarrier& barrier = {}) {
  [[maybe_unused]] auto programs_guard = lock_programs_directory(path);
  BY_HANDLE_FILE_INFORMATION link_identity{};
  BY_HANDLE_FILE_INFORMATION record_identity{};
  {
    auto link = open_file(path, GENERIC_READ, FILE_SHARE_READ);
    if (!link.valid()) {
      if (missing(GetLastError())) {
        auto orphan_record = open_file(owner_path(path), GENERIC_READ, FILE_SHARE_READ);
        if (orphan_record.valid()) return 4;
        if (missing(GetLastError())) return 0;
      }
      throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
    }
    auto record = open_file(owner_path(path), GENERIC_READ, FILE_SHARE_READ);
    if (!record.valid()) {
      if (missing(GetLastError())) return 4;
      throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
    }
    link_identity = identity(link.get());
    record_identity = identity(record.get());
    if (!record_matches(record.get(), link_identity, token) || !shortcut_matches(link.get(), app_id)) return 4;
  }
  if (barrier) barrier(RegistrationStage::before_remove_reopen, path);
  auto link = open_file(path, GENERIC_READ | DELETE, FILE_SHARE_READ);
  if (!link.valid()) return 4;
  auto record = open_file(owner_path(path), GENERIC_READ | DELETE, FILE_SHARE_READ);
  if (!record.valid()) return 4;
  if (!same_file(identity(link.get()), link_identity) || !same_file(identity(record.get()), record_identity) ||
      !record_matches(record.get(), link_identity, token) || !shortcut_matches(link.get(), app_id)) return 4;
  delete_owned_handle(link.get());
  delete_owned_handle(record.get());
  return 0;
}

}  // namespace
