# -*- coding: utf-8 -*-
"""store/sync_run_files.py 离线单元测试。

约束:
  - 不访问 GitHub API、不下载任何资源;
  - 不执行真实 .run 自解压(测试不经过 main()/extract_ipks_from_runs());
  - 不修改仓库真实文件(所有生成器测试在临时目录中运行);
  - 仅使用标准库 unittest。
"""
import os
import sys
import tempfile
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "store"))

import sync_run_files as srf  # noqa: E402


class HelperTests(unittest.TestCase):
    """纯函数解析 helper 测试。"""

    def test_channel_of(self):
        self.assertEqual(srf.channel_of("25-argon-2.4.7_x86_64.run"), "apk")
        self.assertEqual(srf.channel_of("25_quickfile_1.0.16_x86_64.run"), "apk")
        self.assertEqual(srf.channel_of("24_quickfile_1.0.16_x86_64.run"), "ipk")
        self.assertEqual(srf.channel_of("argon-2.4.3-r20250722_x86_64.run"), "ipk")

    def test_arch_of(self):
        self.assertEqual(srf.arch_of("foo_1.0_x86_64.run"), ["x86"])
        self.assertEqual(srf.arch_of("foo_1.0_aarch64_generic.run"), ["arm64"])
        self.assertEqual(srf.arch_of("foo_1.0_aarch32.run"), ["skip"])
        self.assertEqual(srf.arch_of("foo_1.0_i386.run"), ["skip"])
        self.assertEqual(srf.arch_of("foo_1.0_all.run"), ["x86", "arm64"])

    def test_ipk_package_name(self):
        self.assertEqual(srf.ipk_package_name("luci-app-adguardhome-all.ipk"), "luci-app-adguardhome")
        self.assertEqual(
            srf.ipk_package_name("23.05-24.10_luci-app-passwall_26.9.9-r1_all.ipk"),
            "23.05-24.10_luci-app-passwall",
        )
        self.assertEqual(srf.ipk_package_name("easytier-noweb_2.6.4_x86_64.ipk"), "easytier-noweb")

    def test_apk_package_name(self):
        self.assertEqual(srf.apk_package_name("sing-box-1.14.0-r1_x86_64.apk"), "sing-box")

    def test_app_dir_of(self):
        self.assertEqual(srf.app_dir_of("25-SSRP-mihomo-x86_64-196-r9.run"), "ssrp-mihomo")

    def test_read_enabled_apps(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "custom-packages.sh")
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    "# header\n"
                    + srf.SH_BEGIN
                    + "\n"
                    + "# 自动生成: easytier | 异地组网 | 说明\n"
                    + 'CUSTOM_PACKAGES="$CUSTOM_PACKAGES easytier luci-app-easytier"\n'
                    + "# 自动生成: luci-theme-shadcn | Shadcn主题 | 说明\n"
                    + '#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-theme-shadcn"\n'
                    + srf.SH_END
                    + "\n"
                    + "# fixed section\n"
                )
            self.assertEqual(srf.read_enabled_apps(path), {"easytier"})

    def test_excluded_apps(self):
        # aurora 全系(主题+配置中心)已于 2026-09-18 恢复: EXCLUDED_APPS 为空
        self.assertEqual(srf.EXCLUDED_APPS, set())
        self.assertIn("luci-app-aurora-config", srf.APP_META)
        self.assertIn("luci-theme-aurora", srf.APP_META)
        # 其它主题不受影响
        self.assertIn("luci-theme-shadcn", srf.APP_META)

    def test_is_excluded_package(self):
        # 与主包文件冲突的冗余包应剔除(ipk 与 apk 双通道)
        self.assertTrue(srf.is_excluded_package("easytier-noweb_2.6.4_x86_64.ipk"))
        self.assertTrue(srf.is_excluded_package("easytier-noweb-2.6.4.apk"))
        self.assertTrue(
            srf.is_excluded_package("luci-i18n-easytier-zh-cn_git-26.136.03667-39d7eda_all.ipk")
        )
        self.assertTrue(
            srf.is_excluded_package("luci-i18n-easytier-zh-cn-26.136.03667~39d7eda.apk")
        )
        # 主包与 luci 界面包不受影响
        self.assertFalse(srf.is_excluded_package("easytier_2.6.4_x86_64.ipk"))
        self.assertFalse(srf.is_excluded_package("easytier-2.6.4.apk"))
        self.assertFalse(srf.is_excluded_package("luci-app-easytier_2.6.4_all.ipk"))
        self.assertFalse(srf.is_excluded_package("luci-app-easytier-2.6.4-r1.apk"))


class ChooseTests(unittest.TestCase):
    """run_sync 变体选择(按通道区分)测试。"""

    def test_channel_scoped_variant(self):
        key = "easytier"
        cands = [
            {"name": "25_easytier_2.6.4_aarch64_generic.run"},
            {"name": "25_easytier_2.6.4_aarch64_cortex-a53.run"},
        ]
        # ipk 通道的既有 cortex-a53 变体不应影响 apk 通道选择
        # (修复前 existing_variants 未按通道索引, 会误选 cortex-a53)
        existing = {("ipk", key, "arm64"): "cortex-a53"}
        chosen = srf.choose(cands, key, "arm64", existing, "apk")
        self.assertEqual(srf.variant_of(chosen["name"]), "generic")
        # apk 通道自己的既有变体应被延续
        existing2 = {("apk", key, "arm64"): "cortex-a53"}
        chosen2 = srf.choose(cands, key, "arm64", existing2, "apk")
        self.assertEqual(srf.variant_of(chosen2["name"]), "cortex-a53")


class MaintainListsTests(unittest.TestCase):
    """生成器行为: 标记边界、幂等、启用状态保持、冲突警告、停更判定。"""

    def setUp(self):
        self._saved = {
            k: getattr(srf, k) for k in ("ROOT", "RUN_DIR", "ARCH_DIRS", "STATE_FILE")
        }
        self.tmp = tempfile.TemporaryDirectory()
        root = self.tmp.name
        srf.ROOT = root
        srf.RUN_DIR = os.path.join(root, "store", "run")
        srf.ARCH_DIRS = {
            "x86": os.path.join(srf.RUN_DIR, "x86"),
            "arm64": os.path.join(srf.RUN_DIR, "arm64"),
        }
        srf.STATE_FILE = os.path.join(root, "store", ".sync-state.json")
        os.makedirs(os.path.join(root, "store"), exist_ok=True)
        os.makedirs(os.path.join(root, "shell"), exist_ok=True)
        self.root = root

        self.header = "# header line\n"
        self.fixed = (
            "\n# ======= fixed imm section =======\n"
            '#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-gost-zh-cn"\n'
        )

    def tearDown(self):
        for k, v in self._saved.items():
            setattr(srf, k, v)
        self.tmp.cleanup()

    def _write_fixtures(self, ipk_enabled, ipk_disabled):
        """ipk_enabled/ipk_disabled: {app: 包名列表} 已启用/已注释的生成段条目。"""
        lines = [srf.SH_BEGIN]
        for app, pkgs in ipk_enabled.items():
            lines.append("# 自动生成: %s | 名称 | 说明 | 取消下一行注释即启用" % app)
            lines.append('CUSTOM_PACKAGES="$CUSTOM_PACKAGES %s"' % " ".join(pkgs))
        for app, pkgs in ipk_disabled.items():
            lines.append("# 自动生成: %s | 名称 | 说明 | 取消下一行注释即启用" % app)
            lines.append('#CUSTOM_PACKAGES="$CUSTOM_PACKAGES %s"' % " ".join(pkgs))
        lines.append(srf.SH_END)

        with open(os.path.join(self.root, "store", "README.md"), "w", encoding="utf-8") as f:
            f.write("# store readme\n\n" + srf.MARK_BEGIN + "\n" + srf.MARK_END + "\n\n# footer\n")
        with open(os.path.join(self.root, "shell", "custom-packages.sh"), "w", encoding="utf-8") as f:
            f.write(self.header + "\n".join(lines) + self.fixed)
        with open(os.path.join(self.root, "shell", "apk-custom-packages.sh"), "w", encoding="utf-8") as f:
            f.write(self.header + srf.SH_BEGIN + "\n# empty\n" + srf.SH_END + self.fixed)

    def _read(self, rel):
        with open(os.path.join(self.root, rel), encoding="utf-8") as f:
            return f.read()

    def test_idempotent_and_preserves_enabled_state(self):
        self._write_fixtures(
            ipk_enabled={"easytier": ["easytier", "luci-app-easytier"]},
            ipk_disabled={"luci-theme-shadcn": ["luci-theme-shadcn"]},
        )
        summary = {
            ("ipk", "easytier"): {
                "version": "v2.6.4",
                "archs": {"x86"},
                "ipks": {
                    "easytier_2.6.4_x86_64.ipk",
                    "easytier-noweb_2.6.4_x86_64.ipk",
                    "luci-app-easytier_2.6.4_all.ipk",
                },
                "apks": set(),
            },
            ("ipk", "luci-theme-shadcn"): {
                "version": "0.5.0-r20260830",
                "archs": {"x86"},
                "ipks": {"luci-theme-shadcn_0.5.0-r20260830_all.ipk"},
                "apks": set(),
            },
            ("apk", "sing-box"): {
                "version": "v1.14.0",
                "archs": {"x86"},
                "ipks": set(),
                "apks": {"sing-box-1.14.0-r1_x86_64.apk"},
            },
        }
        srf.maintain_lists(summary, valid_names=None, dry_run=False)

        ipk_sh = self._read("shell/custom-packages.sh")
        apk_sh = self._read("shell/apk-custom-packages.sh")
        readme = self._read("store/README.md")

        # 标记边界之外的内容保持不变
        self.assertTrue(ipk_sh.startswith(self.header))
        self.assertTrue(ipk_sh.endswith(self.fixed))
        self.assertTrue(apk_sh.startswith(self.header))
        self.assertTrue(apk_sh.endswith(self.fixed))
        self.assertTrue(readme.startswith("# store readme\n"))
        self.assertTrue(readme.endswith("# footer\n"))

        # 已启用的应用保持启用; 注释状态的应用保持注释
        self.assertRegex(ipk_sh, r'(?m)^CUSTOM_PACKAGES="\$CUSTOM_PACKAGES easytier[^"]*"$')
        self.assertRegex(ipk_sh, r'(?m)^#CUSTOM_PACKAGES="\$CUSTOM_PACKAGES luci-theme-shadcn"$')
        # apk 通道文件只包含 apk 条目
        self.assertIn("sing-box", apk_sh)
        self.assertNotIn("easytier", apk_sh)
        # README 表格包含两个通道的条目
        self.assertIn("easytier", readme)
        self.assertIn("sing-box", readme)
        self.assertIn("ipk (24.10)", readme)
        self.assertIn("apk (25.12)", readme)
        # 仅 Argon 基础启用、无其它主题启用时, 不应产生冲突警告
        self.assertNotIn("冲突警告", ipk_sh)

        # 幂等: 第二次生成结果字节级一致
        before = {p: self._read(p) for p in (
            "shell/custom-packages.sh",
            "shell/apk-custom-packages.sh",
            "store/README.md",
            "store/.sync-state.json",
        )}
        srf.maintain_lists(summary, valid_names=None, dry_run=False)
        for p, content in before.items():
            self.assertEqual(self._read(p), content)

    def test_alternate_theme_warning_with_base_argon(self):
        self._write_fixtures(
            ipk_enabled={"luci-theme-shadcn": ["luci-theme-shadcn"]},
            ipk_disabled={},
        )
        summary = {
            ("ipk", "luci-theme-shadcn"): {
                "version": "0.5.0-r20260830",
                "archs": {"x86"},
                "ipks": {"luci-theme-shadcn_0.5.0-r20260830_all.ipk"},
                "apks": set(),
            },
        }
        srf.maintain_lists(summary, valid_names=None, dry_run=False)
        ipk_sh = self._read("shell/custom-packages.sh")
        # 构建脚本固定加入 Argon(BASE_ENABLED_APPS), 启用 Shadcn 时应提示多主题冲突
        self.assertIn("冲突警告", ipk_sh)
        self.assertIn("argon", ipk_sh)
        self.assertIn("luci-theme-shadcn", ipk_sh)
        # 警告不阻断: 用户显式启用的 Shadcn 仍保持启用
        self.assertRegex(ipk_sh, r'(?m)^CUSTOM_PACKAGES="\$CUSTOM_PACKAGES luci-theme-shadcn"$')

    def test_mark_stale_runs_threshold(self):
        os.makedirs(srf.ARCH_DIRS["x86"], exist_ok=True)
        run_name = "old-app_1.0_x86_64.run"
        with open(os.path.join(srf.ARCH_DIRS["x86"], run_name), "w", encoding="utf-8") as f:
            f.write("")

        state = {"misses": {}, "stale": []}
        for _ in range(srf.STALE_THRESHOLD):
            srf.mark_stale_runs(set(), state)
        self.assertIn("ipk|old-app", state["stale"])
        # 上游以同名资产重新出现后解除停更
        srf.mark_stale_runs({run_name}, state)
        self.assertNotIn("ipk|old-app", state["stale"])
        self.assertNotIn("ipk|old-app", state["misses"])

    def test_stale_clears_on_version_bump_return(self):
        # 回归: 旧实现按 .run 文件名登记, 应用带新版本(新文件名)回归时,
        # cleanup_old 先删旧文件, 旧文件名的停更标记成孤儿永不解除
        os.makedirs(srf.ARCH_DIRS["x86"], exist_ok=True)
        old = os.path.join(srf.ARCH_DIRS["x86"], "old-app_1.0_x86_64.run")
        with open(old, "w", encoding="utf-8") as f:
            f.write("")

        state = {"misses": {}, "stale": []}
        for _ in range(srf.STALE_THRESHOLD):
            srf.mark_stale_runs(set(), state)
        self.assertIn("ipk|old-app", state["stale"])

        # 模拟同步: 旧文件被 cleanup_old 删除, 新版本资产(新文件名)落盘
        os.remove(old)
        new = "old-app_1.1_x86_64.run"
        with open(os.path.join(srf.ARCH_DIRS["x86"], new), "w", encoding="utf-8") as f:
            f.write("")
        srf.mark_stale_runs({new}, state)
        self.assertNotIn("ipk|old-app", state["stale"])
        self.assertNotIn("ipk|old-app", state["misses"])

    def test_mark_stale_counts_once_per_app_per_run(self):
        # 同一应用 x86 + arm64 两份文件, 每轮同步缺失只计一次
        for arch in ("x86", "arm64"):
            os.makedirs(srf.ARCH_DIRS[arch], exist_ok=True)
        with open(os.path.join(srf.ARCH_DIRS["x86"], "foo_1.0_x86_64.run"), "w", encoding="utf-8") as f:
            f.write("")
        with open(os.path.join(srf.ARCH_DIRS["arm64"], "foo_1.0_aarch64_generic.run"), "w", encoding="utf-8") as f:
            f.write("")

        state = {"misses": {}, "stale": []}
        srf.mark_stale_runs(set(), state)
        srf.mark_stale_runs(set(), state)
        self.assertEqual(state["misses"].get("ipk|foo"), 2)
        self.assertNotIn("ipk|foo", state["stale"])
        # 第 3 次才标记停更
        srf.mark_stale_runs(set(), state)
        self.assertIn("ipk|foo", state["stale"])

    def test_state_migration_from_filename_keys(self):
        # 旧格式 state(按 .run 文件名登记)加载时自动迁移为「通道|应用」标识
        state_file = srf.STATE_FILE
        with open(state_file, "w", encoding="utf-8") as f:
            f.write(
                '{"misses": {"luci-theme-shadcn-0.5.0-r20260830_all.run": 148},'
                ' "stale": ["luci-theme-shadcn-0.5.0-r20260830_all.run"]}'
            )
        state = srf.load_state()
        self.assertEqual(state["stale"], ["ipk|luci-theme-shadcn"])
        self.assertEqual(state["misses"], {"ipk|luci-theme-shadcn": 148})

    def test_stale_label_in_generated_lists(self):
        # 停更应用在 README 表格与开关文件注释中带「上游停更」说明(文件仍保留)
        self._write_fixtures(
            ipk_enabled={},
            ipk_disabled={"old-app": ["old-app"]},
        )
        with open(srf.STATE_FILE, "w", encoding="utf-8") as f:
            f.write('{"misses": {}, "stale": ["ipk|old-app"]}')
        summary = {
            ("ipk", "old-app"): {
                "version": "1.0",
                "archs": {"x86"},
                "ipks": {"old-app_1.0_x86_64.ipk"},
                "apks": set(),
            },
        }
        srf.maintain_lists(summary, valid_names=None, dry_run=False)
        readme = self._read("store/README.md")
        ipk_sh = self._read("shell/custom-packages.sh")
        self.assertIn("⚠️上游停更", readme)
        self.assertIn("上游停更(保留旧版)", ipk_sh)
        # 列表条目本身仍在(保留旧版, 不删除)
        self.assertIn("old-app", readme)
        self.assertIn("old-app", ipk_sh)


if __name__ == "__main__":
    unittest.main()
