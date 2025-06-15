---
author: admin@pldz1.com
category: chat-playground
date: '2025-02-01'
serialNo: 3
status: publish
summary: 简单的Python全代理服务器:支持 HTTP 和 WebSocket 请求转发。通过aiohttp库实现异步处理，有效支持高并发请求，适用于需要代理服务的场景.
tags:
- Python
- WEB
- HTTP
thumbnail: /api/v1/website/image/chat-playground/3_pyproxy_thumbnail.png
title: Python代理服务器
---

# 0️⃣ 前言

因为在做 aigc 的服务免不了出现代理的情况, 所以用 Python 的 `aiohttp` 库来实现一个简单的全代理服务器。这个代理服务器能够同时处理 `HTTP` 请求和 `WebSocket` 连接

**😎 快速体验**

👉 下面的代码源码被放在了: [chat-playground/samples/python_proxy](https://github.com/pldz1/chat-playground)

# 1️⃣ 实现介绍

完整的代码如下：

```python

import asyncio
from aiohttp import web, ClientSession, WSMsgType
from urllib.parse import urlparse

# 定义真实目标主机（请根据需要修改
DEFM = "defm/"

# 按照 RFC 要求，需要过滤一些跳过传递的头部
HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}

async def proxy_handler(request: web.Request) -> web.StreamResponse:
    """
    根据请求类型选择 HTTP 代理或 WebSocket 代理
    """
    if request.headers.get("Upgrade", "").lower() == "websocket":
        return await websocket_handler(request)
    else:
        return await http_handler(request)

async def http_handler(request: web.Request) -> web.StreamResponse:
    """
    处理普通 HTTP 请求（包括 SSE 流）。
    将请求转发给目标服务器，并以流的方式将响应转发给客户端。
    """
    # 构造目标 URL（包括 path 和 query string）
    target_url = TARGET + request.rel_url.raw_path
    if request.rel_url.query_string:
        target_url += "?" + request.rel_url.query_string

    # 防止路径拼接时出现连续的双斜杠
    target_url = target_url.replace("defm/", "")
    # print(target_url)

    # 构造转发时使用的请求头（过滤掉 hop-by-hop 头部）
    headers = {}
    for name, value in request.headers.items():
        if name.lower() not in HOP_HEADERS:
            headers[name] = value

    # 将 Host 头改为目标主机
    parsed_target = urlparse(TARGET)
    headers["Host"] = parsed_target.netloc
    ## ===== 这下面可以写你的header的信息 ============
    # header['api-key'] = "hello-world"
    # headers['Authorization'] = f"Bearer hello-world"
    # print(headers)

    # 读取客户端请求体（如果有的话）
    body = await request.read()

    async with ClientSession() as session:
        async with session.request(
            request.method,
            target_url,
            headers=headers,
            data=body,
            allow_redirects=False
        ) as resp:
            # 使用 StreamResponse 实现流式转发，适合 SSE 或大文件下载
            proxy_response = web.StreamResponse(status=resp.status, reason=resp.reason)
            # 复制响应头（排除 hop-by-hop 头）
            for name, value in resp.headers.items():
                if name.lower() not in HOP_HEADERS:
                    proxy_response.headers[name] = value
            await proxy_response.prepare(request)
            async for chunk in resp.content.iter_chunked(1024):
                await proxy_response.write(chunk)
            await proxy_response.write_eof()
            return proxy_response

async def websocket_handler(request: web.Request) -> web.WebSocketResponse:
    """
    处理 WebSocket 连接。将客户端和目标服务器之间的数据进行双向转发。
    """
    ws_server = web.WebSocketResponse()
    await ws_server.prepare(request)

    # 将 http(s) 协议转换为 ws(s) 协议
    if TARGET.startswith("https://"):
        ws_target = TARGET.replace("https://", "wss://")
    elif TARGET.startswith("http://"):
        ws_target = TARGET.replace("http://", "ws://")
    else:
        ws_target = TARGET
    ws_target += str(request.rel_url)

    # 防止路径拼接时出现连续的双斜杠
    ws_target = ws_target.replace('//', '/')

    # 如果客户端请求中包含子协议，可以获取并转发
    protocols = request.headers.getall("Sec-WebSocket-Protocol", [])

    async with ClientSession() as session:
        async with session.ws_connect(ws_target, protocols=protocols) as ws_client:
            async def ws_forward(ws_from, ws_to):
                async for msg in ws_from:
                    if msg.type == WSMsgType.TEXT:
                        await ws_to.send_str(msg.data)
                    elif msg.type == WSMsgType.BINARY:
                        await ws_to.send_bytes(msg.data)
                    elif msg.type == WSMsgType.CLOSE:
                        await ws_to.close()
                    elif msg.type == WSMsgType.ERROR:
                        break

            # 使用 asyncio.gather 同时转发双向数据
            await asyncio.gather(
                ws_forward(ws_server, ws_client),
                ws_forward(ws_client, ws_server)
            )
    return ws_server

def main():
    app = web.Application()
    # 捕获所有以 /defm 开头的 URL 路径
    app.router.add_route("*", "/defm/{tail:.*}", proxy_handler)
    web.run_app(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()


```

## 关键点

1. **跳过传递的头部**  
   根据 RFC 规定，有些 HTTP 头部字段在代理转发时需要被忽略，比如 `Connection` 和 `Transfer-Encoding` 等。为了确保代理服务器符合标准，我们需要在处理请求和响应时过滤掉这些头部字段。

2. **HTTP 请求处理**  
   对于常规的 HTTP 请求，代理服务器会将请求转发给目标服务器，然后将响应流式转发给客户端。这对于长连接或流媒体数据（如 SSE）非常适用。

3. **WebSocket 连接处理**  
   对于 WebSocket 请求，代理服务器会通过升级连接，将 WebSocket 数据从客户端和目标服务器之间进行双向转发。

## 1. 过滤跳过的头部

```python
HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
}
```

这部分不会被转发到目标服务器。

## 2. 代理处理函数

```python
async def proxy_handler(request: web.Request) -> web.StreamResponse:
    if request.headers.get("Upgrade", "").lower() == "websocket":
        return await websocket_handler(request)
    else:
        return await http_handler(request)
```

`proxy_handler` 根据请求的类型（WebSocket 或 HTTP）选择不同的处理函数。

## 3. HTTP 请求转发

`http_handler` 函数处理 HTTP 请求，将客户端请求转发到目标 URL，同时将响应流式返回给客户端。

## 4. WebSocket 转发

`websocket_handler` 函数处理 WebSocket 请求，并将客户端和目标服务器之间的 WebSocket 数据进行双向转发。

## 5. 启动应用

```python
def main():
    app = web.Application()
    app.router.add_route("*", "/defm/{tail:.*}", proxy_handler)
    web.run_app(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main()
```

`main` 函数创建并运行一个 aiohttp 应用，代理服务器会监听 `127.0.0.1:8000`，并处理所有以 `/defm` 开头的请求。

# 后续优化

- 可以添加日志记录、请求缓存等功能来增强性能和可维护性。
- 支持更多的 HTTP 请求方法，如 `PATCH` 或 `OPTIONS` 等。
- 可以进一步优化错误处理和异常捕获。