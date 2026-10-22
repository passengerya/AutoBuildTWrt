#!/bin/sh
# zz-turboacc-tune.sh —— 默认开启 turboacc 的 BBR + fullcone(防错 #49)
#
# uci-defaults 按 ls 字典序执行: 99-custom.sh < turboacc < zz-*, 本脚本排在
# turboacc 自带的 uci-defaults 之后, 首启即生效(不用等第二次启动)。
#
# 为什么需要: turboacc 的 uci-defaults 首次启动会整文件重写 /etc/config/turboacc
# (tcpcca 强制 cubic; fullcone 只认 xt_FULLCONENAT.ko, imm 无此模块于是写 0)。
# 而 imm 的 firewall4 默认就支持 fullcone(硬依赖 kmod-nft-fullcone), 写 0 反而
# 丢掉了默认加速——这里把它恢复, 并补上 BBR。
#
# 幂等门: global.set=1 表示配置已初始化(本脚本或用户在 LuCI 保存都会写 1),
# 用户手动改过就不重踩。保留配置升级后 turboacc 的 uci-defaults 会重现并把
# 配置重写回 cubic(此时 set 又变 0), 本脚本随之重新调优——不用标记文件,
# 标记文件反而会阻止升级后的重调(防错 #49)。
#
# 注意: 只对固件自带 turboacc 生效; 刷机后手动安装的包不会执行本脚本。
# glinet 变体不挂本目录(且不支持第三方包, 防错 #22), 天然不受影响。

LOGFILE="/etc/config/uci-defaults-log.txt"

[ -f /etc/config/turboacc ] || exit 0
[ "$(uci -q get turboacc.global.set)" = "1" ] && exit 0
[ -n "$(uci -q get turboacc.config.tcpcca)" ] || exit 0

uci set turboacc.config.tcpcca='bbr'
uci set turboacc.config.fullcone='1'
uci set turboacc.global.set='1'
uci commit turboacc

echo "zz-turboacc-tune: tcpcca=bbr fullcone=1 set=1" >>$LOGFILE

exit 0
