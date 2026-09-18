#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从 CloudRunFilesBuilder 的 latest release 同步 .run 文件到本仓库内嵌 store/run/ 目录,
然后把每个 .run 自解压包里的 .ipk 解压到应用同名子目录(软件包目录)——
store 中的所有文件均来源于 passengerya/CloudRunFilesBuilder。

.run 分类规则:
  - 文件名含 x86_64 / x86-64          -> store/run/x86/
  - 文件名含 aarch64 / arm64           -> store/run/arm64/
  - 文件名含 aarch32 / arm32 / i386    -> 跳过
  - 无架构标记(如 *_all.run、luci-app-uninstall-*.run) -> 同时放入 x86 和 arm64

同一应用同一架构存在多个资产时(例如 cortex-a53 与 generic 两个变体):
  - 优先保留本仓库现有文件使用的变体(不改变现有设备的安装习惯)
  - 本仓库没有该应用时, 新应用按 ARM64_VARIANT_PRIORITY 的顺序选择

24/25 通道分离:
  - 24.10 ipk 通道(前缀 24_/24- 或无前缀)与 25.12 apk 通道(前缀 25_/25-)
    各自独立选择变体, 两版 .run 在 store 中共存、互不挤占
  - 24 对应 shell/custom-packages.sh(opkg 构建), 25 对应 shell/apk-custom-packages.sh(apk 构建)

同步完成后, 删除同一应用、同一架构、同日期前缀下的旧版本 .run 文件
(24_ 只删 24_, 25- 只删 25-, 避免同步 apk 版时误删 ipk 版),
只清理 run/x86、run/arm64 根目录下的 .run。

软件包目录(.ipk)规则:
  - 每个 .run 解压出的 .ipk 放入以该 .run 推导出的应用同名子目录,
    如 dufs-0.46.0-r1_x86_64.run -> store/run/x86/dufs/*.ipk
  - 由本脚本解压生成的应用目录每次同步会重建(该目录归同步管理);
    人工新增 ipk 请放入独立的、与 .run 推导名不冲突的目录, 不会被删除
  - 不含 .ipk 的 .run(如 25.12 的 apk 包)不生成目录

阶段三(软件列表维护):
  - store/README.md 的软件列表表格: 每次同步按 store 实际内容自动增加/删除行
  - shell/custom-packages.sh 生成段: ipk 通道(24.10)编译用 package 列表
  - shell/apk-custom-packages.sh 生成段: apk 通道(25.12)编译用 package 列表
  - 生成段内部按 APP_META 的 cat 字段分大分类(见 CATEGORY_ORDER), 新应用
    填好 cat 即自动归类, 分类在每次同步后保持一致
  - 生成段中已取消注释(启用)的应用在后续同步中保留启用状态
  - 连续 3 次同步不在上游 Release 的应用标记为「停更」: .run 与软件包目录
    全部保留, 仅在 README 表格版本列与生成段注释中附加"上游停更(保留旧版)"
    说明; 应用重新出现在 Release 时自动解除标记

用法:
  BUILDER_REPO=owner/repo GITHUB_TOKEN=xxx python3 store/sync_run_files.py
  --dry-run: 只打印将执行的操作, 不下载、不删除
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request

BUILDER_REPO = os.environ.get("BUILDER_REPO", "passengerya/CloudRunFilesBuilder").rstrip("/")
TOKEN = os.environ.get("GITHUB_TOKEN", "")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RUN_DIR = os.path.join(ROOT, "store", "run")
ARCH_DIRS = {"x86": os.path.join(RUN_DIR, "x86"), "arm64": os.path.join(RUN_DIR, "arm64")}
STATE_FILE = os.path.join(ROOT, "store", ".sync-state.json")
STALE_THRESHOLD = 3  # 连续 N 次不在上游 Release 即标记停更

# 阶段三维护的生成段落标记(手动修改生成段会在下次同步被覆盖)
MARK_BEGIN = "<!-- AUTO-SOFTWARE-TABLE:START (Sync Store 自动维护, 勿手动修改) -->"
MARK_END = "<!-- AUTO-SOFTWARE-TABLE:END -->"
SH_BEGIN = "# ============ 以下由 Sync Store 自动维护(根据内嵌 store 实际内容生成) ============"
SH_END = "# ============ 自动维护结束 ============"

# 软件元数据: 应用名 -> {中文名, 用途, 来源, 分类}
# 阶段三生成开关文件注释与 store/README 软件列表时使用; 新增应用时在这里补充一行。
# cat 为生成段大分类(见 CATEGORY_ORDER), 新应用按用途填写即可自动归类; 未写/未知分类落入「其他」。
APP_META = {
    "adguardhome": {"cn": "本地DNS去广告", "desc": "AdGuardHome 广告拦截与 DNS 服务", "src": "AdguardTeam/AdGuardHome", "cat": "广告与DNS"},
    "argon": {"cn": "Argon主题", "desc": "简洁主题, 支持明暗自动切换", "src": "ImmortalWrt 官方源", "cat": "系统与界面"},
    "bandix": {"cn": "流量监控", "desc": "Bandix 实时流量监控与统计", "src": "timsaya/luci-app-bandix + dl.openwrt.ai", "cat": "网络服务"},
    "clashoo": {"cn": "Clashoo代理", "desc": "代理工具(与 nikki 冲突勿同时开启)", "src": "kenzok8/openwrt-clashoo", "cat": "代理工具"},
    "dufs": {"cn": "文件服务器", "desc": "轻量文件服务器(静态托管/上传/WebDAV)", "src": "sigoden/dufs", "cat": "文件与存储"},
    "easytier": {"cn": "异地组网", "desc": "EasyTier 点对点组网工具", "src": "EasyTier/luci-app-easytier", "cat": "网络服务"},
    "homeproxy": {"cn": "代理平台", "desc": "现代代理平台(基于 sing-box)", "src": "immortalwrt/homeproxy", "cat": "代理工具"},
    "luci-app-advancedplus": {"cn": "高级设置", "desc": "进阶设置(与 argon-config 冲突勿同时开启)", "src": "sirpdboy/luci-app-advancedplus", "cat": "系统与界面"},
    "luci-app-amlogic": {"cn": "晶晨宝盒", "desc": "晶晨机顶盒管理(仅 ARM64 平台)", "src": "ophub/luci-app-amlogic", "cat": "设备管理"},
    "luci-app-aurora-config": {"cn": "极光配置中心", "desc": "Aurora 主题配置中心(提供 /etc/config/aurora, 与主题配套启用)", "src": "eamonxg/luci-app-aurora-config", "cat": "系统与界面"},
    "luci-app-nekobox": {"cn": "NekoBox代理", "desc": "NekoBox 代理工具", "src": "Thaolga/openwrt-nekobox", "cat": "代理工具"},
    "luci-app-store": {"cn": "iStore商店", "desc": "iStore 应用商店", "src": "linkease/istore", "cat": "设备管理"},
    "luci-app-tailscale-community": {"cn": "Tailscale组网", "desc": "Tailscale 组网(Community 版)", "src": "Tokisaki-Galaxy/luci-app-tailscale-community", "cat": "网络服务"},
    "luci-app-uninstall": {"cn": "高级卸载", "desc": "彻底卸载插件的工具", "src": "上游 run 直采", "cat": "系统与界面"},
    "luci-theme-aurora": {"cn": "极光主题", "desc": "极光主题界面(需配套 luci-app-aurora-config 配置中心, 会接管 LuCI 菜单/路由, 谨慎启用)", "src": "eamonxg/luci-theme-aurora", "cat": "系统与界面"},
    "luci-theme-shadcn": {"cn": "Shadcn主题", "desc": "现代 Shadcn 风格界面主题(会接管 LuCI 菜单/路由, 24.10 下谨慎启用)", "src": "eamonxg/luci-theme-shadcn", "cat": "系统与界面"},
    "lucky": {"cn": "Lucky大吉", "desc": "端口转发/反向代理/内网穿透", "src": "gdy666/lucky via dl.openwrt.ai", "cat": "网络服务"},
    "momo": {"cn": "Momo代理", "desc": "基于 sing-box 的透明代理", "src": "nikkinikki-org/OpenWrt-momo", "cat": "代理工具"},
    "mosdns": {"cn": "DNS分流", "desc": "高性能 DNS 分流(DoH/DoQ 等)", "src": "sbwml/luci-app-mosdns", "cat": "广告与DNS"},
    "nikki": {"cn": "Nikki代理", "desc": "代理工具(与 clashoo 冲突勿同时开启)", "src": "nikkinikki-org/OpenWrt-nikki", "cat": "代理工具"},
    "openclash": {"cn": "OpenClash", "desc": "Clash 代理客户端", "src": "vernesong/OpenClash", "cat": "代理工具"},
    "openlist2": {"cn": "网盘聚合", "desc": "OpenList2 网盘聚合(Alist 变体)", "src": "sbwml/luci-app-openlist2", "cat": "文件与存储"},
    "openwrt-daede": {"cn": "eBPF代理", "desc": "基于 eBPF 的高性能透明代理(dae/daed)", "src": "kenzok8/openwrt-daede", "cat": "代理工具"},
    "passwall": {"cn": "PassWall", "desc": "代理工具(自带依赖)", "src": "Openwrt-Passwall/openwrt-passwall", "cat": "代理工具"},
    "passwall2": {"cn": "PassWall2", "desc": "代理工具(自带依赖)", "src": "Openwrt-Passwall/openwrt-passwall2", "cat": "代理工具"},
    "quickfile": {"cn": "文件管理", "desc": "轻量网页文件管理器(与 luci-app-run 冲突勿同时开启)", "src": "sbwml/luci-app-quickfile", "cat": "文件与存储"},
    "rtp2httpd": {"cn": "IPTV转发", "desc": "IPTV 流媒体转发服务器", "src": "stackia/rtp2httpd", "cat": "网络服务"},
    "sing-box": {"cn": "Sing-box内核", "desc": "通用代理内核", "src": "SagerNet/sing-box", "cat": "代理工具"},
    "ssrp-mihomo": {"cn": "SSRP代理", "desc": "SSR-Plus 代理工具(mihomo 内核)", "src": "fw876/helloworld", "cat": "代理工具"},
}

# 生成段大分类(按用途, 顺序即输出顺序): 新应用在 APP_META 里写 cat 字段即自动归类
CATEGORY_ORDER = ["代理工具", "网络服务", "广告与DNS", "文件与存储", "系统与界面", "设备管理", "其他"]
CAT_HEADER_FMT = "# ───────────────────── %s ─────────────────────"

# 冲突组: 同一组内同时开启会在固件里互相冲突(参考各应用上游说明)。
# 阶段三检测到同组内 >=2 个应用同时启用时, 在生成段顶部输出 ⚠️ 警告行。
CONFLICT_GROUPS = [
    {"clashoo", "nikki"},
    {"luci-app-advancedplus", "argon"},
    {"quickfile", "luci-app-run"},
    {"argon", "luci-theme-aurora", "luci-theme-shadcn"},
]

# 各机型 build 脚本默认都会加入 Argon; 生成段里即使没取消注释 argon,
# 启用其它主题时实际固件仍会形成多主题组合, 需要参与冲突提示。
BASE_ENABLED_APPS = {"argon"}

# 与 CloudRunFilesBuilder f82f32f 保持一致的冗余包剔除名单:
# easytier-noweb 与 easytier 提供相同二进制、luci-i18n-easytier-zh-cn 的文件
# 已由 luci-app-easytier 内置, 同时安装必然 check_data_file_clashes 导致构建失败。
# builder 新 Release 已不再打包, 但同步按「资产最多的 Release」选择时可能仍拿到
# 旧资产, 故同步侧兜底剔除, 直到上游资产完全替换为止。
EXCLUDED_PACKAGE_RE = [
    re.compile(r"^easytier-noweb[-_].*\.(ipk|apk)$"),
    re.compile(r"^luci-i18n-easytier-zh-cn[-_].*\.(ipk|apk)$"),
]

# 已下架应用(不再同步/解压/生成列表, 双通道生效): 当前为空。
# aurora 全系(主题+配置中心+语言包)已于 2026-09-18 按用户要求恢复
# (luci-theme-aurora 为主题, luci-app-aurora-config 为配置中心)。
EXCLUDED_APPS = set()


def is_excluded_package(name):
    """判断包文件是否属于已知冗余冲突包(解压时应剔除)。"""
    base = os.path.basename(name)
    return any(p.match(base) for p in EXCLUDED_PACKAGE_RE)

# arm64 变体优先级(仅当本仓库中该应用没有既有文件时生效):
# generic 兼容性最好, 其次是 cortex-a53 优化构建、a53, 最后是纯 aarch64
ARM64_VARIANT_PRIORITY = ["generic", "cortex-a53", "a53", ""]

# 形如 "25-"/"24_" 的开头日期前缀(上游每日构建加在文件名前的标记)
RE_LEADING_PREFIX = re.compile(r"^\d{2}[-_]")
# 架构/变体标记(注意 aarch64 带变体的写法放在前面)
# 注意: all 必须带 _ 前缀且处于边界, 避免误删应用名内部的 "all"(如 passwall)
RE_ARCH = re.compile(r"_?(?:x86_64|x86-64|aarch64(?:_cortex-a53|_a53|_generic)?|aarch32|arm64)|_all(?=[-_.]|$)")
# 版本号: 可带 v 前缀的主版本 + 可选的 -r修订号(修订号后面必须是分隔符或结尾, 避免误吞 git hash)
RE_VERSION = re.compile(r"v?(\d+(?:\.\d+)+)(?:-r?(\d+)(?=[-_.]|$))?")
RE_REV = re.compile(r"r\d+")                 # 独立的 r9 之类修订标记
RE_RC = re.compile(r"-rc\d+")                # 预发布 rc 标记(如 nekobox 的 -rc14)
RE_HASH = re.compile(r"(?<![0-9a-z])[0-9a-f]{7,}(?![0-9a-z])")  # git 短 hash
RE_NUM = re.compile(r"(?<![0-9a-z])\d+(?![0-9a-z])")            # 独立数字(如 ssrp 的 196)
RE_ARCH_X86 = re.compile(r"x86_64|x86-64")
RE_ARCH_ARM64 = re.compile(r"aarch64|arm64")
RE_ARCH_ARM32 = re.compile(r"aarch32|arm32")
RE_ARCH_X8632 = re.compile(r"i386|x86_32")


def api_get(url, retries=2, delay=10):
    """带重试的 API 请求: 限流(403/429)、5xx、网络抖动不中断整个同步; 404 直接抛出。"""
    last_exc = None
    for attempt in range(retries + 1):
        try:
            headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "sync-run-files",
            }
            if TOKEN:
                headers["Authorization"] = "Bearer %s" % TOKEN
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last_exc = e
        except Exception as e:
            last_exc = e
        if attempt < retries:
            print("[重试] api_get 失败(%s), %ds 后重试 %d/%d: %s" % (last_exc, delay, attempt + 1, retries, url))
            time.sleep(delay)
    raise last_exc


def app_dir_of(name):
    """从 .run 文件名推导应用目录名(去掉前缀/架构/版本/修订/hash, 保留连字符, 小写)。"""
    s = name[:-4] if name.endswith(".run") else name
    s = RE_LEADING_PREFIX.sub("", s)
    s = RE_ARCH.sub("", s)
    s = RE_VERSION.sub("", s)
    s = RE_REV.sub("", s)
    s = RE_RC.sub("", s)
    s = RE_HASH.sub("", s)
    s = RE_NUM.sub("", s)
    return re.sub(r"[^0-9a-z-]+", "-", s.lower()).strip("-")


def channel_of(name):
    """返回通道: ipk(24.10, 前缀 24_/24- 或无前缀) 或 apk(25.12, 前缀 25_/25-)。

    24 对应 shell/custom-packages.sh(opkg/ipk 构建), 25 对应 shell/apk-custom-packages.sh(apk 构建),
    两版 .run 在 store 中按通道共存, 互不挤占。
    """
    m = RE_LEADING_PREFIX.match(name)
    if not m:
        return "ipk"
    return "apk" if m.group(0).startswith("25") else "ipk"


def norm_key(name):
    """从文件名提取应用标识(去掉前缀、架构、版本、hash, 统一小写)。"""
    s = name[:-4] if name.endswith(".run") else name
    s = RE_LEADING_PREFIX.sub("", s)
    s = RE_ARCH.sub("", s)
    s = RE_VERSION.sub("", s)
    s = RE_REV.sub("", s)
    s = RE_RC.sub("", s)
    s = RE_HASH.sub("", s)
    s = RE_NUM.sub("", s)
    return re.sub(r"[^0-9a-z]+", "_", s.lower()).strip("_")


def version_of(name):
    """解析版本用于排序, 返回 (主版本元组, 修订号), 没有版本返回 ((), 0)。"""
    s = name[:-4] if name.endswith(".run") else name
    s = RE_LEADING_PREFIX.sub("", s)
    m = RE_VERSION.search(s)
    if m:
        main = tuple(int(p) for p in m.group(1).split("."))
        rev = int(m.group(2)) if m.group(2) else 0
        return (main, rev)
    m = re.search(r"(?:^|[-_])r(\d+)(?:[-_.]|$)", s)
    if m:
        return ((), int(m.group(1)))
    return ((), 0)


def variant_of(name):
    """返回 arm64 变体: generic / cortex-a53 / a53 / ""(纯 aarch64); 非 arm64 返回 None。"""
    if "cortex-a53" in name:
        return "cortex-a53"
    if "generic" in name:
        return "generic"
    if "_a53" in name or "-a53" in name:
        return "a53"
    if RE_ARCH_ARM64.search(name):
        return ""
    return None


def arch_of(name):
    """返回资产应放入的目录列表。"""
    if RE_ARCH_ARM32.search(name) or RE_ARCH_X8632.search(name):
        return ["skip"]
    if RE_ARCH_X86.search(name):
        return ["x86"]
    if RE_ARCH_ARM64.search(name):
        return ["arm64"]
    return ["x86", "arm64"]  # 架构无关, 两个目录都放


def choose(cands, key, arch, existing_variants, channel):
    """同一(应用, 架构)的多个候选里选一个。

    existing_variants 按 (通道, 应用, 架构) 索引, 24/25 通道各自的既有变体互不影响。
    """
    existing = existing_variants.get((channel, key, arch))

    def sel(a):
        name = a["name"]
        variant = variant_of(name)
        m = RE_LEADING_PREFIX.match(name)
        prefix = int(m.group(0)[:2]) if m else -1
        keep_variant = (variant == existing) if existing is not None else False
        if arch == "arm64" and variant is not None:
            prio = ARM64_VARIANT_PRIORITY.index(variant)
        else:
            prio = 0
        return (
            version_of(name),   # 1. 版本高者优先
            keep_variant,       # 2. 优先保留本仓库现有变体
            not m,              # 3. 优先无日期前缀的命名(与仓库现有风格一致)
            prefix,             # 4. 有前缀时取日期较新者
            -prio,              # 5. 新应用按变体优先级
        )

    return sorted(cands, key=sel, reverse=True)[0]


def download_asset(asset, dest_dir, retries=2, delay=10):
    os.makedirs(dest_dir, exist_ok=True)
    out = os.path.join(dest_dir, asset["name"])
    if os.path.isfile(out) and os.path.getsize(out) == asset.get("size", 0):
        print("[%s] 已存在且大小一致, 跳过下载: %s" % (os.path.basename(dest_dir), asset["name"]))
        return
    print("[%s] 下载 %s" % (os.path.basename(dest_dir), asset["name"]))
    headers = {"User-Agent": "sync-run-files"}
    if TOKEN:
        headers["Authorization"] = "Bearer %s" % TOKEN
    req = urllib.request.Request(asset["browser_download_url"], headers=headers)
    tmp = out + ".tmp"
    last_exc = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp, open(tmp, "wb") as f:
                shutil.copyfileobj(resp, f)
            if os.path.getsize(tmp) == 0:
                raise RuntimeError("下载失败(空文件): %s" % asset["name"])
            os.replace(tmp, out)
            return
        except Exception as e:
            last_exc = e
            if attempt < retries:
                print("[重试] 下载失败(%s), %ds 后重试 %d/%d: %s" % (e, delay, attempt + 1, retries, asset["name"]))
                time.sleep(delay)
    if os.path.isfile(tmp):
        os.remove(tmp)
    raise last_exc


def leading_prefix(name):
    """返回文件名开头的日期前缀(如 24_ / 25-), 无前缀返回空串。"""
    m = RE_LEADING_PREFIX.match(name)
    return m.group(0) if m else ""


def cleanup_old(key, arch, keep_name, dry_run=False):
    """删除 run/<arch>/ 根目录下同应用旧版本的 .run 文件(不触碰 .ipk 和子目录)。

    只清理与 keep_name 同前缀的旧文件(24_ 只删 24_, 25- 只删 25-),
    避免同步 apk 版(25_)时误删 ipk 版(24_)。
    """
    keep_prefix = leading_prefix(keep_name)
    d = ARCH_DIRS[arch]
    if not os.path.isdir(d):
        return
    for f in sorted(os.listdir(d)):
        p = os.path.join(d, f)
        if not f.endswith(".run") or f == keep_name or not os.path.isfile(p):
            continue
        if leading_prefix(f) != keep_prefix:
            continue
        if norm_key(f) == key:
            print("[%s] %s: %s" % (arch, "将删除" if dry_run else "删除旧版本", f))
            if not dry_run:
                os.remove(p)


def extract_ipks_from_runs(dry_run=False):
    """把 store/run/<arch>/ 根目录下每个 .run 解压出的 .ipk 放入应用同名子目录。

    来源即 CloudRunFilesBuilder 拉取的 .run 包本身(store 中所有文件均来源于 builder);
    解压生成的应用目录每次同步会重建, 不含 .ipk 的 .run(如 25.12 apk 包)不生成目录。

    返回汇总: {(通道, 应用): {"version": str, "archs": set, "ipks": set, "apks": set}}
    供阶段三(软件列表维护)使用。
    """
    print("== 开始从 .run 解压 ipk 到应用子目录(软件包目录) ==")
    count = 0
    summary = {}
    for arch, d in sorted(ARCH_DIRS.items()):
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if not f.endswith(".run") or not os.path.isfile(p):
                continue
            app = app_dir_of(f)
            if not app:
                print("[%s] 无法推导应用名, 跳过: %s" % (arch, f))
                continue
            if app in EXCLUDED_APPS:
                print("[%s] 跳过(已下架应用): %s" % (arch, f))
                continue
            key = (channel_of(f), app)
            info = summary.setdefault(key, {"version": "", "archs": set(), "ipks": set(), "apks": set()})
            info["archs"].add(arch)
            info["version"] = version_str_of(f) or info["version"]
            tmp = os.path.join(d, ".unpack-" + app)
            try:
                result = subprocess.run(
                    ["sh", p, "--target", tmp, "--noexec"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
                if result.returncode != 0:
                    print("[%s] 解压失败(返回码 %s), 跳过: %s" % (arch, result.returncode, f))
                    continue
                ipks, apks = [], []
                for root, _, names in os.walk(tmp):
                    for n in names:
                        if is_excluded_package(n):
                            print("[%s] 剔除冗余冲突包: %s" % (arch, n))
                            continue
                        if n.endswith(".ipk"):
                            ipks.append(os.path.join(root, n))
                        elif n.endswith(".apk"):
                            apks.append(os.path.join(root, n))
                for src in apks:
                    info["apks"].add(os.path.basename(src))
                if not ipks:
                    print("[%s] 不含 ipk(apk 包或空包), 跳过目录生成: %s" % (arch, f))
                    continue
                dest = os.path.join(d, app)
                if dry_run:
                    print("[%s] %s -> %s/ (%d 个 ipk)" % (arch, f, app, len(ipks)))
                    count += len(ipks)
                    for src in ipks:
                        info["ipks"].add(os.path.basename(src))
                    continue
                if os.path.isdir(dest):
                    shutil.rmtree(dest)
                os.makedirs(dest)
                for src in ipks:
                    shutil.copy2(src, dest)
                    info["ipks"].add(os.path.basename(src))
                    print("[%s] ipk 解压: %s/%s" % (arch, app, os.path.basename(src)))
                    count += 1
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    print("ipk 解压结束, 共处理 %d 个文件。" % count)
    return summary


def version_str_of(name):
    """从 .run 文件名提取版本号文本(展示用), 无版本返回空串。"""
    s = name[:-4] if name.endswith(".run") else name
    s = RE_LEADING_PREFIX.sub("", s)
    m = RE_VERSION.search(s)
    return m.group(0) if m else ""


def ipk_package_name(name):
    """从 ipk 文件名提取包名(去掉末尾架构段与版本段)。

    架构段可以是 _x86_64/_all, 也可能是上游的非规范写法 -all
    (如 luci-app-adguardhome-all.ipk, 其真实包名是 luci-app-adguardhome)。
    """
    s = name[:-4] if name.endswith(".ipk") else name
    s = re.sub(r"[_-](?:all|x86_64|aarch64(?:_[a-z0-9.-]+)?|arm_[a-z0-9._-]+|mips(?:el)?_[\w.-]+|i386(?:_[\w.-]+)?)$", "", s)
    parts = s.split("_")
    for i in range(len(parts) - 1, 0, -1):
        if re.match(r"^(?:v?\d|r\d|git-)", parts[i]):
            return "_".join(parts[:i])
    return s


def apk_package_name(name):
    """从 apk 文件名提取包名。apk 命名: <名>-<版本>-<修订>-<架构>.apk(连字符多段式, 从左扫描首个版本段)"""
    s = name[:-4] if name.endswith(".apk") else name
    s = re.sub(r"[_-](?:x86_64|aarch64(?:_[a-z0-9.-]+)?|arm_[a-z0-9._-]+|all)$", "", s)
    parts = re.split(r"[-_]", s)
    for i in range(1, len(parts)):
        if re.match(r"^(?:v?\d|r\d)", parts[i]):
            return re.sub(r"[_-]+", "-", "-".join(parts[:i]))
    return re.sub(r"[_-]+", "-", s)


def regenerate_marked(path, begin, end, content, dry_run=False):
    """在 path 文件的两处标记之间替换为 content; 首次使用时追加到文件末尾。"""
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            src = f.read()
        b = src.find(begin)
        e = src.find(end)
        if b != -1 and e != -1 and e > b:
            new = src[:b] + begin + "\n" + content + "\n" + end + src[e + len(end):]
            if not dry_run:
                with open(path, "w", encoding="utf-8", newline="\n") as f:
                    f.write(new)
            print("[维护] %s: 更新生成列表" % os.path.basename(path))
            return
        new = src.rstrip("\n") + "\n\n" + begin + "\n" + content + "\n" + end + "\n"
        if not dry_run:
            with open(path, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)
        print("[维护] %s: 首次追加生成列表" % os.path.basename(path))
    else:
        print("[维护] %s: 文件不存在, 跳过" % path)


def load_state():
    if os.path.isfile(STATE_FILE):
        try:
            with open(STATE_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"misses": {}, "stale": []}


def save_state(state, dry_run=False):
    if dry_run:
        return
    state.pop("managed_dirs", None)  # 旧版下线删除方案的遗留字段, 清理
    with open(STATE_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def read_enabled_apps(path):
    """解析 shell 文件生成段中已启用(取消注释)的应用集合。"""
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as f:
        src = f.read()
    b, e = src.find(SH_BEGIN), src.find(SH_END)
    if b == -1 or e == -1 or e <= b:
        return set()
    section = src[b + len(SH_BEGIN):e]
    enabled = set()
    cur_app = None
    for line in section.splitlines():
        m = re.match(r"^# 自动生成: (\S+)", line)
        if m:
            cur_app = m.group(1)
            continue
        if line.startswith("CUSTOM_PACKAGES=") and cur_app:
            enabled.add(cur_app)
            cur_app = None
    return enabled


def mark_stale_runs(valid_names, state, dry_run=False):
    """连续 3 次同步不在上游 Release 的应用标记为「停更」: 保留文件与列表, 仅在注释中附加停更说明。

    停更应用重新出现在 Release 时自动解除标记(恢复更新)。

    valid_names: 本次 Release 的全部 .run 资产名(无法获取 Release 时应传 None 跳过判定)。
    """
    if valid_names is None:
        print("[维护] 未获取到上游 Release 信息, 跳过停更判定")
        return
    misses = state.setdefault("misses", {})
    stale = set(state.get("stale", []))
    for arch, d in sorted(ARCH_DIRS.items()):
        if not os.path.isdir(d):
            continue
        for f in sorted(os.listdir(d)):
            p = os.path.join(d, f)
            if not f.endswith(".run") or not os.path.isfile(p):
                continue
            if f in valid_names:
                if misses.pop(f, None) is not None:
                    print("[%s] 应用恢复更新: %s" % (arch, f))
                if f in stale:
                    stale.discard(f)
                    print("[%s] 解除停更标记: %s" % (arch, f))
                continue
            misses[f] = misses.get(f, 0) + 1
            if misses[f] >= STALE_THRESHOLD and f not in stale:
                stale.add(f)
                print("[%s] 标记停更(连续 %d 次不在 Release): %s" % (arch, STALE_THRESHOLD, f))
    state["stale"] = sorted(stale)


def maintain_lists(summary, valid_names, dry_run=False):
    """阶段三: 根据内嵌 store 实际内容维护软件列表汇总。

    1. store/README.md 的软件列表表格(增加/删除行)
    2. shell/custom-packages.sh 生成段(ipk 通道, 24.10 编译用 package 列表)
    3. shell/apk-custom-packages.sh 生成段(apk 通道, 25.12 编译用 package 列表)
    4. 下线应用的 .run/软件包目录清理(连续 3 次不在上游 Release)
    """
    print("== 阶段三: 维护软件列表 ==")
    state = load_state()
    mark_stale_runs(valid_names, state, dry_run=dry_run)
    stale_keys = {(channel_of(n), app_dir_of(n)) for n in state.get("stale", [])}

    # 汇总表: 按(应用, 通道)排序
    rows = []
    for (channel, app), info in sorted(summary.items()):
        archs = sorted(info["archs"])
        pkgs = sorted(info["ipks"]) if channel == "ipk" else sorted(info["apks"])
        if not pkgs:
            continue
        rows.append((app, channel, info["version"], archs, pkgs))

    # store/README.md 软件列表: 软件 | 中文名 | 通道 | 版本 | 架构 | 用途 | 来源
    lines = ["| 软件 | 中文名 | 通道 | 版本 | 架构 | 用途 | 来源 |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    for app, channel, ver, archs, pkgs in rows:
        meta = APP_META.get(app, {})
        cn = meta.get("cn", "—")
        desc = meta.get("desc", "—")
        src = meta.get("src", "—")
        ch_label = "ipk (24.10)" if channel == "ipk" else "apk (25.12)"
        archs_label = " / ".join(archs)
        if (channel, app) in stale_keys:
            ver = (ver + " ⚠️上游停更") if ver else "⚠️上游停更"
        lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (app, cn, ch_label, ver, archs_label, desc, src))
    table = "\n".join(lines)
    regenerate_marked(os.path.join(ROOT, "store", "README.md"), MARK_BEGIN, MARK_END, table, dry_run=dry_run)

    # 编译 package 列表: 分通道写入两个 shell 文件
    # 注意: 行内必须是包名(去版本/架构段), 否则 opkg/apk install 找不到包
    for channel, sh_path in (("ipk", os.path.join(ROOT, "shell", "custom-packages.sh")),
                             ("apk", os.path.join(ROOT, "shell", "apk-custom-packages.sh"))):
        enabled = read_enabled_apps(sh_path)
        enabled_for_conflicts = enabled | BASE_ENABLED_APPS
        pkg_name_fn = ipk_package_name if channel == "ipk" else apk_package_name
        sec = []
        # 冲突组检查: 同组内同时启用 >=2 个应用时, 在生成段顶部输出警告(仅提示, 不阻断)
        for group in CONFLICT_GROUPS:
            hit = sorted(group & enabled_for_conflicts)
            if len(hit) >= 2:
                sec.append("# ⚠️ 冲突警告: %s 同时开启, 可能互相冲突, 请只保留其中一个" % " 与 ".join(hit))
        # 按大分类分组: 新应用按 APP_META 的 cat 自动归类, 分类顺序见 CATEGORY_ORDER
        by_cat = {}
        for app, ch, ver, archs, pkgs in rows:
            if ch != channel:
                continue
            pkg_names = sorted({pkg_name_fn(p) for p in pkgs if pkg_name_fn(p)})
            if not pkg_names:
                continue
            meta = APP_META.get(app, {})
            cn = meta.get("cn", "")
            desc = meta.get("desc", "")
            note_bits = []
            if ver:
                note_bits.append(ver)
            if (channel, app) in stale_keys:
                note_bits.append("上游停更(保留旧版)")
            note_label = " ".join(note_bits)
            prefix = "" if app in enabled else "#"
            block = [
                "# 自动生成: %s | %s | %s | %s | 取消下一行注释即启用" % (app, cn, desc, note_label),
                '%sCUSTOM_PACKAGES="$CUSTOM_PACKAGES %s"' % (prefix, " ".join(pkg_names)),
            ]
            cat = meta.get("cat", "其他")
            by_cat.setdefault(cat, []).extend(block)
        ordered = [c for c in CATEGORY_ORDER if c in by_cat]
        ordered += [c for c in by_cat if c not in CATEGORY_ORDER]
        for cat in ordered:
            if sec:
                sec.append("")
            sec.append(CAT_HEADER_FMT % cat)
            sec.extend(by_cat[cat])
        content = "\n".join(sec) if sec else "# （当前 store 中没有该通道的第三方软件）"
        regenerate_marked(sh_path, SH_BEGIN, SH_END, content, dry_run=dry_run)

    save_state(state, dry_run=dry_run)
    print("阶段三完成: 汇总 %d 个(应用, 通道)条目" % len(rows))


def main():
    parser = argparse.ArgumentParser(description="同步 run/ipk 文件到内嵌 store")
    parser.add_argument("--dry-run", action="store_true", help="只打印将执行的操作, 不下载、不删除")
    args = parser.parse_args()

    valid_names = None  # 上游 Release 的全部 .run 资产名; 无法获取时为 None(跳过下线清理)
    try:
        releases = api_get("https://api.github.com/repos/%s/releases?per_page=5" % BUILDER_REPO)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print("源仓库 %s 暂无 release, 跳过 run 同步。" % BUILDER_REPO)
        else:
            raise
    else:
        if not releases:
            print("源仓库 %s 暂无 release, 跳过 run 同步。" % BUILDER_REPO)
        else:
            # 从最近 5 个 Release 中选 .run 资产最多的那个:
            # 每日 cron 分批上传时最新的 Release 可能还在填充中(资产不全),
            # 直接取最新会把多数应用误判为缺失(误标停更)。
            def run_count(r):
                return sum(1 for a in r.get("assets", []) if a["name"].endswith(".run"))
            release = max(releases, key=run_count)
            print("使用 release: %s (%s, %d 个 .run 资产; 最新为 %s, %d 个)"
                  % (release["tag_name"], release.get("name", ""), run_count(release),
                     releases[0]["tag_name"], run_count(releases[0])))

            assets = [a for a in release.get("assets", []) if a["name"].endswith(".run")]
            valid_names = {a["name"] for a in assets}
            if not assets:
                print("该 release 中没有 .run 资产, 跳过 run 同步。")
            else:
                run_sync(assets, args.dry_run)

    # 阶段二独立执行: 即使上游暂无新 .run 资产, 也要保持软件包目录与 .run 一致
    summary = extract_ipks_from_runs(dry_run=args.dry_run)

    # 阶段三: 维护 store/README 软件列表与 shell 编译 package 列表
    maintain_lists(summary, valid_names, dry_run=args.dry_run)

    print("同步完成。" if not args.dry_run else "dry-run 结束, 未做任何修改。")


def run_sync(assets, dry_run=False):
    """从 CloudRunFilesBuilder Release 同步 .run 资产到内嵌 store(原有逻辑)。"""
    # 统计本仓库现有的变体选择(用于同名应用延续原变体; 按通道区分, 24/25 互不影响)
    existing_variants = {}
    for arch, d in ARCH_DIRS.items():
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith(".run"):
                v = variant_of(f)
                if v is not None:
                    existing_variants[(channel_of(f), norm_key(f), arch)] = v

    # 按(通道, 应用, 架构)分组: 24/25 两个通道各自保留一个变体, 互不挤占
    groups = {}
    for a in assets:
        # 注意: 用 app_dir_of(连字符保留)与 EXCLUDED_APPS 比对, 与解压环节一致;
        # norm_key 会把连字符转下划线, 直接比对会漏判。
        if app_dir_of(a["name"]) in EXCLUDED_APPS:
            print("跳过(已下架应用): %s" % a["name"])
            continue
        for arch in arch_of(a["name"]):
            if arch == "skip":
                print("跳过(架构不支持): %s" % a["name"])
                continue
            groups.setdefault((channel_of(a["name"]), norm_key(a["name"]), arch), []).append(a)

    for (channel, key, arch) in sorted(groups):
        cands = groups[(channel, key, arch)]
        chosen = choose(cands, key, arch, existing_variants, channel)
        if len(cands) > 1:
            for c in cands:
                mark = "  <- 选中" if c is chosen else ""
                print("[%s] 候选: %s%s" % (arch, c["name"], mark))
        print("[%s] 同步: %s" % (arch, chosen["name"]))
        if dry_run:
            cleanup_old(key, arch, chosen["name"], dry_run=True)
            continue
        download_asset(chosen, ARCH_DIRS[arch])
        cleanup_old(key, arch, chosen["name"])


if __name__ == "__main__":
    main()
