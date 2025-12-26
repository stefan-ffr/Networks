#!/usr/bin/env python3
import os
import requests

UA = "de-prefix-exporter/1.0 (github-actions)"

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
    # RIPE country resource list
    # v4_format=prefix => IPv4 ranges → CIDR
    url = (
        "https://stat.ripe.net/data/country-resource-list/data.json"
        "?resource=DE&v4_format=prefix"
    )

    payload = get_json(url)
    resources = payload["data"]["resources"]

    ipv4 = sorted(set(resources.get("ipv4", [])))
    ipv6 = sorted(set(resources.get("ipv6", [])))
    combined = sorted(ipv4 + ipv6)

    asns = sorted({f"AS{a}" for a in resources.get("asn", [])})

    write_lines("ipv4/de.txt", ipv4)
    write_lines("ipv6/de.txt", ipv6)
    write_lines("combined/de.txt", combined)
    write_lines("asn/de.txt", asns)

if __name__ == "__main__":
    main()
