import json
import os
import re
import sys
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import requests


def _must_env(name: str) -> str:
    v = os.getenv(name, "").strip()
    if not v:
        raise SystemExit(f"Missing env var: {name}")
    return v


def _opt_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _j(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, indent=2, default=str)


@dataclass
class SmokeConfig:
    base_url: str
    email: str
    password: str
    client: str
    campaign_name: str
    sheet_hhs: str
    sheet_ohs: str
    sheet_ctv: str
    sheet_disney: str
    sheet_netflix: str
    sheet_spotify: str
    sheet_youtube: str
    timeout_sec: int = 40


def _norm_base(url: str) -> str:
    return url.rstrip("/")


def login(sess: requests.Session, cfg: SmokeConfig) -> None:
    r = sess.post(
        f"{cfg.base_url}/api/auth/login",
        json={"email": cfg.email, "password": cfg.password},
        timeout=cfg.timeout_sec,
    )
    try:
        data = r.json()
    except Exception:
        raise AssertionError(f"Login: expected JSON, got status={r.status_code}, body={r.text[:2000]}")
    assert r.status_code == 200, f"Login status={r.status_code} body={data}"
    assert data.get("success") is True, f"Login failed: {data}"


def generate_multicanal(sess: requests.Session, cfg: SmokeConfig) -> Dict[str, Any]:
    payload = {
        "client": cfg.client,
        "campaign_name": cfg.campaign_name,
        "channels": [
            {
                "channel_name": "HHS",
                "action_description": "Smoke HHS",
                "kpi": "CPM",
                "sheet_id": cfg.sheet_hhs,
                "use_footfall": 1,
            },
            {
                "channel_name": "OHS",
                "action_description": "Smoke OHS",
                "kpi": "CPM",
                "sheet_id": cfg.sheet_ohs,
                "use_footfall": 1,
            },
            {
                "channel_name": "CTV",
                "action_description": "Smoke CTV",
                "kpi": "CPV",
                "sheet_id": cfg.sheet_ctv,
                "use_footfall": 0,
            },
            {
                "channel_name": "Disney",
                "action_description": "Smoke Disney",
                "kpi": "CPV",
                "sheet_id": cfg.sheet_disney,
                "use_footfall": 0,
            },
            {
                "channel_name": "Netflix",
                "action_description": "Smoke Netflix",
                "kpi": "CPV",
                "sheet_id": cfg.sheet_netflix,
                "use_footfall": 0,
            },
            {
                "channel_name": "Spotify",
                "action_description": "Smoke Spotify",
                "kpi": "CPE",
                "sheet_id": cfg.sheet_spotify,
                "use_footfall": 0,
            },
            {
                "channel_name": "Youtube",
                "action_description": "Smoke Youtube",
                "kpi": "CPV",
                "sheet_id": cfg.sheet_youtube,
                "use_footfall": 0,
            },
        ],
    }
    r = sess.post(
        f"{cfg.base_url}/api/generate-dashboard-multicanal",
        json=payload,
        timeout=cfg.timeout_sec,
    )
    data = r.json() if "application/json" in (r.headers.get("content-type") or "") else {"raw": r.text}
    assert r.status_code == 200, f"Generate multicanal status={r.status_code} body={_j(data)}"
    assert data.get("success") is True, f"Generate multicanal failed: {_j(data)}"
    return data


def fetch_dashboard_html(cfg: SmokeConfig, campaign_key: str) -> str:
    # Dashboard is public; no need session cookie.
    r = requests.get(f"{cfg.base_url}/api/dashboard/{campaign_key}", timeout=cfg.timeout_sec)
    assert r.status_code == 200, f"Dashboard HTML status={r.status_code} body={r.text[:2000]}"
    return r.text


def fetch_campaign_data(cfg: SmokeConfig, campaign_key: str) -> Dict[str, Any]:
    r = requests.get(f"{cfg.base_url}/api/{campaign_key}/data", timeout=cfg.timeout_sec)
    data = r.json() if "application/json" in (r.headers.get("content-type") or "") else {"raw": r.text}
    assert r.status_code == 200, f"Campaign data status={r.status_code} body={_j(data)}"
    assert data.get("success") is True, f"Campaign data failed: {_j(data)}"
    return data.get("data") or {}


def extract_embedded_data(html: str) -> Optional[Dict[str, Any]]:
    # window.EMBEDDED_CAMPAIGN_DATA = {...};
    m = re.search(r"window\.EMBEDDED_CAMPAIGN_DATA\s*=\s*({.*?})\s*;\s*</script>", html, re.DOTALL)
    if not m:
        return None
    raw = m.group(1)
    try:
        return json.loads(raw)
    except Exception:
        return None


def assert_new_multicanal_template(html: str) -> None:
    # Strong markers for our new template.
    required = [
        'id="tabsNav"',
        'id="footfallPanelsMount"',
        "renderFootfallTabs",
        "setupTabs(",
        "channelSelect",
    ]
    missing = [s for s in required if s not in html]
    assert not missing, f"Expected new multicanal footfall template markers missing: {missing}"


def assert_has_footfall_sources(html: str) -> Tuple[int, str]:
    embedded = extract_embedded_data(html)
    assert embedded is not None, "Expected window.EMBEDDED_CAMPAIGN_DATA to be embedded in HTML"
    sources = embedded.get("footfall_sources")
    assert isinstance(sources, list), f"Expected footfall_sources list, got: {type(sources)}"
    return len(sources), _j(sources[:2])


def main() -> int:
    cfg = SmokeConfig(
        base_url=_norm_base(_must_env("BASE_URL")),
        email=_must_env("SMOKE_EMAIL"),
        password=_must_env("SMOKE_PASSWORD"),
        client=_opt_env("SMOKE_CLIENT", "SMOKE"),
        campaign_name=_opt_env("SMOKE_CAMPAIGN_NAME", f"smoke_multicanal_{int(time.time())}"),
        sheet_hhs=_must_env("SMOKE_SHEET_HHS"),
        sheet_ohs=_must_env("SMOKE_SHEET_OHS"),
        sheet_ctv=_must_env("SMOKE_SHEET_CTV"),
        sheet_disney=_must_env("SMOKE_SHEET_DISNEY"),
        sheet_netflix=_must_env("SMOKE_SHEET_NETFLIX"),
        sheet_spotify=_must_env("SMOKE_SHEET_SPOTIFY"),
        sheet_youtube=_must_env("SMOKE_SHEET_YOUTUBE"),
        timeout_sec=int(_opt_env("SMOKE_TIMEOUT_SEC", "40") or "40"),
    )

    print("### Smoke test config")
    print(_j({**cfg.__dict__, "password": "***"}))

    sess = requests.Session()
    sess.headers.update({"User-Agent": "south-media-ia-smoke-test/1.0"})

    print("\n### Login")
    login(sess, cfg)
    print("OK: logged in")

    print("\n### Generate multicanal")
    gen = generate_multicanal(sess, cfg)
    campaign_key = gen.get("campaign_key")
    assert campaign_key, f"Missing campaign_key in response: {gen}"
    print(f"OK: generated campaign_key={campaign_key}")

    print("\n### Fetch dashboard HTML")
    html = fetch_dashboard_html(cfg, campaign_key)
    print(f"OK: html_size={len(html)}")

    print("\n### Validate template markers")
    assert_new_multicanal_template(html)
    print("OK: new template markers present")

    print("\n### Validate embedded footfall_sources")
    n_sources, sample = assert_has_footfall_sources(html)
    print(f"OK: footfall_sources_count={n_sources}")
    print(sample)

    print("\n### Fetch /data (public)")
    data = fetch_campaign_data(cfg, campaign_key)
    print(f"OK: data_keys={sorted(list(data.keys()))[:20]}")

    print("\n✅ SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AssertionError as e:
        print("\n❌ SMOKE TEST FAILED")
        print(str(e))
        raise SystemExit(2)
