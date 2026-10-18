#!/usr/bin/env python3
"""Skip verified packages-feed backports already present in pinned 2.3.11."""
import argparse
import hashlib
import re
import shutil
import subprocess
import tarfile
import tempfile
from pathlib import Path

OBSOLETE_PATCH_SHA256 = '4e0f8ddf58cb130044a5f3b92bdf3a8859f8c15e0edbcbcb2b8df42f99e41da1'
OBSOLETE_ALLOW_PRIVATE_PATCH_SHA256 = 'c667bfaa2f1028d1dc44547d4dd4302891799fc0de271a17618eff537b1a2339'
SOURCE_SHA256 = '91994b127da735b2c97f19992e34420648c0e8c4ace8a4bcb0596e7685c48678'
PACKAGE_VERSION = '2.3.11'
REBASED_PATCHES = {
    '040-improve-logging.patch': 'aad6802ab9d01ecea2c143d7495644b714e171552434049f8669d4f28611bcba',
    '900-miniupnpd-format-xml-to-make-some-app-happy.patch': 'b8acd4ab735ff0f1bb937c4991549e5f92c5fa614ab400e849d772f88e3cbcd8',
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile(root):
    package = root / 'feeds/packages/net/miniupnpd'
    makefile = (package / 'Makefile').read_text()
    version = re.search(r'^PKG_VERSION:=(.+)$', makefile, re.M)
    source_hash = re.search(r'^PKG_HASH:=(.+)$', makefile, re.M)
    patches = (
        (package / 'patches/020-descr-filter-fix.patch', OBSOLETE_PATCH_SHA256, 'parser'),
        (package / 'patches/030-allow-private-fix.patch', OBSOLETE_ALLOW_PRIVATE_PATCH_SHA256, 'allow-private'),
    )
    matching = [(path, kind) for path, digest, kind in patches
                if path.exists() and sha256(path) == digest]
    replacements = [(package/'patches'/name, name) for name, digest in REBASED_PATCHES.items()
                    if (package/'patches'/name).is_file() and sha256(package/'patches'/name) == digest]
    if not matching and not replacements:
        print('miniupnpd: no matching stale 2.3.11 backport; left feed unchanged')
        return False

    assert version and version[1] == PACKAGE_VERSION, 'Stale patch identity found with an unreviewed miniupnpd version'
    assert source_hash and source_hash[1] == SOURCE_SHA256, 'miniupnpd 2.3.11 source hash changed'
    archives = list((root / 'dl').glob('miniupnpd-2.3.11.tar.*'))
    assert len(archives) == 1 and sha256(archives[0]) == SOURCE_SHA256, 'Verified miniupnpd source archive missing or changed'

    with tarfile.open(archives[0], 'r:*') as archive:
        members = {Path(member.name).name: member for member in archive.getmembers()}
        source_files = {}
        for name in ('upnppermissions.c', 'upnppermissions.h', 'upnpsoap.c'):
            member = members.get(name)
            if member and member.isfile():
                source_files[name] = archive.extractfile(member).read().decode('utf-8')

    for patch, kind in matching:
        if kind == 'parser':
            source = source_files.get('upnppermissions.c', '')
            header = source_files.get('upnppermissions.h', '')
            # 2.3.11 contains the parser rewrite from 020 with upstream
            # changes to helper names/signatures. Verify its relevant routines.
            for token in ('iseol(', 'get_sep(', 'get_range(', 'get_addr_or_mask(',
                          'read_permission_line(struct upnpperm * perm,',
                          'const char * p)', 'write_permlist(', "t[j] = '\\0';"):
                assert token in source, 'Expected parser rewrite missing from pinned 2.3.11 source: ' + token
            assert 'read_permission_line(struct upnpperm * perm,\n                     const char * p)' in source
            assert 'const char * p);' in header
        elif kind == 'allow-private':
            source = source_files.get('upnpsoap.c', '')
            condition = re.compile(
                r'else\s+if\s*\(addr_is_reserved\(&addr\)\)\s*\{\s*'
                r'if\s*\(GETFLAG\(ALLOWPRIVATEIPV4MASK\)\)\s*\{\s*'
                r'syslog\(LOG_WARNING,\s*"IGNORED : private/reserved address %s is not suitable for external IP",\s*ext_ip_addr\);\s*'
                r'\}\s*else\s*\{\s*'
                r'syslog\(LOG_NOTICE,\s*"private/reserved address %s is not suitable for external IP",\s*ext_ip_addr\);\s*'
                r'ext_ip_addr\[0\]\s*=\s*\'\\0\'\s*;\s*\}', re.S)
            assert condition.search(source), 'Expected ALLOWPRIVATEIPV4MASK fix missing from pinned 2.3.11 source'

        patch.unlink()
        print(f'miniupnpd: omitted obsolete {patch.name}; verified native 2.3.11 implementation and archive SHA-256')
    for path, name in replacements:
        replacement = Path(__file__).resolve().parents[1]/'source-patches/miniupnpd-2.3.11'/name
        assert replacement.is_file(), 'Reviewed replacement patch missing: '+name
        shutil.copyfile(replacement, path)
        print('miniupnpd: rebased '+name+'; preserves upstream buffer sizing, NFQUEUE assignments, logging and XML compatibility')
    if replacements:
        makefile, count = re.subn(r'^PKG_RELEASE:=1$', 'PKG_RELEASE:=2', makefile, flags=re.M)
        assert count == 1, 'Unexpected miniupnpd feed release'
        (package/'Makefile').write_text(makefile)
    return True


def check_series(root):
    """Apply the entire retained feed series before a long world build."""
    archives=list((root/'dl').glob('miniupnpd-2.3.11.tar.*'))
    assert len(archives)==1 and sha256(archives[0])==SOURCE_SHA256, 'Unverified miniupnpd archive'
    with tempfile.TemporaryDirectory(prefix='miniupnpd-series-') as directory:
        work=Path(directory)
        with tarfile.open(archives[0]) as archive:
            archive.extractall(work, filter='data')
        source=work/'miniupnpd-2.3.11'
        overlay=root/'feeds/packages/net/miniupnpd/src'
        if overlay.is_dir():shutil.copytree(overlay,source,dirs_exist_ok=True)
        patches=sorted((root/'feeds/packages/net/miniupnpd/patches').glob('*.patch'))
        assert patches, 'Miniupnpd feed patch series missing'
        for patch in patches:
            result=subprocess.run(['patch','--batch','--forward','--fuzz=0','-p1','-d',str(source),'-i',str(patch.resolve())],capture_output=True,text=True)
            assert result.returncode==0, 'Complete miniupnpd series failed at '+patch.name+'\n'+result.stdout+result.stderr
        print('miniupnpd: full retained patch series verified without fuzz: '+', '.join(p.name for p in patches))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='OpenWrt source root after make download')
    args = parser.parse_args()
    reconcile(args.root)
    check_series(args.root)
