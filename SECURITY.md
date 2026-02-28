# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 1.x     | ✅ Current          |

## Reporting a Vulnerability

If you discover a security vulnerability, please **do not** open a public issue.

Instead, email **[samsonganta@gmail.com](mailto:samsonganta@gmail.com)** with:

1. A description of the vulnerability
2. Steps to reproduce
3. Potential impact

You will receive a response within 48 hours. Confirmed issues will be patched and credited in the release notes.

## Security Considerations

- **Local Socket (port 8492)**: The backend listens on `127.0.0.1` only — not exposed to the network.
- **API Keys**: Stored in `.env` (gitignored). Never committed to the repository.
- **On-Device Processing**: Voice recognition and local LLM run entirely on your machine.
