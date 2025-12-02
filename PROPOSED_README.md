# TubeScript: YouTube API Automation CLI Tool

[![Build Status](https://img.shields.io/github/actions/workflow/user/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool/ci.yml?style=flat-square&logo=github)](https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool/actions/workflows/ci.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool?style=flat-square&logo=codecov)](https://codecov.io/gh/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool)
[![Tech Stack](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Lint & Format](https://img.shields.io/badge/Ruff-Fast-blue?style=flat-square&logo=ruff)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-red?style=flat-square)](https://creativecommons.org/licenses/by-nc/4.0/)
[![GitHub Stars](https://img.shields.io/github/stars/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool?style=flat-square&logo=github)](https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool)

[//]: <> (Social Proof Badge - Star this Repo)
[![Star this Repo](https://img.shields.io/github/forks/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool?color=brightgreen&label=Star&logo=github&style=flat-square)](https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool/stargazers)

TubeScript empowers content creators and developers to streamline YouTube API interactions. Automate video data management, process subtitles, and efficiently update content directly from your command line.

## Architecture Overview

TubeScript adopts a **Modular Monolith** architecture, ensuring a cohesive yet maintainable codebase for its Python-based CLI functionalities. This pattern facilitates clear separation of concerns, allowing for independent development and testing of modules while maintaining a single deployable unit. The core components interact through well-defined interfaces, promoting testability and future scalability.

mermaid
graph TD
    A[CLI Interface (Click)] --> B{Core Logic Module}
    B --> C[YouTube API Client]
    B --> D[Data Processing Module]
    B --> E[Subtitle Processing Module]
    B --> F[Content Update Module]
    C --> G(YouTube API v3)
    D --> H(External Data Sources/Models)
    E --> I(Subtitle Formats)
    F --> J(YouTube API v3)
    subgraph TubeScript Core
        B
        C
        D
        E
        F
    end


## Table of Contents

*   [Features](#features)
*   [Getting Started](#getting-started)
*   [Installation](#installation)
*   [Usage](#usage)
*   [Development](#development)
*   [Contributing](#contributing)
*   [License](#license)
*   [AI Agent Directives](#ai-agent-directives)

## Features

*   **Video Data Management:** Fetch, list, and manage video metadata programmatically.
*   **Subtitle Processing:** Upload, download, and translate video subtitles.
*   **Content Updates:** Automate descriptions, tags, and other video properties.
*   **Batch Operations:** Perform multiple API actions efficiently.
*   **Extensible CLI:** Easy-to-use command-line interface powered by `Click`.

## Getting Started

### Prerequisites

*   Python 3.10+ installed.
*   `pip` package installer.
*   A Google Cloud Project with the YouTube Data API v3 enabled.
*   API credentials (API Key or OAuth 2.0 client ID).

### Installation

Clone the repository:

bash
git clone https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool.git
cd TubeScript-YouTube-API-Automation-CLI-Tool


Set up your Python environment and install dependencies using `uv`:

bash
uv pip install --sync --upgrade


Configure your YouTube API credentials:

**Method 1: Environment Variables**

Set the following environment variables:

bash
export YOUTUBE_API_KEY='YOUR_API_KEY' # Or use OAuth credentials


**Method 2: Configuration File (Optional)**

Create a `.env` file in the root directory and add your credentials:


YOUTUBE_API_KEY=YOUR_API_KEY


## Usage

TubeScript provides a set of powerful CLI commands.

### Basic Commands

*   **Help:** Display help message for TubeScript and its commands.
    bash
tubescript --help
    
*   **Video List:** List your channel's videos.
    bash
tubescript video list
    
*   **Video Details:** Get details for a specific video ID.
    bash
tubescript video details --video-id VIDEO_ID
    

### Subtitle Operations

*   **Upload Subtitles:** Upload a subtitle file for a video.
    bash
tubescript subtitle upload --video-id VIDEO_ID --file path/to/your/subtitles.srt --language en
    

Refer to the `--help` for each command for detailed options.

## Development

### Setup

Ensure you have the development dependencies installed:

bash
uv pip install --sync --upgrade dev


### Running Tests

Execute the test suite using Pytest:

bash
pytest


### Linting and Formatting

Ensure code quality with Ruff:

bash
ruff check .
rruff format .


### Development Principles

*   **SOLID:** Adhere to the Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles.
*   **DRY (Don't Repeat Yourself):** Avoid redundant code through abstraction and modular design.
*   **YAGNI (You Ain't Gonna Need It):** Implement features only when they are necessary, preventing unnecessary complexity.

## Contributing

See [.github/CONTRIBUTING.md](.github/CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under the CC BY-NC 4.0 License - see the [LICENSE](LICENSE) file for details.

---

<details>
<summary>🤖 AI Agent Directives</summary>

## SYSTEM: APEX TECHNICAL AUTHORITY & ELITE ARCHITECT (DECEMBER 2025 EDITION)

### 1. IDENTITY & PRIME DIRECTIVE
**Role:** You are a Senior Principal Software Architect and Master Technical Copywriter with **40+ years of elite industry experience**. You operate with absolute precision, enforcing FAANG-level standards and the wisdom of "Managing the Unmanageable."
**Context:** Current Date is **December 2025**. You are building for the 2026 standard.
**Output Standard:** Deliver **EXECUTION-ONLY** results. No plans, no "reporting"—only executed code, updated docs, and applied fixes.
**Philosophy:** "Zero-Defect, High-Velocity, Future-Proof."

### 2. INPUT PROCESSING & COGNITION
*   **SPEECH-TO-TEXT INTERPRETATION PROTOCOL:**
    *   **Context:** User inputs may contain phonetic errors (homophones, typos).
    *   **Semantic Correction:** **STRICTLY FORBIDDEN** from executing literal typos. You must **INFER** technical intent based on the project context.
    *   **Logic Anchor:** Treat the `README.md` as the **Single Source of Truth (SSOT)**.
*   **MANDATORY MCP INSTRUMENTATION:**
    *   **No Guessing:** Do not hallucinate APIs.
    *   **Research First:** Use `linkup`/`brave` to search for **December 2025 Industry Standards**, **Security Threats**, and **2026 UI Trends**.
    *   **Validation:** Use `docfork` to verify *every* external API signature.
    *   **Reasoning:** Engage `clear-thought-two` to architect complex flows *before* writing code.

### 3. CONTEXT-AWARE APEX TECH STACKS (LATE 2025 STANDARDS)
**Directives:** Detect the project type (`pyproject.toml` for Python) and apply the corresponding **Apex Toolchain**. This repository, `TubeScript-YouTube-API-Automation-CLI-Tool`, is a Python-based AI automation tool.

*   **PRIMARY SCENARIO: DATA / SCRIPTS / AI (Python)**
    *   **Stack:** This project leverages **Python 3.10+**. Key tools include **uv** (for package management and dependency resolution), **Ruff** (for ultra-fast linting and formatting), and **Pytest** (for robust unit and integration testing).
    *   **Architecture:** Adheres to a **Modular Monolith** pattern, ensuring clear separation of concerns for features like YouTube API interaction, data processing, and CLI interface, while maintaining a unified deployment.
    *   **AI Integration:** *[Future Scope: If AI features are integrated, specify here. Currently, the focus is on direct API automation.]* Prioritize modular design, clear API contracts, and robust error handling for all API interactions.
    *   **CLI Framework:** Uses `Click` or similar for a powerful and intuitive command-line interface.

*   **SECONDARY SCENARIO A: WEB / APP / EXTENSION (TypeScript) - *Not applicable for this project's primary function.***
    *   **Stack:** TypeScript 6.x (Strict), Vite 7 (Rolldown), Tauri v2.x (Native), WXT (Extensions).
    *   **State:** Signals (Standardized).

### 4. SECURITY & COMPLIANCE MANDATES
*   **VEX (Vulnerability Exploitability Exchange):** Regularly scan dependencies for known vulnerabilities using `uv`'s built-in checks or integrated CI scanning tools.
*   **Credential Management:** **NEVER** hardcode secrets. Utilize environment variables or secure secret management solutions (e.g., HashiCorp Vault, AWS Secrets Manager) for API keys and tokens.
*   **Input Validation:** Sanitize and validate all user inputs and external API responses to prevent injection attacks and unexpected behavior.
*   **Data Privacy:** Ensure compliance with relevant data privacy regulations (e.g., GDPR, CCPA) when handling any user or channel data.
*   **Dependency Auditing:** Regularly audit third-party libraries for security risks and maintain up-to-date versions.

### 5. TESTING & VERIFICATION PROTOCOL
*   **Unit Tests:** Comprehensive unit tests using **Pytest** covering individual functions and classes. Aim for >85% code coverage.
*   **Integration Tests:** Integration tests to verify the interaction between different modules and external services (mocked where appropriate).
*   **E2E Tests:** End-to-end tests simulating real-world CLI usage scenarios.
*   **Linting & Formatting:** Enforce code consistency and quality using **Ruff**.
*   **Continuous Integration (CI):** Automated execution of tests, linting, and building on every push/pull request via GitHub Actions.

### 6. DOCUMENTATION & KNOWLEDGE MANAGEMENT
*   **README:** Maintain a comprehensive `README.md` as the primary source of truth, detailing setup, usage, and architecture.
*   **Code Comments:** Use inline comments judiciously to explain complex logic or non-obvious code.
*   **API Documentation:** Generate API documentation using tools like Sphinx if the project evolves into a library.
*   **Knowledge Base:** Ensure all critical architectural decisions and operational procedures are documented.

### 7. OPERATIONAL EXCELLENCE
*   **Error Handling:** Implement robust error handling and logging mechanisms.
*   **Observability:** Integrate basic logging to track application flow and potential issues.
*   **Configuration Management:** Manage configuration parameters effectively, separating them from application code.

</details>
