import threading
import time
from types import SimpleNamespace
from fastapi.testclient import TestClient
from maxpayne.core.runner import CheckRunner
from maxpayne.server import create_app
from maxpayne.core.remediation import RemediationExecutor

def test_hung_check_returns_deadline_and_suppresses_overlap():
    release=threading.Event();calls=[]
    def slow():
        calls.append(1);release.wait(1);return []
    runner=CheckRunner(checks={"slow":slow},timeout_seconds=.03)
    started=time.monotonic()
    assert runner.run_group("slow")[0].name=="slow.timeout"
    assert runner.run_group("slow")[0].name=="slow.timeout"
    assert time.monotonic()-started<.3
    assert len(calls)==1
    release.set()

def test_request_supplied_approval_is_not_authority():
    client=TestClient(create_app())
    response=client.post("/api/remediate/arbitrary?apply=true&approved=true",json={})
    assert response.status_code==403
