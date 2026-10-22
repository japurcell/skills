#include "registration-core.hpp"

#include <filesystem>
#include <iostream>
#include <stdexcept>

namespace {
constexpr wchar_t kAppId[] = L"SoftwareFactory.Repository.0123456789ABCDEF01234567";
constexpr wchar_t kToken[] = L"0123456789ABCDEF0123456789ABCDEF";

void expect(bool condition, const char* message) {
  if (!condition) throw std::runtime_error(message);
}

std::wstring test_path(const std::wstring& root, const wchar_t* name) {
  return root + L"\\" + name + L".lnk";
}

bool exists(const std::wstring& path) {
  const DWORD attributes = GetFileAttributesW(path.c_str());
  return attributes != INVALID_FILE_ATTRIBUTES;
}

void put_foreign(const std::wstring& path, DWORD disposition = CREATE_NEW) {
  FileHandle file(CreateFileW(path.c_str(), GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                              nullptr, disposition, FILE_ATTRIBUTE_NORMAL, nullptr));
  expect(file.valid(), "foreign file creation failed");
  constexpr char text[] = "foreign shortcut";
  DWORD written = 0;
  expect(WriteFile(file.get(), text, static_cast<DWORD>(sizeof(text)), &written, nullptr) &&
         written == sizeof(text),
         "foreign file write failed");
}

void expect_write_blocked(const std::wstring& path) {
  FileHandle writer(CreateFileW(path.c_str(), GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE,
                                nullptr, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, nullptr));
  expect(!writer.valid() && GetLastError() == ERROR_SHARING_VIOLATION,
         "held shortcut allowed in-place write");
}

BY_HANDLE_FILE_INFORMATION file_identity(const std::wstring& path) {
  auto file = open_file(path, GENERIC_READ, FILE_SHARE_READ);
  expect(file.valid(), "expected shortcut missing");
  return identity(file.get());
}

std::wstring fresh_root(const std::wstring& parent) {
  for (int attempt = 0; attempt < 4; ++attempt) {
    GUID guid{};
    check_hresult(CoCreateGuid(&guid));
    wchar_t suffix[40]{};
    expect(StringFromGUID2(guid, suffix, static_cast<int>(std::size(suffix))) != 0, "GUID conversion failed");
    const auto root = parent + L"\\factory-notify-registration-" + suffix;
    if (CreateDirectoryW(root.c_str(), nullptr)) return root;
    expect(GetLastError() == ERROR_ALREADY_EXISTS, "temp directory creation failed");
  }
  throw std::runtime_error("no fresh temp directory");
}

void run(const std::wstring& root) {
  const auto missing_link = test_path(root, L"missing");
  expect(check_registration_at(missing_link, kAppId, kToken).status == 3,
         "missing registration did not return 3");

  const auto tampered_link = test_path(root, L"tampered-save");
  expect(install_shortcut_at(tampered_link, kAppId, kToken,
      [](RegistrationStage stage, const std::wstring& path) {
        if (stage == RegistrationStage::temporary_saved) put_foreign(path, CREATE_ALWAYS);
      }) == 4, "modified saved shortcut was accepted");
  expect(!exists(owner_path(tampered_link)), "tampered shortcut got an owner record");

  const auto owned_link = test_path(root, L"owned");
  bool temp_held = false, published_held = false;
  expect(install_shortcut_at(owned_link, kAppId, kToken,
      [&](RegistrationStage stage, const std::wstring& path) {
        if (stage == RegistrationStage::temporary_held) {
          expect_write_blocked(path);
          temp_held = true;
        }
        if (stage == RegistrationStage::published_held) {
          expect_write_blocked(path);
          published_held = true;
        }
      }) == 0, "valid install failed");
  expect(temp_held && published_held, "publication barriers did not run");
  expect(check_registration_at(owned_link, kAppId, kToken).status == 0,
         "published registration is not owned");

  const auto identical_link = test_path(root, L"identical-foreign");
  expect(CopyFileW(owned_link.c_str(), identical_link.c_str(), TRUE), "identical shortcut copy failed");
  const auto identical_identity = file_identity(identical_link);
  expect(install_shortcut_at(identical_link, kAppId, kToken) == 4,
         "identical preexisting shortcut was adopted");
  expect(same_file(file_identity(identical_link), identical_identity) && !exists(owner_path(identical_link)),
         "identical preexisting shortcut changed");

  const auto collision_link = test_path(root, L"publication-collision");
  expect(install_shortcut_at(collision_link, kAppId, kToken,
      [&](RegistrationStage stage, const std::wstring&) {
        if (stage == RegistrationStage::temporary_held) put_foreign(collision_link);
      }) == 4, "foreign publication collision was overwritten");
  expect(exists(collision_link) && !exists(owner_path(collision_link)),
         "foreign publication collision changed");

  const auto renamed_source_link = test_path(root, L"renamed-source");
  const auto renamed_temp = root + L"\\renamed-temp.lnk";
  expect(install_shortcut_at(renamed_source_link, kAppId, kToken,
      [&](RegistrationStage stage, const std::wstring& path) {
        if (stage == RegistrationStage::temporary_held) {
          expect(MoveFileExW(path.c_str(), renamed_temp.c_str(), 0), "temporary rename failed");
          put_foreign(path);
        }
      }) == 4, "renamed temporary shortcut acquired ownership");
  expect(exists(renamed_source_link) && !exists(owner_path(renamed_source_link)),
         "renamed temporary shortcut acquired an owner record");

  const auto remove_race_link = test_path(root, L"remove-race");
  expect(install_shortcut_at(remove_race_link, kAppId, kToken) == 0,
         "remove race setup failed");
  const auto foreign_replacement = test_path(root, L"replacement-source");
  put_foreign(foreign_replacement);
  expect(remove_shortcut_at(remove_race_link, kAppId, kToken,
      [&](RegistrationStage stage, const std::wstring&) {
        if (stage == RegistrationStage::before_remove_reopen)
          expect(MoveFileExW(foreign_replacement.c_str(), remove_race_link.c_str(),
                             MOVEFILE_REPLACE_EXISTING), "replacement race setup failed");
      }) == 4, "removal deleted a foreign replacement");
  expect(exists(remove_race_link) && exists(owner_path(remove_race_link)),
         "foreign replacement or ownership evidence was deleted");

  const auto record_race_link = test_path(root, L"record-race");
  expect(install_shortcut_at(record_race_link, kAppId, kToken) == 0,
         "record race setup failed");
  const auto moved_record = root + L"\\saved-record";
  expect(remove_shortcut_at(record_race_link, kAppId, kToken,
      [&](RegistrationStage stage, const std::wstring&) {
        if (stage == RegistrationStage::before_remove_reopen) {
          expect(MoveFileExW(owner_path(record_race_link).c_str(), moved_record.c_str(), 0),
                 "record rename failed");
          put_foreign(owner_path(record_race_link));
        }
      }) == 4, "removal accepted a foreign ownership record");
  expect(exists(record_race_link) && exists(owner_path(record_race_link)),
         "record replacement deleted an unrelated file");

  expect(remove_shortcut_at(owned_link, kAppId, kToken) == 0,
         "valid owned pair removal failed");
  expect(!exists(owned_link) && !exists(owner_path(owned_link)),
         "owned pair remained after removal");

  const auto orphan_link = test_path(root, L"orphan-record");
  expect(install_shortcut_at(orphan_link, kAppId, kToken) == 0,
         "orphan setup failed");
  {
    auto link = open_file(orphan_link, GENERIC_READ | DELETE, FILE_SHARE_READ);
    expect(link.valid(), "orphan setup link missing");
    delete_owned_handle(link.get());
  }
  expect(install_shortcut_at(orphan_link, kAppId, kToken) == 4 &&
         remove_shortcut_at(orphan_link, kAppId, kToken) == 4,
         "orphan record was adopted or removed");
  expect(exists(owner_path(orphan_link)), "orphan record was deleted");
}
}  // namespace

int wmain(int argc, wchar_t* argv[]) {
  if (argc != 2) return 2;
  std::wstring root;
  try {
    init_apartment(apartment_type::single_threaded);
    wchar_t temp_parent[32768]{};
    const DWORD temp_length = GetEnvironmentVariableW(L"RUNNER_TEMP", temp_parent,
                                                        static_cast<DWORD>(std::size(temp_parent)));
    expect(temp_length > 0 && temp_length < std::size(temp_parent), "RUNNER_TEMP is required");
    FileHandle parent(CreateFileW(argv[1], FILE_READ_ATTRIBUTES, FILE_SHARE_READ | FILE_SHARE_WRITE,
                                  nullptr, OPEN_EXISTING,
                                  FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, nullptr));
    expect(parent.valid(), "temp parent missing");
    FileHandle configured(CreateFileW(temp_parent, FILE_READ_ATTRIBUTES, FILE_SHARE_READ | FILE_SHARE_WRITE,
                                      nullptr, OPEN_EXISTING,
                                      FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OPEN_REPARSE_POINT, nullptr));
    expect(configured.valid() && same_file(identity(parent.get()), identity(configured.get())),
           "parent must be RUNNER_TEMP");
    const auto info = identity(parent.get());
    expect((info.dwFileAttributes & FILE_ATTRIBUTE_DIRECTORY) != 0 &&
           (info.dwFileAttributes & FILE_ATTRIBUTE_REPARSE_POINT) == 0,
           "temp parent must be a directory without reparse points");
    root = fresh_root(argv[1]);
    run(root);
    std::filesystem::remove_all(root);
    std::cout << "registration temp-folder tests passed\n";
    return 0;
  } catch (const std::exception& error) {
    std::cerr << error.what() << '\n';
    if (!root.empty()) std::filesystem::remove_all(root);
    return 1;
  } catch (...) {
    if (!root.empty()) std::filesystem::remove_all(root);
    return 1;
  }
}
