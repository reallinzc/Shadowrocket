#!/usr/bin/env python3
"""Validate generated configuration invariants without Shadowrocket."""

from __future__ import annotations

import pathlib
import re


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG = ROOT / "shadowrocket.conf"


def validate_rule_list(path: pathlib.Path) -> None:
    rules = [line for line in path.read_text().splitlines() if line and not line.startswith("#")]
    if not rules:
        raise ValueError(f"{path} has no rules")
    if len(rules) != len(set(rules)):
        raise ValueError(f"{path} contains duplicate rules")
    for rule in rules:
        if not re.fullmatch(r"DOMAIN-SUFFIX,[a-z0-9._-]+", rule):
            raise ValueError(f"Invalid rule in {path}: {rule}")


def main() -> None:
    config = CONFIG.read_text()
    required_sections = ["[General]", "[Proxy]", "[Proxy Group]", "[Rule]"]
    for section in required_sections:
        if config.count(section) != 1:
            raise ValueError(f"Expected exactly one {section}")

    required_fragments = [
        "长桥证券 = select,",
        "富途证券 = select,",
        "/rules/Longbridge.list,长桥证券",
        "/rules/Futu.list,富途证券",
        "FINAL,PROXY",
    ]
    for fragment in required_fragments:
        if fragment not in config:
            raise ValueError(f"Missing required config fragment: {fragment}")

    if config.index("/rules/Longbridge.list") > config.index("GEOIP,CN,DIRECT"):
        raise ValueError("Broker rules must precede GEOIP fallback")

    validate_rule_list(ROOT / "rules" / "Longbridge.list")
    validate_rule_list(ROOT / "rules" / "Futu.list")
    print("OK: config and broker rule sets are valid")


if __name__ == "__main__":
    main()
