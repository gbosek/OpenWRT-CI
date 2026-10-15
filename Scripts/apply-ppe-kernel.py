#!/usr/bin/env python3
"""Install the requested Airoha PPE flow-statistics fallback patch."""
import argparse
import re
import shutil
from pathlib import Path

PATCH = "931-net-airoha-keep-PPE-offload-when-NPU-refuses-flow-stats.patch"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, nargs="?", default=Path.cwd())
    args = parser.parse_args()
    source = args.source.resolve()
    origin = Path(__file__).resolve().parent.parent / "kernel-patches/airoha" / PATCH
    destination = source / "target/linux/airoha/patches-6.18"
    config = source / "target/linux/airoha/an7581/config-6.18"
    if not origin.is_file() or not destination.is_dir() or not config.is_file():
        parser.error("expected the reviewed patch and an AN7581 kernel 6.18 source tree")
    text = config.read_text()
    if not re.search(r"^CONFIG_NET_AIROHA_NPU=[ym]$", text, re.M):
        parser.error("the source configuration does not enable the Airoha NPU")
    for existing in destination.glob("931-*.patch"):
        if existing.name != PATCH or existing.read_bytes() != origin.read_bytes():
            parser.error(f"conflicting patch order 931: {existing}")
    shutil.copyfile(origin, destination / PATCH)
    for companion in ('932-net-airoha-return-sram-flush-failures.patch',
                      '933-net-airoha-preserve-tc-template-on-idle-refresh.patch'):
        reviewed = origin.parent / companion
        assert reviewed.is_file(), f'Missing reviewed companion: {companion}'
        shutil.copyfile(reviewed, destination / companion)
    text = re.sub(
        r"^(?:# CONFIG_NET_AIROHA_FLOW_STATS is not set|CONFIG_NET_AIROHA_FLOW_STATS=.*)\n?",
        "", text, flags=re.M,
    )
    config.write_text(text.rstrip() + "\nCONFIG_NET_AIROHA_FLOW_STATS=y\n")
    print(f"PPE patch installed: {PATCH}")
    print("AN7581 flow statistics enabled with NPU-refusal fallback")


if __name__ == "__main__":
    main()
