#!/usr/bin/env python3
"""Build a customized Shadowrocket config from maintained upstream sources."""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import urllib.request


ROOT = pathlib.Path(__file__).resolve().parents[1]
CONFIG_URL = (
    "https://raw.githubusercontent.com/Johnshall/"
    "Shadowrocket-ADBlock-Rules-Forever/release/lazy_group.conf"
)
DOMAIN_SOURCES = {
    "Longbridge": (
        "https://raw.githubusercontent.com/v2fly/"
        "domain-list-community/master/data/longbridge"
    ),
    "Futu": (
        "https://raw.githubusercontent.com/v2fly/"
        "domain-list-community/master/data/futu"
    ),
}
RAW_BASE = "https://raw.githubusercontent.com/reallinzc/Shadowrocket/main"

GROUPS = """\
# 券商分流（由 reallinzc/Shadowrocket 自动注入）
长桥证券 = select,香港节点,新加坡节点,PROXY,DIRECT,policy-select-name=香港节点
富途证券 = select,香港节点,新加坡节点,美国节点,PROXY,DIRECT,policy-select-name=香港节点

"""

RULES = f"""\
# 券商分流（域名源：v2fly/domain-list-community）
RULE-SET,{RAW_BASE}/rules/Longbridge.list,长桥证券
RULE-SET,{RAW_BASE}/rules/Futu.list,富途证券

"""


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "reallinzc/Shadowrocket builder"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_domains(source: str) -> list[str]:
    domains: set[str] = set()
    for raw_line in source.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or line.startswith("include:"):
            continue
        domain = line.split()[0].removeprefix("full:").removeprefix("domain:")
        if domain.startswith("regexp:") or domain.startswith("keyword:"):
            raise ValueError(f"Unsupported domain-list entry: {line}")
        domains.add(domain.lower().rstrip("."))
    return sorted(domains)


def render_rule_list(name: str, domains: list[str], source_url: str) -> str:
    date = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    header = [
        f"# NAME: {name}",
        "# FORMAT: Shadowrocket classical rule-set",
        f"# SOURCE: {source_url}",
        f"# GENERATED: {date} UTC",
        f"# DOMAIN-SUFFIX: {len(domains)}",
    ]
    rules = [f"DOMAIN-SUFFIX,{domain}" for domain in domains]
    return "\n".join(header + rules) + "\n"


def customize_config(config: str) -> str:
    if "[Proxy Group]" not in config or "[Rule]" not in config:
        raise ValueError("Upstream config is missing required sections")
    if "长桥证券 =" in config or "rules/Longbridge.list" in config:
        raise ValueError("Upstream config already contains custom broker rules")

    config = config.replace("[Proxy Group]\n", "[Proxy Group]\n" + GROUPS, 1)
    config = config.replace("[Rule]\n", "[Rule]\n" + RULES, 1)

    attribution = (
        "# Customized by reallinzc/Shadowrocket\n"
        "# Base: Johnshall/Shadowrocket-ADBlock-Rules-Forever (CC BY-SA 4.0)\n"
        "# Longbridge/Futu domains: v2fly/domain-list-community (MIT)\n\n"
    )
    return attribution + config.lstrip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source-dir",
        type=pathlib.Path,
        help="Read lazy_group.conf, longbridge, and futu from a local directory",
    )
    args = parser.parse_args()

    if args.source_dir:
        config = (args.source_dir / "lazy_group.conf").read_text()
        domain_text = {
            name: (args.source_dir / name.lower()).read_text()
            for name in DOMAIN_SOURCES
        }
    else:
        config = fetch(CONFIG_URL)
        domain_text = {name: fetch(url) for name, url in DOMAIN_SOURCES.items()}

    (ROOT / "shadowrocket.conf").write_text(customize_config(config))
    rules_dir = ROOT / "rules"
    rules_dir.mkdir(exist_ok=True)
    for name, source_url in DOMAIN_SOURCES.items():
        domains = parse_domains(domain_text[name])
        (rules_dir / f"{name}.list").write_text(
            render_rule_list(name, domains, source_url)
        )


if __name__ == "__main__":
    main()
