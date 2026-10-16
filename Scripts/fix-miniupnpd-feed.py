#!/usr/bin/env python3
"""Skip one obsolete packages-feed patch only for the verified 2.3.11 source."""
import argparse
import hashlib
import re
import tarfile
from pathlib import Path

OBSOLETE_PATCH_SHA256 = '4e0f8ddf58cb130044a5f3b92bdf3a8859f8c15e0edbcbcb2b8df42f99e41da1'
SOURCE_SHA256 = '91994b127da735b2c97f19992e34420648c0e8c4ace8a4bcb0596e7685c48678'
PACKAGE_VERSION = '2.3.11'


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconcile(root):
    package = root / 'feeds/packages/net/miniupnpd'
    makefile = (package / 'Makefile').read_text()
    version = re.search(r'^PKG_VERSION:=(.+)$', makefile, re.M)
    source_hash = re.search(r'^PKG_HASH:=(.+)$', makefile, re.M)
    patch = package / 'patches/020-descr-filter-fix.patch'
    if not patch.exists() or sha256(patch) != OBSOLETE_PATCH_SHA256:
        print('miniupnpd: no matching stale 2.3.11 parser patch; left feed unchanged')
        return False

    assert version and version[1] == PACKAGE_VERSION, 'Stale patch identity found with an unreviewed miniupnpd version'
    assert source_hash and source_hash[1] == SOURCE_SHA256, 'miniupnpd 2.3.11 source hash changed'
    archives = list((root / 'dl').glob('miniupnpd-2.3.11.tar.*'))
    assert len(archives) == 1 and sha256(archives[0]) == SOURCE_SHA256, 'Verified miniupnpd source archive missing or changed'

    with tarfile.open(archives[0], 'r:*') as archive:
        members = {Path(member.name).name: member for member in archive.getmembers()}
        source_member = members.get('upnppermissions.c')
        header_member = members.get('upnppermissions.h')
        assert source_member and header_member and source_member.isfile() and header_member.isfile()
        source = archive.extractfile(source_member).read().decode('utf-8')
        header = archive.extractfile(header_member).read().decode('utf-8')

    # 2.3.11 contains the permission-parser rewrite from 020, with upstream
    # changes to helper names/signatures. Check the behavior-bearing routines
    # in this hash-pinned source before omitting the now-conflicting backport.
    for token in ('iseol(', 'get_sep(', 'get_range(', 'get_addr_or_mask(',
                  'read_permission_line(struct upnpperm * perm,',
                  'const char * p)', 'write_permlist(', 't[j] = \'\\0\';'):
        assert token in source, 'Expected parser rewrite missing from pinned 2.3.11 source: ' + token
    assert 'read_permission_line(struct upnpperm * perm,\n                     const char * p)' in source
    assert 'const char * p);' in header

    patch.unlink()
    print('miniupnpd: omitted obsolete 020 parser patch; verified native 2.3.11 implementation and archive SHA-256')
    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='OpenWrt source root after make download')
    args = parser.parse_args()
    reconcile(args.root)
