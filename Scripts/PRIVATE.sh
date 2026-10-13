#!/bin/bash
# XG2010G additions, applied after the upstream package update script.
set -e

if [[ "$WRT_CONFIG" != "AIROHA" ]]; then
	return 0
fi

mkdir -p ./package/custom
packages=(luci-app-pon-status luci-app-airoha-npu xg2010g-rps)
case "${WRT_MWAN:-mwan4}" in
	mwan4)
		packages+=(mwan4 luci-app-mwan4)
		source_file=MWAN4-SOURCE.json
		;;
	mwan3-nft)
		# Replace the stock backend and frontend together with the pinned nft port.
		rm -rf ./feeds/packages/net/mwan3 ./feeds/luci/applications/luci-app-mwan3
		rm -f ./package/feeds/packages/mwan3 ./package/feeds/luci/luci-app-mwan3
		packages+=(mwan3 luci-app-mwan3)
		source_file=MWAN3-SOURCE.json
		;;
	*)
		echo "Unsupported multi-WAN variant: $WRT_MWAN" >&2
		exit 1
		;;
esac
for name in "${packages[@]}"; do
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

# Preserve the validated baseline kernel routing configuration.
kernel_config=./target/linux/airoha/an7581/config-6.18
sed -i '/^# CONFIG_IP_ROUTE_MULTIPATH is not set$/d; /^CONFIG_IP_ROUTE_MULTIPATH=/d' "$kernel_config"
echo 'CONFIG_IP_ROUTE_MULTIPATH=y' >> "$kernel_config"
python3 "$GITHUB_WORKSPACE/Scripts/apply-ppe-kernel.py" .

install -m 0755 "$GITHUB_WORKSPACE/Scripts/tempinfo" ./package/emortal/autocore/files/tempinfo
dos2unix ./package/emortal/autocore/files/tempinfo
PROFILE=gemtek_xg2010g python3 "$GITHUB_WORKSPACE/Scripts/Integrate-Overview.py" .

mkdir -p ./files/etc
cp "$GITHUB_WORKSPACE/$source_file" ./files/etc/xg2010g-multiwan-source.json
if [[ "${WRT_MWAN:-mwan4}" == mwan4 ]]; then
	cp "$GITHUB_WORKSPACE/$source_file" ./files/etc/xg2010g-mwan4-source.json
fi

mkdir -p files/etc
cp "$GITHUB_WORKSPACE/AIROHA-SOURCE.json" files/etc/airoha-build-source.json
