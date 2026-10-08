# XG2010G 编译基线

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

本次仅完成源码与构建流程集成，尚未在新基线上编译、刷机或验证双 WAN 硬件卸载。

源码提交已固定；feeds 和第三方插件仍沿用上游更新脚本读取其分支，
因此这是该版本源码上的定制构建，不保证与上游发布包逐字节一致。
