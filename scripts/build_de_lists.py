#!/usr/bin/env python3
import os
import requests

UA = "country-prefix-exporter/1.0 (github-actions)"

def get_json(url: str):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    return r.json()

def write_lines(path: str, lines: list[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

def main():
    cc = "DE"
    out = cc.lower()

    url = (
        "https://stat.ripe.net/data/country-resource-list/data.json"
        f"?resource={cc}&v4_format=prefix"
    )

    payload = get_json(url)
    resources = payload["data"]["resources"]

    ipv4 = sorted(set(resources.get("ipv4", [])))
    ipv6 = sorted(set(resources.get("ipv6", [])))
    combined = sorted(ipv4 + ipv6)
    asns = sorted({f"AS{a}" for a in resources.get("asn", [])})

    write_lines(f"ipv4/{out}.txt", ipv4)
    write_lines(f"ipv6/{out}.txt", ipv6)
    write_lines(f"combined/{out}.txt", combined)
    write_lines(f"asn/{out}.txt", asns)

if __name__ == "__main__":
    main()
