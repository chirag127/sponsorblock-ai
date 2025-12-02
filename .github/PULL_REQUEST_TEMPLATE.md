# Pull Request Template: Apex Standard Verification

**Project:** TubeScript-YouTube-API-Automation-CLI-Tool

This template enforces the **Zero-Defect, High-Velocity, Future-Proof** standard dictated by the Apex Technical Authority.

---

## 1. Feature/Fix Summary (BLUF)

**Briefly describe the purpose of this Pull Request.**

*What problem does this solve, or what new capability does it introduce?* 

---

## 2. Architectural & Compliance Checklist

Ensure all critical steps mandated by the Apex Protocol have been addressed before requesting review.

### Code Quality & Linting (Ruff Enforced)
- [ ] All new/modified code passes static analysis (Ruff Linter/Formatter checks are clean).
- [ ] Adherence to SOLID/DRY principles maintained in new modules.
- [ ] Dependency management updated via `uv` (if applicable); no hardcoded dependencies outside of `pyproject.toml`.

### Testing & Verification (Pytest Standard)
- [ ] New features include corresponding Pytest unit/integration tests.
- [ ] Existing test suites run successfully locally (`pytest`).
- [ ] Edge cases related to YouTube API interaction are considered and tested.

### Documentation & Metadata
- [ ] `README.md` updated if the change is user-facing or alters configuration.
- [ ] Any new public functions/classes have clear docstrings (Type Hinting mandatory).
- [ ] **CRITICAL:** Links and badges in the `README.md` still point to the correct repository URL: `https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool`.

### Agent Alignment (Referencing AGENTS.md)
- [ ] The changes align with the documented Python/AI/CLI standards defined in `.github/AGENTS.md`.

---

## 3. Detailed Description of Changes

<!-- Provide a comprehensive technical breakdown here. If this is a feature, explain the flow. If it is a fix, explain the root cause identified. -->


## 4. Related Issues

Fixes #<issue_number> OR Closes #<issue_number>

---

## 5. Verification Steps (For Reviewer)

To validate this PR, please execute the following steps:

1. Clone this branch and install dependencies using `uv`.
2. Run full linting: `ruff check .`
3. Execute the test suite: `pytest`
4. Manually verify the CLI command/workflow changed.

---

## 6. Self-Review Notes

*What did you specifically focus on during development? What areas might require extra scrutiny from the reviewer?*
