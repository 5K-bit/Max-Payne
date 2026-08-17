"""Diagnostic profiles for common MaxPayne operating modes."""

from __future__ import annotations

PROFILE_GROUPS: dict[str, tuple[str, ...] | None] = {
    "all": None,
    "minimal": ("python", "git"),
    "workstation": ("python", "git", "node", "docker", "ollama", "ports", "env", "windows"),
    "obeos": ("python", "git", "docker", "ollama", "ports", "env", "windows", "services"),
}


def profile_names() -> list[str]:
    return list(PROFILE_GROUPS)


def resolve_profile(profile: str, available_groups: list[str]) -> list[str]:
    normalized = profile.strip().lower()
    if normalized not in PROFILE_GROUPS:
        choices = ", ".join(profile_names())
        raise ValueError(f"Unknown profile: {profile}. Available profiles: {choices}")
    configured = PROFILE_GROUPS[normalized]
    if configured is None:
        return list(available_groups)
    missing = [name for name in configured if name not in available_groups]
    if missing:
        raise ValueError(f"Profile '{normalized}' requires unavailable groups: {', '.join(missing)}")
    return list(configured)
