# Security

## Reporting a vulnerability

Please open a private security advisory on this repository
(Security → Advisories → Report a vulnerability). Do not post exploit details in a public issue.

## Design boundaries

- MaxPayne reads local state (Python, Git, Docker, Ollama, listening ports, optional service probes).
  It sends nothing off the machine. The only network traffic is the probes you configure.
- Remediation is dry-run by default. A mutating remediation needs `--apply` **and** `--approve`.
  A destructive remediation (such as terminating the process on a port) additionally needs `--allow-destructive`.
- The optional dashboard/API (`maxpayne serve`) binds to `127.0.0.1` by default and has no authentication.
  Do not expose it on a shared network.
- Scan history is stored unencrypted at `~/.maxpayne/history.db`. Reports can contain hostnames,
  paths and versions; review them before sharing.
