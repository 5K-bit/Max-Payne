"""Optional local HTTP API and zero-build dashboard."""

from __future__ import annotations
from pathlib import Path
from maxpayne.core.engine import MaxPayneEngine
from maxpayne.core.history import HistoryStore
from maxpayne.core.profiles import profile_names
from maxpayne.core.remediation import RemediationExecutor

DASHBOARD_HTML = """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>MaxPayne Health Console</title><style>:root{color-scheme:dark;font-family:Inter,system-ui,sans-serif}body{margin:0;background:#0b0d10;color:#eef2f7}main{max-width:1180px;margin:auto;padding:28px}header{display:flex;justify-content:space-between;gap:16px;align-items:center;margin-bottom:20px}h1{margin:0}.muted{color:#8d98a7}.controls{display:flex;gap:10px}select,button{background:#151a21;color:#eef2f7;border:1px solid #2d3642;border-radius:8px;padding:9px 12px}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:18px 0}.card{background:#11151b;border:1px solid #232b35;border-radius:12px;padding:16px}.metric{font-size:28px;font-weight:700;margin-top:6px}.pass{color:#6ee7a8}.warn{color:#f5c96a}.fail{color:#ff7a88}table{width:100%;border-collapse:collapse}th,td{padding:11px 10px;border-bottom:1px solid #232b35;text-align:left;vertical-align:top}th{color:#8d98a7;font-size:12px;text-transform:uppercase}.pill{display:inline-block;border:1px solid currentColor;border-radius:999px;padding:2px 7px;font-size:11px;font-weight:700}@media(max-width:800px){.grid{grid-template-columns:repeat(2,1fr)}header{align-items:flex-start;flex-direction:column}}</style></head><body><main><header><div><h1>MAXPAYNE</h1><div class='muted'>Local health & recovery engine</div></div><div class='controls'><select id='profile'></select><button id='scan'>Run diagnostic</button></div></header><div id='error' class='fail'></div><section class='grid'><div class='card'><div class='muted'>Overall</div><div id='overall' class='metric'>—</div></div><div class='card'><div class='muted'>Pass</div><div id='pass' class='metric pass'>0</div></div><div class='card'><div class='muted'>Warn</div><div id='warn' class='metric warn'>0</div></div><div class='card'><div class='muted'>Fail</div><div id='fail' class='metric fail'>0</div></div></section><section class='card'><strong>Findings</strong> <span id='meta' class='muted'></span><table><thead><tr><th>Status</th><th>Check</th><th>Message</th><th>Suggestion</th></tr></thead><tbody id='rows'></tbody></table></section></main><script>const p=document.querySelector('#profile'),r=document.querySelector('#rows'),e=document.querySelector('#error');const esc=v=>String(v??'').replace(/[&<>\"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;',"'":'&#039;'}[c]));async function init(){const h=await fetch('/api/health').then(x=>x.json());h.profiles.forEach(n=>{const o=document.createElement('option');o.value=n;o.textContent=n;p.append(o)});p.value='workstation'}async function scan(){e.textContent='';try{const d=await fetch('/api/diagnose?profile='+encodeURIComponent(p.value),{method:'POST'}).then(async x=>{if(!x.ok)throw new Error((await x.json()).detail||'Diagnostic failed');return x.json()});document.querySelector('#overall').textContent=d.overall_status.toUpperCase();document.querySelector('#overall').className='metric '+d.overall_status;['pass','warn','fail'].forEach(k=>document.querySelector('#'+k).textContent=d.summary[k]);document.querySelector('#meta').textContent=`${d.node} • ${d.duration_ms} ms • ${d.scan_id.slice(0,8)}`;r.innerHTML=d.results.map(x=>`<tr><td><span class='pill ${esc(x.status)}'>${esc(x.status.toUpperCase())}</span></td><td><code>${esc(x.check_id)}</code><div class='muted'>${esc(x.severity)}</div></td><td>${esc(x.message)}${x.details?`<div class='muted'>${esc(x.details)}</div>`:''}</td><td>${esc(x.suggestion)}</td></tr>`).join('')}catch(x){e.textContent=x.message}}document.querySelector('#scan').addEventListener('click',scan);init().then(scan).catch(x=>e.textContent=x.message)</script></body></html>"""


def default_history_path() -> Path:
    return Path.home() / ".maxpayne" / "history.db"


def create_app(engine: MaxPayneEngine | None = None, remediation_executor: RemediationExecutor | None = None):
    try:
        from fastapi import FastAPI, HTTPException
        from fastapi.responses import HTMLResponse
    except ImportError as exc:
        raise RuntimeError('Web support is not installed. Run `python -m pip install -e ".[web]"`.') from exc
    active_engine = engine or MaxPayneEngine(history=HistoryStore(default_history_path()))
    active_executor = remediation_executor or RemediationExecutor()
    app = FastAPI(title="MaxPayne", version="0.2.0")
    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str: return DASHBOARD_HTML
    @app.get("/api/health")
    def health() -> dict[str, object]: return {"status":"ok","service":"maxpayne","version":"0.2.0","profiles":profile_names(),"remediations":active_executor.registry.list()}
    @app.post("/api/diagnose")
    def diagnose(profile: str = "all") -> dict[str, object]:
        try: return active_engine.diagnose(profile=profile).to_dict()
        except ValueError as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    @app.get("/api/history")
    def history(limit: int = 20) -> list[dict[str, object]]:
        return [] if active_engine.history is None else active_engine.history.list_scans(limit=limit)
    @app.post("/api/remediate/{remediation_id}")
    def remediate(remediation_id: str, parameters: dict[str,str] | None = None, apply: bool = False, approved: bool = False) -> dict[str, object]:
        try: return active_executor.execute(remediation_id, parameters=parameters, dry_run=not apply, approved=approved).to_dict()
        except (ValueError, TypeError) as exc: raise HTTPException(status_code=400, detail=str(exc)) from exc
    return app


def run_server(host: str = "127.0.0.1", port: int = 8788) -> None:
    try: import uvicorn
    except ImportError as exc: raise RuntimeError('Web support is not installed. Run `python -m pip install -e ".[web]"`.') from exc
    uvicorn.run(create_app(), host=host, port=port)
