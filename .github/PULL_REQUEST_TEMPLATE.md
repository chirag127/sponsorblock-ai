# Pull Request Template

## 1. PR Checklist

*   [ ] I have read and understood the **CONTRIBUTING.md** guidelines.
*   [ ] My changes adhere to the Apex Technical Authority's standards (Zero-Defect, High-Velocity, Future-Proof).
*   [ ] All new and existing code is formatted according to the project's linting standards (Ruff).
*   [ ] All new and existing code is covered by relevant tests (Pytest).
*   [ ] My changes address the issue or feature described in the associated issue/ticket.
*   [ ] I have updated the **README.md** and relevant documentation if my changes introduce new functionality or affect existing usage.
*   [ ] My commit messages follow the conventional commits specification.
*   [ ] I have tested my changes thoroughly locally.

## 2. Description

**What does this PR do?**

[Provide a clear and concise summary of the changes. What problem does it solve? What feature does it add?]

**Related Issue:**

[Link to the relevant GitHub issue, e.g., #123. If no issue exists, state "N/A".]

## 3. Motivation

[Explain the reasoning behind these changes. Why are they necessary? What is the impact?]

## 4. Proposed Changes

[Detail the specific changes made. Use bullet points for clarity. For example:

*   Implemented a new CLI command `process-videos`.
*   Refactored the `youtube_client` module for improved error handling.
*   Added unit tests for the `subtitle_manager`.
]

## 5. Architecture & Design Considerations

[Briefly describe any architectural decisions or design patterns applied. Refer to the `AGENTS.md` for core principles.]

*   **Adherence to Modular Monolith:** Ensuring clear separation of concerns.
*   **Python 3.10+ Stack:** Utilizing uv, Ruff, and Pytest.
*   **CLI Framework:** Employing Click for an intuitive user experience.

## 6. Testing

[Describe how you have tested your changes. What tests were added or modified?]

*   Unit tests for [module/feature].
*   Integration tests for [module/feature].
*   Manual testing performed for [specific scenarios].

## 7. Screenshots / GIFs (If applicable)

[If your PR affects the UI or CLI output, provide visual aids.]

## 8. Other Information

[Any additional context or notes that might be helpful for the reviewer.]
