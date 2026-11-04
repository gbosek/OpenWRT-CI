#!/bin/bash
set -euo pipefail
# Run from the disposable OpenWrt source tree.
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
fetch() {
  local url=$1 sha=$2 dir=$3
  git init -q "$dir"
  git -C "$dir" remote add origin "$url"
  git -C "$dir" fetch -q --depth=1 origin "$sha"
  git -C "$dir" checkout -q --detach FETCH_HEAD
  test "$(git -C "$dir" rev-parse HEAD)" = "$sha"
}
fetch https://github.com/gbosek/mwan4.git bf79656d4d2685b7e76b6e4cff140386677624aa "$tmp/mwan4"
fetch https://github.com/gbosek/luci-app-mwan4.git 7bfdef0088d32efec2aa01a718502da38841c287 "$tmp/luci"
fetch https://github.com/naoki66/luci-app-airoha.git 0b1d8a0a250cb2e4a218b1fad5df2b923a0b0e00 "$tmp/airoha"
fetch https://github.com/naoki66/OpenWrt_ONU_CONFIG.git 3cb13560459f1d51136dac662baa1f399028b2b4 "$tmp/onu"
for name in mwan4 luci-app-mwan4 luci-app-airoha-npu luci-app-pon-status; do
  find package feeds -mindepth 2 \( -type d -o -type l \) -name "$name" -prune -exec rm -rf {} +
done
mkdir -p package/custom
cp -a "$tmp/mwan4" package/custom/mwan4
cp -a "$tmp/luci" package/custom/luci-app-mwan4
cp -a "$tmp/airoha/luci-app-airoha-npu" package/custom/
cp -a "$tmp/onu/luci-app-pon-status" package/custom/
rm -rf package/custom/{mwan4,luci-app-mwan4}/.git
sed -i 's|include ../../luci.mk|include $(TOPDIR)/feeds/luci/luci.mk|' package/custom/luci-app-mwan4/Makefile
cp package/custom/luci-app-airoha-npu/po/zh_Hans/luci-app-airoha-npu.po package/custom/luci-app-airoha-npu/po/zh_Hans/airoha-npu.po
python3 "$GITHUB_WORKSPACE/Scripts/xg2010g-mwan4-adjust.py"
mkdir -p files/etc/uci-defaults
cat > files/etc/uci-defaults/99-xg2010g-mwan4-off <<'SCRIPT'
#!/bin/sh
[ "$(cat /tmp/sysinfo/board_name 2>/dev/null)" = 'gemtek,xg2010g' ] || exit 0
/etc/init.d/mwan4 stop >/dev/null 2>&1 || true
/etc/init.d/mwan4 disable >/dev/null 2>&1 || true
exit 0
SCRIPT
chmod +x files/etc/uci-defaults/99-xg2010g-mwan4-off
