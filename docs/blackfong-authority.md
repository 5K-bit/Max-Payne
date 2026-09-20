# Diagnostic deadlines and Blackfong approval

CheckRunner bounds caller wait time (15 seconds by default, maximum 60), limits concurrent diagnostic workers to four, and prevents overlapping work for the same check group. A timed-out Python callable may finish in its existing daemon thread; it is not forcibly killed. Further scans cannot create an unbounded set of replacement workers.

The HTTP remediation route defaults to dry-run. Request-supplied `approved=true` is not authority. Applied requests require an injected Blackfong approval verifier. OBEOS provides `ApprovalGrants` and `build_maxpayne_app(authority)`; grants are short-lived, single-use and bound to the remediation ID and exact parameters. Issue them only from a trusted operator confirmation surface. The web API has no grant-issuance endpoint.

Standalone MaxPayne HTTP deployments therefore deny applied remediation until a trusted authority is composed into the server. The explicit local CLI approval flow remains available. This change does not apply any remediation to the host.
