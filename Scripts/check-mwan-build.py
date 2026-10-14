#!/usr/bin/env python3
"""Check the selected multi-WAN stack before compilation and in the image."""
import argparse
import re
from pathlib import Path

STACKS = {
    "mwan4": ("mwan4", "luci-app-mwan4", "luci-i18n-mwan4-zh-cn"),
    "mwan3-nft": ("mwan3", "luci-app-mwan3", "luci-i18n-mwan3-zh-cn"),
}
COMMON = (
    "ttyd", "luci-app-ttyd", "luci-i18n-ttyd-zh-cn", "xg2010g-rps",
    "luci-app-airoha-npu", "luci-i18n-airoha-npu-zh-cn",
)
PON = {
    "naoki": ("airoha-pond", "airoha-ponctl", "airoha-pon-debug", "luci-app-onu", "luci-i18n-onu-zh-cn"),
    "luanmuc": ("luci-app-pon-status",),
}
OLD_NAOKI_PON = ("luci-app-pon", "luci-i18n-pon-zh-cn", "luci-app-iptv", "luci-i18n-iptv-zh-cn", "luci-app-pon-status")


def check(path, variant, is_config, npu):
    text = path.read_text()
    if is_config:
        packages = set(re.findall(r"^CONFIG_PACKAGE_(.+)=y$", text, re.M))
        devices = re.findall(r"^CONFIG_TARGET_DEVICE_airoha_an7581_DEVICE_(.+)=y$", text, re.M)
        if devices != ["gemtek_xg2010g"] or "CONFIG_TARGET_ALL_PROFILES=y" in text:
            raise ValueError("expected Gemtek XG2010G as the only selected device")
    else:
        packages = set(re.findall(r"^(\S+) - .+$", text, re.M))
    missing = sorted(set(COMMON + STACKS[variant] + PON[npu]) - packages)
    other = "mwan3-nft" if variant == "mwan4" else "mwan4"
    conflicting = sorted(set(STACKS[other]) & packages)
    if npu == "naoki":
        conflicting += sorted(set(OLD_NAOKI_PON) & packages)
    if missing or conflicting:
        raise ValueError(f"missing packages: {missing}; conflicting packages: {conflicting}")
    print(f"XG2010G {variant} {'configuration' if is_config else 'firmware manifest'} OK")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", required=True, choices=STACKS)
    parser.add_argument("--npu", required=True, choices=PON)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--config", type=Path)
    inputs.add_argument("--manifest", type=Path)
    args = parser.parse_args()
    try:
        check(args.config or args.manifest, args.variant, args.config is not None, args.npu)
    except (ValueError, OSError) as error:
        parser.exit(1, f"Multi-WAN build check failed: {error}\n")


if __name__ == "__main__":
    main()
