#!/usr/bin/env python3
import json
import time
import requests
from typing import Any, Dict, List

UA = "de-prefix-exporter/1.0 (github-actions)"

def get_json(url: str) -> Dict[str, Any]:
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    return r.json()

def main() -> None:
    # Liefert ASNs + IPv4 + IPv6 für DE aus RIR stats files
    # v4_format=prefix: IPv4 ranges -> CIDR prefixes
    url = "https://stat.ripe.net/data/country-resource-list/data.json?resource=DE&v4_format=prefix"
    payload = get_json(url)

    data = payload.get("data", {})
    resources = data.get("resources", {})

    asns: List[int] = resources.get("asn", [])
    ipv4: List[str] = resources.get("ipv4", [])
    ipv6: List[str] = resources.get("ipv6", [])

    out = {
        "country": "DE",
        "query_time": data.get("query_time"),
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "asns": asns,
        "ipv4": ipv4,
        "ipv6": ipv6,
    }

    with open("de_ip_prefixes.json", "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")

if __name__ == "__main__":
    main()
