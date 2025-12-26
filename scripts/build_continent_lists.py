#!/usr/bin/env python3
import os
import re
import time
import requests
from collections import defaultdict

UA = "continent-prefix-exporter/1.0 (github-actions)"

# UN/ISO Mapping (vollständig: ISO alpha-2 + UN-M49 Region)
MAPPING_URL = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.json"

RIPE_COUNTRY_URL = (
    "https://stat.ripe.net/data/country-resource-list/data.json"
    "?resource={cc}&v4_format=prefix"
)

OUT_BASE_DIRS = ["ipv4", "ipv6", "combined", "asn"]

def norm_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.strip().lower()).strip("_")

def get_json(url: str, timeout: int = 60):
    r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
    r.raise_for_status()
    return r.json()

def write_lines(path: str, lines: list[str]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    lines = sorted(set(lines))
    with open(path, "w", encoding="utf-8") as f:
        for l in lines:
            f.write(l + "\n")

def extract_region(item) -> str:
    region = item.get("region")
    if isinstance(region, str):
        return region.strip()
    if isinstance(region, dict):
        return (region.get("name") or "").strip()
    return ""

def main():
    mapping = get_json(MAPPING_URL)

    # continent -> list of ISO alpha-2 country codes
    continent_to_countries = defaultdict(list)
    for item in mapping:
        cc = (item.get("alpha-2") or "").strip().upper()
        region = extract_region(item)
        if cc and region:
            continent_to_countries[norm_key(region)].append(cc)

    # continent -> aggregated sets
    agg_ipv4 = defaultdict(set)
    agg_ipv6 = defaultdict(set)
    agg_asn  = defaultdict(set)

    # Throttling: ~250 Länder => höflich abfragen
    countries_total = sum(len(v) for v in continent_to_countries.values())
    done = 0

    for continent, countries in continent_to_countries.items():
        # Für stabile Ergebnisse (und Debugbarkeit)
        for cc in sorted(set(countries)):
            done += 1
            try:
                payload = get_json(RIPE_COUNTRY_URL.format(cc=cc), timeout=60)
                resources = payload.get("data", {}).get("resources", {})

                ipv4 = resources.get("ipv4", []) or []
                ipv6 = resources.get("ipv6", []) or []
                asns = resources.get("asn", []) or []

                for p in ipv4:
                    agg_ipv4[continent].add(p)
                for p in ipv6:
                    agg_ipv6[continent].add(p)
                for a in asns:
                    agg_asn[continent].add(f"AS{a}")

            except Exception as e:
                # Nicht alles abbrechen, sondern überspringen (z.B. Sondergebiete / temporäre API-Probleme)
                print(f"Warn: failed {cc} ({continent}): {e}")

            # kleine Pause, um Rate-Limits zu vermeiden
            if done % 25 == 0:
                print(f"Progress {done}/{countries_total} ...")
                time.sleep(1)

    # Kontinent-Dateien schreiben (alle Kontinente, auch wenn leer)
    for continent in sorted(continent_to_countries.keys()):
        ipv4 = sorted(agg_ipv4[continent])
        ipv6 = sorted(agg_ipv6[continent])
        asn  = sorted(agg_asn[continent])
        combined = sorted(ipv4 + ipv6)

        write_lines(f"ipv4/{continent}.txt", ipv4)
        write_lines(f"ipv6/{continent}.txt", ipv6)
        write_lines(f"asn/{continent}.txt", asn)
        write_lines(f"combined/{continent}.txt", combined)

    # Optional: Timestamp
    os.makedirs("meta", exist_ok=True)
    with open("meta/continents_generated_at_utc.txt", "w", encoding="utf-8") as f:
        f.write(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()) + "\n")

if __name__ == "__main__":
    main()
