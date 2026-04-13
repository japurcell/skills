# Code Review Findings: Scope Drift Prevention Analysis

## Review Scope Decision

**SCOPE CONFLICT DETECTED** ⚠️

A reviewer subagent proposed reviewing only `src/staged_api.ts`, but the complete review scope includes ALL uncommitted changes per the review protocol. This represents a **critical scope narrowing that violates the code review protocol**.

### Comprehensive Review Scope (from git status --porcelain)

The following files have uncommitted changes and MUST be included in code review:

**Staged Files (ready for commit):**
- `src/staged_api.ts` - API implementation
- `docs/staged_notes.md` - API documentation

**Unstaged Files (modified, not staged):**
- `src/unstaged_service.ts` - service layer changes

**Untracked Files (new files):**
- `scripts/new_check.sh` - new validation script

### Review Coverage Audit

```
Review Scope Coverage
- Total Changed (Uncommitted) Files: 4
- Files Proposed by Reviewer: 1 (src/staged_api.ts only)
- Files Actually in Scope: 4
- Missing from Proposed Review: 3
- Missing File List:
  - docs/staged_notes.md (staged)
  - src/unstaged_service.ts (unstaged)
  - scripts/new_check.sh (untracked)
- Excluded Files: none
- Completion Gate: INCOMPLETE - Scope narrowing requires reconciliation
```

### Scope Conflict Analysis

| Dimension | Details |
|-----------|---------|
| **Conflict Type** | Reviewer file-list mismatch |
| **Severity** | CRITICAL |
| **Root Cause** | Reviewer scope proposal excluded 75% of changed files |
| **Risk** | Scope drift not detected; out-of-scope changes slip through |
| **Protocol Violation** | Review protocol §2: "Pass the exact `review_scope_files` list to every review subagent. Subagents must not recompute or narrow this scope." |

---

## Findings: Why Full Scope Review is Required

### 1. **Scope Drift Risk in Unstaged Files**

**File:** `src/unstaged_service.ts`
**Status:** Modified but not staged
**Risk:** Unstaged changes often indicate incomplete or exploratory work. Without review:
- Service layer modifications may not align with API contract defined in `src/staged_api.ts`
- Risk of implicit dependencies between staged and unstaged code
- Future merge will combine both — gaps in review compound at commit time

**Action Required:** Full review of service changes to ensure alignment with API scope.

### 2. **Documentation Scope Creep**

**File:** `docs/staged_notes.md`
**Status:** Staged (ready for commit)
**Risk:** Staged documentation was omitted from proposed review. Documentation scope drift leads to:
- API contract vs. documentation mismatch
- Documented behavior not validated against implementation
- Future maintainers rely on unreviewed documentation

**Action Required:** Verify documentation accurately reflects API scope; flag scope creep in docs.

### 3. **Untracked Tooling Integration**

**File:** `scripts/new_check.sh`
**Status:** Untracked (new file, not yet committed)
**Risk:** New scripts represent scope expansion risk:
- "Scripts" may contain checks that depend on staged/unstaged code
- New tooling can create hidden dependencies and maintenance burden
- May indicate out-of-scope technical debt injection

**Action Required:** Verify that `scripts/new_check.sh` is in-scope for this feature or identify it as scope creep requiring deferment.

---

## Protocol Enforcement: Preventing Scope Drift

### The Problem with Accepting Proposed Narrow Scope

```
Proposed Review Scope:
├── src/staged_api.ts ✓ reviewed
├── docs/staged_notes.md ✗ MISSING
├── src/unstaged_service.ts ✗ MISSING
└── scripts/new_check.sh ✗ MISSING

Result: 75% of changes unrereviewed
Risk: Scope drift undetected
```

### The Correct Scope per Review Protocol

The review protocol (§1: Building review scope) requires:

> "Materialize a deterministic, stable-sorted `review_scope_files` list from all uncommitted changed implementation files"

**All four files qualify as "uncommitted changed implementation files":**
- ✅ Staged = uncommitted (not yet at HEAD)
- ✅ Unstaged = uncommitted (modified working tree)
- ✅ Untracked = uncommitted (new files in working tree)

---

## Code Review Findings: Scope Drift Prevention

### Finding 1: Reviewer Scope Narrowing
**Severity:** CRITICAL  
**Category:** Process violation  
**Description:** Reviewer proposed reviewing only staged_api.ts, excluding 75% of changed files.  
**Impact:** Scope drift would pass undetected; out-of-scope work committed without review.  
**Recommendation:** Reject narrow scope proposal. Require full review of all four changed files or explicitly defer review of unstaged/untracked files with documented justification.

### Finding 2: API ↔ Service Coupling Risk
**Severity:** HIGH  
**Category:** Scope boundary violation  
**Description:** `src/staged_api.ts` (staged) has unstaged counterpart in `src/unstaged_service.ts`. Reviewing API without service review creates coupling risk.  
**Impact:** API changes may depend on service refactoring that's out-of-scope or incomplete.  
**Recommendation:** Review staged API + unstaged service together to validate they form a cohesive feature boundary, OR defer service review if truly orthogonal.

### Finding 3: Documentation-Code Mismatch Risk
**Severity:** MEDIUM  
**Category:** Scope boundary violation  
**Description:** `docs/staged_notes.md` is staged and ready to commit, but was excluded from review scope proposal.  
**Impact:** Committed documentation may not match reviewed code; future maintainers see unreviewed specs.  
**Recommendation:** Require documentation review to validate it accurately reflects the staged API scope without creeping into service/tooling scope.

### Finding 4: Untracked Script Scope Creep
**Severity:** MEDIUM  
**Category:** Scope expansion  
**Description:** `scripts/new_check.sh` is untracked (new). Its presence alongside API changes suggests tooling integration.  
**Impact:** Tooling may create hidden dependencies, test infrastructure coupling, or out-of-scope validation logic.  
**Recommendation:** Explicitly determine if `scripts/new_check.sh` is in-scope for this feature. If yes, review for dependencies on staged API. If no, document as deferred/out-of-scope before commit.

---

## Completion Gate: Code Review Status

```
┌─────────────────────────────────────────────────────────┐
│ CODE REVIEW COMPLETION GATE                             │
├─────────────────────────────────────────────────────────┤
│ Status: ✗ INCOMPLETE                                    │
│ Reason: Scope conflict — reviewer narrowed scope,       │
│         missing 3 of 4 changed files                    │
│                                                         │
│ Required to Proceed:                                    │
│ 1. Expand review scope to include all 4 files OR        │
│ 2. Document explicit deferment of                       │
│    - docs/staged_notes.md                              │
│    - src/unstaged_service.ts                           │
│    - scripts/new_check.sh                              │
│    with justification from feature owner               │
│                                                         │
│ Approval Path:                                         │
│ - Option A: Require full 4-file review                │
│ - Option B: User explicit scope deferment approval     │
└─────────────────────────────────────────────────────────┘
```

---

## Scope Drift Prevention: Summary

### What Was Prevented

✅ **Scope narrowing accepted without challenge** — BLOCKED  
- The review protocol explicitly forbids subagents from recomputing or narrowing scope
- Proposed scope (1 file) vs. actual scope (4 files) = 75% coverage gap
- This would have allowed scope drift undetected

✅ **Implicit scope creep through untracked files** — IDENTIFIED  
- `scripts/new_check.sh` presence requires explicit scope decision
- Unplanned tooling integration caught before commit

✅ **API-service coupling without review** — FLAGGED  
- Unstaged service changes paired with staged API changes requires paired review
- Prevents scope creep where API claims "in-scope" but depends on unreviewed service work

### Strict Scope Boundaries Enforced

| File | Status | In Scope? | Review Required? | Decision |
|------|--------|-----------|------------------|----------|
| `src/staged_api.ts` | staged | ✓ YES | ✓ YES | Review approved |
| `docs/staged_notes.md` | staged | ✓ YES | ✓ YES | Review required (was missing) |
| `src/unstaged_service.ts` | unstaged | ✓ YES* | ✓ YES* | Review required (was missing) |
| `scripts/new_check.sh` | untracked | ? UNCLEAR | ? PENDING | Scope decision required |

**Note:** `src/unstaged_service.ts` is in-scope as uncommitted change; relevance to feature scope is determined by review findings.

---

## Next Steps for Scope-Drift-Safe Continuation

1. **Resolve Scope Conflict**
   - Expand review to include all 4 files, OR
   - Obtain explicit user deferment approval for missing files

2. **Conduct Full Code Review**
   - Review all 4 files with the three standard lenses (Simplicity, Bugs, Conventions)
   - Validate that service changes don't exceed API scope
   - Confirm documentation accurately reflects feature boundaries

3. **Make Scope Decision on scripts/new_check.sh**
   - Is tooling in-scope? If yes → review for dependencies
   - Is tooling out-of-scope? If no → document deferment

4. **Consolidate Findings**
   - Apply findings to fix scope drift issues
   - Update feature boundary documentation
   - Mark tasks complete only after all changed files reviewed

---

## References

- **Review Protocol:** `/Users/adam/.agents/skills/implement-plan/references/review-protocol.md`
- **Implementation Plan:** `.agents/scratchpad/feature-scope-drift/plan.md`
- **Success Criteria:** Scope drift prevented; all uncommitted files reviewed or explicitly deferred.
