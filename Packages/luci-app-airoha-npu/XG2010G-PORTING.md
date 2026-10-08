# XG2010G port notes

Based on upstream `luanmuc/luci-app-airoha-npu` commit `5c6e9e079ad9ecb1446c674e964f797842675856`, with selected compatibility and reporting improvements from `rchen14b/luci-app-airoha-npu`.

- Keep upstream CPU, NPU, PPE, and Frame Engine RPC implementation and Chinese translation.
- Use device-tree SoC detection and backend-provided overclock availability/range; restrict register writes to Gemtek XG2010G on AN7581.
- Keep optional PPE and Frame Engine reads non-fatal so missing debugfs/register data does not blank the whole page.
- Exclude Wi-Fi token, station, and radio monitoring; XG2010G is used as a wired optical terminal.
- Remove board-specific physical LAN labels and show every PSE queue, including P3.
- The XG2010G board DTS explicitly opts into the kernel direct-PLL CPU PM-domain path, adapted from the upstream fallback patch. The board OPP table advertises up to 1600 MHz; startup uses `ondemand` with a 1400 MHz ceiling, and the user may select up to 1600 MHz. Other boards retain the SMC path. This source is experimental and not flash-ready until hardware stability and thermal behavior are verified; the failed locally signed boot chain is not reused.
- Do not grant the browser session direct `/dev/mem` access. CPU PLL programming is performed by the kernel CPU PM-domain driver; the root rpcd helper only sets the cpufreq maximum via sysfs.
