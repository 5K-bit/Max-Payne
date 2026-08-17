import pytest
from maxpayne.core.profiles import resolve_profile
from maxpayne.core.registry import CheckRegistry
from maxpayne.core.result import CheckResult


def test_registry_registers_and_clones_groups() -> None:
    registry=CheckRegistry(); registry.register("one",lambda:[CheckResult("one.ok","PASS","ok","none")]); clone=registry.clone(); assert registry.names()==["one"]; assert clone.get("one")()[0].name=="one.ok"

def test_registry_rejects_duplicate_without_replace() -> None:
    registry=CheckRegistry({"one":lambda:[]})
    with pytest.raises(ValueError): registry.register("one",lambda:[])

def test_profile_resolution() -> None:
    available=["python","git","node","docker","ollama","ports","env","windows","services"]
    assert resolve_profile("minimal",available)==["python","git"]; assert "services" in resolve_profile("obeos",available); assert resolve_profile("all",available)==available
