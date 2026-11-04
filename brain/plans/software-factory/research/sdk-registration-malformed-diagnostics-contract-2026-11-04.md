# SDK malformed observation: next prerequisite design

2026-11-04. Read-only Root decision. No source, test, build, native query, SDK acquisition or execution release follows this packet.

## Retained facts and uncertainty

- Exact pushed863f20bf, metadata run41897732087/job126811642361, artifact13356342800: strict wire2 and closed control validate. Metadata259065bytes SHA7bd61cfaec1af05c0709f34c2d291cc3b1c315c225b2f50513dde2b24108cd58, control428bytes SHA82a778599b2734179c0f27113ae675c36497f49451acc2e67ec86ab3debf35cc. SDK section is version1/blocked/malformed/empty records; top tool-provenance-unproven and255 file facts remain. Source5405/current10f2 and all false authorities are retained. ZIP22774bytes/de29efb6805ed436919da8dd40f8b90bddbd8621e504c3275c117383d858d7ac is retained.
- Full evidence: /tmp/factory-sdk-metadata-41897732087-job.log, /tmp/factory-sdk-metadata-artifact-validation-postflight.json, and the two extracted files. Original source and host facts remain tied only to this run. No actual malformed branch, SDK version, Windows ABI correctness, complete registry observation, tool selection or SDK authentication has been established.
- Source narrows malformed to enumerated key shape/Unicode or Read-SdkRegistryString type/size/Unicode/termination/control checks at DisplayName, DisplayVersion or Publisher. Current wire intentionally hides which branch. Generic native/binding errors are not proof of any particular malformed branch. Do not infer the branch from these alternatives.
- Microsoft documents that successful RegQueryValueExW string reads need not include a terminating NUL. This is a possible input class, not the observed cause. Keep strict termination and all admission rules; do not repair or accept unproven input to make the job pass.

## Selected next approach

Use a bounded closed refusal diagnostic before any further native observation. An unchanged native retry cannot identify the branch and is not released. Do not install an SDK, execute a tool, expand discovery, inspect arbitrary registry fields, or add raw values to logs.

The source handback should preserve the same four read-only APIs, logical root/two views/two passes, all source roles, file/sample caps and byte/time/closure limits. Keep prior wire1 and wire2 pure validators and historical artifacts unchanged. Introduce a separate strict live wire3 validator with SDK section version2. This explicit version pair avoids silently broadening old live admission.

The SDK version2 section retains status/reason/records and adds exactly one closed fault code. Fault codes identify only source-defined malformed checks: entry-name-shape, entry-name-unicode, display-name-type, display-name-size, display-name-unicode, display-name-termination, display-name-control, and the corresponding display-version/publisher codes. Use none except on blocked/malformed; blocked records remain empty. No raw key/value, type number, index, byte prefix, path, SID, timing or arbitrary exception text is exported. The full section including the new field must stay within32768 bytes and the full wire within1MiB.

Classify faults at their exact fixed throw sites. Never derive a code from a caller label or arbitrary exception message. Unexpected exceptions remain an existing fixed refusal. Closure/deadline failures still override tentative data and cannot be disguised as a string fault. New protocol comparisons use primitive ordinal equality. All selection/build/native authority fields remain false; existing tool/SDK sample predicates and precedence remain unchanged.

## Proof and independent context gates

1. First meaningful pure RED: exact public live parser rejects the proposed wire3 closed malformed record while historical wire2 and old context controls still behave as recorded. No actual registry API, binder construction or collector CLI is permitted in this source proof.
2. Exercise actual extracted Open/Enum/Query/Close wrapper bodies against inert Invoke-shaped stubs, then actual query/classifier functions. Check byte-array/data-size/typed byref result handling and every closed fault, including closure override and no canary leakage. Such tests prove PowerShell data flow only, never MethodInfo/native marshaling or Windows ABI. Do not mirror wrapper code in tests or instantiate New-SdkRegistryApi.
3. Complete portable historical/current parser, context, outer artifact/refusal and source/cap/AST checks. No runtime build is needed unless authenticated app inputs change. Stop at a clean source handback; no native query follows automatically.
4. Root independently derives the new current selection from accepted Git source, preserves exact current10f2 as historical, and writes its sidecar/provenance. Coordinator separately integrates strict outer wire3 admission and rejects old live wire/context without changing historical parsing. PhaseA3 remains immutable.
5. Only after exact integrated proof and an independent execution proposal may Root release one changed metadata-only native observation. It must carry fresh file facts plus the closed diagnostic under its own source/host identity. The first unmet prerequisite still stops selection/build; no retry, fallback, servicing-package join or SDK acquisition is implied.

## Ownership and status

A future separately routed qualification author owns only existing metadata PS/MJS, narrowly scoped pure tests and a note. Coordinator owns outer admission/CI/canonical integration; Root owns authoritative current context. This packet selects the diagnostic design but SOURCE and native execution remain unreleased. The current hook-fixture/owner diagnostic, H2 projection and Darwin timing source tasks have their existing separate owners and priority.

Primary reference: https://learn.microsoft.com/en-us/windows/win32/api/winreg/nf-winreg-regqueryvalueexw . No claim about actual stored values follows from that reference.
