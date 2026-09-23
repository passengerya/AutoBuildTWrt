# AutoBuildTWrt 开发说明文档（当前实现）

| 项目 | 内容 |
| --- | --- |
| 文档版本 | v2.0（按当前实现重构） |
| 更新日期 | 2026-09-14 |
| 用途 | 描述新项目**当前的真实实现流程**，供开发审阅与排查问题 |
| 本地工作区 | `E:\Code\Mine\` 下仅保留 [CloudRunFilesBuilder](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/README.md)（第一层）与本项目；本文档位于本项目根目录 `AutoBuildTWrt开发说明.md`；参考仓库 store / AutoBuildImmortalWrt 本地副本已删除，内容以 GitHub 为准 |

---

## 1. 系统总览

### 1.1 三仓库流水线

```
① CloudRunFilesBuilder（第一层, 独立仓库, 主分支 daily）
   51 个工作流每天北京时间 6:00 起错峰运行:
   拉取上游 ipk → makeself 打包 .run → 上传当日 Release(tag=YYYY-MM-DD)
        │
        ▼
② 内嵌 store/（本仓库内, 由 Sync Store 工作流维护, 主分支 master）
   第一层全部完成后即时同步(repository_dispatch), 每天北京时间 7:00 定时兜底,
   分三阶段(见 §3):
   阶段一 .run 同步 → 阶段二 ipk 解压 → 阶段三 软件列表维护 → 自动提交
        │
        ▼
③ 固件构建（本仓库 15 个构建工作流, 手动触发 + 每日自动构建开关控制）
   docker imagebuilder 容器挂载 store/ shell/ 等 → build24/25.sh → make image
        │
        ▼
   最终产物: OpenWrt/ImmortalWrt 固件包 → 上传各机型 Release
```

### 1.2 两条软件通道（严格分离, 互不挤占）

| | 24.10 通道（ipk/opkg） | 25.12 通道（apk） |
| --- | --- | --- |
| 构建脚本 | 各机型 `build24.sh` | 各机型 `build25.sh` |
| 软件开关文件 | `shell/custom-packages.sh` | `shell/apk-custom-packages.sh` |
| .run 文件名前缀 | 无前缀 / `24_` / `24-` | `25_` / `25-` |
| .run 内安装命令 | `opkg install *.ipk` | `apk add --allow-untrusted *.apk` |
| 软件包目录 | store/run/<arch>/<应用>/（.ipk） | 不生成软件包目录（apk 在构建时由 apk-prepare-packages.sh 从 25.x .run 解出） |

### 1.3 当前状态（2026-09-15）

- 第一层：51 个工作流（29 个 24.10 + 19 个 25.12 + 3 个维护）
- 内嵌 store：每架构 27 个应用目录、45 个 .run（共 90）、287 个 ipk（24/25 两通道并存，25 通道已内嵌）
- 软件列表汇总：store/README.md 表格 37 个（应用×通道）条目
- 分支：第一层 daily（生产）/ dev；本仓库 master（生产）/ dev
- **2026-09-15 新增能力**：①同步脚本冗余包剔除（easytier-noweb/luci-i18n-easytier-zh-cn，与 builder f82f32f 一致）与按通道区分的变体选择修复；②构建工作流失败日志/包清单 artifact（宿主 runner tee + `if: failure()` 上传）+ PPPoE 输入掩码；③prepare 脚本 fail-fast（.run 解压非零即失败）+ TSV 包清单 + 重名检测；④离线单元测试 `tests/test_sync_run_files.py`；⑤LuCI 界面元素缺失根因已修复（nginx 前端不转发会话 cookie，见防错清单 #27，固件侧在 99-custom.sh 首启用自动修复）

---

## 2. 第一层 CloudRunFilesBuilder

### 2.1 工作流清单（53 个）

**24.10 ipk 通道（30 个）**：adguardhome、argon、aurora-theme、aurora-config、shadcn、oaf、advancedplus、amlogic（仅 ARM64）、bandix、clashoo、dufs、easytier、homeproxy、lucky、momo、mosdns、nekobox、nikki、openclash(oc)、openlist2、openwrt-daede、passwall(main)、passwall2(pw2)、quickfile(24-quickfile)、rtp2httpd、sing-box(singbox)、ssr-plus(ssrp)、tailscale-community、iStore(store)、高级卸载(advance_uninstall)

**25.12 apk 通道（20 个）**：argon25、build-pw、mosdns25、oc25、pw2-25、ssrp25、store25、25-quickfile、25-singbox、25-openwrt-daede、25-clashoo、25-rtp2httpd、25-advancedplus、25-aurora-theme、25-aurora-config、25-oaf、25-amlogic、25-tailscale-community、25-easytier、25-shadcn

> aurora 全系（主题+配置中心+语言包）2026-09-18 按用户要求恢复：luci-theme-aurora 为主题、luci-app-aurora-config 为配置中心（含 zh-cn 语言包）。此前 2026-09-16 曾整体下架（见防错清单 #33/#34 的历史记录）。同日新增 **oaf 应用过滤**（destan19/OpenAppFilter，24 ipk+25 apk 双通道，含 zh-cn 语言包）——注意上游 v7.x 起只发 apk，24.10 工作流自动选择「最近 20 个 release 中含 ipk 资产的最新一个」；25.12 的 zh-cn apk 名无版本后缀，匹配模式需放宽。

**维护（3 个）**：clean（旧运行记录）、clean-release（旧 Release）、remove（全部 tag）

> xray-core 已从第一层移除（imm 官方仓库自带，第三层已在开关文件 imm 固定段提供，24/25 两通道）。

### 2.2 单个工作流标准流程（5 段式）

```
checkout → 装 makeself → 下载 ipk 分平台目录 → apk 文件名规范化(25 通道, normalize_apk_names.py)
→ 拷 install.sh → 提版本号 → makeself 打包 → 上传当日 Release → 通知下游 Sync Store(领导选举)
```

上游资产分三种来源，对应三种模板（新软件照抄其一）：
1. **Release 直接发 ipk**（最常用）：jq 按架构正则解析资产 URL（参考 rtp2httpd.yml）
2. **Release 发 zip**：下载 zip → unzip 出 ipk（参考 easytier.yml）
3. **目录列表型源**（dl.openwrt.ai 等）：curl 目录页 grep ipk 链接（参考 lucky.sh / bandix.sh）

### 2.3 产物命名规范（★ 整条链路的基石）

```
[通道前缀]<应用名>_<版本>_<架构>.run
```

| 元素 | 规范 | 实例 |
| --- | --- | --- |
| 通道前缀 | 24.10 无前缀或 `24_`；25.12 `25_`/`25-` | `mosdns_v5.3.4-r14_x86_64.run`、`25-argon-2.4.7_aarch64_generic.run` |
| 应用名 | 全小写连字符 | `sing-box`、`luci-app-store` |
| 版本号 | `v1.2.3` 或 `1.2.3`，可带 `-rN` | `v5.3.4-r14`、`0.46.0-r1` |
| 架构 | `x86_64` / `aarch64_generic` / `aarch64_cortex-a53` / `aarch64_a53` / `_all` | `_all` = 架构无关，双目录都放 |

下游同步脚本完全依赖这些文件名做正则解析，**改名规则需三层同步评估**。

### 2.4 Release 与调度

- 所有工作流上传到**同一个当日 tag**（`YYYY-MM-DD` 北京时间），softprops/action-gh-release 自动合并资产；
- cron 全部在北京时间 06:00（UTC 22:00）起，**分钟数错开**（0~20），避免并发抢 tag；
- **完成即通知（领导选举）**：每个上传工作流末尾有「Notify Sync Store」步骤——sleep 15s 让同期构建入队后，由「最新启动且仍在运行/排队」的运行向第三层发 repository_dispatch（event_type: builder-done）即时触发同步，确定性单通知（跨仓库 PAT 存于 secrets.SYNC_DISPATCH_TOKEN，未配置时跳过、依赖定时兜底）；
- 注意事项（历史教训）：
  - 所有 GitHub API curl 必须带 `Authorization: token ${{ secrets.GITHUB_TOKEN }}`，否则会撞共享 IP 限流（60 次/小时）；
  - 版本号提取 sed 必须覆盖 `_all.ipk` 后缀（曾有 4 个应用版本号提取为空，产出 `bandix__x86_64.run` 等坏名）；
  - 新 workflow 必须**合并到 daily** 后才能通过 API dispatch（dispatch 按文件名只在默认分支查找）。

### 2.5 分支

- **daily**：生产（默认）。定时构建只读该分支；
- **dev**：开发，验证通过后合并 daily。

---

## 3. 第二层 内嵌 store（本仓库 `store/` 目录）

### 3.1 目录结构

```
store/
├── sync_run_files.py      # 同步脚本（三阶段, 唯一入口）
├── .sync-state.json       # 同步状态（管理目录名单 + 下线计数）
├── README.md              # 含软件列表汇总表格（自动维护）
└── run/
    ├── x86/               # .run 根目录 + 应用同名 .ipk 子目录
    └── arm64/             # 同上
```

### 3.2 触发与提交（.github/workflows/sync-store.yml）

- 触发：①即时——第一层全部构建完成后发 repository_dispatch（types: `builder-done`）；②定时兜底 `0 23 * * *`（北京 07:00 = UTC 23:00，晚于第一层 06:00 的构建）；③手动 workflow_dispatch（可指定 `builder_repo`）；
- 提交：`git add store/ shell/` → `sync: 从 <仓库> 同步 run 文件到内嵌 store (日期)`；
- 只读默认分支（master）的 workflow 文件，改动需合并 master 才生效。

### 3.3 阶段一：.run 同步

| 步骤 | 规则 |
| --- | --- |
| 拉取 | 取 BUILDER_REPO（默认 passengerya/CloudRunFilesBuilder）最新 Release 的全部 .run 资产 |
| 分组 | 按 `(通道, 应用, 架构)` 分组——通道由前缀判定（`25_`/`25-`→apk，其余→ipk），**24/25 两版各自独立保留、互不挤占**；架构由文件名正则判定 |
| 架构归类 | `x86_64`→`run/x86/`；`aarch64*`→`run/arm64/`；`aarch32`/`i386`→跳过；`_all`→两目录都放 |
| 变体选择 | 同组多候选时：版本高者优先 → 延续已有变体 → 无前缀命名优先 → 日期前缀新者优先 → 新应用按 `generic > cortex-a53 > a53 > 纯aarch64` |
| 旧版本清理 | 只删**同前缀、同应用**的旧 .run（`24_` 只删 `24_`），**不触碰 .ipk 和子目录** |
| 下载优化 | 文件已存在且大小一致则跳过 |

### 3.4 阶段二：ipk 解压

- 每个 .run 执行 `sh xxx.run --target tmp --noexec` 解压；
- 解出的 .ipk 放入应用同名子目录（`dufs-0.46.0-r1_x86_64.run` → `store/run/x86/dufs/*.ipk`），目录**每次重建**；
- 应用目录名由文件名推导（清洗前缀/架构/版本/`-rN`/`-rcNN`/hash/孤立数字）；
- 25.12 的 .run 内含 .apk → 不生成目录，但收集 apk 文件名供阶段三使用；
- **冗余包剔除**（2026-09-15 新增）：`EXCLUDED_PACKAGE_RE`/`is_excluded_package()` 在解压时剔除已知与主包文件冲突的包（easytier-noweb 与 easytier 提供相同二进制、luci-i18n-easytier-zh-cn 的文件已由 luci-app-easytier 内置），ipk/apk 双通道生效——被剔除的包不进应用目录、不进阶段三汇总，生成段自然保持干净；与 builder f82f32f 的剔除保持一致，上游资产完全替换后自动成为 no-op；
- 手动放入的 ipk 目录（与 .run 推导名不冲突）永不删除。

### 3.5 阶段三：软件列表自动维护

每次同步后自动维护三个文件（均在 `START/END` 标记段落内，手工内容不受影响）：

1. **store/README.md 软件列表表格**——按（应用×通道）汇总增删行，列：软件 / 中文名 / 通道 / 版本 / 架构 / 用途 / 来源；
2. **shell/custom-packages.sh**（ipk 通道，24.10 编译 package 列表）——每应用两行，注释含中文名/用途/版本：
   ```bash
   # 自动生成: bandix | 流量监控 | Bandix 实时流量监控与统计 | 0.11.0-r25 | 取消下一行注释即启用
   #CUSTOM_PACKAGES="$CUSTOM_PACKAGES bandix luci-app-bandix luci-i18n-bandix-zh-cn"
   ```
3. **shell/apk-custom-packages.sh**（apk 通道，25.12 编译 package 列表）——同上，行内为 apk 包名。
   元数据（中文名/用途/来源）维护在同步脚本的 `APP_META` 表中，新增应用时补一行即可。

关键机制：

| 机制 | 实现 |
| --- | --- |
| 包名提取 | 行内是**真实包名**（opkg/apk install 用包名）：ipk 文件名从右扫版本段（兼容 `23.05-24.10_luci-app-passwall` 这类带前缀包名）；apk 文件名从左扫（版本是连字符多段式，如 `mosdns-5.3.4-r14`） |
| 启用状态保留 | 用户在生成段取消注释的应用，按应用名识别，后续同步**保持启用** |
| 停更标记 | .run **连续 3 次同步**不在上游 Release → 标记为「停更」：.run 与软件包目录**全部保留**，README 表格版本列附加 `⚠️上游停更`、生成段注释附加「上游停更(保留旧版)」；应用重新出现在 Release 时自动解除标记；计数与停更名单存 `store/.sync-state.json` |
| 手动 ipk 安全 | 手动目录不进管理名单，永不被删 |
| 冗余包剔除 | 解压时按 `EXCLUDED_PACKAGE_RE` 剔除已知文件冲突包（见 §3.4），不进目录与汇总 |
| 变体选择按通道 | `existing_variants` 按 (通道, 应用, 架构) 索引，24/25 通道的既有变体互不影响（2026-09-15 修复：此前 24 通道变体会错误影响 25 通道选择） |
| 冲突提示含基础包 | 冲突检查使用 `enabled ∪ BASE_ENABLED_APPS`（各 build 脚本固定加入 Argon），启用 shadcn 等备选主题时生成段顶部输出 ⚠️ 警告（仅提示不阻断，供用户显式选择） |
| 幂等 | 无新资产时也重跑三阶段，保持列表与实际内容一致 |

---

## 4. 第三层 固件构建

### 4.1 构建工作流（15 个, 手动触发 + 每日自动构建开关控制）

| 工作流 | 机型/产物 | 镜像 |
| --- | --- | --- |
| build-x86-64-24.10.x.yml / 25.12.x.yml | x86-64 EFI 固件 | `x86-64-openwrt-<luci>` |
| build-iso.yml / build-iso-25.12.x.yml | x86-64 ISO 安装器 | `x86-64-openwrt-<luci>` |
| build-rockchip-immortalWrt-24.10.x.yml / 25.12.x.yml | rockchip | `rockchip-armv8-openwrt-<luci>` |
| build-sunxi-cortexa53-24.10.x.yml / 25.12.x.yml | 全志 sunxi | `sunxi-cortexa53-openwrt-<luci>` |
| build-N1.yml / build-boxs-by-ophub.yml / build-dev-board-by-flippy.yml / build-QEMU-arm64-24.10.x.yml | 盒类/ARM64 | `armsr-armv8-openwrt-<luci>` |
| build-RaspBerryPi-24.10.x.yml | 树莓派 | 专用 `$tag` 镜像 |
| build-wireless-router.yml / 25.12.yml | 无线硬路由（MTK/高通/博通） | 专用 `$tag` 镜像 |
| clean-workflow.yml | 维护 | — |

**统一输入参数**：luci 版本、管理 IP（多网口）、软件包空间（1G~4G）、enable_store、include_docker、enable_pppoe+账号密码。

**每日自动构建（2026-09-17 起）**：
- **集中开关**：仓库根目录 [build-flags.conf](build-flags.conf)，每工作流一行 `AUTO_BUILD_<机型>_<通道>=0/1`，改文件推 master 即生效；
- **触发链**：每日定时同步（北京时间 07:00 = UTC 23:00）成功后发 `store-synced` → 开关开启的工作流**即刻构建**；各构建工作流另有 **北京时间 07:40（UTC 23:40）定时兜底**（同步失败/漏发时仍会构建）；
- **去重**：同一工作流 20 小时内只自动构建一次（当日已手动构建过的自动跳过）；
- **闸门**：[autobuild-gate.yml](.github/workflows/autobuild-gate.yml)（可复用工作流）统一裁决：手动触发始终放行并标识「手动构建」；自动触发读开关 + 去重后标识「每日自动构建」；标识与时间会追加到各机型的 Release 说明中，与手动构建区分；
- **参数**：自动构建用各输入项的默认值；自定义参数请手动运行工作流。
- **发布模型（2026-09-18 起, 按日一个 Release, 天然不覆盖）**：每个工作流在上传前计算 Release 标签（`TZ=Asia/Shanghai` 取北京日期）——自动构建 `tag=设备基础名-北京日期`（如 `Autobuild-x86-64-2026-09-18`，当天各通道固件进同一清单）；手动构建 `tag=设备基础名-北京日期-HHMM`（每次手动构建独立一个新 Release）。softprops 会自动创建不存在的 tag，历史固件全部保留、永不覆盖。Release 说明另有「构建方式 + 时间」标注。此前 2026-09-17 的时间戳文件名+保留 20 个方案已废弃（那是固定 tag 模型下的补救措施）

**统一规范**（全部工作流已应用）：
- 输入引用统一经**工作流级 env**（`env.xxx`，默认值取输入项 default）——自动触发时输入为空也始终有值；
- 构建日志写到**宿主 runner**（`mkdir -p "$RUNNER_TEMP/build-logs"` + 宿主侧 `set -o pipefail` + `| tee "$RUNNER_TEMP/build-logs/….log"`，`make image … V=s`）——**不要写进 `docker --rm` 容器内 /tmp**（容器退出即丢日志，2026-09-15 之前 Build #8/#9 失败因此无法取证）；
- 失败诊断 artifact：`actions/upload-artifact` + `if: failure()` 上传 runner 日志与容器内 `bin/build-diag/`（prepare 脚本包清单 TSV + 重名报告）；**不允许 `|| true` 掩盖失败**；
- PPPoE 输入用 `::add-mask::` 掩码；build 脚本只回显 `<redacted>`，不打印明文密码；
- 上传加 `fail_on_unmatched_files: true` 防止产物路径错误时静默成功；
- **store 目录挂载**：`-v ${{ github.workspace }}/store:/home/build/immortalwrt/store`。

### 4.2 构建脚本七环节（以 x86-64/build24.sh 为例）

```
1. source shell/custom-packages.sh        # 读取软件开关(手写段+自动生成段)
2. 写 files/etc/config/pppoe-settings     # UI 输入传入
3. 按通道过滤拷贝内嵌 store(禁止克隆): 24.10 构建只拷非 25_/25- 前缀的 .run, 25.12 构建只拷 25_/25- 前缀的 .run, 外加应用 ipk/apk 子目录 → extra-packages/
4. sh shell/prepare-packages.sh           # 只解压本通道 .run(脚本内再过滤一道)+ 收集一级子目录 ipk → packages/ 软件包目录
   └─ 2026-09-15 起带预检: .run 解压非零立即失败(不再静默继续); 生成 TSV 包清单
      (channel/source/basename/package/version/architecture/name_source, IPK 读 control
      元数据、APK 读 .PKGINFO, 文件名兜底)写入 ${BUILD_LOG_DIR}; 同名文件内容不同=硬错误,
      内容相同或仅逻辑包名重复=告警(依赖包被多应用目录携带是已知现象, 旧行为为按序覆盖);
      无包可收集立即失败。build 脚本用 `|| { echo 预处理失败; exit 1; }` 接住其退出码
5. 拼接 PACKAGES = 官方基础包 + $CUSTOM_PACKAGES(+ openclash/ssrp 内核下载)
6. make image PROFILE=... PACKAGES=... FILES=... ROOTFS_PARTSIZE=... V=s
7. 失败 exit 1(工作流红灯); 成功产物上传 Release(Autobuild-<机型> 等 tag)
```

**机型差异**：
- ARM 机型取 `store/run/arm64/*`，并额外在 repositories.conf 头部加架构优先级：
  `arch aarch64_generic 10` / `arch aarch64_cortex-a53 15`；
- build25.sh 差异：`source apk-custom-packages.sh`，**同样使用内嵌 store**（只拷 `25_/25-` 前缀 .run，25.x 的 .run 内含 apk），用 `apk-prepare-packages.sh` 把 .apk 收集进 `packages/`（不克隆任何仓库，与 24 通道同逻辑；两个 prepare 脚本内部都有通道防御，防止误解压另一通道的包）；
- gl-axt1800 / gl-ax1800（snapshot+apk）不支持第三方包，build24 内特判跳过；
- n1 附晶晨宝盒（写 eMMC）；无线路由按 model/*.txt 机型清单。

### 4.3 软件开关机制（个人选择，软件来源分两部分）

软件来源两部分：
- **上游同步的第三方软件**：由 Sync Store 每日同步进内嵌 store（来源 CloudRunFilesBuilder）；
- **imm 仓库内软件**：ImmortalWrt 官方仓库内的软件（固件编译的底层来源），**无需同步**，
  构建时直接从官方源解析安装；固定清单见 [store/imm-packages.md](store/imm-packages.md)（141 个，含中文说明）。

开关文件 `custom-packages.sh`（24.10）/ `apk-custom-packages.sh`（25.12）分两段：
- **自动生成段**（上半部分，Sync Store 维护）：每应用两行——注释行（应用名 | 中文名 | 用途 | 版本）+ `CUSTOM_PACKAGES` 行，取消注释即启用，启用状态跨同步保留；段内按用途分大分类（`CATEGORY_ORDER`：代理工具/网络服务/广告与DNS/文件与存储/系统与界面/设备管理/其他），**新应用在同步脚本 APP_META 里填 `cat` 字段即自动归类**，分类跨同步保持；
- **固定段**（下半部分「以下imm仓库内的软件」）：中文注释 + `CUSTOM_PACKAGES` 行，取消注释即启用，同步不触碰该段；
- 冲突提示已并入生成段用途栏；iStore 商店由工作流 UI 的 enable_store 布尔开关追加。

---

## 5. 命名规范汇总（三层统一）

| 层 | 对象 | 规范 |
| --- | --- | --- |
| ① | workflow 文件 | 24.10 `<app>.yml` / 25.12 `25-<app>.yml` |
| ① | shell 脚本 | `shell/<app>.sh`、`shell/<app>25.sh`、`install.sh`(opkg)/`install25.sh`(apk) |
| ① | .run 产物 | `[通道前缀]<应用>_<版本>_<架构>.run`（§2.3） |
| ① | Release | tag = 北京时间日期，所有应用合并上传 |
| ② | store 目录 | `store/run/{x86,arm64}/`；.run 根目录；.ipk 应用同名子目录 |
| ③ | 构建脚本 | `build.sh` / `build24.sh`+`build25.sh` / 无线路由 `build23/24/25.sh` |
| ③ | 工作流 | `build-<机型>-<版本>.yml`；Release tag `Autobuild-<机型>` |
| 全局 | 软件名 | 三层完全一致（builder 应用名 = store 目录名 = 开关文件包名） |

---

## 6. 防错清单（历史踩坑全集）

| # | 规则 | 原因 |
| --- | --- | --- |
| 1 | .run 文件名必须可被正则解析（前缀/架构/版本规范） | 同步脚本按文件名归类与去重，坏名会归错架构或无法清理 |
| 2 | 25.12 版 .run 必须带 `25_`/`25-` 前缀 | 与 24.10 版按通道共存，无前缀区分会互删 |
| 3 | ipk 文件名中的 `~` 打包前替换为 `-` | 上游 sbwml 等 ipk 常含 `~`，opkg 安装会失败 |
| 4 | opkg/ipk 与 apk 两条通道的脚本/命令/扩展名严禁混用 | 24.10 用 opkg，25.12 用 apk |
| 5 | ARM 机型 repositories.conf 头部加架构优先级 | 同仓库双变体并存，不加会选错变体 |
| 6 | x86 机型拷 `store/run/x86/*`，ARM 拷 `store/run/arm64/*` | 拷错架构构建必失败 |
| 7 | 硬路由闪存有限，开关文件按需开启 | 包太多构建失败或固件过大 |
| 8 | 冲突组勿同时开启：run↔quickfile、clashoo↔nikki、advancedplus↔argon-config | 上游注释明示冲突 |
| 9 | 工作流输入用 `${{ github.event.inputs.xxx }}` | `${{ inputs. }}` 在部分场景解析失败（dev 修过） |
| 10 | Release 上传加 `fail_on_unmatched_files: true` | 防产物路径错误时静默"成功" |
| 11 | 构建命令 `V=s` + `pipefail` + `tee` 日志 | 失败时能拿到完整日志 |
| 12 | 第一层 cron 分钟错开；Sync Store 由 builder 完成后即时触发（repository_dispatch），定时 7:00 兜底 | 先构建后同步，store 拿到当天完整 Release；通知漏发时定时仍会补同步 |
| 13 | 第一层所有 API curl 带 GITHUB_TOKEN | 未认证撞共享 IP 限流（easytier 首跑即失败） |
| 14 | 新 workflow 先合并默认分支再 dispatch | dispatch API 按文件名只在默认分支查找 |
| 15 | 版本号提取覆盖 `_all.ipk` 后缀 | 漏掉会产出 `xxx-_all.run` 空版本坏名 |
| 16 | 开关文件行内写**包名**不是文件名 | opkg/apk install 用包名（`bandix` 而非 `bandix_0.11.0-r25_x86_64.ipk`） |
| 17 | 应用名归一化含 `-rcNN` 处理 | nekobox `-rc14` 曾导致新旧 run 无法互删 |
| 18 | `.sh`/`.yml` 强制 LF 行尾（.gitattributes）；`.run`/`.ipk` 标记 binary | CRLF 会在 Linux 容器里报 bad interpreter；binary 转换会损坏载荷 |
| 19 | store/README 表格与开关文件的**自动生成段**勿手改 | 下次同步会被覆盖；元数据修改请改同步脚本的 `APP_META` 表；imm 固定段（以下imm仓库内的软件）可正常取消注释，同步不触碰 |
| 20 | 开关文件无手写段，不存在重复行问题 | 已通过统一为生成段从机制上消除 |
| 21 | 同步改动先 `--dry-run` 验证 | 防首跑误删/误放 |
| 22 | gl-axt1800/gl-ax1800 不支持第三方包 | snapshot+apk 包管理器特判 |
| 23 | 25.12 通道 .run 内的 apk 必须命名为 `${name}-${version}.apk`（无架构后缀），builder 的 `normalize_apk_names.py` 自动规范化 | imagebuilder `apk mkndx` 本地索引不写 filename 字段，安装时按默认规范推导文件名，带 `_arch` 后缀的文件 ENOENT → APKE_INDEX_STALE "package mentioned in index not found"（2026-09-14 验收构建发现，蓝本同样存在） |
| 24 | 同一 ipk 集的 luci 主包已内置 i18n 时，不要附加独立 luci-i18n-* 包 | opkg check_data_file_clashes 硬失败（bandix 案例：kiddin9 的 luci-app-bandix 内置 zh-cn lmo，加 luci-i18n-bandix-zh-cn 构建失败）。正确解法是切到上游官方发布「主包不含 lmo + 独立语言包」配套（2026-09-23 bandix 全链切换 timsaya 官方 Release：二进制 openwrt-bandix 0.12.10 + luci-app 0.12.11 + zh-cn 语言包，无冲突、依赖全部可解析） |
| 25 | apk v3 包格式 = `ADBd` 魔数 + raw-deflate（非 gzip），验证/解析勿按 v2 处理 | 官方 imm 25.12 源同样为 ADBd 格式；v2 才是 gzip tar 三流拼接 |
| 26 | easytier 家族只保留主包：`easytier-noweb` 与 `easytier` 提供相同二进制、`luci-i18n-easytier-zh-cn` 文件已由 `luci-app-easytier` 内置 | 同时安装 opkg `check_data_file_clashes` 硬失败（Build #8/#9 根因：启用行含 4 包 → package_install Error 255）。builder f82f32f 已剔除；store 中既有旧 4 包 .run 在新资产同步前仍会保留 → **同步侧 `EXCLUDED_PACKAGE_RE` 兜底剔除**（ipk/apk 双通道，构建侧 prepare 脚本同名单再兜底） |
| 27 | LuCI 走 nginx 前端时（quickfile 引入 luci-nginx）：nginx 包自带 `uwsgi_params` **不转发 HTTP_COOKIE**，必须在 `luci.locations` 的 location 内补 `uwsgi_param HTTP_COOKIE $http_cookie;` | ucode cgi 读 `getenv('HTTP_COOKIE')` 拿会话 cookie，拿不到则页面无会话渲染 → HTML 不嵌入 sessionid → 前端 RPC 回退 rpcd 全零匿名会话 → `uci/get 没有权限`、动态面板空白 =「界面元素缺失」（2026-09-15 用户刷机后主诉，与主题/静态资源无关）。固件侧 99-custom.sh quickfile 块首启用自动 sed 修复；另动态模块场景兜底添加 /ubus location（上游 60_nginx-luci-support 的 `nginx -V` 检测不到 .so 模块）。诊断口诀：菜单 JSON 正常 + CSS 正常 + `session.login` 返回完整 ACL 但页面 `L.env.sessionid` 为 null → 必是会话没传到前端 |
| 28 | shadcn 不是纯 CSS 主题（first-boot 设置 `luci.main.mediaurlbase` 并自带 menu/router JS），默认固件只留 Argon；启用备选主题属显式选择，同步会输出 ⚠️ 冲突警告（`BASE_ENABLED_APPS={"argon"}` 参与冲突检查） | 多主题并存会互相接管 LuCI 菜单/路由，界面异常难排查 |
| 29 | prepare 脚本重名包检查：**内容不同才硬错误**，内容相同/逻辑包名重复只告警 | store 中同一依赖被多个应用目录携带是常态（如 chinadns-ng 同时出现在 depends/passwall/passwall2），旧行为按序覆盖即可正常构建；硬错误会误杀构建（2026-09-15 验证构建 #10 实测） |
| 30 | PPPoE 密码不进日志：workflow `::add-mask::` + build 脚本只回显 `<redacted>` | 构建日志将作为失败 artifact 保留，明文密码会泄露 |
| 31 | 同步脚本变体选择必须按通道索引（`(channel_of(f), norm_key(f), arch)`） | 不按通道会把 24 通道既有变体错误用于 25 通道候选选择（测试 test_channel_scoped_variant 覆盖） |
| 32 | 构建失败日志要落在宿主 runner 并 `if: failure()` 上传 artifact | `docker --rm` 容器内日志随容器销毁（Build #8 因此无法取证；用 GCM 凭据认证 GitHub API 才能下载 job 日志） |
| 33 | aurora 全系（`luci-theme-aurora` 主题、`luci-app-aurora-config` 配置中心、`luci-i18n-aurora-config-*` 语言包）2026-09-16 起彻底移除：builder 侧 4 个工作流删除，同步侧 `EXCLUDED_APPS` 全链路剔除（不下载/不解压/不生成列表），`EXCLUDED_PACKAGE_RE` 与构建侧 prepare 脚本兜底过滤历史旧 .run 资产（三层防线） | aurora 烘焙进固件渲染始终异常：主题+配置中心+语言包烘焙 → 顶部功能选项栏排版错乱、Design Studio 元素缺失；只删语言包 → 恢复正常；只留主题（配置中心也没了）→ 依然错乱；而同一 ipk 运行时安装完全正常（md5 相同、重启后正常）——烘焙环境差异，机制未明，最终决定整体移除。两个通用教训：①剔除名单必须三层（builder 打包层 + 同步解压层 + 构建 prepare 层），因为同步选源当时按「资产最多的 Release」（2026-09-18 起已改为直接取最新 Release），修复资产刚上传时最新 Release 资产数最少，同步仍选旧 Release 的旧 .run，仅同步侧剔除保不住 .run 文件本身；②24.10 的 lmo 是无魔数的新格式（值块+哈希索引+尾部总长），勿按旧 0x950412DE 魔数判断损坏 |
| 34 | 主题类应用排查先查**运行时依赖来源**：aurora 主题 header.ut/sysauth.ut 直接读 UCI `/etc/config/aurora`（顶部工具栏 `toolbar_item` 条目、颜色/nav 等 tokens 全来自该配置），此文件由配置中心的 uci-defaults（`80_aurora`/`81_aurora-fonts`）首次启动生成，主题 ipk 自身不含——所以「只装主题」必然错乱，「主题+配置中心」才是设计上的最小组合 | 只烘焙主题=配置文件不存在→顶部工具栏条目全丢+Design Studio 视图（配置中心提供）缺失=排版错乱。2026-09-16 曾把配置中心一起下架，结果主题单独烘焙仍错乱，暴露了主题对配置的隐藏依赖。教训：下架/改包组合前先解包验证目标应用的运行时依赖来源，勿把「配套组件」当「问题组件」一并移除 |
| 35 | 99-custom.sh quickfile 块补 **else 分支**：无 quickfile/nginx 时清除残留的 `nginx.global.uci_enable` 并 `uhttpd enable` 恢复网页服务 | 保留配置从带 quickfile 的旧固件升级到无 quickfile 的新固件时：nginx/quickfile 包没了，但 UCI 里的 nginx 接管标志还在 → uhttpd 一直处于禁用状态 → 网页服务整体消失（2026-09-16 用户工控机实测：uhttpd 二进制与 init 脚本都在但不运行、netstat 80 无监听、`nginx.global.uci_enable=true` 残留）。现象三件套：网页打不开 + uhttpd 装着不运行 + nginx 接管标志残留。修复已入 fe95e18（验证构建 #22 success） |
| 36 | 判断「刷机/升级是否真正生效」**勿被化石证据误导**：①保留配置升级会带来旧系统的化石——uci-defaults 日志停在旧日期、/rom 里所有文件时间戳都被钳制为**源构建日期**（squashfs SOURCE_DATE_EPOCH，该机全部显示 Apr 22）——都不能证明「没升级」；②决定性判据是 /rom 文件**内容/大小**与 git 历史逐版本比对（本次 99-custom.sh 9243 字节与 #19-21 完全一致 → 实锤新固件已装上）；③`/etc/uci-defaults/` 为空且目录 mtime 是当天，只是 sysupgrade 删除旧脚本的痕迹，不代表首启脚本执行过；④首启脚本「执行了但写入全失败」的症状：无新日志条目、主题未重置、服务未恢复——判定用 `touch` 写测试，恢复靠手动执行脚本内容 | 2026-09-16 用户工控机「刷 #21 后登录页打不开」曾险些误判为「升级没生效」要求重刷，实际新固件已装上，只是 nginx 接管标志残留 + 首启写入丢失。x86 设备 LuCI「备份与升级」sysupgrade 大镜像并不可靠，写盘工具整盘写入最稳 |
| 37 | workflow 的 `run:` 里写 shell 参数展开**只能单花括号 `${var%...}`**，写成 `${{var%...}}` 会被 GitHub 校验器当作表达式解析（`%` 是非法表达式语法）→ 工作流校验失败：push 该文件时产生 event=push、无 job、name=文件路径的失败运行，且 workflow_dispatch 返回 422 | 2026-09-17 固件重命名步骤踩到（`${{f%.img.gz}}` → 运行 #25/#26 全失败、手动触发 422）。特征识别：运行名是 `.github/workflows/xxx.yml` 而不是工作流 name、jobs 列表为空、conclusion=failure。本地 PyYAML 解析正常不代表 GitHub 校验通过——GitHub 只校验 `${{ }}` 内部的表达式语法 |
| 38 | sync-store 的 push 要带 **rebase 重试**（3 次）：上游 builder 完成通知集中到达时一批同步接连触发，checkout 与 push 之间远程 master 可能被其它提交更新 → `fetch first` 非快进拒绝 | 2026-09-18 上午 08:00-08:25 北京实测 4 个同步失败（另 4 个取消=并发组排队溢出，属正常）；失败的本地提交被后续同步自然覆盖，store 状态一致，但工作流红着难看。已在 Commit 步骤加 retry loop |
| 39 | 同步选源**直接取最新 Release**（跳过 draft/prerelease），缺失应用不回落旧 Release，由停更机制接管；最新 Release 尚无 .run 资产时跳过同步且不判定停更 | 旧「资产最多的 Release」策略被 2026-09-14 的 99 资产旧 Release 长期霸榜（每日新 Release 约 88 资产达不到阈值），aurora 修复与 oaf 新应用都无法同步，需人工放置 store（b43115b）。触发链已保证最新 Release 完整：builder 全部构建完才发 `builder-done` 通知，07:00 定时兜底时当日构建也已结束；上传中途的空 Release 由「不判定停更」守卫保护 |
| 40 | 停更/恢复判定按「通道\|应用」标识登记（2026-09-18），不用 .run 文件名 | 文件名随版本升级变化：按文件名登记时，应用带新版本回归 → cleanup_old 先删旧文件 → 旧文件名的停更标记成孤儿，README/开关永远挂着「上游停更」（版本不变的回归才能解除）。同应用两架构文件每轮只计一次缺失；store/.sync-state.json 旧格式加载时自动迁移（文件名→通道\|应用，misses 同键取最大计数） |
| 41 | oaf 首启配置生成在个别设备上静默失败：脚本被正常执行器删除、`/etc/config/appfilter` 却没生成 → 菜单不显示。99-custom.sh 加「appfilter 缺失则逐条 uci set 重建」自愈（2026-09-23） | 用户工控机实测：`appfilter.lua` 在（包已装入）但配置缺失；94/95 脚本（heredoc `uci batch`）在首启环境失败且 `-q` 吞掉报错，退出码 0 被 `( . ./file ) && rm` 删除。同设备上逐条 `uci set`（99-custom 写 hostname）、`echo >>日志`、touch 新建文件全部正常 → 自愈用逐条 set 而非 batch。交互 shell 里 heredoc 粘贴也会失败（Windows 终端 CRLF/缩进），喂文件则 batch exit=0——批量写配置一律用 `printf`/文件方式，别依赖终端粘贴 heredoc |

---

## 7. 日常维护与故障排查

| 场景 | 排查方法 |
| --- | --- |
| 每日例行 | ① 早 6:00 后看 builder 各 workflow 是否全绿（个别上游改名的会红，参考 pw2-25 改为动态解析）；② 早 7:00 后看 Sync Store 提交是否正常；③ store/README 表格与 store/run 实际内容是否一致 |
| 某应用多日不更新 | 查 builder 对应 workflow 运行记录 → 查上游是否改名/停更 → 查 Sync Store 日志中该资产的下载/清理行为 |
| 应用被标记停更 | 该 .run 连续 3 次不在 Release（上游 workflow 连续失败或上游停更）→ 文件与列表保留，注释带「上游停更」说明；builder 修好后应用重新出现在 Release，下次同步自动解除标记 |
| 手动加 ipk | 放入 store/run/<arch>/ 下**与 .run 推导名不冲突**的目录，同步不删；会自动出现在阶段三的软件列表中 |
| 启用软件后构建失败 | ① 包名是否写对（对照生成段）；② 冲突组；③ 该包在对应架构目录是否存在；④ 看 build 日志中 opkg 的报错；⑤ 日志/包清单 artifact 从该次运行页面的 Artifacts 区下载（失败自动上传，含 prepare 包清单与重名报告）；⑥ opkg 报 `check_data_file_clashes` 时对照防错清单 #24/#26 |
| 刷机后 LuCI 界面元素缺失 | 按防错清单 #27 的取证三步走：浏览器访问 `/cgi-bin/luci/admin/menu`（应返回完整 JSON）与 `/luci-static/argon/css/cascade.css`（应返回 CSS）→ Console 执行 `L.env.sessionid` 与 session.access 检查 → 会话在而页面没嵌入 sessionid 即 nginx cookie 转发问题（quickfile 场景），临时修复：`sed -i 's#^location /cgi-bin/luci {#&\n\tuwsgi_param HTTP_COOKIE $http_cookie;#' /etc/nginx/conf.d/luci.locations && /etc/init.d/nginx reload`，随后强制刷新重新登录 |
| 刷机/升级后网页**完全打不开** | 按防错 #35/#36 排查：① `netstat -lntp \| grep :80`（无监听=服务没跑）；② `uci get nginx.global.uci_enable`（=true 即残留接管标志，恢复：`uci set nginx.global.uci_enable='false'; uci commit nginx; /etc/init.d/uhttpd enable && /etc/init.d/uhttpd start`）；③ 判断升级是否生效不要看日志日期/文件时间戳（化石证据），要看 /rom 文件内容与构建版本比对；④ 首启脚本可能执行了但写入丢失（`touch` 测试 overlay 可写性）——手动执行对应恢复命令即可，新固件（fe95e18 起）首启自带自愈 |
| Release 积累过多 | builder 手动触发 clean-release（保留最近 N 天）；本仓库 Release 按机型 tag 复用，无积累问题 |

---

## 8. 附录：关键文件索引

**第一层 CloudRunFilesBuilder（本地 + GitHub）**
- 标准 ipk 模板：[rtp2httpd.yml](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/.github/workflows/rtp2httpd.yml)、[mosdns.yml](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/.github/workflows/mosdns.yml)
- zip 模板：[easytier.yml](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/.github/workflows/easytier.yml)
- 目录列表模板：[lucky.yml](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/.github/workflows/lucky.yml) + [lucky.sh](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/shell/lucky.sh)、[bandix.sh](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/shell/bandix.sh)
- 安装脚本：[install.sh](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/shell/install.sh)（opkg）/ [install25.sh](https://github.com/passengerya/CloudRunFilesBuilder/blob/daily/shell/install25.sh)（apk）

**本仓库 AutoBuildTWrt**
- 同步脚本：[store/sync_run_files.py](store/sync_run_files.py)
- 同步工作流：[sync-store.yml](.github/workflows/sync-store.yml)
- 同步状态：[store/.sync-state.json](store/.sync-state.json)
- 软件列表汇总：[store/README.md](store/README.md)（自动维护段）
- 开关文件：[shell/custom-packages.sh](shell/custom-packages.sh)（24.10）、[shell/apk-custom-packages.sh](shell/apk-custom-packages.sh)（25.12）
- 构建脚本：[x86-64/build24.sh](x86-64/build24.sh)、[x86-64/build25.sh](x86-64/build25.sh)、[armsr-armv8/build.sh](armsr-armv8/build.sh)
- 公共脚本：[shell/prepare-packages.sh](shell/prepare-packages.sh)、[shell/apk-prepare-packages.sh](shell/apk-prepare-packages.sh)
- 固件开机定制：[files/etc/uci-defaults/99-custom.sh](files/etc/uci-defaults/99-custom.sh)（网络/防火墙/PPPoE/quickfile-nginx 配置 + LuCI 会话 cookie 修复 + nginx 接管残留自愈）
- 离线单元测试：[tests/test_sync_run_files.py](tests/test_sync_run_files.py)（同步脚本纯函数 + 生成器幂等/标记边界/启用状态保持/冲突警告/停更判定/通道化变体选择；不联网、不执行 .run）

**参考仓库（GitHub, 本地已删）**
- [passengerya/store](https://github.com/passengerya/store)（内嵌方案参考实现）
- [passengerya/AutoBuildImmortalWrt](https://github.com/passengerya/AutoBuildImmortalWrt)（新项目蓝本）
