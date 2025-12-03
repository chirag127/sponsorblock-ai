# Contributing to TubeScript-YouTube-API-Automation-CLI-Tool

Thank you for considering contributing to TubeScript-YouTube-API-Automation-CLI-Tool! We welcome your help in making this project even better.

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to `chirag127@users.noreply.github.com`.

## How to Contribute

We appreciate contributions of all kinds, from reporting bugs to suggesting new features and submitting pull requests.

### 1. Reporting Bugs

If you find a bug, please open an issue on GitHub. Be sure to include:

*   A clear and concise description of the bug.
*   Steps to reproduce the bug.
*   The expected behavior.
*   The actual behavior.
*   Your environment (e.g., Python version, OS).
*   Any relevant logs or error messages.

We use GitHub Issue Templates to standardize bug reports. Please select the `bug_report.md` template when creating a new issue.

### 2. Suggesting Enhancements or Features

If you have an idea for a new feature or an improvement, please open an issue on GitHub.

*   Describe the proposed feature or enhancement.
*   Explain why it would be beneficial.
*   If applicable, provide mockups or examples.

### 3. Submitting Pull Requests

Contributions via pull requests are highly encouraged. Please follow these steps:

1.  **Fork the Repository:** Create a fork of the `chirag127/TubeScript-YouTube-API-Automation-CLI-Tool` repository.
2.  **Clone Your Fork:** Clone your forked repository to your local machine:
    bash
    git clone https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool.git
    cd TubeScript-YouTube-API-Automation-CLI-Tool
    
3.  **Create a New Branch:** Create a feature branch for your changes:
    bash
    git checkout -b feat/your-feature-name
    
    (Use `fix/` for bug fixes, `feat/` for new features, `chore/` for maintenance, etc.)
4.  **Install Dependencies:** Ensure you have the development dependencies installed.
    bash
    uv pip install --dev
    
5.  **Make Your Changes:** Implement your feature or fix the bug.
6.  **Run Tests:** Ensure all tests pass:
    bash
    pytest
    
    *If you are adding new functionality, please add corresponding tests.*
7.  **Lint and Format:** Ensure your code adheres to project standards:
    bash
    ruff check .
    ruff format .
    
8.  **Commit Your Changes:** Commit your changes with a clear and descriptive message.
    bash
    git commit -m "feat: Add new feature X for YouTube API automation"
    
9.  **Push to Your Fork:** Push your changes to your feature branch on your fork:
    bash
    git push origin feat/your-feature-name
    
10. **Open a Pull Request:** Create a pull request from your feature branch on your fork to the `main` branch of the `chirag127/TubeScript-YouTube-API-Automation-CLI-Tool` repository.

### Development Workflow

*   **Environment:** We use Python 3.10+ with `uv` for dependency management.
*   **Linting & Formatting:** `Ruff` is used for static analysis and code formatting. It enforces the project's coding standards.
*   **Testing:** `Pytest` is used for unit and integration testing. Ensure all tests pass before submitting a PR.
*   **AI Integration:** For AI-related changes, ensure you are familiar with the `Google Gemini API` and have appropriate API keys configured (refer to development setup instructions).

### Pull Request Guidelines

*   **Descriptive Title:** Use a clear title that summarizes the changes.
*   **Detailed Description:** Explain what the PR does, why it's needed, and how it was tested.
*   **Link to Issue:** If the PR closes an issue, reference it using keywords like `Closes #123`.
*   **Code Reviews:** Be prepared to respond to feedback from reviewers.

### Dependencies

When adding new dependencies, please ensure they are necessary, well-maintained, and compatible with the project's license (CC BY-NC).

## Getting Started

Refer to the `README.md` file for detailed setup and installation instructions.

Thank you for contributing!
