# miniupnpd 2.3.11 feed 补丁适配

归档 SHA256：`91994b127da735b2c97f19992e34420648c0e8c4ace8a4bcb0596e7685c48678`。

ImmortalWrt packages 的 020/030 补丁已由该归档的原生实现覆盖，继续按版本和哈希核实后省略。040 日志及 900 XML 兼容补丁仍有用途，不能整份删除；这里提供它们对 2.3.11 的适配版本。

- 040：适应 `print_usage()` 移到前方，以及 HTTP/HTTPS 端口设置间新增的 NFQUEUE 赋值；保留日志级别、启动协议说明和安全模式提示。
- 900：适应 XML 栈索引写法及 `512+MINIUPNPD_DESC_SIZE` 的缓冲区长度；保留新版缓冲区保护和所有 CRLF 格式兼容修改。
- 010 Microsoft/Apple IGDv2 兼容补丁不改。

`Scripts/fix-miniupnpd-feed.py` 只处理已确认 SHA256 的旧补丁，改包 release 为 2；重复执行不再改动。开始整机编译前，以验证过的源码归档实际应用全部剩余补丁，使用 `--fuzz=0`；未知/失配补丁不能被静默删除。测试覆盖重复运行、未知补丁保留、版本和归档哈希不匹配时拒绝处理。

本地已完成包含全部补丁的 nftables / IPv6 / IGDv2 配置 ARM64 musl 交叉编译与链接，未执行目标程序。整机固件仍必须通过 GitHub 构建及成品检查。
