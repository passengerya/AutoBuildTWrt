# ImmortalWrt 仓库内软件列表（固定列表）

本列表为 **imm 官方仓库内**的软件（构建固件的底层来源），**无需同步**——
构建时由 ImageBuilder 直接从 ImmortalWrt 官方源解析安装。
在 `shell/custom-packages.sh` / `shell/apk-custom-packages.sh` 的
「以下imm仓库内的软件」固定段中取消注释对应行即可装入固件。

| 软件包 | 中文说明 |
| --- | --- |
| luci-i18n-3cat-zh-cn | 3Cat - 简易端口转发（基于 3proxy） |
| luci-i18n-3ginfo-lite-zh-cn | 3G/4G 上网卡 - 移动网络连接信息显示 |
| luci-i18n-acl-zh-cn | ACL - LuCI 账户管理 |
| luci-i18n-acme-zh-cn | ACME - SSL 证书自动申请（Let's Encrypt） |
| luci-i18n-adblock-fast-zh-cn | Adblock Fast - 广告拦截 |
| luci-i18n-adblock-zh-cn | Adblock - 广告拦截 |
| luci-i18n-advanced-reboot-zh-cn | 高级重启 - 支持双分区机型切换系统 |
| luci-i18n-airplay2-zh-cn | AirPlay 2 - 苹果音频接收器 |
| luci-i18n-amule-zh-cn | aMule - 电驴下载（eD2k 网络） |
| luci-i18n-aria2-zh-cn | Aria2 - 多协议下载工具 |
| luci-i18n-arpbind-zh-cn | ARP 绑定 - 防 ARP 欺骗 |
| luci-i18n-attendedsysupgrade-zh-cn | 无人值守在线升级 |
| luci-i18n-autoreboot-zh-cn | 定时重启 |
| luci-i18n-banip-zh-cn | banIP - 入侵 IP 自动封禁 |
| luci-i18n-battstatus-zh-cn | 电池电量 - 状态显示 |
| luci-i18n-bcp38-zh-cn | BCP38 - 反向路径过滤（防地址欺骗） |
| luci-i18n-bitsrunlogin-go-zh-cn | 深澜校园网 - 自动认证客户端 |
| luci-i18n-bmx7-zh-cn | BMX7 - 无线网状网络协议 |
| luci-i18n-cd8021x-zh-cn | 有线 802.1X 认证 - 校园网客户端 |
| luci-i18n-cifs-mount-zh-cn | CIFS/SMB - 网络共享挂载 |
| luci-i18n-clamav-zh-cn | ClamAV - 杀毒软件 |
| luci-i18n-cloudflared-zh-cn | Cloudflared - Cloudflare Zero Trust 隧道 |
| luci-i18n-commands-zh-cn | 自定义命令 - Shell 命令执行 |
| luci-i18n-coovachilli-zh-cn | CoovaChilli - 强制门户（WiFi 热点认证） |
| luci-i18n-cpulimit-zh-cn | cpulimit - CPU 使用率限制 |
| luci-i18n-crowdsec-firewall-bouncer-zh-cn | CrowdSec - 防火墙联动防护 |
| luci-i18n-cshark-zh-cn | CloudShark - 远程抓包分析（⚠️ 依赖 mbedtls 版 libustream，与固件 openssl 后端冲突，请勿开启） |
| dae | Dae - 基于 eBPF 的高性能透明代理 |
| luci-i18n-dashboard-zh-cn | 仪表盘 - LuCI 首页仪表盘 |
| luci-i18n-dawn-zh-cn | DAWN - WiFi 漫游优化（802.11k/v） |
| luci-i18n-dcwapd-zh-cn | dcwapd - 双频无线 AP 守护 |
| luci-i18n-ddns-go-zh-cn | DDNS-Go - 动态域名解析 |
| luci-i18n-ddns-zh-cn | DDNS - 动态 DNS 客户端 |
| luci-i18n-diskman-zh-cn | 磁盘管理 |
| luci-i18n-dsl-zh-cn | DSL - 调制解调器状态监控 |
| luci-i18n-dump1090-zh-cn | dump1090 - ADS-B 航空信号接收（1090MHz） |
| luci-i18n-dynapoint-zh-cn | DynaPoint - 动态点对点组网 |
| luci-i18n-email-zh-cn | 邮件通知 - EmailRelay 发送 |
| luci-i18n-eoip-zh-cn | EoIP - 以太网隧道（MikroTik 兼容） |
| luci-i18n-eqos-zh-cn | EasyQoS - 简单流量控制 |
| luci-i18n-example-zh-cn | 示例应用 - LuCI JS 开发模板 |
| luci-i18n-filebrowser-go-zh-cn | FileBrowser - 网页文件管理器 |
| luci-i18n-filebrowser-zh-cn | FileBrowser - 网页文件管理器 |
| luci-i18n-filemanager-zh-cn | 文件管理器 - 网页文件管理 |
| luci-i18n-frpc-zh-cn | frp 客户端 - 内网穿透 |
| luci-i18n-frps-zh-cn | frp 服务端 - 内网穿透 |
| luci-i18n-fwknopd-zh-cn | fwknop - 单包授权（Port Knocking） |
| luci-i18n-gost-zh-cn | GOST - 加密隧道/代理 |
| luci-i18n-haproxy-tcp-zh-cn | HAProxy - TCP 负载均衡 |
| luci-i18n-hd-idle-zh-cn | 硬盘休眠 - 空闲自动停转 |
| luci-i18n-https-dns-proxy-zh-cn | HTTPS DNS 代理 - DoH 加密解析 |
| hysteria | Hysteria - 高性能 QUIC 代理 |
| luci-i18n-ipsec-vpnd-zh-cn | IPsec VPN 服务器（IKEv1 PSK/Xauth） |
| luci-i18n-irqbalance-zh-cn | irqbalance - 中断负载均衡 |
| luci-i18n-keepalived-zh-cn | Keepalived - 高可用（VRRP） |
| luci-i18n-ksmbd-zh-cn | ksmbd - 内核级 SMB 文件共享 |
| luci-i18n-lldpd-zh-cn | LLDP - 链路层邻居发现 |
| luci-i18n-lxc-zh-cn | LXC - Linux 容器管理 |
| luci-i18n-microsocks-zh-cn | MicroSocks - 微型 SOCKS5 代理 |
| luci-i18n-minidlna-zh-cn | MiniDLNA - 媒体服务器 |
| luci-i18n-minieap-zh-cn | MiniEAP - 校园网认证客户端 |
| luci-i18n-mjpg-streamer-zh-cn | MJPG-Streamer - 摄像头视频流 |
| luci-i18n-modemband-zh-cn | ModemBand - 4G/5G 模组频段锁定 |
| luci-i18n-mosquitto-zh-cn | Mosquitto - MQTT 消息代理 |
| luci-i18n-msd_lite-zh-cn | msd_lite - 组播转单播（IPTV 直播） |
| luci-i18n-music-remote-center-zh-cn | 音乐远程控制中心 |
| luci-i18n-mwan3-zh-cn | MWAN3 - 多线负载均衡 |
| luci-i18n-n2n-zh-cn | n2n - P2P VPN 组网 |
| luci-i18n-natmap-zh-cn | NATMap - NAT 端口映射 |
| luci-i18n-netdata-zh-cn | Netdata - 实时系统监控 |
| luci-i18n-nextdns-zh-cn | NextDNS - 加密 DNS 服务 |
| luci-i18n-nfs-zh-cn | NFS - 网络文件系统 |
| luci-i18n-nft-qos-zh-cn | nftables QoS - 限速 |
| luci-i18n-ngrokc-zh-cn | ngrok 客户端 - 内网穿透 |
| luci-i18n-nlbwmon-zh-cn | nlbwmon - 局域网流量统计 |
| luci-i18n-nps-zh-cn | NPS - 内网穿透 |
| luci-i18n-nut-zh-cn | NUT - UPS 不间断电源管理 |
| luci-i18n-ocserv-zh-cn | OpenConnect VPN 服务器 |
| luci-i18n-oled-zh-cn | OLED - 屏幕显示 |
| luci-i18n-olsr-services-zh-cn | OLSR - 服务通告 |
| luci-i18n-olsr-viz-zh-cn | OLSR - 拓扑可视化 |
| luci-i18n-olsr-zh-cn | OLSR - 网状路由协议 |
| luci-i18n-omcproxy-zh-cn | omcproxy - IGMP 组播代理 |
| luci-i18n-openlist-zh-cn | OpenList - 网盘聚合（Alist） |
| luci-i18n-openwisp-zh-cn | OpenWISP - 集中管理代理 |
| luci-i18n-oscam-zh-cn | OSCam - 电视卡共享服务器 |
| luci-i18n-p910nd-zh-cn | p910nd - 打印服务器 |
| luci-i18n-pagekitec-zh-cn | PageKite - 反向隧道 |
| luci-i18n-pbr-zh-cn | PBR - 策略路由 |
| luci-i18n-pppoe-relay-zh-cn | PPPoE 中继 |
| luci-i18n-pppoe-server-zh-cn | PPPoE 拨号服务器 |
| luci-i18n-privoxy-zh-cn | Privoxy - 隐私过滤代理 |
| luci-i18n-ps3netsrv-zh-cn | PS3NETSRV - PS3 游戏共享 |
| luci-i18n-qbittorrent-zh-cn | qBittorrent - BT 下载 |
| luci-i18n-qos-zh-cn | QoS - 服务质量 |
| luci-i18n-radicale-zh-cn | Radicale - 日历/通讯录服务器（CalDAV/CardDAV） |
| luci-i18n-ramfree-zh-cn | 内存清理 - 释放缓存 |
| luci-i18n-rclone-zh-cn | Rclone - 云盘同步 |
| luci-i18n-rp-pppoe-server-zh-cn | PPPoE 服务器（Roaring Penguin） |
| luci-i18n-rustdesk-server-zh-cn | RustDesk - 远程桌面服务器 |
| luci-i18n-samba4-zh-cn | Samba4 - SMB 文件共享 |
| luci-i18n-ser2net-zh-cn | ser2net - 串口转网络 |
| luci-i18n-smartdns-zh-cn | SmartDNS - 智能 DNS 分流 |
| luci-i18n-sms-tool-js-zh-cn | 短信工具 - SMS/USSD/AT 命令 |
| luci-i18n-snmpd-zh-cn | SNMP - 网络监控代理 |
| luci-i18n-softethervpn-zh-cn | SoftEther VPN |
| luci-i18n-splash-zh-cn | Splash - 网络认证启动页 |
| luci-i18n-spotifyd-zh-cn | spotifyd - Spotify 音乐播放器 |
| luci-i18n-sqm-zh-cn | SQM - 智能队列管理（抗缓冲膨胀） |
| luci-i18n-squid-zh-cn | Squid - 代理缓存服务器 |
| luci-i18n-sshtunnel-zh-cn | SSH 隧道 |
| luci-i18n-statistics-zh-cn | 系统统计 - 图表监控 |
| luci-i18n-syncthing-zh-cn | Syncthing - 文件同步 |
| luci-i18n-sysuh3c-zh-cn | 中山大学校园网 - H3C 认证 |
| tailscale | Tailscale - 异地组网（WireGuard） |
| luci-i18n-timewol-zh-cn | TimeWOL - 定时网络唤醒 |
| luci-i18n-tinyproxy-zh-cn | TinyProxy - 轻量 HTTP 代理 |
| luci-i18n-tor-zh-cn | Tor - 匿名网络 |
| luci-i18n-transmission-zh-cn | Transmission - BT 下载 |
| luci-i18n-travelmate-zh-cn | Travelmate - 无线中继自动漫游 |
| luci-i18n-ttyd-zh-cn | ttyd - Web 终端 |
| luci-i18n-ua2f-zh-cn | UA2F - 校园网防检测 |
| luci-i18n-udpxy-zh-cn | udpxy - 组播转 HTTP 单播 |
| luci-i18n-uhttpd-zh-cn | uHTTPd - Web 服务器配置 |
| luci-i18n-unbound-zh-cn | Unbound - 递归 DNS 解析器 |
| luci-i18n-upnp-zh-cn | UPnP - 端口自动映射 |
| luci-i18n-usb-printer-zh-cn | USB 打印服务器 |
| luci-i18n-usteer-zh-cn | usteer - WiFi 频段引导漫游 |
| luci-i18n-v2raya-zh-cn | v2rayA - 透明代理面板 |
| luci-i18n-vlmcsd-zh-cn | vlmcsd - KMS 激活服务器 |
| luci-i18n-vnstat2-zh-cn | vnStat - 流量统计 |
| luci-i18n-vsftpd-zh-cn | vsftpd - FTP 服务器 |
| luci-i18n-watchcat-zh-cn | Watchcat - 网络看门狗（断网重启） |
| luci-i18n-wechatpush-zh-cn | 微信推送 - 通知 |
| luci-i18n-wifischedule-zh-cn | WiFi 定时开关 |
| luci-i18n-wol-zh-cn | Wake-on-LAN - 网络唤醒 |
| luci-i18n-xfrpc-zh-cn | xfrpc - 内网穿透 |
| luci-i18n-xinetd-zh-cn | xinetd - 超级服务管理 |
| xray-core | Xray-core - 代理内核 |
| luci-i18n-xlnetacc-zh-cn | 迅雷快鸟 - 宽带加速 |
| luci-i18n-zerotier-zh-cn | ZeroTier - 虚拟局域网 |
| adguardhome | AdGuardHome - 本地DNS去广告(25.12 官方源) |
| luci-app-adguardhome | AdGuardHome - LuCI 界面(25.12 官方源, 无 zh-cn 语言包) |
| dufs | Dufs - 轻量文件服务器(25.12 官方源) |
| luci-app-dufs | Dufs - LuCI 界面(25.12 官方源) |
| luci-i18n-dufs-zh-cn | Dufs - 简体中文语言包 |
| luci-app-homeproxy | HomeProxy - 现代代理平台 LuCI 界面(25.12 官方源, 内核用 store 的 sing-box) |
| luci-i18n-homeproxy-zh-cn | HomeProxy - 简体中文语言包 |
