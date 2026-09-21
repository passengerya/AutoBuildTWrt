#!/bin/bash
# ============= 第三方软件开关（24.10 ipk 通道） =============
# 本文件由 Sync Store 工作流自动维护（每天北京时间 7:00 更新），请勿手动修改。
# 选择软件：把对应软件行行首的 # 去掉（取消注释）即可；下次同步保持你的选择。
# 与 25.12 通道对应文件：shell/apk-custom-packages.sh
# ==========================================================

# ============ 以下由 Sync Store 自动维护(根据内嵌 store 实际内容生成) ============
# ⚠️ 冲突警告: argon 与 luci-theme-aurora 与 luci-theme-shadcn 同时开启, 可能互相冲突, 请只保留其中一个

# ───────────────────── 代理工具 ─────────────────────
# 自动生成: clashoo | Clashoo代理 | 代理工具(与 nikki 冲突勿同时开启) | 2026.09.19 | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES clashoo luci-app-clashoo luci-i18n-clashoo-zh-cn"
# 自动生成: homeproxy | 代理平台 | 现代代理平台(基于 sing-box) | 26.187.07809 | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-homeproxy luci-i18n-homeproxy-zh-cn sing-box-tiny"
# 自动生成: luci-app-nekobox | NekoBox代理 | NekoBox 代理工具 | 2.0.9 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-nekobox"
# 自动生成: momo | Momo代理 | 基于 sing-box 的透明代理 | v1.2.1 | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-momo luci-i18n-momo-zh-cn momo"
# 自动生成: nikki | Nikki代理 | 代理工具(与 clashoo 冲突勿同时开启) | v1.26.1 | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-nikki luci-i18n-nikki-ru luci-i18n-nikki-zh-cn luci-i18n-nikki-zh-tw mihomo-alpha mihomo-meta nikki"
# 自动生成: openclash | OpenClash | Clash 代理客户端 | v0.47.156 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-openclash"
# 自动生成: openwrt-daede | eBPF代理 | 基于 eBPF 的高性能透明代理(dae/daed) | 2026.09.20 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES dae daed luci-app-daede vmlinux-btf"
# 自动生成: passwall | PassWall | 代理工具(自带依赖) | 26.9.9-1 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES 23.05-24.10_luci-app-passwall 23.05-24.10_luci-i18n-passwall-zh-cn chinadns-ng dns2socks geoview ipt2socks microsocks naiveproxy shadow-tls shadowsocks-rust-sslocal shadowsocks-rust-ssserver shadowsocksr-libev-ssr-local shadowsocksr-libev-ssr-redir shadowsocksr-libev-ssr-server simple-obfs-client tcping trojan-plus tuic-client v2ray-geoip v2ray-geosite v2ray-plugin xray-core xray-plugin"
# 自动生成: passwall2 | PassWall2 | 代理工具(自带依赖) | 26.9.12-2 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES chinadns-ng geoview luci-app-passwall2 luci-i18n-passwall2-zh-cn naiveproxy shadowsocks-rust-sslocal shadowsocks-rust-ssserver shadowsocksr-libev-ssr-local shadowsocksr-libev-ssr-redir shadowsocksr-libev-ssr-server simple-obfs-client tcping tuic-client v2ray-geoip v2ray-geosite v2ray-plugin xray-core"
# 自动生成: sing-box | Sing-box内核 | 通用代理内核 | v1.14.1 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES sing-box"
# 自动生成: ssrp-mihomo | SSRP代理 | SSR-Plus 代理工具(mihomo 内核) | 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES chinadns-ng dns2socks dns2socks-rust dns2tcp hysteria ipt2socks ipt2socks-rs libopenssl3 libudns lua-neturl luci-app-ssr-plus luci-i18n-ssr-plus-zh-cn microsocks mosdns naiveproxy redsocks2 shadow-tls shadowsocks-libev-ss-server shadowsocks-rust-sslocal shadowsocks-rust-ssmanager shadowsocks-rust-ssserver shadowsocks-rust-ssservice shadowsocks-rust-ssurl shadowsocksr-libev-ssr-check shadowsocksr-libev-ssr-local shadowsocksr-libev-ssr-nat shadowsocksr-libev-ssr-redir shadowsocksr-libev-ssr-server simple-obfs-client tcping tcping-simple trojan trojan-plus tuic-client v2ray-plugin xray-core"

# ───────────────────── 网络服务 ─────────────────────
# 自动生成: bandix | 流量监控 | Bandix 实时流量监控与统计 | 0.11.0-r25 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES bandix luci-app-bandix"
# 自动生成: easytier | 异地组网 | EasyTier 点对点组网工具 | v2.6.4 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES easytier luci-app-easytier"
# 自动生成: luci-app-oaf | 应用过滤 | OpenAppFilter 应用过滤(基于 nftables, 程序管控/游戏加速) | 6.1.4-r1 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-oaf luci-i18n-oaf-zh-cn"
# 自动生成: luci-app-tailscale-community | Tailscale组网 | Tailscale 组网(Community 版) | 4.2.3-r1 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-tailscale-community luci-i18n-tailscale-community-zh-cn"
# 自动生成: lucky | Lucky大吉 | 端口转发/反向代理/内网穿透 | 2.20.2-r13 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-lucky lucky"
# 自动生成: rtp2httpd | IPTV转发 | IPTV 流媒体转发服务器 | 3.17.1-r1 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-rtp2httpd luci-i18n-rtp2httpd-zh-cn rtp2httpd"

# ───────────────────── 广告与DNS ─────────────────────
# 自动生成: adguardhome | 本地DNS去广告 | AdGuardHome 广告拦截与 DNS 服务 | v0.107.79 | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-adguardhome"
# 自动生成: mosdns | DNS分流 | 高性能 DNS 分流(DoH/DoQ 等) | v5.3.4-r14 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES geo2txt luci-app-mosdns luci-i18n-mosdns-zh-cn mosdns v2ray-geoip v2ray-geosite"

# ───────────────────── 文件与存储 ─────────────────────
# 自动生成: dufs | 文件服务器 | 轻量文件服务器(静态托管/上传/WebDAV) | 0.46.0-r1 | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES dufs luci-app-dufs luci-i18n-dufs-zh-cn"
# 自动生成: openlist2 | 网盘聚合 | OpenList2 网盘聚合(Alist 变体) | v4.2.6 | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-openlist2 luci-i18n-openlist2-zh-cn openlist2"
# 自动生成: quickfile | 文件管理 | 轻量网页文件管理器(与 luci-app-run 冲突勿同时开启) | 1.0.16 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-quickfile luci-i18n-quickfile-zh-cn quickfile"

# ───────────────────── 系统与界面 ─────────────────────
# 自动生成: argon | Argon主题 | 简洁主题, 支持明暗自动切换 | 2.4.3-r20250722 | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-argon-config luci-i18n-argon-config-zh-cn luci-theme-argon"
# 自动生成: luci-app-advancedplus | 高级设置 | 进阶设置(与 argon-config 冲突勿同时开启) | 1.8.7-r20251116 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-advancedplus luci-i18n-advancedplus-zh-cn"
# 自动生成: luci-app-aurora-config | 极光配置中心 | Aurora 主题配置中心(提供 /etc/config/aurora, 与主题配套启用) | 1.2.5-r20260920 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-aurora-config luci-i18n-aurora-config-zh-cn"
# 自动生成: luci-app-uninstall | 高级卸载 | 彻底卸载插件的工具 | v1.2.6 | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-uninstall"
# 自动生成: luci-theme-aurora | 极光主题 | 极光主题界面(需配套 luci-app-aurora-config 配置中心, 会接管 LuCI 菜单/路由, 谨慎启用) | 1.4.0-r20260920 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-theme-aurora"
# 自动生成: luci-theme-shadcn | Shadcn主题 | 现代 Shadcn 风格界面主题(会接管 LuCI 菜单/路由, 24.10 下谨慎启用) | 0.6.0-r20260920 上游停更(保留旧版) | 取消下一行注释即启用
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-theme-shadcn"

# ───────────────────── 设备管理 ─────────────────────
# 自动生成: luci-app-amlogic | 晶晨宝盒 | 晶晨机顶盒管理(仅 ARM64 平台) | 3.1.321-r1 上游停更(保留旧版) | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-amlogic luci-i18n-amlogic-zh-cn"
# 自动生成: luci-app-store | iStore商店 | iStore 应用商店 | 0.2.1-r1 | 取消下一行注释即启用
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-app-store luci-lib-taskd luci-lib-xterm taskd"
# ============ 自动维护结束 ============

#===========================以下imm仓库内的软件==============================↓
# (imm 仓库内软件为固定列表, 无需同步; 构建时直接从 ImmortalWrt 官方源解析安装)
# ───────────────────── 代理与VPN ─────────────────────
# Dae - 基于 eBPF 的高性能透明代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES dae"
# GOST - 加密隧道/代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-gost-zh-cn"
# Hysteria - 高性能 QUIC 代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES hysteria"
# IPsec VPN 服务器（IKEv1 PSK/Xauth）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ipsec-vpnd-zh-cn"
# MicroSocks - 微型 SOCKS5 代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-microsocks-zh-cn"
# OpenConnect VPN 服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ocserv-zh-cn"
# Privoxy - 隐私过滤代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-privoxy-zh-cn"
# SoftEther VPN
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-softethervpn-zh-cn"
# Squid - 代理缓存服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-squid-zh-cn"
# SSH 隧道
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-sshtunnel-zh-cn"
# TinyProxy - 轻量 HTTP 代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-tinyproxy-zh-cn"
# Tor - 匿名网络
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-tor-zh-cn"
# v2rayA - 透明代理面板
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-v2raya-zh-cn"
# Xray-core - 代理内核
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES xray-core"
# ───────────────────── 网络服务 ─────────────────────
# 3Cat - 简易端口转发（基于 3proxy）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-3cat-zh-cn"
# 3G/4G 上网卡 - 移动网络连接信息显示
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-3ginfo-lite-zh-cn"
# ARP 绑定 - 防 ARP 欺骗
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-arpbind-zh-cn"
# banIP - 入侵 IP 自动封禁
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-banip-zh-cn"
# BCP38 - 反向路径过滤（防地址欺骗）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-bcp38-zh-cn"
# BMX7 - 无线网状网络协议
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-bmx7-zh-cn"
# CoovaChilli - 强制门户（WiFi 热点认证）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-coovachilli-zh-cn"
# CrowdSec - 防火墙联动防护
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-crowdsec-firewall-bouncer-zh-cn"
# DAWN - WiFi 漫游优化（802.11k/v）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-dawn-zh-cn"
# dcwapd - 双频无线 AP 守护
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-dcwapd-zh-cn"
# DDNS-Go - 动态域名解析
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ddns-go-zh-cn"
# DDNS - 动态 DNS 客户端
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ddns-zh-cn"
# DSL - 调制解调器状态监控
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-dsl-zh-cn"
# EasyQoS - 简单流量控制
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-eqos-zh-cn"
# fwknop - 单包授权（Port Knocking）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-fwknopd-zh-cn"
# HAProxy - TCP 负载均衡
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-haproxy-tcp-zh-cn"
# Keepalived - 高可用（VRRP）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-keepalived-zh-cn"
# LLDP - 链路层邻居发现
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-lldpd-zh-cn"
# ModemBand - 4G/5G 模组频段锁定
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-modemband-zh-cn"
# Mosquitto - MQTT 消息代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-mosquitto-zh-cn"
# MWAN3 - 多线负载均衡
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-mwan3-zh-cn"
# nftables QoS - 限速
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-nft-qos-zh-cn"
# nlbwmon - 局域网流量统计
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-nlbwmon-zh-cn"
# OLSR - 服务通告
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-olsr-services-zh-cn"
# OLSR - 拓扑可视化
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-olsr-viz-zh-cn"
# OLSR - 网状路由协议
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-olsr-zh-cn"
# omcproxy - IGMP 组播代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-omcproxy-zh-cn"
# PBR - 策略路由
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-pbr-zh-cn"
# PPPoE 中继
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-pppoe-relay-zh-cn"
# PPPoE 拨号服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-pppoe-server-zh-cn"
# QoS - 服务质量
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-qos-zh-cn"
# PPPoE 服务器（Roaring Penguin）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-rp-pppoe-server-zh-cn"
# ser2net - 串口转网络
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ser2net-zh-cn"
# 短信工具 - SMS/USSD/AT 命令
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-sms-tool-js-zh-cn"
# SNMP - 网络监控代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-snmpd-zh-cn"
# Splash - 网络认证启动页
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-splash-zh-cn"
# SQM - 智能队列管理（抗缓冲膨胀）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-sqm-zh-cn"
# TimeWOL - 定时网络唤醒
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-timewol-zh-cn"
# Travelmate - 无线中继自动漫游
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-travelmate-zh-cn"
# UPnP - 端口自动映射
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-upnp-zh-cn"
# usteer - WiFi 频段引导漫游
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-usteer-zh-cn"
# vnStat - 流量统计
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-vnstat2-zh-cn"
# Watchcat - 网络看门狗（断网重启）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-watchcat-zh-cn"
# WiFi 定时开关
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-wifischedule-zh-cn"
# Wake-on-LAN - 网络唤醒
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-wol-zh-cn"
# ───────────────────── 广告与DNS ─────────────────────
# Adblock Fast - 广告拦截
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-adblock-fast-zh-cn"
# Adblock - 广告拦截
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-adblock-zh-cn"
# HTTPS DNS 代理 - DoH 加密解析
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-https-dns-proxy-zh-cn"
# NextDNS - 加密 DNS 服务
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-nextdns-zh-cn"
# SmartDNS - 智能 DNS 分流
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-smartdns-zh-cn"
# Unbound - 递归 DNS 解析器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-unbound-zh-cn"
# ───────────────────── 穿透与组网 ─────────────────────
# Cloudflared - Cloudflare Zero Trust 隧道
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-cloudflared-zh-cn"
# DynaPoint - 动态点对点组网
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-dynapoint-zh-cn"
# EoIP - 以太网隧道（MikroTik 兼容）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-eoip-zh-cn"
# frp 客户端 - 内网穿透
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-frpc-zh-cn"
# frp 服务端 - 内网穿透
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-frps-zh-cn"
# n2n - P2P VPN 组网
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-n2n-zh-cn"
# NATMap - NAT 端口映射
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-natmap-zh-cn"
# ngrok 客户端 - 内网穿透
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ngrokc-zh-cn"
# NPS - 内网穿透
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-nps-zh-cn"
# PageKite - 反向隧道
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-pagekitec-zh-cn"
# Tailscale - 异地组网（WireGuard）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES tailscale"
# xfrpc - 内网穿透
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-xfrpc-zh-cn"
# ZeroTier - 虚拟局域网
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-zerotier-zh-cn"
# ───────────────────── 文件与存储 ─────────────────────
# CIFS/SMB - 网络共享挂载
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-cifs-mount-zh-cn"
# 磁盘管理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-diskman-zh-cn"
# FileBrowser - 网页文件管理器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-filebrowser-go-zh-cn"
# FileBrowser - 网页文件管理器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-filebrowser-zh-cn"
# 文件管理器 - 网页文件管理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-filemanager-zh-cn"
# 硬盘休眠 - 空闲自动停转
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-hd-idle-zh-cn"
# ksmbd - 内核级 SMB 文件共享
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ksmbd-zh-cn"
# NFS - 网络文件系统
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-nfs-zh-cn"
# OpenList - 网盘聚合（Alist）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-openlist-zh-cn"
# p910nd - 打印服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-p910nd-zh-cn"
# PS3NETSRV - PS3 游戏共享
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ps3netsrv-zh-cn"
# Rclone - 云盘同步
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-rclone-zh-cn"
# Samba4 - SMB 文件共享
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-samba4-zh-cn"
# Syncthing - 文件同步
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-syncthing-zh-cn"
# USB 打印服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-usb-printer-zh-cn"
# vsftpd - FTP 服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-vsftpd-zh-cn"
# ───────────────────── 下载与媒体 ─────────────────────
# AirPlay 2 - 苹果音频接收器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-airplay2-zh-cn"
# aMule - 电驴下载（eD2k 网络）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-amule-zh-cn"
# Aria2 - 多协议下载工具
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-aria2-zh-cn"
# MiniDLNA - 媒体服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-minidlna-zh-cn"
# MJPG-Streamer - 摄像头视频流
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-mjpg-streamer-zh-cn"
# msd_lite - 组播转单播（IPTV 直播）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-msd_lite-zh-cn"
# 音乐远程控制中心
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-music-remote-center-zh-cn"
# OSCam - 电视卡共享服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-oscam-zh-cn"
# qBittorrent - BT 下载
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-qbittorrent-zh-cn"
# spotifyd - Spotify 音乐播放器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-spotifyd-zh-cn"
# Transmission - BT 下载
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-transmission-zh-cn"
# udpxy - 组播转 HTTP 单播
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-udpxy-zh-cn"
# ───────────────────── 系统管理 ─────────────────────
# ACL - LuCI 账户管理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-acl-zh-cn"
# ACME - SSL 证书自动申请（Let's Encrypt）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-acme-zh-cn"
# 高级重启 - 支持双分区机型切换系统
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-advanced-reboot-zh-cn"
# 无人值守在线升级
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-attendedsysupgrade-zh-cn"
# 定时重启
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-autoreboot-zh-cn"
# 电池电量 - 状态显示
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-battstatus-zh-cn"
# ClamAV - 杀毒软件
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-clamav-zh-cn"
# 自定义命令 - Shell 命令执行
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-commands-zh-cn"
# cpulimit - CPU 使用率限制
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-cpulimit-zh-cn"
# CloudShark - 远程抓包分析 (⚠️ 依赖 mbedtls 版 libustream, 与本固件 openssl 后端冲突, 请勿开启)
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-cshark-zh-cn"
# 仪表盘 - LuCI 首页仪表盘
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-dashboard-zh-cn"
# 邮件通知 - EmailRelay 发送
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-email-zh-cn"
# irqbalance - 中断负载均衡
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-irqbalance-zh-cn"
# LXC - Linux 容器管理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-lxc-zh-cn"
# Netdata - 实时系统监控
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-netdata-zh-cn"
# NUT - UPS 不间断电源管理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-nut-zh-cn"
# OLED - 屏幕显示
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-oled-zh-cn"
# OpenWISP - 集中管理代理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-openwisp-zh-cn"
# Radicale - 日历/通讯录服务器（CalDAV/CardDAV）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-radicale-zh-cn"
# 内存清理 - 释放缓存
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ramfree-zh-cn"
# RustDesk - 远程桌面服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-rustdesk-server-zh-cn"
# 系统统计 - 图表监控
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-statistics-zh-cn"
# ttyd - Web 终端
CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ttyd-zh-cn"
# uHTTPd - Web 服务器配置
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-uhttpd-zh-cn"
# vlmcsd - KMS 激活服务器
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-vlmcsd-zh-cn"
# 微信推送 - 通知
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-wechatpush-zh-cn"
# xinetd - 超级服务管理
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-xinetd-zh-cn"
# ───────────────────── 校园网 ─────────────────────
# 深澜校园网 - 自动认证客户端
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-bitsrunlogin-go-zh-cn"
# 有线 802.1X 认证 - 校园网客户端
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-cd8021x-zh-cn"
# MiniEAP - 校园网认证客户端
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-minieap-zh-cn"
# 中山大学校园网 - H3C 认证
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-sysuh3c-zh-cn"
# UA2F - 校园网防检测
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-ua2f-zh-cn"
# 迅雷快鸟 - 宽带加速
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-xlnetacc-zh-cn"
# ───────────────────── 其他 ─────────────────────
# dump1090 - ADS-B 航空信号接收（1090MHz）
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-dump1090-zh-cn"
# 示例应用 - LuCI JS 开发模板
#CUSTOM_PACKAGES="$CUSTOM_PACKAGES luci-i18n-example-zh-cn"
#===========================imm仓库内的软件结束==============================↑

