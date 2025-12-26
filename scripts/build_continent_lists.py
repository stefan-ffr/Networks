#!/usr/bin/env python3
import os
from continents import CONTINENTS

BASE_DIRS = ["ipv4", "ipv6", "combined", "asn"]

def read_lines(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]

def write_lines(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for l in sorted(set(lines)):
            f.write(l + "\n")

def main():
    for continent, countries in CONTINENTS.items():
        print(f"Building continent: {continent}")

        for base in BASE_DIRS:
            combined = []
            for cc in countries:
                cc = cc.lower()
                combined += read_lines(f"{base}/{cc}.txt")

            if combined:
                write_lines(f"{base}/{continent}.txt", combined)

if __name__ == "__main__":
    main()
