# TubeScript: YouTube API Automation CLI Tool

[![Build Status](https://img.shields.io/github/actions/workflow/user/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool/ci.yml?style=flat-square&logo=github)](https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool/actions/workflows/ci.yml)
[![Code Coverage](https://img.shields.io/codecov/c/github/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool?style=flat-square&logo=codecov)](https://codecov.io/gh/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg?style=flat-square&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgray.svg?style=flat-square)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool.svg?style=flat-square&logo=github)](https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool)

--- 

**Streamline your YouTube channel operations with TubeScript, a powerful Python CLI tool designed for efficient YouTube API automation. Effortlessly manage video data, process subtitles, and automate content updates to elevate your YouTube workflow.**

## 🚀 Overview

TubeScript provides a robust command-line interface for interacting with the YouTube Data API v3 and other related services. It's built to simplify complex, repetitive tasks, allowing creators and developers to focus on content strategy rather than manual management.

## 🏗️ Architecture

TubeScript employs a **Modular Monolith** architecture, ensuring a maintainable and scalable codebase while keeping all functionalities within a single project. This design promotes clear separation of concerns for distinct features like API interaction, data processing, subtitle management, and the CLI interface.

ascii
TubeScript-YouTube-API-Automation-CLI-Tool/
├── src/
│   ├── __init__.py
│   ├── cli.py           # Main CLI entry point
│   ├── youtube_api/
│   │   ├── __init__.py
│   │   ├── client.py      # YouTube API client
│   │   ├── videos.py      # Video management operations
│   │   └── subtitles.py   # Subtitle processing operations
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py     # Common utility functions
│   └── ...              # Other modules (e.g., authentication, data parsing)
├── tests/
│   ├── __init__.py
│   ├── youtube_api/
│   │   ├── test_client.py
│   │   └── test_videos.py
│   └── ...              # Other test modules
├── scripts/
│   └── ...              # Helper scripts (e.g., setup, deployment)
├── .gitignore
├── pyproject.toml     # Project configuration and dependencies
├── README.md
├── LICENSE
└── ...


## 📚 Table of Contents

*   [Overview](#-overview)
*   [Architecture](#-architecture)
*   [Table of Contents](#-table-of-contents)
*   [🤖 AI Agent Directives](#-ai-agent-directives)
*   [🛠️ Development Standards](#-development-standards)
    *   [Installation](#installation)
    *   [Usage](#usage)
    *   [Core Principles](#core-principles)
*   [💡 Contributing](#-contributing)
*   [📄 License](#-license)

## 🤖 AI Agent Directives

<details>
<summary>View Agent Directives</summary>

This section details the operational protocols and technical stack configurations for AI agents interacting with this repository.

### 1. Identity & Prime Directive

*   **Role:** Senior Principal Software Architect, Master Technical Copywriter, and DevOps Strategist with **40+ years of elite industry experience**. Operating with absolute precision, enforcing FAANG-level standards and the wisdom of "Managing the Unmanageable." 
*   **Context:** Current Date is **December 2025**. Building for the 2026 standard.
*   **Output Standard:** **EXECUTION-ONLY**. No plans, no reporting—only executed code, updated docs, and applied fixes.
*   **Philosophy:** "Zero-Defect, High-Velocity, Future-Proof."

### 2. Input Processing & Cognition

*   **Speech-to-Text Interpretation Protocol:** 
    *   **Context:** User inputs may contain phonetic errors (homophones, typos).
    *   **Semantic Correction:** **STRICTLY FORBIDDEN** from executing literal typos. You must **INFER** technical intent based on the project context.
    *   **Logic Anchor:** Treat the `README.md` as the **Single Source of Truth (SSOT)**.
*   **Mandatory MCP Instrumentation:**
    *   **No Guessing:** Do not hallucinate APIs.
    *   **Research First:** Use `linkup`/`brave` to search for **December 2025 Industry Standards**, **Security Threats**, and **2026 UI Trends**.
    *   **Validation:** Use `docfork` to verify *every* external API signature.
    *   **Reasoning:** Engage `clear-thought-two` to architect complex flows *before* writing code.

### 3. Context-Aware Apex Tech Stacks (Late 2025 Standards)

*   **Project Type:** Python-based AI Automation CLI Tool.
*   **Primary Scenario: DATA / SCRIPTS / AI (Python)**
    *   **Stack:** **Python 3.10+**. Leveraging **uv** (package management), **Ruff** (linting/formatting), and **Pytest** (testing).
    *   **Architecture:** **Modular Monolith**. Features clear separation of concerns for API interaction, AI processing, and CLI interface.
    *   **AI Integration:** Integrated with **Google Gemini API** (`gemini-3-pro` by default). Prioritize modular design, clear API contracts, and robust error handling for all AI model interactions.
    *   **CLI Framework:** Uses `Click` for a powerful and intuitive command-line interface.

### 4. Version Control & Deployment Strategy

*   **Branching:** GitFlow (`main`, `develop`, `feature/*`, `release/*`, `hotfix/*`).
*   **CI/CD:** GitHub Actions (`ci.yml`) orchestrating build, test, lint, and deployment pipelines.
*   **Package Management:** `uv` for managing project dependencies.

### 5. Testing & Verification Protocols

*   **Unit Tests:** **Pytest** framework. Ensure comprehensive test coverage for all core modules.
*   **Integration Tests:** **Pytest**. Verify interactions between different modules and external services (mocked where appropriate).
*   **Linting & Formatting:** **Ruff**. Enforce strict code style and quality across the entire codebase. Automated via CI.
*   **Type Checking:** **Mypy** (or Ruff's built-in type checking). Ensure static type safety.

### 6. Security Mandates

*   **Dependency Scanning:** Regular scans using tools like `Dependabot` or `Snyk`.
*   **API Key Management:** Secure storage and handling of API keys (e.g., environment variables, secrets management systems). NEVER commit secrets to the repository.
*   **Input Validation:** Rigorous validation of all user inputs and API payloads to prevent injection attacks and ensure data integrity.

</details>

## 🛠️ Development Standards

### Installation

1.  **Clone the repository:**
    bash
    git clone https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool.git
    cd TubeScript-YouTube-API-Automation-CLI-Tool
    

2.  **Set up your development environment using `uv`:**
    bash
    uv venv # Creates a virtual environment
    uv pip install --frozen-inputs -e .[dev] # Installs project and development dependencies
    
    *Note: Ensure your `pyproject.toml` is correctly configured for editable installs and development dependencies.* 

3.  **Configure API Credentials:**
    Set your YouTube API key and any other necessary credentials as environment variables.
    bash
    export YOUTUBE_API_KEY='YOUR_API_KEY'
    # Other necessary environment variables...
    

### Usage

Execute commands using the `tube_script` entry point:

bash
# Example: List videos
tube_script videos list --max-results 10

# Example: Upload a video (requires more parameters)
tube_script videos upload --file "/path/to/your/video.mp4" --title "My Awesome Video"

# Example: Process subtitles for a video
tube_script subtitles process --video-id "VIDEO_ID" --language "en"


For detailed usage of specific commands, use the `--help` flag:

bash
tube_script --help
tube_script videos --help
tube_script subtitles --help


### Core Principles

*   **SOLID:** Strive for Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, and Dependency Inversion principles.
*   **DRY (Don't Repeat Yourself):** Abstract common logic into reusable functions and classes.
*   **YAGNI (You Ain't Gonna Need It):** Implement only the features that are currently required, avoiding over-engineering.
*   **Readability:** Write clear, concise, and well-documented code.

## 💡 Contributing

Contributions are welcome! Please refer to the [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on submitting issues, pull requests, and reporting security vulnerabilities.

## 📄 License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0)**. See the [LICENSE](LICENSE) file for more details.

--- 

:star: Star this repo if you find it useful! :star:
