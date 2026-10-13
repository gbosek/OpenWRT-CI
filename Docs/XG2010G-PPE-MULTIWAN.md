# XG2010G PPE v2 multi-WAN firmware

Two build branches use the same source and existing XG2010G customizations:

| Branch | Selected stack |
| --- | --- |
| `xg2010g-mwan4-ppe` | Existing mossdef MWAN4 / brauliobo LuCI compatibility forks |
| `xg2010g-mwan3-nft-ppe` | Pinned Sysrous MWAN3-nft backend and matching nft LuCI frontend |

Both build only Gemtek XG2010G on VIKINGYFY/immortalwrt `owrt` commit
`a38520034ee4bdd25dd6e88c4c59261f289ee17e` (Linux 6.18.54). They preserve the
current Airoha NPU r10, Aurora, temperature/PON overview, ttyd, RPS, disk and
partition management, and package exclusions. Plugin feeds still follow the
existing update script; the multi-WAN sources are recorded in the variant JSON.

The only added kernel patch is the requested net v2 flow-statistics fallback:
`931-net-airoha-keep-PPE-offload-when-NPU-refuses-flow-stats.patch`.
With `CONFIG_NET_AIROHA_FLOW_STATS=y`, an NPU stats refusal disables the stats
capability while allowing PPE initialization to continue. This does not establish
that both WAN paths offload correctly on a particular running configuration.

The new branches build on push and also allow manual workflow dispatch. Output
names and release tags include `MOSSDEF-MWAN4-PPE` or `MWAN3-NFT-PPE`. Checks
reject missing Chinese/backend/frontend packages, selection of both stacks,
selection of another device, or a kernel built without the requested fallback.

When changing between MWAN4 and MWAN3-nft, configure interfaces and policies for
the selected stack. No ISP credentials or device-specific network configuration
are included in this repository.
