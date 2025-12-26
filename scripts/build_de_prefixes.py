#!/usr/bin/env python3
import json
import time
import requests
from typing import Any, Dict, List

BASE = "https://stat.ripe.net/data"
UA = "de-prefix-exporter/1.0 (github-actions)"

def get_json(url: str) -> Dict[str, Any]:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    return r.json()

def main() -> None:
    # 1) Alle ASNs mit Country=DE
    asns_url = f"{BASE}/country-asns/data.json?resource=DE"
    asns = get_json(asns_url)["data"]["asns"]

    result: List[Dict[str, Any]] = []
    # optional: stabile Sortierung
    asns = sorted(asns)

    for i, asn in enumerate(asns, start=1):
        # 2) Prefixe (announced prefixes) pro ASN
        p_url = f"{BASE}/announced-prefixes/data.json?resource=AS{asn}"
        data = get_json(p_url)["data"]

        prefixes = data.get("prefixes", [])
        ipv4 = sorted({p["prefix"] for p in prefixes if ":" not in p["prefix"]})
        ipv6 = sorted({p["prefix"] for p in prefixes if ":" in p["prefix"]})

        result.append({
            "asn": f"AS{asn}",
            "ipv4": ipv4,
            "ipv6": ipv6,
        })

        # kleine Pause, um höflich zu sein + weniger Rate-Limit-Risiko
        if i % 25 == 0:
            time.sleep(1)

    out = {
        "country": "DE",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count_asns": len(asns),
        "data": result,
    }

    with open("de_ip_prefixes.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

if __name__ == "__main__":
    main()
