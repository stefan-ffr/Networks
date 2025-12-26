#!/usr/bin/env python3
import json
import os
import re
import requests
from collections import defaultdict

UA = "country-prefix-exporter/1.0 (github-actions)"

# JSON mit ISO-3166 alpha2 + UN M49 region/sub-region
# (Repo liefert mehrere Formate; dieses JSON ist sehr praktisch)
MAPPING_URL = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json"

BASE_DIRS = ["ipv4", "ipv6", "combined", "asn"]

# Optional: falls du "Americas" lieber in north_america + south_america trennen willst, müsstest du subregion nutzen.
# Für jetzt: Kontinente nach UN-M49 "region".
def norm_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")

def get_json(url: str):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
    r.raise_for_status()
    return r.json()

def read_lines(path: str):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def write_lines(path: str, lines: list[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = sorted(set(lines))
    with open(path, "w", encoding="utf-8") as f:
        for l in lines:
            f.write(l + "\n")

def main():
    mapping = get_json(MAPPING_URL)

    # continent_key -> [CC, CC...]
    cont_to_cc = defaultdict(list)
    for item in mapping:
        cc = (item.get("alpha-2") or "").strip().upper()
        region = (((item.get("region") or {}) .get("name")) or "").strip()
        if not cc or not region:
            continue
        cont_to_cc[norm_key(region)].append(cc)

    # Für jede Region (Kontinent) die Listen zusammenführen
    for cont_key, countries in cont_to_cc.items():
        print(f"Building continent: {cont_key} ({len(countries)} countries/areas)")
        for base in BASE_DIRS:
            merged = []
            for cc in countries:
                merged += read_lines(f"{base}/{cc.lower()}.txt")
            if merged:
                write_lines(f"{base}/{cont_key}.txt", merged)

if __name__ == "__main__":
    main()
