# Security Policy

At TubeScript-YouTube-API-Automation-CLI-Tool, we are committed to ensuring the security and integrity of our project and protecting our users. We take all security vulnerabilities seriously and appreciate the community's efforts in identifying and responsibly disclosing them.

## Supported Versions

We prioritize security updates for the latest major release of TubeScript-YouTube-API-Automation-CLI-Tool. Users are strongly encouraged to keep their installations updated to the most recent stable version to benefit from the latest security patches and features.

## Reporting a Vulnerability

If you discover a security vulnerability within TubeScript-YouTube-API-Automation-CLI-Tool, please report it to us as soon as possible through our **private reporting channel**. This allows us to address the issue discreetly before public disclosure, minimizing potential harm.

**Please DO NOT open a public GitHub issue for security vulnerabilities.**

### How to Report:

1.  **GitHub Security Advisories (Preferred):** The most secure and recommended method is to use GitHub's private vulnerability reporting feature. You can find this option on the project's repository page:
    *   Go to [https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool](https://github.com/chirag127/TubeScript-YouTube-API-Automation-CLI-Tool)
    *   Navigate to the "Security" tab.
    *   Click on "Report a vulnerability."

2.  **Direct Email:** If GitHub Security Advisories are not suitable for any reason, you may send an email directly to the maintainer:
    *   `chirag127@proton.me`

### When Reporting, Please Include:

*   A clear and concise description of the vulnerability.
*   Steps to reproduce the vulnerability.
*   The affected version(s) of TubeScript-YouTube-API-Automation-CLI-Tool.
*   The potential impact of the vulnerability.
*   Any suggested remediation (if known).

## Our Security Disclosure Process

Upon receiving a security report, we will adhere to the following process:

1.  **Acknowledgment:** We will acknowledge receipt of your report within **48 hours**.
2.  **Investigation:** Our team will investigate the reported vulnerability thoroughly.
3.  **Resolution:** We will work to develop a patch or mitigation strategy.
4.  **Notification:** We will keep you informed of our progress and, upon resolution, will coordinate with you regarding public disclosure. We aim to release a fix within **7-14 days** for critical vulnerabilities.
5.  **Credit:** We will credit you for your responsible disclosure, if you wish to be acknowledged, in the security advisory or release notes.

## Best Practices for Users

To help ensure the security of your deployments of TubeScript-YouTube-API-Automation-CLI-Tool:

*   **Keep Updated:** Always use the latest stable version of the tool. Updates often include security patches.
*   **Dependency Management:** Regularly update your Python dependencies using `uv` to pull the latest secure versions. For example:
    bash
    uv update
    
*   **API Key Management:** Treat your YouTube API keys and other credentials as sensitive information. Never hardcode them directly into your scripts or commit them to version control. Use environment variables or a secure configuration management system.
*   **Input Validation:** Be cautious with user-supplied inputs if you extend the tool. Ensure all external inputs are properly sanitized and validated.
*   **System Security:** Ensure the environment where TubeScript-YouTube-API-Automation-CLI-Tool is run is secure and follows general security best practices.

## Development Security Guidelines (for Contributors)

Contributors to TubeScript-YouTube-API-Automation-CLI-Tool are expected to adhere to secure coding practices:

*   **Input Validation & Sanitization:** All external inputs and data received from the YouTube API should be meticulously validated and sanitized to prevent common vulnerabilities like injection attacks.
*   **Error Handling:** Implement robust error handling to prevent sensitive information disclosure through error messages.
*   **Dependency Audits:** Regularly use tools like `uv` to audit and update dependencies, ensuring no known vulnerabilities are introduced.
*   **Least Privilege:** Design components to operate with the minimum necessary permissions.
*   **Data Protection:** Handle any collected data (e.g., from YouTube API responses) with care, especially if it contains personal or sensitive information. Ensure temporary files are securely handled and deleted.

We appreciate your collaboration in making TubeScript-YouTube-API-Automation-CLI-Tool a secure and reliable tool.