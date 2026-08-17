from pathlib import Path
from maxpayne.core.engine import MaxPayneEngine
from maxpayne.core.history import HistoryStore
from maxpayne.core.remediation import RemediationDefinition, RemediationExecutor, RemediationPolicy, RemediationRegistry
from maxpayne.core.result import CheckResult
from maxpayne.core.runner import CheckRunner


def test_engine_enriches_and_persists_report(tmp_path: Path) -> None:
    runner = CheckRunner(checks={"sample": lambda: [CheckResult("sample.warning", "WARN", "Something needs attention.", "Inspect it.", evidence={"key":"value"})]})
    history = HistoryStore(tmp_path / "history.db"); engine = MaxPayneEngine(runner=runner, history=history)
    report = engine.diagnose(groups=["sample"])
    assert report.overall_status == "warn"; assert report.summary == {"pass":0,"warn":1,"fail":0}
    assert report.results[0].severity == "MEDIUM"; assert report.results[0].duration_ms is not None
    scans = history.list_scans(); assert len(scans) == 1; assert scans[0]["scan_id"] == report.scan_id
    findings = history.list_findings(report.scan_id); assert findings[0]["check_id"] == "sample.warning"; assert findings[0]["evidence"] == {"key":"value"}


def test_remediation_is_dry_run_by_default() -> None:
    calls=[]; registry=RemediationRegistry(); registry.register(RemediationDefinition("test.mutate","Mutate something.","MUTATING",lambda params:(calls.append(params) or CheckResult("test.mutate","PASS","done","none")),("value",)))
    result=RemediationExecutor(registry=registry).execute("test.mutate",parameters={"value":"x"})
    assert result.status=="planned"; assert not result.executed; assert calls==[]


def test_destructive_remediation_requires_policy_and_approval() -> None:
    registry=RemediationRegistry(); registry.register(RemediationDefinition("test.destroy","Destroy something.","DESTRUCTIVE",lambda _params:CheckResult("test.destroy","PASS","done","none")))
    blocked=RemediationExecutor(registry=registry).execute("test.destroy",dry_run=False,approved=True); assert blocked.status=="blocked"; assert not blocked.executed
    allowed=RemediationExecutor(registry=registry,policy=RemediationPolicy(allow_destructive=True)).execute("test.destroy",dry_run=False,approved=True); assert allowed.executed; assert allowed.status=="pass"
