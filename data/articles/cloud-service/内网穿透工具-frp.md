---
author: admin@pldz1.com
category: cloud-service
date: '2025-08-24'
serialNo: 5
status: publish
summary: frp 更适合轻量级的端口暴露与远程调试，而 OpenVPN/ZeroTier/Tailscale 更像是把你“拉进”内网，适合完整网络互通
tags:
- 云服务器
- 内网穿透
thumbnail: /api/v1/website/image/cloud-service/cloud-service-frp-thumbnail.png
title: 内网穿透工具-frp
---

# 内网穿透工具随笔

最近折腾内网穿透，顺手记录下自己的理解，算是一篇小笔记，或许能帮到后来人。

---

## frp vs OpenVPN

一开始很多人会把 **frp** 和 **OpenVPN** 放在一起比较，其实定位还是有点差别的：

* **OpenVPN**
  基于 SSL/TLS 的 VPN 技术，本质是搞一条加密隧道，把远程设备“虚拟”到目标网络里，好像你直接插了根网线连在公司局域网。

  * 适合点对点、点对多点的安全访问
  * 全流量加密，认证机制完善
  * 配置相对复杂

* **frp (Fast Reverse Proxy)**
  更像是一个专注做 **内网穿透 / 端口映射** 的小工具。它通过客户端和服务端建立一条隧道，服务端暴露的端口就能反向代理到内网服务。

  * 更轻量，部署简单
  * 适合快速把 Web、SSH、RDP 等服务暴露到外网
  * 配置文件一丢就能跑，不用折腾证书

一句话总结：
👉 OpenVPN 像是“把你拉进局域网”，而 frp 是“把局域网的一个口子掏给外网”。

---

## frp 适用场景

日常用下来，frp 特别适合这些情况：

* 临时或长期暴露内网服务（NAS、相机、家庭自动化、SSH 等）
* 开发者远程调试项目，不想搞复杂 VPN
* 在云服务器和家里/公司的机器之间建立一条稳定的“中转通道”

官方仓库在这 👉 [https://github.com/fatedier/frp](https://github.com/fatedier/frp)

---

## 类似的工具

除了 frp，其实还有不少工具能解决“内网穿透”问题：

* **ngrok**
  当年大火的神器，支持 HTTP/TCP/TLS，开箱即用。缺点是免费版有点受限，比如域名临时分配。

* **Serveo**
  不用装客户端，直接一条 SSH 命令就能把本地端口映射出去，轻量级的神器。

* **localtunnel**
  基于 Node.js，安装配置简单，适合做开发调试。

* **Tunnelmole**
  算是 localtunnel 的“后来者”，配置更简洁。

如果你追求 **企业级稳定性**，可以考虑：

* **Cloudflare Tunnel (Argo Tunnel)**：免费+安全，把服务挂在 Cloudflare CDN 上，省心。
* **ZeroTier / Tailscale**：虚拟组网方案，设备像在同一个虚拟局域网里。

---

## 一个 frp 小 Demo

场景：

* 三台主机
* 主机1 ↔ 主机2 可通
* 主机2 ↔ 主机3 可通
* 主机1 ❌ 主机3 不能通

解决办法：

* 主机2跑 frp server
* 主机3跑 frp client
* 主机1 就能通过主机2中转，访问到主机3 的 SSH

![cloud-service-frp-demo-preparation](/api/v1/website/image/cloud-service/cloud-service-frp-demo-preparation.png)

---

### 服务端配置

```bash
# frps.toml
bindPort = 7000
```

---

### 客户端配置

```bash
# frpc.toml
serverAddr = "192.168.10.230"
serverPort = 7000

[[proxies]]
name = "ssh"
type = "tcp"
localIP = "127.0.0.1"
localPort = 22
remotePort = 6000
```

---

### 效果

![cloud-service-frp-demo](/api/v1/website/image/cloud-service/cloud-service-frp-demo.png)

这样主机1只要连 `主机2:6000`，就能直接 SSH 到主机3。简单粗暴，秒搞定。

---

## 写在最后

frp 的定位就是“小巧好用的内网穿透工具”。如果你只是需要把某个端口暴露出去，frp 几乎是最轻量的方案。
当然，如果你需要更完整的网络打通，**VPN (OpenVPN/WireGuard)** 或 **SDN (ZeroTier/Tailscale)** 可能更合适。

工具没有绝对的好坏，关键还是看场景。