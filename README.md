# AutoBuildTWrt

> 基于 CI 的 ImageBuilder 工作流，自动化构建 ImmortalWrt 固件。
> 本项目为个人自建项目，以 [wukongdaily/AutoBuildImmortalWrt](https://github.com/wukongdaily/AutoBuildImmortalWrt) 为蓝本，并在此基础上实现了**内嵌 store 软件同步方案**。

**⚠️ 重要声明**：本项目为个人独立维护的第三方项目（脚本），与 ImmortalWrt 官方没有关联。项目中使用了 ImmortalWrt 官方 ImageBuilder 工具打包生成固件，但用户自行定制产生的任何 bug，均不代表 ImmortalWrt 官方固件的 bug；相关问题请勿在 ImmortalWrt 群内反馈。

[![GitHub](https://img.shields.io/github/license/passengerya/AutoBuildTWrt.svg?label=LICENSE&logo=github&logoColor=%20)](https://github.com/passengerya/AutoBuildTWrt/blob/master/LICENSE)

---

## 🤔 这是什么？

一个**免费、开源的 OpenWrt/ImmortalWrt 固件自动构建项目**：fork 本仓库、点击几下鼠标，GitHub Actions 就会在云端构建出定制固件，无需本地编译环境。

核心特性：

| 特性 | 说明 |
| --- | --- |
| 🧩 第三方软件即时自动同步 | 上游软件包由 [CloudRunFilesBuilder](https://github.com/passengerya/CloudRunFilesBuilder) 每日打包，构建完成后即时通知（repository_dispatch）本仓库 Sync Store 同步进内嵌 `store/` 目录（北京时间 07:00 定时兜底），**新版本软件当天即可用** |
| ⚙️ 按需集成软件 | 在 `shell/custom-packages.sh` 中**取消注释**即可把软件装进固件（详见下文"如何开启第三方软件"） |
| 📦 自定义固件大小 | 默认 1GB，可选 1G~4G；也可用分区扩容插件自行扩容 |
| 🐳 可选预装 Docker | UI 勾选即可 |
| 🏪 可选集成 iStore 商店 | UI 布尔开关控制 |
| ⏰ 每日自动构建 | 集中开关控制（`build-flags.conf`），Sync Store 同步成功后即刻构建 + 北京时间 07:40 定时兜底，Release 标注「每日自动构建/手动构建」区分 |
| 🌐 支持 24.10.x 与 25.12.x | 两条软件通道严格分离（opkg/ipk 与 apk），互不干扰 |
| 📡 多机型 | x86-64（含 ISO 安装器）、rockchip、armsr-armv8、sunxi、N1、无线路由器（MTK/高通/博通）、树莓派等，详见 [SUPPORT.md](SUPPORT.md) |
| 🔧 自定义管理地址 | 多网口机型可在 UI 设置 LAN IP（默认 `192.168.100.1`） |

## 🔄 具体实现流程

本项目是一条**三仓库流水线**的最后一环，第三方软件的完整流转过程如下：

### 阶段一：软件同步（每日全自动）

```
① CloudRunFilesBuilder（第一层，独立仓库）
   51 个工作流每天北京时间 6:00 起错峰运行：
   拉取上游最新 ipk → makeself 打包成 .run 自解压包 → 上传当日 Release
   → 「最新启动且仍在运行」的构建（领导选举）即时通知本仓库（repository_dispatch）

        ↓ Sync Store 工作流（即时触发；每天北京时间 7:00 定时兜底）

② 内嵌 store/（本仓库内，由同步脚本维护）
   store/sync_run_files.py 三阶段：
   阶段 A：从最新 Release 同步 .run 到 store/run/x86/、store/run/arm64/
           （24.10 ipk 版与 25.12 apk 版按通道共存，各自保留一个变体；
            同前缀旧版本自动清理，不触碰 ipk 子目录）
   阶段 B：把每个 .run 自解压包里的 ipk 解压到应用同名子目录
           （如 dufs-0.46.0-r1_x86_64.run → store/run/x86/dufs/*.ipk）
   阶段 C：自动维护软件列表——更新 store/README 软件表与两个开关文件的生成段
           （启用状态跨同步保留；连续 3 次不在上游的应用标记「停更」并保留；
            冲突组同时开启时在生成段顶部输出 ⚠️ 警告）
   完成后自动 git 提交推送
```

### 阶段二：固件构建（手动触发）

```
③ 构建工作流（15 个，手动触发，或由每日自动构建开关控制）
   参数示例：luci 版本 / 管理 IP / 软件包空间 / 集成 iStore / 集成 Docker / PPPoE
   （每日自动构建见下文「每日自动构建」，开关集中在仓库根目录 build-flags.conf）

   ↓ docker 挂载本仓库目录到 ImageBuilder 容器
     store/ shell/ 机型配置文件 files/ → /home/build/immortalwrt/

④ 容器内 build24.sh（或 build25.sh）七环节：
   1. source shell/custom-packages.sh —— 读取你开启的软件包列表
   2. 写入 PPPoE 配置（UI 输入）
   3. 拷贝内嵌 store（按通道过滤）：24.10 构建只拷非 25_/25- 前缀的 .run，25.12 只拷 25_/25- 前缀的 .run，外加应用 ipk/apk 子目录 → extra-packages/
   4. prepare-packages.sh（或 apk 版）：只解压本通道 .run + 收集 ipk/apk → 更新 ImageBuilder 的 packages/ 软件包目录
      （2026-09-15 起带预检：解压失败立即中断；生成 TSV 包清单；重名包内容冲突报错、其余告警）
   5. 拼接 PACKAGES = 官方基础包 + 你开启的第三方包（openclash/ssrp 额外下载内核）
   6. make image ... V=s 构建（完整日志写到宿主 runner，失败时自动上传日志与包清单 artifact 供排查）
   7. 固件上传到对应 Release（Autobuild-x86-64 等，fail_on_unmatched_files 防静默失败）

⑤ 产出：OpenWrt/ImmortalWrt 固件包（.img.gz / rootfs.tar.gz / ISO 安装器）
```

### 两条软件通道（严格分离）

| | 24.10 通道（ipk/opkg） | 25.12 通道（apk） |
| --- | --- | --- |
| 软件开关文件 | `shell/custom-packages.sh` | `shell/apk-custom-packages.sh` |
| 构建脚本 | 各机型的 `build24.sh` | 各机型的 `build25.sh` |
| store 中 .run 前缀 | 无前缀 / `24_` | `25_` / `25-` |
| 安装命令（.run 内） | `opkg install *.ipk` | `apk add --allow-untrusted *.apk` |

## 📂 项目结构

```
AutoBuildTWrt/
├── .github/workflows/    # 15 个机型构建工作流 + sync-store.yml 同步 + autobuild-gate.yml 自动构建闸门
├── store/                # 内嵌第三方软件包库（Sync Store 工作流每日自动更新）
│   ├── sync_run_files.py # 同步脚本：.run 拉取 + ipk 解压 + 列表维护三阶段
│   └── run/x86/  run/arm64/   # .run 根目录 + 应用同名 ipk 子目录
├── shell/                # 公共脚本（所有机型共用）
│   ├── custom-packages.sh        # 24.10 第三方软件开关（取消注释开启）
│   ├── apk-custom-packages.sh    # 25.12 第三方软件开关
│   ├── prepare-packages.sh       # 解 .run / 收集 ipk → packages/ 软件包目录
│   └── switch_repository.sh      # 软件源切换预留
├── x86-64/  rockchip/  armsr-armv8/  sunxi-cortexa53/
├── n1/  mediatek-filogic/  raspberrypi/   # 各机型：build24/25.sh + imm 配置文件
├── files/  arch/  model/  glinet/         # 固件开机定制 / 架构 / 机型清单
└── PACKAGES.md  SUPPORT.md                # 软件支持列表 / 机型支持列表
```

## 🚀 使用方法

1. **fork 本仓库**（或直接使用）；
2. 进入 **Actions** 页面，选择对应机型的工作流（例如 `Build 24.10.x x86-64`），点击 **Run workflow** 填写参数：

   | 输入项 | 说明 |
   | --- | --- |
   | luci_version | 选择 ImmortalWrt 版本（24.10.0 ~ 24.10.6 / 25.12.x） |
   | custom_router_ip | 路由器管理地址（仅多网口机型生效） |
   | profile | 软件包空间大小：1G / 2G / 3G / 4G |
   | enable_store | 是否集成 iStore 商店 |
   | include_docker | 是否预装 Docker |
   | enable_pppoe + 账号密码 | 是否配置 PPPoE 拨号 |

3. 构建约 8~15 分钟，产物自动上传到 Release（各机型的 tag 如 `Autobuild-x86-64`），下载刷机即可。

> 第三方软件无需手动处理：只要在 `custom-packages.sh`（或 apk 版）里取消了注释，构建时自动从内嵌 store 装进固件。

## ⏰ 每日自动构建

1. 编辑仓库根目录的 **[build-flags.conf](build-flags.conf)**，把想自动构建的机型开关改为 `1`（`AUTO_BUILD_<机型>_<通道>=1`），推送到 master 即生效；
2. 触发链：每天北京时间 07:00（UTC 23:00）定时同步内嵌 store **成功后即刻触发**自动构建；若同步失败/漏发，各构建工作流还有 **北京时间 07:40（UTC 23:40）定时兜底**；
3. 去重：同一工作流 20 小时内只自动构建一次，当日已手动构建过的自动跳过；
4. 参数：自动构建使用各输入项的默认值（如需自定义请手动运行工作流）；
5. 区分：Release 说明会标注 **「每日自动构建」或「手动构建」+ 北京时间**；
6. 固件文件**不覆盖**：每个固件文件名带构建时间戳（如 `…-combined-efi-20260917-0740.img.gz`），历史固件全部保留，一个固件对应一个文件。

## ✅ 如何开启软件（两种来源）

**来源一：上游同步的第三方软件**（每日自动同步进内嵌 store，自动生成段）
1. 确认该软件在 [store/run](https://github.com/passengerya/AutoBuildTWrt/tree/master/store/run) 里有对应目录（x86 看 `x86/`，ARM 看 `arm64/`）；
2. 编辑 `shell/custom-packages.sh`（24.10）或 `shell/apk-custom-packages.sh`（25.12），**把对应行行首的 `#` 去掉**，例如：
3. 两个开关文件的列表都按用途分了大分类（`代理工具 / 网络服务 / 广告与DNS / 文件与存储 / 系统与界面 / 设备管理`，imm 固定段还有 `穿透与组网 / 下载与媒体 / 系统管理 / 校园网`），可按分类标题快速定位要开启的软件；分类由同步自动维护，新增软件会自动归入对应分类。

```bash
# 自动生成: lucky | Lucky大吉 | 端口转发/反向代理/内网穿透 | 2.20.2-r13 | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-lucky lucky"   # ← 去掉行首 # 即开启
```

**来源二：imm 仓库内软件**（ImmortalWrt 官方仓库内的软件，无需同步，固定段）
- 构建固件的底层来源就是 imm 仓库，这些软件构建时**直接从官方源解析安装**；
- 清单见 [store/imm-packages.md](store/imm-packages.md)（含中文说明），在开关文件下半部分「以下imm仓库内的软件」固定段中取消注释即可，例如：

```bash
#===========================以下imm仓库内的软件==============================↓
# DDNS-Go - 动态域名解析
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ddns-go-zh-cn"   # ← 去掉行首 # 即开启
```

3. 触发构建，软件即被打进固件。

> 注意：24.10 与 25.12 是两条独立通道，请按固件版本改对应的开关文件；部分软件存在冲突组合（如 `luci-app-run` 与 `quickfile`、`clashoo` 与 `nikki`、`advancedplus` 与 `argon-config`），注释里已标注请勿同时开启——若被同时开启，Sync Store 会在生成段顶部自动输出 ⚠️ 冲突警告行。
> 主题提示：各机型 build 脚本固定加入 Argon 主题；`shadcn` 并非纯 CSS 主题（会接管 LuCI 菜单/路由），如需启用请只保留一个主题界面，同步脚本会在多主题并存时输出 ⚠️ 警告。aurora 主题全系（主题/配置中心/语言包）已彻底移除不再提供。
> 若开启 `quickfile`（会引入 nginx 前端接管 80 端口），固件首次启动会自动修复 LuCI 会话 cookie 转发（历史教训见开发说明防错清单 #27）；反之，**不带 quickfile 的固件**首次启动会自动清除残留的 nginx 接管标志并恢复 uhttpd——从带 quickfile 的旧固件「保留配置」升级过来也不会丢网页服务（见防错 #35）。

## 📟 固件默认行为

- **单网口设备**：默认 DHCP 自动获取 IP（旁路由模式），在上级路由器查看分配的地址访问后台；
- **多网口设备**：WAN 口 DHCP（勾选 PPPoE 则为拨号），LAN IP 为 UI 中设置的值（默认 `192.168.100.1`），eth0 为 WAN；
- 后台：用户名 `root`，密码无（建议首次登录后设置）；
- 主机名：默认统一为 `Twrt`（可在 系统 → 系统 → 主机名 中修改）；
- 为易用性，WAN 口防火墙入站默认开启，调试完毕后建议自行关闭（网络 → 防火墙 → WAN 入站改为拒绝）；
- 以上行为均可通过 `files/etc/uci-defaults/99-custom.sh` 调整。

## 🌿 分支策略

- **master**：生产分支（默认）。`Sync Store` 定时同步与 Actions 手动构建都只使用 master 上的文件，改动需合并到 master 才生效；
- **dev**：开发分支，验证通过后合并 master。

## 🎉 鸣谢

本项目基于以下项目与作者，感谢他们的贡献与灵感：

- [wukongdaily/AutoBuildImmortalWrt](https://github.com/wukongdaily/AutoBuildImmortalWrt) —— 项目蓝本
- [wukongdaily/RunFilesBuilder](https://github.com/wukongdaily/RunFilesBuilder) —— run 打包方案
- [ImmortalWrt](https://github.com/immortalwrt) —— 固件与 ImageBuilder
- [passengerya/CloudRunFilesBuilder](https://github.com/passengerya/CloudRunFilesBuilder) —— 上游软件同步层
- 以及各第三方软件的上游作者（passwall、mosdns、sirpdboy、ophub、linkease 等，详见 [PACKAGES.md](PACKAGES.md)）
