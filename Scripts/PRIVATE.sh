#!/bin/bash
# XG2010G additions, applied after the upstream package update script.
set -e

if [[ "$WRT_CONFIG" != "AIROHA" ]]; then
	return 0
fi

mkdir -p ./package/custom
for name in mwan4 luci-app-mwan4 luci-app-pon-status luci-app-airoha-npu; do
	# Reject duplicate package definitions instead of silently using another feed.
	if find ./feeds -name Makefile -path "*/$name/Makefile" | grep -q .; then
		echo "Unexpected duplicate package: $name" >&2
		exit 1
	fi
	cp -a "$GITHUB_WORKSPACE/Packages/$name" ./package/custom/
done

# Git checkouts on Windows can lose executable bits and gain CRLF endings.
find ./package/custom -type f -exec dos2unix {} +
find ./package/custom -type f -path '*/root/etc/init.d/*' -exec chmod 0755 {} +
find ./package/custom -type f -path '*/root/usr/libexec/*' -exec chmod 0755 {} +

# ECMP requires the multipath routing support used by today's Rust MWAN4.
kernel_config=./target/linux/airoha/an7581/config-6.18
sed -i '/^# CONFIG_IP_ROUTE_MULTIPATH is not set$/d; /^CONFIG_IP_ROUTE_MULTIPATH=/d' "$kernel_config"
echo 'CONFIG_IP_ROUTE_MULTIPATH=y' >> "$kernel_config"

install -m 0755 "$GITHUB_WORKSPACE/Scripts/tempinfo" ./package/emortal/autocore/files/tempinfo
dos2unix ./package/emortal/autocore/files/tempinfo
PROFILE=gemtek_xg2010g python3 "$GITHUB_WORKSPACE/Scripts/Integrate-Overview.py" .
