# Security Policy

MaxPayne inspects developer environments and can optionally perform corrective actions. That makes the remediation boundary part of the product's security model, not an implementation detail.

## Supported version

| Version | Supported |
|---|---|
| 0.2.x | Yes |
| 0.1.x | Security fixes only |

## Security model

MaxPayne follows five rules:

1. **Diagnostics are read-first.** Health checks should prefer observation and evidence collection over mutation.
2. **Remediation is default-deny.** A finding does not grant permission to modify the machine.
3. **Dry-run is the default.** Remediations can be inspected before execution.
4. **Mutation requires explicit approval.** Applying a remediation requires an explicit apply/approval decision. Destructive actions require an additional destructive-action allowance.
5. **Evidence must not leak secrets.** Service probes and reports should redact credentials, authorization headers, tokens, and sensitive URL components.

## Remediation risk levels

| Risk | Examples | Expected behavior |
|---|---|---|
| Low | Generate a sanitized `.env.example` | Dry-run first; explicit approval to apply |
| Medium | Modify developer configuration | Dry-run first; explicit approval to apply |
| High | Terminate a process, free a port, change runtime state | Explicit approval plus destructive-action permission |

MaxPayne is designed so that an automation layer such as OBEOS can request a diagnosis without automatically inheriting permission to repair the system.

## Local-first behavior

Core diagnostics run locally. Ollama-based explanation is optional and MaxPayne continues to function using deterministic checks and heuristic explanations when no model is available.

The optional HTTP API is intended to bind locally by default. Do not expose the API directly to the public internet without an authentication and network-access layer in front of it.

## Sensitive data

Diagnostic evidence may contain process names, local paths, ports, runtime versions, hostnames, and service state. Treat exported reports as operational data.

MaxPayne should never intentionally persist:

- API keys or bearer tokens
- passwords
- cookies or session tokens
- full credential-bearing URLs
- `.env` secret values

When adding a new check, sanitize evidence before returning a `CheckResult`.

## Reporting a vulnerability

Do not publish an exploit or credential exposure in a public issue. Use GitHub's private vulnerability reporting feature for this repository when available, or contact the repository owner privately through the contact method listed on the owner's GitHub profile.

Include:

- affected MaxPayne version
- operating system and Python version
- minimal reproduction steps
- security impact
- whether the issue can cause data exposure, command execution, or unintended remediation

## Scope

Security reports are especially useful for:

- remediation policy bypasses
- command injection
- secret leakage in reports or logs
- unsafe path handling
- unintended remote exposure of the API
- privilege-boundary mistakes
- destructive actions that can execute without the documented approval flow

General bugs and feature requests should use normal GitHub issues.