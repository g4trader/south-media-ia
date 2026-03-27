#!/usr/bin/env python3
"""
Gera static/modelo_multicanal_footfall_v1.html com dados reais das planilhas Sonho (multicanal).

Uso (na raiz do repo):
  python3 build_modelo_multicanal_footfall_v1.py

Requer credenciais Google (mesmo fluxo do RealGoogleSheetsExtractor / GoogleSheetsService).
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from real_google_sheets_extractor import RealGoogleSheetsExtractor  # noqa: E402


@dataclass
class ChannelSpec:
    name: str
    sheet_id: str
    kpi: str
    use_footfall: bool


# Cliente / campanha (protótipo Sonho)
CLIENT = "Sonho"
CAMPAIGN = "Sonho Sabão em pó"

CHANNELS: List[ChannelSpec] = [
    ChannelSpec("HHS", "1QE3j5QH1Pma96PbXchf3Yvr1NAA8E8UrUOGh1oc6kWw", "CPM", True),
    ChannelSpec("OHS", "1AKLK3-wvc_QCo_0WI5hzAZh9TdMKozEAmCOEYIvRRAs", "CPM", True),
    ChannelSpec("CTV", "1Z7ve-apdWDwslJla61QEIyBZKv2T1A4FLeAkFSH7UbU", "CPV", False),
    ChannelSpec("Disney", "1tXNqOMhKEbhCeGTXr2SOgAiHwJAFGgoV5hu2iZkEUP4", "CPV", False),
    ChannelSpec("Netflix", "1YNdTgG0paromW2YrHVroIG_4jWwnt70Zl6iYyGbwylo", "CPV", False),
    ChannelSpec("Spotify", "1vG031mf1Ga4q8frTGDsbk1t-E8adfS1FdVAba1F1pZs", "CPE", False),
    ChannelSpec("Youtube", "1AY-2zERZ4eT61RkQxHhrrOQr6nFzulrGwbt9EmQymvM", "CPV", False),
]


class CampaignConfig:
    def __init__(
        self,
        campaign_key: str,
        client: str,
        campaign_name: str,
        sheet_id: str,
        channel: Optional[str] = None,
        kpi: Optional[str] = None,
    ):
        self.campaign_key = campaign_key
        self.client = client
        self.campaign_name = campaign_name
        self.sheet_id = sheet_id
        self.channel = channel or "Video Programática"
        self.kpi = kpi or "CPV"
        self.use_footfall = False


def _date_to_br(iso: str) -> str:
    if not iso:
        return ""
    s = str(iso).strip()[:10]
    try:
        d = datetime.strptime(s, "%Y-%m-%d")
        return d.strftime("%d/%m/%Y")
    except Exception:
        return s


def _per_row(ch: ChannelSpec, data: Dict[str, Any]) -> Dict[str, Any]:
    s = data.get("campaign_summary") or {}
    c = data.get("contract") or {}
    inv = float(c.get("investment") or 0)
    sp = float(s.get("total_spend") or 0)
    imp = int(s.get("total_impressions") or 0)
    clicks = int(s.get("total_clicks") or 0)
    vc = int(s.get("total_video_completions") or 0)
    vs = int(s.get("total_video_starts") or 0)
    ctr_frac = (clicks / imp) if imp else 0.0
    vtr_frac = (vc / vs) if vs else 0.0
    cpv = float(s.get("cpv") or 0)
    # Para CPM, queremos exibir o CPM contratado (não CPM médio/realizado).
    cpm_contracted = float(c.get("cpv_contracted") or 0) if ch.kpi.upper() == "CPM" else 0.0
    pacing = (sp / inv) if inv else 0.0
    return {
        "Canal": ch.name,
        "Budget Contratado (R$)": inv,
        "Budget Utilizado (R$)": sp,
        "Impressões": imp,
        "Cliques": clicks,
        "CTR (%)": ctr_frac,
        "VC (100%)": vc,
        "VTR (100%)": vtr_frac,
        "CPV (R$)": cpv,
        "CPM (R$)": cpm_contracted,
        "Pacing (%)": pacing,
        "Criativos Únicos": 0,
    }


def _daily_rows(ch: ChannelSpec, data: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for r in data.get("daily_data") or []:
        out.append(
            {
                "date": _date_to_br(str(r.get("date") or "")),
                "channel": ch.name,
                "creative": str(r.get("creative") or r.get("line_item") or ""),
                "spend": float(r.get("spend") or 0),
                "starts": int(r.get("video_starts") or 0),
                "q25": int(r.get("video_25") or 0),
                "q50": int(r.get("video_50") or 0),
                "q75": int(r.get("video_75") or 0),
                "q100": int(r.get("video_completions") or 0),
                "impressions": int(r.get("impressions") or 0),
                "clicks": int(r.get("clicks") or 0),
                "visits": 0,
            }
        )
    return out


def _consolidate_cons(per_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    inv = sum(float(r["Budget Contratado (R$)"]) for r in per_rows)
    sp = sum(float(r["Budget Utilizado (R$)"]) for r in per_rows)
    imp = sum(int(r["Impressões"]) for r in per_rows)
    clk = sum(int(r["Cliques"]) for r in per_rows)
    ctr = (clk / imp) if imp else 0.0
    pacing = (sp / inv) if inv else 0.0
    vc = sum(int(r["VC (100%)"]) for r in per_rows)
    # No multicanal, CPM é relevante apenas para HHS/OHS; no consolidado deixamos 0 (ou poderia ser N/A no UI)
    cpm_w = 0.0
    return {
        "Budget Contratado (R$)": inv,
        "Budget Utilizado (R$)": sp,
        "Impressões": imp,
        "Cliques": clk,
        "CTR (%)": ctr,
        "CPM (R$)": cpm_w,
        "Pacing (%)": pacing,
        "VC (100%)": vc,
        "VTR (100%)": 0.0,
        "CPV (R$)": 0.0,
    }


def extract_all() -> Tuple[List[Dict], List[Dict], Dict, List[Dict], List[Dict], List[str]]:
    per: List[Dict[str, Any]] = []
    daily: List[Dict[str, Any]] = []
    foot_hhs: List[Dict[str, Any]] = []
    foot_ohs: List[Dict[str, Any]] = []
    errors: List[str] = []

    for ch in CHANNELS:
        cfg = CampaignConfig(
            campaign_key=f"proto_{ch.name.lower()}",
            client=CLIENT,
            campaign_name=CAMPAIGN,
            sheet_id=ch.sheet_id,
            channel=ch.name,
            kpi=ch.kpi.upper(),
        )
        cfg.use_footfall = ch.use_footfall
        try:
            ext = RealGoogleSheetsExtractor(cfg)
            data = ext.extract_data()
            if not data:
                errors.append(f"{ch.name}: sem dados")
                continue
            per.append(_per_row(ch, data))
            daily.extend(_daily_rows(ch, data))
            pts = data.get("footfall_points") or []
            if ch.name == "HHS":
                foot_hhs = [
                    {
                        "lat": float(p["lat"]),
                        "lon": float(p["lon"]),
                        "name": str(p.get("name") or ""),
                        "users": int(p.get("users") or 0),
                        "rate": float(p.get("rate") or 0),
                    }
                    for p in pts
                    if p
                ]
            elif ch.name == "OHS":
                foot_ohs = [
                    {
                        "lat": float(p["lat"]),
                        "lon": float(p["lon"]),
                        "name": str(p.get("name") or ""),
                        "users": int(p.get("users") or 0),
                        "rate": float(p.get("rate") or 0),
                    }
                    for p in pts
                    if p
                ]
        except Exception as e:
            errors.append(f"{ch.name}: {e}")

    cons = _consolidate_cons(per) if per else {
        "Budget Contratado (R$)": 0.0,
        "Budget Utilizado (R$)": 0.0,
        "Impressões": 0,
        "Cliques": 0,
        "CTR (%)": 0.0,
        "CPM (R$)": 0.0,
        "Pacing (%)": 0.0,
        "VC (100%)": 0,
        "VTR (100%)": 0.0,
        "CPV (R$)": 0.0,
    }
    return per, daily, cons, foot_hhs, foot_ohs, errors


def _js_obj(name: str, obj: Any) -> str:
    return f"const {name} = {json.dumps(obj, ensure_ascii=False, indent=2)};"


def inject_data(html: str, cons: dict, per: list, daily: list, foot_hhs: list, foot_ohs: list) -> str:
    """Substitui bloco const CONS ... até // Helpers (antes dos helpers) pelo gerado."""
    block = "\n".join(
        [
            "// --- Dados gerados por build_modelo_multicanal_footfall_v1.py ---",
            _js_obj("CONS", cons),
            "",
            _js_obj("PER", per),
            "",
            _js_obj("DAILY", daily),
            "",
            "// Footfall por fonte (HHS / OHS) — use os botões na aba Footfall para alternar",
            _js_obj("FOOTFALL_POINTS_HHS", foot_hhs),
            _js_obj("FOOTFALL_POINTS_OHS", foot_ohs),
            "let CURRENT_FOOTFALL_POINTS = (FOOTFALL_POINTS_HHS && FOOTFALL_POINTS_HHS.length) ? FOOTFALL_POINTS_HHS : FOOTFALL_POINTS_OHS;",
            "",
        ]
    )
    m = re.search(r"const CONS\s*=\s*\{", html)
    if not m:
        raise RuntimeError("Marcador const CONS não encontrado no HTML")
    start = m.start()
    idx_helpers = html.find("// Helpers", start)
    if idx_helpers < 0:
        raise RuntimeError("// Helpers não encontrado após CONS")
    return html[:start] + block + "\n" + html[idx_helpers:]


def main() -> int:
    modelo_path = ROOT / "static" / "modelo_multicanal_footfall_v1.html"
    if not modelo_path.exists():
        print(f"Arquivo não encontrado: {modelo_path}", file=sys.stderr)
        return 1

    print("Extraindo planilhas (pode levar alguns minutos)...")
    per, daily, cons, foot_hhs, foot_ohs, errors = extract_all()
    for e in errors:
        print(f"  Aviso: {e}", file=sys.stderr)

    html = modelo_path.read_text(encoding="utf-8")
    html = inject_data(html, cons, per, daily, foot_hhs, foot_ohs)
    modelo_path.write_text(html, encoding="utf-8")
    print(f"OK: {modelo_path} atualizado ({len(per)} canais, {len(daily)} linhas diárias).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
