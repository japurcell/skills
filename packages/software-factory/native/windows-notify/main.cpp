#include "registration-core.hpp"
#include <winrt/Windows.Foundation.h>

namespace {
constexpr wchar_t kPrefix[] = L"SoftwareFactory.Repository.";

bool valid_token(const std::wstring& token) {
  if (token.size() != 32) return false;
  for (const auto c : token) if (!((c >= L'0' && c <= L'9') || (c >= L'A' && c <= L'F'))) return false;
  return true;
}

bool valid_app_id(const std::wstring& app_id) {
  const size_t prefix_length = std::wcslen(kPrefix);
  if (app_id.size() != prefix_length + 24 || app_id.compare(0, prefix_length, kPrefix) != 0) return false;
  for (size_t index = prefix_length; index < app_id.size(); ++index) {
    const wchar_t c = app_id[index];
    if (!((c >= L'0' && c <= L'9') || (c >= L'A' && c <= L'F'))) return false;
  }
  return true;
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

int install_shortcut(const std::wstring& app_id, const std::wstring& token) {
  return install_shortcut_at(shortcut_path(app_id), app_id, token);
}

int remove_shortcut(const std::wstring& app_id, const std::wstring& token) {
  return remove_shortcut_at(shortcut_path(app_id), app_id, token);
}

int send_toast(const std::wstring& app_id, const std::wstring& token, const std::wstring& title, const std::wstring& body) {
  if (title.empty() || body.empty() || title.size() > 256 || body.size() > 4096) return 2;
  const auto path = shortcut_path(app_id);
  [[maybe_unused]] auto programs_guard = lock_programs_directory(path);
  [[maybe_unused]] auto registration = check_registration_at(path, app_id, token);
  if (registration.status != 0) return registration.status;
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
    if (argc < 3 || argc > 6) return 2;
    const std::wstring app_id(argv[2]);
    if (!valid_app_id(app_id)) return 2;
    if (argc < 4) return 2;
    const std::wstring token(argv[3]);
    if (!valid_token(token)) return 2;
    init_apartment(apartment_type::single_threaded);
    if (argc == 4 && std::wcscmp(argv[1], L"install") == 0) return install_shortcut(app_id, token);
    if (argc == 4 && std::wcscmp(argv[1], L"remove") == 0) return remove_shortcut(app_id, token);
    if (argc == 6 && std::wcscmp(argv[1], L"send") == 0) return send_toast(app_id, token, argv[4], argv[5]);
    return 2;
  } catch (const hresult_error& error) {
    if (error.code() == E_ACCESSDENIED) return 4;
    return 5;
  } catch (...) {
    return 5;
  }
}
