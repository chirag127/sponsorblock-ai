# Security Policy

## Supported Versions

We are committed to providing secure software. For the latest security updates and patches, please refer to the `main` branch of this repository. We aim to support and patch recent versions. Older versions might not receive security updates.

## Reporting a Vulnerability

We take security vulnerabilities very seriously. If you discover a security issue in this project, please report it responsibly.

**DO NOT** open a public issue or pull request for security vulnerabilities. Instead, please follow these steps:

1.  **Email Us:** Send a detailed report to `chirag.dev@example.com` (replace with actual security contact email if available).
2.  **Include Details:** In your report, please provide:
    *   A clear description of the vulnerability.
    *   The affected version(s) (e.g., commit hash, tag).
    *   Steps to reproduce the vulnerability.
    *   Any potential impact or mitigation.
    *   (Optional) A Proof-of-Concept (PoC) exploit.
3.  **Confidentiality:** We will acknowledge receipt of your report within **48 hours** and will work to address the issue as quickly as possible.
4.  **Disclosure Timeline:** We will aim to release a fix within **7 days** of validating the vulnerability. Public disclosure will happen after a fix is available and deployed, allowing users to update safely.

We appreciate your responsible disclosure and helping us improve the security of `TubeScript-YouTube-API-Automation-CLI-Tool`.

## Security Best Practices

This project adheres to the following security principles:

*   **Dependency Management:** Regularly scan and update dependencies using `uv` and `Ruff` to mitigate known vulnerabilities.
*   **Input Validation:** All external inputs, especially those interacting with the YouTube API, are rigorously validated and sanitized.
*   **Least Privilege:** Components operate with the minimum necessary permissions.
*   **Secure API Usage:** Adhere to best practices for interacting with the YouTube API, including proper credential management and rate limiting.
*   **Code Auditing:** Security is a consideration in code reviews and automated checks.

Thank you for helping to keep `TubeScript-YouTube-API-Automation-CLI-Tool` secure!
