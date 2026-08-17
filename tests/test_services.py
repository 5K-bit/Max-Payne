from maxpayne.checks import services_check


def test_services_check_is_noop_when_unconfigured(monkeypatch) -> None:
    monkeypatch.delenv("MAXPAYNE_SERVICE_URLS",raising=False); results=services_check.run_service_checks(); assert len(results)==1; assert results[0].name=="services.configuration"; assert results[0].status=="PASS"

def test_service_url_evidence_redacts_credentials(monkeypatch) -> None:
    monkeypatch.setenv("MAXPAYNE_SERVICE_URLS","demo=http://user:secret@127.0.0.1:9/health"); monkeypatch.setenv("MAXPAYNE_SERVICE_TIMEOUT","0.25"); results=services_check.run_service_checks(); assert len(results)==1; assert "secret" not in str(results[0].evidence); assert "user" not in str(results[0].evidence)
