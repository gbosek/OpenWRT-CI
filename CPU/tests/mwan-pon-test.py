#!/usr/bin/env python3
"""Check real multi-WAN validation for replacement and original PON stacks."""
import contextlib
import importlib.util
import io
import tempfile
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('mwan', repo / 'Scripts/check-mwan-build.py')
mwan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mwan)
checks = 0
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'packages'
    for npu in mwan.PON:
        for variant in mwan.STACKS:
            wanted = set(mwan.COMMON + mwan.STACKS[variant] + mwan.PON[npu])
            other = 'mwan3-nft' if variant == 'mwan4' else 'mwan4'
            for config in (True, False):
                def check(packages, expected):
                    global checks
                    prefix = 'CONFIG_TARGET_DEVICE_airoha_an7581_DEVICE_gemtek_xg2010g=y\n'
                    text = prefix + ''.join('CONFIG_PACKAGE_' + p + '=y\n' for p in sorted(packages)) if config else ''.join(p + ' - 1.0-r1\n' for p in sorted(packages))
                    path.write_text(text)
                    try:
                        with contextlib.redirect_stdout(io.StringIO()):
                            mwan.check(path, variant, config, npu)
                    except ValueError:
                        assert not expected, (npu, variant, packages)
                    else:
                        assert expected, (npu, variant, packages)
                    checks += 1
                check(wanted, True)
                for package in wanted:
                    check(wanted - {package}, False)
                check(wanted | set(mwan.STACKS[other]), False)
                if npu == 'naoki':
                    for package in mwan.OLD_NAOKI_PON:
                        check(wanted | {package}, False)
print(f'PASS: {checks} config/manifest checks cover both NPU providers, ONU dependencies, missing packages and conflicting stacks')
