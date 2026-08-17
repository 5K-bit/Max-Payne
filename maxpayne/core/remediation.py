"""Policy-controlled remediation layer for automation-safe repair actions."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Callable, Literal

from maxpayne.core.result import CheckResult

Safety = Literal["SAFE", "MUTATING", "DESTRUCTIVE"]
Handler = Callable[[dict[str, str]], CheckResult]


@dataclass(slots=True)
class RemediationDefinition:
    remediation_id: str
    description: str
    safety: Safety
    handler: Handler
    parameters: tuple[str, ...] = ()
    def public_dict(self) -> dict[str, object]:
        return {"remediation_id": self.remediation_id, "description": self.description, "safety": self.safety, "parameters": list(self.parameters)}


@dataclass(slots=True)
class RemediationPolicy:
    allow_mutating: bool = True
    allow_destructive: bool = False
    require_approval: bool = True
    def permits(self, safety: Safety, *, approved: bool) -> tuple[bool, str | None]:
        if self.require_approval and not approved:
            return False, "Explicit approval is required."
        if safety == "DESTRUCTIVE" and not self.allow_destructive:
            return False, "Destructive remediations are disabled by policy."
        if safety == "MUTATING" and not self.allow_mutating:
            return False, "Mutating remediations are disabled by policy."
        return True, None


@dataclass(slots=True)
class RemediationExecution:
    remediation_id: str
    safety: Safety
    dry_run: bool
    approved: bool
    executed: bool
    status: str
    message: str
    result: CheckResult | None = None
    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        if self.result is not None:
            payload["result"] = self.result.to_dict(lowercase_status=True)
        return payload


class RemediationRegistry:
    def __init__(self) -> None:
        self._definitions: dict[str, RemediationDefinition] = {}
    def register(self, definition: RemediationDefinition) -> None:
        if definition.remediation_id in self._definitions:
            raise ValueError(f"Remediation already registered: {definition.remediation_id}")
        self._definitions[definition.remediation_id] = definition
    def get(self, remediation_id: str) -> RemediationDefinition:
        try:
            return self._definitions[remediation_id]
        except KeyError as exc:
            raise ValueError(f"Unknown remediation: {remediation_id}") from exc
    def list(self) -> list[dict[str, object]]:
        return [definition.public_dict() for definition in self._definitions.values()]


class RemediationExecutor:
    def __init__(self, registry: RemediationRegistry | None = None, policy: RemediationPolicy | None = None) -> None:
        self.registry = registry or default_remediation_registry()
        self.policy = policy or RemediationPolicy()
    def execute(self, remediation_id: str, *, parameters: dict[str, str] | None = None, dry_run: bool = True, approved: bool = False) -> RemediationExecution:
        definition = self.registry.get(remediation_id)
        supplied = parameters or {}
        missing = [name for name in definition.parameters if not supplied.get(name)]
        if missing:
            return RemediationExecution(remediation_id, definition.safety, dry_run, approved, False, "blocked", f"Missing parameters: {', '.join(missing)}")
        if dry_run:
            return RemediationExecution(remediation_id, definition.safety, True, approved, False, "planned", f"Would execute: {definition.description}")
        permitted, reason = self.policy.permits(definition.safety, approved=approved)
        if not permitted:
            return RemediationExecution(remediation_id, definition.safety, False, approved, False, "blocked", reason or "Blocked by policy.")
        result = definition.handler(supplied)
        return RemediationExecution(remediation_id, definition.safety, False, approved, True, result.status.lower(), result.message, result)


def default_remediation_registry() -> RemediationRegistry:
    from maxpayne.heal import heal_dependency, heal_env_files, heal_git_config, heal_port
    registry = RemediationRegistry()
    registry.register(RemediationDefinition("env.generate_example", "Generate a sanitized .env.example from the current .env file.", "MUTATING", lambda _params: heal_env_files()))
    registry.register(RemediationDefinition("git.configure_identity", "Configure missing global Git identity values.", "MUTATING", lambda _params: heal_git_config(interactive=False)))
    registry.register(RemediationDefinition("python.install_dependency", "Install a Python package into the active interpreter environment.", "MUTATING", lambda params: heal_dependency(params["package"]), ("package",)))
    registry.register(RemediationDefinition("port.free", "Terminate the process listening on a local TCP port.", "DESTRUCTIVE", lambda params: heal_port(int(params["port"]), interactive=False), ("port",)))
    return registry
