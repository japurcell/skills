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
#include <iterator>
#include <string>
#include <vector>

using Microsoft::WRL::ComPtr;
using namespace winrt;
using namespace Windows::UI::Notifications;

namespace {
constexpr wchar_t kPrefix[] = L"SoftwareFactory.Repository.";
constexpr wchar_t kActivationArgument[] = L"activated";

bool valid_app_id(const std::wstring& app_id) {
  const size_t prefix_length = std::wcslen(kPrefix);
  if (app_id.size() != prefix_length + 24 || app_id.compare(0, prefix_length, kPrefix) != 0) return false;
  for (size_t index = prefix_length; index < app_id.size(); ++index) {
    const wchar_t c = app_id[index];
    if (!((c >= L'0' && c <= L'9') || (c >= L'A' && c <= L'F'))) return false;
  }
  return true;
}

std::wstring executable_path() {
  std::vector<wchar_t> buffer(32768);
  const DWORD length = GetModuleFileNameW(nullptr, buffer.data(), static_cast<DWORD>(buffer.size()));
  if (length == 0 || static_cast<size_t>(length) >= buffer.size()) throw hresult_error(E_FAIL);
  return std::wstring(buffer.data(), length);
}

std::wstring shortcut_path(const std::wstring& app_id) {
  PWSTR programs = nullptr;
  check_hresult(SHGetKnownFolderPath(FOLDERID_Programs, KF_FLAG_DEFAULT, nullptr, &programs));
  std::wstring path;
  try { path = std::wstring(programs) + L"\\Software Factory " + app_id.substr(std::wcslen(kPrefix)) + L".lnk"; }
  catch (...) { CoTaskMemFree(programs); throw; }
  CoTaskMemFree(programs);
  return path;
}

ComPtr<IShellLinkW> new_link() {
  ComPtr<IShellLinkW> link;
  check_hresult(CoCreateInstance(CLSID_ShellLink, nullptr, CLSCTX_INPROC_SERVER, IID_PPV_ARGS(&link)));
  return link;
}

bool shortcut_exists(const std::wstring& path) {
  const DWORD attributes = GetFileAttributesW(path.c_str());
  if (attributes == INVALID_FILE_ATTRIBUTES) {
    if (GetLastError() == ERROR_FILE_NOT_FOUND || GetLastError() == ERROR_PATH_NOT_FOUND) return false;
    throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  }
  if ((attributes & FILE_ATTRIBUTE_DIRECTORY) != 0 || (attributes & FILE_ATTRIBUTE_REPARSE_POINT) != 0) throw hresult_error(E_ACCESSDENIED);
  return true;
}

bool shortcut_is_owned(const std::wstring& path, const std::wstring& app_id) {
  if (!shortcut_exists(path)) return false;
  auto link = new_link();
  ComPtr<IPersistFile> file;
  check_hresult(link.As(&file));
  check_hresult(file->Load(path.c_str(), STGM_READ));
  wchar_t target[32768]{};
  WIN32_FIND_DATAW target_data{};
  check_hresult(link->GetPath(target, static_cast<int>(std::size(target)), &target_data, SLGP_RAWPATH));
  wchar_t arguments[64]{};
  check_hresult(link->GetArguments(arguments, static_cast<int>(std::size(arguments))));
  ComPtr<IPropertyStore> properties;
  check_hresult(link.As(&properties));
  PROPVARIANT value{};
  check_hresult(properties->GetValue(PKEY_AppUserModel_ID, &value));
  const bool owned = value.vt == VT_LPWSTR && value.pwszVal && app_id == value.pwszVal &&
      _wcsicmp(target, executable_path().c_str()) == 0 && std::wcscmp(arguments, kActivationArgument) == 0;
  PropVariantClear(&value);
  return owned;
}

int install_shortcut(const std::wstring& app_id) {
  const auto path = shortcut_path(app_id);
  if (shortcut_exists(path)) return shortcut_is_owned(path, app_id) ? 0 : 4;
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
  check_hresult(file->Save(path.c_str(), TRUE));
  return 0;
}

int remove_shortcut(const std::wstring& app_id) {
  const auto path = shortcut_path(app_id);
  if (!shortcut_exists(path)) return 0;
  if (!shortcut_is_owned(path, app_id)) return 4;
  if (!DeleteFileW(path.c_str())) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
  return 0;
}

int send_toast(const std::wstring& app_id, const std::wstring& title, const std::wstring& body) {
  if (title.empty() || body.empty() || title.size() > 256 || body.size() > 4096) return 2;
  const auto path = shortcut_path(app_id);
  if (!shortcut_exists(path)) return 3;
  if (!shortcut_is_owned(path, app_id)) return 4;
  auto notifier = ToastNotificationManager::CreateToastNotifier(hstring(app_id));
  if (notifier.Setting() != NotificationSetting::Enabled) return 4;
  auto xml = ToastNotificationManager::GetTemplateContent(ToastTemplateType::ToastText02);
  const auto nodes = xml.GetElementsByTagName(L"text");
  if (nodes.Length() < 2) return 5;
  nodes.Item(0).AppendChild(xml.CreateTextNode(hstring(title)));
  nodes.Item(1).AppendChild(xml.CreateTextNode(hstring(body)));
  ToastNotification toast(xml);
  // The desktop API requires an in-process activation handler. It has no workflow effect.
  toast.Activated([](auto const&, auto const&) noexcept {});
  notifier.Show(toast);
  return 0;
}
}  // namespace

int wmain(int argc, wchar_t* argv[]) {
  try {
    if (argc == 2 && std::wcscmp(argv[1], kActivationArgument) == 0) return 0;
    if (argc < 3 || argc > 5) return 2;
    const std::wstring app_id(argv[2]);
    if (!valid_app_id(app_id)) return 2;
    init_apartment(apartment_type::single_threaded);
    if (argc == 3 && std::wcscmp(argv[1], L"install") == 0) return install_shortcut(app_id);
    if (argc == 3 && std::wcscmp(argv[1], L"remove") == 0) return remove_shortcut(app_id);
    if (argc == 5 && std::wcscmp(argv[1], L"send") == 0) return send_toast(app_id, argv[3], argv[4]);
    return 2;
  } catch (const hresult_error& error) {
    if (error.code() == E_ACCESSDENIED) return 4;
    return 5;
  } catch (...) {
    return 5;
  }
}
