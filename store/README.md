# 内嵌 store 目录

本目录存储 **ImmortalWrt 官方仓库以外**的第三方软件包（.run 自解压包 + .ipk），
供本项目各机型的构建脚本直接使用（构建时挂载到 ImageBuilder 容器内的
`/home/build/immortalwrt/store`，由 `shell/prepare-packages.sh` 解包收集到 `packages/` 目录）。

## 目录结构

```
store/
├── run/
│   ├── x86/      # x86_64 架构: .run 放根目录, .ipk 按应用建同名子目录
│   └── arm64/    # aarch64 架构: 同上
├── README.md
└── sync_run_files.py            # 同步脚本（由 sync-store 工作流调用）
```

## 软件来源（两部分）

1. **上游同步的第三方软件**：`run/x86/`、`run/arm64/` 中的 .run 与 ipk 目录，
   由 Sync Store 工作流每日从 CloudRunFilesBuilder 同步（见下方同步机制与自动维护的软件列表）；
2. **imm 仓库内软件（固定列表）**：ImmortalWrt 官方仓库内的软件（固件编译的底层来源），
   **无需同步**，构建时直接从官方源安装；清单见 [imm-packages.md](imm-packages.md)，
   在 `shell/custom-packages.sh` / `shell/apk-custom-packages.sh` 的固定段中取消注释启用。

## 同步机制

同步分三个阶段（`sync_run_files.py`，API 请求带重试，限流/网络抖动不中断同步）：

**阶段一：.run 文件**
- 来源：`passengerya/CloudRunFilesBuilder` 的 Release 资产（每日构建的 .run）
- 选择策略：**直接取最新 Release**（builder 全部构建完成发 `builder-done` 通知触发同步，此时最新 Release 已完整；每日 07:00 定时兜底时当日构建也已结束）。最新 Release 尚无 .run 资产时跳过本次同步且**不判定停更**（避免上传中途误计缺失）；**缺失应用不回落旧 Release**，由停更机制接管——连续 3 次不在最新 Release 即标记「上游停更(保留旧版)」（文件保留，重新出现自动解除）
- 分类规则：
  - 文件名含 `x86_64` → `run/x86/`；含 `aarch64`/`arm64` → `run/arm64/`
  - 含 `aarch32`/`arm32`/`i386` → 跳过；无架构标记（如 `_all`）→ 两个目录都放
  - 同一应用同一架构多个变体时：优先延续**本通道**现有变体（24/25 通道互不影响）；新应用按 `generic > cortex-a53 > a53 > 纯aarch64` 选择
  - 同步后删除**同应用、同架构、同日期前缀**的旧版本 .run（`24_` 只删 `24_`、`25-` 只删 `25-`），不触碰 .ipk 和子目录

**阶段二：软件包目录（.ipk 文件）**
- 来源：阶段一从 CloudRunFilesBuilder 拉取的 **.run 自解压包本身**——同步时把每个 .run 里的 .ipk 解压到应用同名子目录（如 `dufs-0.46.0-r1_x86_64.run` → `run/x86/dufs/*.ipk`）
- 由解压生成的应用目录每次同步会**重建**（归同步管理）；不含 .ipk 的 .run（如 25.12 的 apk 包）不生成目录
- **冗余包剔除**：解压时按 `EXCLUDED_PACKAGE_RE` 剔除已知与主包文件冲突的包（`easytier-noweb`、`luci-i18n-easytier-zh-cn`，与 builder 的剔除一致），ipk/apk 双通道生效——被剔除的包不进应用目录、不进软件列表，上游资产完全替换后自动成为空操作；`shell/prepare-packages.sh`（apk 版同）在构建时对 .run 解包结果做**同样的兜底过滤**，防止选源拿到旧 .run 时剔除包重新进入 packages/
- **已下架应用**：`EXCLUDED_APPS` 中的整应用全链路剔除——不下载 .run、不解压、不进软件列表。当前为空（aurora 全系已于 2026-09-18 恢复：主题 + 配置中心 + 语言包）
- 人工新增 ipk 请放入独立的、与 .run 推导名不冲突的目录，不会被删除

**阶段三：软件列表维护（自动）**
- 更新下方软件列表表格（按 store 实际内容增删行）与两个开关文件的自动生成段；
- **生成段按用途大分类**：分类（代理工具/网络服务/广告与DNS/文件与存储/系统与界面/设备管理）由同步脚本 APP_META 的 `cat` 字段决定，每次同步保持分类，新应用填好 cat 即自动归类；
- **启用状态跨同步保留**：取消注释的应用不会因同步被重新注释；
- **停更保留**：连续 3 次不在上游 Release 的应用保留 .run 与列表，注释附加「上游停更」，重新出现自动解除；
- **冲突警告**：冲突组（clashoo↔nikki、advancedplus↔argon、quickfile↔luci-app-run、argon↔shadcn）同时启用时，生成段顶部输出 ⚠️ 警告行；其中 Argon 由各机型 build 脚本固定加入（`BASE_ENABLED_APPS`），生成段里未取消注释也参与主题冲突检查，启用 shadcn 时会提示多主题并存；
- 完成后自动 git 提交推送（提交范围 store/ + shell/）。

**触发**：`.github/workflows/sync-store.yml`
- 即时：上游 builder 全部构建完成后发 repository_dispatch（event_type: `builder-done`）
- 定时兜底：每天北京时间 07:00（UTC 23:00，晚于上游 06:00 的每日构建）
- 手动：workflow_dispatch（可指定其它源仓库）
- **下游动作**：仅「定时触发」的同步成功后发 repository_dispatch（`store-synced`）通知各构建工作流执行每日自动构建（开关见仓库根目录 `build-flags.conf`；构建工作流另有北京时间 07:40 = UTC 23:40 定时兜底）

> 本目录只由 `sync-store` 工作流自动更新，**不要手动修改**；如需人工新增 ipk，按应用建同名子目录放入即可。

## 如何手动同步

```bash
python3 store/sync_run_files.py --dry-run   # 预览
python3 store/sync_run_files.py             # 正式同步（需要 GITHUB_TOKEN）
```

<!-- AUTO-SOFTWARE-TABLE:START (Sync Store 自动维护, 勿手动修改) -->
| 软件 | 中文名 | 通道 | 版本 | 架构 | 用途 | 来源 |
| --- | --- | --- | --- | --- | --- | --- |
| argon | Argon主题 | apk (25.12) | 2.4.7 ⚠️上游停更 | arm64 / x86 | 简洁主题, 支持明暗自动切换 | ImmortalWrt 官方源 |
| clashoo | Clashoo代理 | apk (25.12) | 2026.09.16 ⚠️上游停更 | arm64 / x86 | 代理工具(与 nikki 冲突勿同时开启) | kenzok8/openwrt-clashoo |
| clashoo-cc0 | — | apk (25.12) | 2026.09.19.5019 ⚠️上游停更 | arm64 / x86 | — | — |
| easytier | 异地组网 | apk (25.12) | v2.6.4 ⚠️上游停更 | arm64 / x86 | EasyTier 点对点组网工具 | EasyTier/luci-app-easytier |
| luci-app-advancedplus | 高级设置 | apk (25.12) | 1.8.7-r20251116 ⚠️上游停更 | arm64 / x86 | 进阶设置(与 argon-config 冲突勿同时开启) | sirpdboy/luci-app-advancedplus |
| luci-app-amlogic | 晶晨宝盒 | apk (25.12) | 3.1.321-r1 ⚠️上游停更 | arm64 / x86 | 晶晨机顶盒管理(仅 ARM64 平台) | ophub/luci-app-amlogic |
| luci-app-aurora-config | 极光配置中心 | apk (25.12) | 1.2.5-r20260920 ⚠️上游停更 | arm64 / x86 | Aurora 主题配置中心(提供 /etc/config/aurora, 与主题配套启用) | eamonxg/luci-app-aurora-config |
| luci-app-oaf | 应用过滤 | apk (25.12) | 7.0-r1 ⚠️上游停更 | arm64 / x86 | OpenAppFilter 应用过滤(基于 nftables, 程序管控/游戏加速) | destan19/OpenAppFilter |
| luci-app-store | iStore商店 | apk (25.12) | 0.2.1-r1 | arm64 / x86 | iStore 应用商店 | linkease/istore |
| luci-app-tailscale-community | Tailscale组网 | apk (25.12) | 4.2.3-r1 ⚠️上游停更 | arm64 / x86 | Tailscale 组网(Community 版) | Tokisaki-Galaxy/luci-app-tailscale-community |
| luci-theme-aurora | 极光主题 | apk (25.12) | 1.4.0-r20260920 ⚠️上游停更 | arm64 / x86 | 极光主题界面(需配套 luci-app-aurora-config 配置中心, 会接管 LuCI 菜单/路由, 谨慎启用) | eamonxg/luci-theme-aurora |
| luci-theme-shadcn | Shadcn主题 | apk (25.12) | 0.6.0-r20260920 ⚠️上游停更 | arm64 / x86 | 现代 Shadcn 风格界面主题(会接管 LuCI 菜单/路由, 24.10 下谨慎启用) | eamonxg/luci-theme-shadcn |
| mosdns | DNS分流 | apk (25.12) | v5.3.4-r14 ⚠️上游停更 | arm64 / x86 | 高性能 DNS 分流(DoH/DoQ 等) | sbwml/luci-app-mosdns |
| openclash | OpenClash | apk (25.12) | v0.47.156 ⚠️上游停更 | arm64 / x86 | Clash 代理客户端 | vernesong/OpenClash |
| openwrt-daede | eBPF代理 | apk (25.12) | 2026.09.22 ⚠️上游停更 | arm64 / x86 | 基于 eBPF 的高性能透明代理(dae/daed) | kenzok8/openwrt-daede |
| passwall | PassWall | apk (25.12) | 26.9.16 ⚠️上游停更 | arm64 / x86 | 代理工具(自带依赖) | Openwrt-Passwall/openwrt-passwall |
| passwall2 | PassWall2 | apk (25.12) | 26.9.16-1 ⚠️上游停更 | arm64 / x86 | 代理工具(自带依赖) | Openwrt-Passwall/openwrt-passwall2 |
| quickfile | 文件管理 | apk (25.12) | 1.0.16 ⚠️上游停更 | arm64 / x86 | 轻量网页文件管理器(与 luci-app-run 冲突勿同时开启) | sbwml/luci-app-quickfile |
| rtp2httpd | IPTV转发 | apk (25.12) | 3.17.1-r1 ⚠️上游停更 | arm64 / x86 | IPTV 流媒体转发服务器 | stackia/rtp2httpd |
| sing-box | Sing-box内核 | apk (25.12) | v1.14.1 ⚠️上游停更 | arm64 / x86 | 通用代理内核 | SagerNet/sing-box |
| ssrp-mihomo | SSRP代理 | apk (25.12) | ⚠️上游停更 | arm64 / x86 | SSR-Plus 代理工具(mihomo 内核) | fw876/helloworld |
| adguardhome | 本地DNS去广告 | ipk (24.10) | v0.107.79 | arm64 / x86 | AdGuardHome 广告拦截与 DNS 服务 | AdguardTeam/AdGuardHome |
| argon | Argon主题 | ipk (24.10) | 2.4.3-r20250722 | arm64 / x86 | 简洁主题, 支持明暗自动切换 | ImmortalWrt 官方源 |
| bandix | 流量监控 | ipk (24.10) | 0.11.0-r25 ⚠️上游停更 | arm64 / x86 | Bandix 实时流量监控与统计 | timsaya/luci-app-bandix + dl.openwrt.ai |
| clashoo | Clashoo代理 | ipk (24.10) | 2026.09.19 | arm64 / x86 | 代理工具(与 nikki 冲突勿同时开启) | kenzok8/openwrt-clashoo |
| dufs | 文件服务器 | ipk (24.10) | 0.46.0-r1 | arm64 / x86 | 轻量文件服务器(静态托管/上传/WebDAV) | sigoden/dufs |
| easytier | 异地组网 | ipk (24.10) | v2.6.4 ⚠️上游停更 | arm64 / x86 | EasyTier 点对点组网工具 | EasyTier/luci-app-easytier |
| homeproxy | 代理平台 | ipk (24.10) | 26.187.07809 | arm64 / x86 | 现代代理平台(基于 sing-box) | immortalwrt/homeproxy |
| luci-app-advancedplus | 高级设置 | ipk (24.10) | 1.8.7-r20251116 ⚠️上游停更 | arm64 / x86 | 进阶设置(与 argon-config 冲突勿同时开启) | sirpdboy/luci-app-advancedplus |
| luci-app-amlogic | 晶晨宝盒 | ipk (24.10) | 3.1.321-r1 ⚠️上游停更 | arm64 / x86 | 晶晨机顶盒管理(仅 ARM64 平台) | ophub/luci-app-amlogic |
| luci-app-aurora-config | 极光配置中心 | ipk (24.10) | 1.2.5-r20260920 ⚠️上游停更 | arm64 / x86 | Aurora 主题配置中心(提供 /etc/config/aurora, 与主题配套启用) | eamonxg/luci-app-aurora-config |
| luci-app-nekobox | NekoBox代理 | ipk (24.10) | 2.0.9 ⚠️上游停更 | arm64 / x86 | NekoBox 代理工具 | Thaolga/openwrt-nekobox |
| luci-app-oaf | 应用过滤 | ipk (24.10) | 6.1.4-r1 ⚠️上游停更 | arm64 / x86 | OpenAppFilter 应用过滤(基于 nftables, 程序管控/游戏加速) | destan19/OpenAppFilter |
| luci-app-store | iStore商店 | ipk (24.10) | 0.2.1-r1 | arm64 / x86 | iStore 应用商店 | linkease/istore |
| luci-app-tailscale-community | Tailscale组网 | ipk (24.10) | 4.2.3-r1 ⚠️上游停更 | arm64 / x86 | Tailscale 组网(Community 版) | Tokisaki-Galaxy/luci-app-tailscale-community |
| luci-app-uninstall | 高级卸载 | ipk (24.10) | v1.2.6 ⚠️上游停更 | arm64 / x86 | 彻底卸载插件的工具 | 上游 run 直采 |
| luci-theme-aurora | 极光主题 | ipk (24.10) | 1.4.0-r20260920 ⚠️上游停更 | arm64 / x86 | 极光主题界面(需配套 luci-app-aurora-config 配置中心, 会接管 LuCI 菜单/路由, 谨慎启用) | eamonxg/luci-theme-aurora |
| luci-theme-shadcn | Shadcn主题 | ipk (24.10) | 0.6.0-r20260920 ⚠️上游停更 | arm64 / x86 | 现代 Shadcn 风格界面主题(会接管 LuCI 菜单/路由, 24.10 下谨慎启用) | eamonxg/luci-theme-shadcn |
| lucky | Lucky大吉 | ipk (24.10) | 2.20.2-r13 ⚠️上游停更 | arm64 / x86 | 端口转发/反向代理/内网穿透 | gdy666/lucky via dl.openwrt.ai |
| momo | Momo代理 | ipk (24.10) | v1.2.1 | arm64 / x86 | 基于 sing-box 的透明代理 | nikkinikki-org/OpenWrt-momo |
| mosdns | DNS分流 | ipk (24.10) | v5.3.4-r14 ⚠️上游停更 | arm64 / x86 | 高性能 DNS 分流(DoH/DoQ 等) | sbwml/luci-app-mosdns |
| nikki | Nikki代理 | ipk (24.10) | v1.26.1 | arm64 / x86 | 代理工具(与 clashoo 冲突勿同时开启) | nikkinikki-org/OpenWrt-nikki |
| openclash | OpenClash | ipk (24.10) | v0.47.156 ⚠️上游停更 | arm64 / x86 | Clash 代理客户端 | vernesong/OpenClash |
| openlist2 | 网盘聚合 | ipk (24.10) | v4.2.6 | arm64 / x86 | OpenList2 网盘聚合(Alist 变体) | sbwml/luci-app-openlist2 |
| openwrt-daede | eBPF代理 | ipk (24.10) | 2026.09.22 ⚠️上游停更 | arm64 / x86 | 基于 eBPF 的高性能透明代理(dae/daed) | kenzok8/openwrt-daede |
| passwall | PassWall | ipk (24.10) | 26.9.9-1 ⚠️上游停更 | arm64 / x86 | 代理工具(自带依赖) | Openwrt-Passwall/openwrt-passwall |
| passwall2 | PassWall2 | ipk (24.10) | 26.9.12-2 ⚠️上游停更 | arm64 / x86 | 代理工具(自带依赖) | Openwrt-Passwall/openwrt-passwall2 |
| quickfile | 文件管理 | ipk (24.10) | 1.0.16 ⚠️上游停更 | arm64 / x86 | 轻量网页文件管理器(与 luci-app-run 冲突勿同时开启) | sbwml/luci-app-quickfile |
| rtp2httpd | IPTV转发 | ipk (24.10) | 3.17.1-r1 ⚠️上游停更 | arm64 / x86 | IPTV 流媒体转发服务器 | stackia/rtp2httpd |
| sing-box | Sing-box内核 | ipk (24.10) | v1.14.1 ⚠️上游停更 | arm64 / x86 | 通用代理内核 | SagerNet/sing-box |
| ssrp-mihomo | SSRP代理 | ipk (24.10) | ⚠️上游停更 | arm64 / x86 | SSR-Plus 代理工具(mihomo 内核) | fw876/helloworld |
<!-- AUTO-SOFTWARE-TABLE:END -->
