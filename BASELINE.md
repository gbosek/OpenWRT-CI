# XG2010G 编译基线

## 专用分支使用方法

GitHub 分支：`xg2010g`。Actions → OWRT-ALL → Run workflow，
将 Branch 选为 `xg2010g`，TEST 不勾选，即编译完整固件。
只启用 `gemtek_xg2010g` 设备；defconfig 后检查设备列表仅有此设备，禁止 ALL_PROFILES。
本分支已保存 MWAN4 r13 及中文 LuCI、ttyd 及中文 LuCI、RPS、Airoha 状态页、
温度/CPU 使用率和 Aurora 全宽 PON 卡片配置。HomeProxy/NAS 保持禁用。
MWAN4 的 IPv4 地址策略路由替代本次需求中的独立 PBR 包。
此前 main 分支的编译继续运行；新分支用于以后的 XG2010G 单型号构建。

- 上游版本：[AIROHA-VIKINGYFY-owrt-26.10.08-11.11.17](https://github.com/VIKINGYFY/OpenWRT-CI/releases/tag/AIROHA-VIKINGYFY-owrt-26.10.08-11.11.17)
- 源码仓库：VIKINGYFY/immortalwrt，分支 owrt。
- 源码提交：`a38520034ee4bdd25dd6e88c4c59261f289ee17e`，由 OWRT-ALL 的 WRT_REVISION 固定。
- 默认地址：192.168.1.1。
- HomeProxy 及 sing-box 后端不选入固件。
- NAS 分类：该版本已选中的 NAS 页面为 Samba4；取消 Samba4、中文包及共享后端，也禁用 ksmbd 相关组件。
- 磁盘管理和分区扩容位于其他分类，保留。
- 编译仅手动触发，需求确认完成前不启动。

## 2026-10-09 状态页和 MWAN4 集成

- 概览温度：CPU、PON、LAN1、LAN2；使用 thermal、PHY hwmon 和 ponctl 的实际读数，缺失项不编造数值。
- CPU 使用率：两次 /proc/stat 差值，500 ms 采样窗口。
- PON 卡片：单列全宽布局，适配 Aurora；上行取 TX、下行取 RX，字节差值除以 1048576 和实际秒数，单位 MiB/s。
- Airoha LuCI：`naoki66/luci-app-airoha` 的 `luci-app-airoha-npu`，提交 `b87d08f8a0140ae98d25ec95350773b7baa7edbb`，包含今天本地固件中的 PON 速率与中文修改。未引入该 feed 中的 factory/recovery/mesh/netmode/fancontrol 页面。
- MWAN4：`gbosek/claus778-mwan4` 提交 `57dd176701c21e7dbf6206aec2152a4321212c70`，1.0.0-r13，及其 LuCI/中文包；源码随仓库保存。沿用今天版本的默认禁用状态，不预设拨号账号或出口。
- 云编译包装改用 OpenWrt 的 rust-package.mk，以目标工具链编译并保留 Cargo.lock，避免依赖本机预装 Cargo 和离线缓存。
- 保留内核 CONFIG_IP_ROUTE_MULTIPATH 支持 ECMP；PPE/NPU 驱动仍使用本次 ImmortalWrt 基线。

首次云编译成功，但产物清单缺少 MWAN4；该产物不能作为插件齐全版。
尚未在新基线上刷机或验证双 WAN 硬件卸载。

## MWAN4 漏包修正和终端补齐

- 修正 mwan4 的 Rust 架构依赖：使用 `$(RUST_ARCH_DEPENDS)`，不再依赖不存在的 `RUST_ARCH_DEPENDS` Kconfig 选项。
- 加入 ttyd、luci-app-ttyd 和中文包。
- MWAN4 r13 已有 IPv4 源/目标 CIDR 策略路由和中文管理页面；按用户要求不另加 pbr/luci-app-pbr。这不表示它包含 pbr 的域名分流等全部功能。
- defconfig 后检查必需包全部为 y，发布前检查固件 manifest；缺包则失败，阻止发布不完整固件。

## RPS 持久化

使用用户 2026-10-09 在相同 VIKINGYFY r0-a385200 / Linux 6.18.54
基线上运行时测试的参数：接收 CPU 掩码 `f`、RFS 总表 `4096`、各接收队列 `1024`。
`xg2010g-rps` 为系统 packet_steering 服务提供平台钩子，开机、网络配置重载、
接口事件都调用同一脚本，避免额外后台脚本和通用分配器相互覆盖。
仅在 Gemtek XG2010G 应用；其他板型沿用通用脚本。packet_steering=0 时尊重关闭设置。
首次启动设置 packet_steering=2。此改动不调整 IRQ、threaded NAPI 或 PPE/NPU 驱动。
用户此前的运行时测试是参数来源，本次固件中的持久化实现仍需刷入后验证。

源码提交已固定；feeds 和第三方插件仍沿用上游更新脚本读取其分支，
因此这是该版本源码上的定制构建，不保证与上游发布包逐字节一致。
