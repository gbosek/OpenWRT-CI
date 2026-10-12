# XG2010G build notes

The `AIROHA` build selects only the Gemtek XG2010G profile. Its `luci-app-airoha-npu` source is synced from `naoki66/luci-app-airoha` commit `24441ffbbf69086745d5b6b7e09a187164f91f07`, package release `2.0.0-9`.

- The upstream package now exposes Frame Engine GDM/CDM/PSE counters. The Makefile selects the kernel `/dev/mem` and BusyBox `devmem` build options needed by those counters.
- Optical module and PON status are provided by the separate `luci-app-pon-status` package in this firmware build.
- CPU PLL behavior remains in the XG2010G kernel/DTS configuration. This LuCI package controls the CPU frequency ceiling through cpufreq sysfs; it does not expose direct PLL register writes.
