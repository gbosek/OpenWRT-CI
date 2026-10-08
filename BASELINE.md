# XG2010G 编译基线

- 上游版本：[AIROHA-VIKINGYFY-owrt-26.10.08-11.11.17](https://github.com/VIKINGYFY/OpenWRT-CI/releases/tag/AIROHA-VIKINGYFY-owrt-26.10.08-11.11.17)
- 源码仓库：VIKINGYFY/immortalwrt，分支 owrt。
- 源码提交：`a38520034ee4bdd25dd6e88c4c59261f289ee17e`，由 OWRT-ALL 的 WRT_REVISION 固定。
- 默认地址：192.168.1.1。
- HomeProxy 及 sing-box 后端不选入固件。
- NAS 分类：该版本已选中的 NAS 页面为 Samba4；取消 Samba4、中文包及共享后端，也禁用 ksmbd 相关组件。
- 磁盘管理和分区扩容位于其他分类，保留。
- 编译仅手动触发，需求确认完成前不启动。

源码提交已固定；feeds 和第三方插件仍沿用上游更新脚本读取其分支，
因此这是该版本源码上的定制构建，不保证与上游发布包逐字节一致。
