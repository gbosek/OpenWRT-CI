#!/usr/bin/env python3
"""Verify only hash-pinned miniupnpd 2.3.11 backports are omitted."""
import argparse
import importlib.util
import shutil
import tempfile
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('fix_miniupnpd_feed', repo / 'Scripts/fix-miniupnpd-feed.py')
fix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fix)


def fixture(root, source_archive, version=fix.PACKAGE_VERSION, source_hash=fix.SOURCE_SHA256):
    package = root / 'feeds/packages/net/miniupnpd'
    (package / 'patches').mkdir(parents=True)
    (root / 'dl').mkdir()
    (package / 'Makefile').write_text(
        f'PKG_VERSION:={version}\nPKG_HASH:={source_hash}\n', encoding='utf-8')
    shutil.copyfile(source_archive, root / 'dl/miniupnpd-2.3.11.tar.gz')
    return package / 'patches'


def expect_assertion(call, message):
    try:
        call()
    except AssertionError:
        return
    raise AssertionError(message)


def main(source_archive):
    assert fix.sha256(source_archive) == fix.SOURCE_SHA256, 'Test requires the pinned miniupnpd source archive'
    parser_fixture = repo / 'CPU/tests/fixtures/miniupnpd-020-descr-filter-fix.patch'
    private_fixture = repo / 'CPU/tests/fixtures/miniupnpd-030-allow-private-fix.patch'
    assert fix.sha256(parser_fixture) == fix.OBSOLETE_PATCH_SHA256
    assert fix.sha256(private_fixture) == fix.OBSOLETE_ALLOW_PRIVATE_PATCH_SHA256

    with tempfile.TemporaryDirectory(prefix='miniupnpd-feed-test-') as temporary:
        root = Path(temporary)
        patches = fixture(root, source_archive)
        parser_patch = patches / '020-descr-filter-fix.patch'
        private_patch = patches / '030-allow-private-fix.patch'
        shutil.copyfile(parser_fixture, parser_patch)
        shutil.copyfile(private_fixture, private_patch)
        (patches / '031-unrelated.patch').write_text('preserve this patch\n', encoding='utf-8')
        assert fix.reconcile(root) is True
        assert not parser_patch.exists()
        assert not private_patch.exists()
        assert (patches / '031-unrelated.patch').read_text(encoding='utf-8') == 'preserve this patch\n'
        assert fix.reconcile(root) is False, 'Repeat run should be idempotent'

    with tempfile.TemporaryDirectory(prefix='miniupnpd-feed-mismatch-') as temporary:
        root = Path(temporary)
        patches = fixture(root, source_archive)
        unknown_patch = patches / '030-allow-private-fix.patch'
        unknown_patch.write_bytes(private_fixture.read_bytes() + b'\nlocal change\n')
        assert fix.reconcile(root) is False
        assert unknown_patch.exists(), 'Unknown patch was modified'

    with tempfile.TemporaryDirectory(prefix='miniupnpd-feed-version-') as temporary:
        root = Path(temporary)
        patches = fixture(root, source_archive, version='2.3.12')
        private_patch = patches / '030-allow-private-fix.patch'
        shutil.copyfile(private_fixture, private_patch)
        expect_assertion(lambda: fix.reconcile(root), 'Unexpected miniupnpd version was accepted')
        assert private_patch.exists(), 'Patch removed for an unreviewed version'

    with tempfile.TemporaryDirectory(prefix='miniupnpd-feed-hash-') as temporary:
        root = Path(temporary)
        patches = fixture(root, source_archive, source_hash='0' * 64)
        private_patch = patches / '030-allow-private-fix.patch'
        shutil.copyfile(private_fixture, private_patch)
        expect_assertion(lambda: fix.reconcile(root), 'Unexpected source hash was accepted')
        assert private_patch.exists(), 'Patch removed for an unreviewed archive'

    print('PASS: 020/030 native fixes, pinned version/hash, mismatch preservation and idempotence')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', type=Path, required=True, help='Downloaded miniupnpd 2.3.11 archive')
    main(parser.parse_args().source.resolve())
