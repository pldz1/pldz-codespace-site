---
author: admin@pldz1.com
category: chat-playground
csdn: 'https://blog.csdn.net/qq_42727752/article/details/145082786'
date: '2025-01-11'
gitee: ''
github: 'https://github.com/pldz1/demos/tree/main/learn_chat_image_api'
juejin: 'https://juejin.cn/post/7458496437614788646'
serialNo: 1
status: publish
summary: 前言 JS 和 Python 是比较受欢迎的两个调用 OpenAI 对话 API 的两个库, 这里 简单记录这两个库对 OpenAI 的对话(Chat)和图像(Image)的使用.
tags:
- AIGC
- Playground
- Python
- JavaScript
thumbnail: /api/v1/website/image/chat-playground/1_chat_image_api_thumbnail.png
title: 对话和图像API简单体验
---

# 前言

JS 和 Python 是比较受欢迎的两个调用 OpenAI 对话 API 的两个库, 这里 简单记录这两个库对 OpenAI 的对话(Chat)和图像(Image)的使用.

使用上这里会包括原生的 `OpenAI API` 和 `Azure OpenAI API` 两个使用例子.

> `JavaScrip` 在网络设置和后端平台开发上不如 `Python` 方便,但是我们的 `chat-playground` 的项目是一个前后端的项目,未来能够在网页上有一个好的体验,并且尽量分离前后端,所以这个项目的请求优先用`JavaScrip`

- 下面的例子 `node` 版本: `v16.20.2`, `Python` 的版本是 `3.10.12`

## OpenAI API 对话和图像接口

### Python

首先 `pip3 install openai`

直接看代码吧 代码比较简单

```py
import httpx
import asyncio
from openai import OpenAI

proxy_url = "http://xxxx:xxxx"
api_key = "xxxx"


def use_proxy():
    http_client = None
    if(not proxy_url):
        http_client = httpx.Client()
        return http_client

    http_client = httpx.Client(proxies={'http://': proxy_url, 'https://': proxy_url})
    return http_client



'''
# ===== 非流式的对话测试 =====
'''
async def no_stream_chat():
    http_client = use_proxy()
    client = OpenAI(api_key=api_key,http_client=http_client)

    # 请求
    results = client.chat.completions.create(model= "gpt-4o-mini", messages=[{"role": "user", "content": [{"type": "text", "text": "Hello?"}]}])
    print(results.choices[0].message.content)


'''
# ===== 流式的对话测试 =====
'''
async def stream_chat():
    http_client = use_proxy()
    client = OpenAI(api_key=api_key,http_client=http_client)

    # 请求
    results = client.chat.completions.create(model= "gpt-4o-mini", messages=[{"role": "user", "content": [{"type": "text", "text": "Hello?"}]}], stream=True)

    for chunk in results:
        choice = chunk.choices
        if choice == []:
            continue

        content = choice[0].delta.content
        print(content)

'''
# ===== 生成图像的函数 =====
'''
async def gen_dell3_pic():
    http_client = use_proxy()
    client = OpenAI(api_key=api_key,http_client=http_client)

    # 请求
    results = client.images.generate(model="dall-e-3", prompt="A cute cat")
    print(results.data[0].url)



if __name__ == "__main__":
    asyncio.run(no_stream_chat())
    asyncio.run(stream_chat())
    asyncio.run(gen_dell3_pic())
```

### JavaScript

首先安装包 `npm install openai https-proxy-agent --save`

再配置 `package.json` 支持 `ES6` 如下:

```json
{
  "type": "module",
  "dependencies": {
    "https-proxy-agent": "^7.0.6",
    "openai": "^4.78.1"
  }
}
```

同样也直接看代码算了

```js
import { OpenAI } from "openai";

const proxyUrl = "http://xxxx:xxx";
const apiKey = "xxxxxxxxxxxxxxxxxxxxxxxxxxxx";

/** 配置网络设置 */
async function useProxy(client) {
  if (!proxyUrl) return;

  // 动态导入 https-proxy-agent 模块
  const { HttpsProxyAgent } = await import("https-proxy-agent");

  // 使用 HttpsProxyAgent
  const agent = new HttpsProxyAgent(proxyUrl);

  const originalFetchWithTimeout = client.fetchWithTimeout;

  client.fetchWithTimeout = async (url, init, ms, controller) => {
    const { signal, ...options } = init || {};
    if (signal) signal.addEventListener("abort", () => controller.abort());

    const timeout = setTimeout(() => controller.abort(), ms);

    const fetchOptions = {
      signal: controller.signal,
      ...options,
      agent: agent,
    };
    if (fetchOptions.method) {
      // Custom methods like 'patch' need to be uppercased
      fetchOptions.method = fetchOptions.method.toUpperCase();
    }

    try {
      return await originalFetchWithTimeout.call(client, url, fetchOptions, ms, controller);
    } finally {
      clearTimeout(timeout);
    }
  };
}

/** ===== 非流式的对话测试 ===== */
async function noStreamChat() {
  const client = new OpenAI({ apiKey, timeout: 5000 });
  await useProxy(client);

  // 请求
  const results = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: [{ type: "text", text: "Hello?" }] }],
  });

  for (const choice of results.choices) {
    console.log(choice.message);
  }
}

/** ===== 流式的对话测试 ===== */
async function streamChat() {
  const client = new OpenAI({ apiKey, timeout: 5000 });
  await useProxy(client);

  // 请求
  const results = await client.chat.completions.create({
    model: "gpt-4o-mini",
    messages: [{ role: "user", content: [{ type: "text", text: "Hello?" }] }],
    stream: true,
  });

  for await (const chunk of results) {
    console.log(chunk.choices[0]?.delta?.content || "");
  }
}

/** ===== 图片请求 ===== */
async function genDell3Pic() {
  const client = new OpenAI({ apiKey, timeout: 60000 });
  await useProxy(client);

  // 请求
  const results = await client.images.generate({
    model: "dall-e-3",
    prompt: "cute cat",
  });
  console.log(results.data[0].url);
}

/** ===== 测试主函数 ===== */
async function main() {
  await noStreamChat();
  await streamChat();
  await genDell3Pic();
}

main().catch((err) => {
  console.error("The sample encountered an error:", err);
});
```

## Azure OpenAI API 对话和图像接口

### Python

装依赖 `pip3 install openai` 看代码

```py
import httpx
import asyncio
from openai import AzureOpenAI

proxy_url = ""
azure_endpoint = "xxxxxxxxxxxxxxxx"
api_key = "xxxxxxxxxxxxxxxx"
chat_deployment = "xxxxxx"
image_deployment = "xxxxxxx"

def use_proxy():
    http_client = None
    if(not proxy_url):
        http_client = httpx.Client()
        return http_client

    http_client = httpx.Client(proxies={'http://': proxy_url, 'https://': proxy_url})
    return http_client



'''
# ===== 非流式的对话测试 =====
'''
async def no_stream_chat():
    deployment = chat_deployment
    api_version = "2024-05-01-preview"
    http_client = use_proxy()
    client = AzureOpenAI(azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version, http_client=http_client)

    # 请求
    results = client.chat.completions.create(model=deployment, messages=[{"role": "user", "content": [{"type": "text", "text": "Hello?"}]}])
    print(results.choices[0].message.content)


'''
# ===== 流式的对话测试 =====
'''
async def stream_chat():
    deployment = chat_deployment
    api_version = "2024-05-01-preview"
    http_client = use_proxy()
    client = AzureOpenAI(azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version, http_client=http_client)

    # 请求
    results = client.chat.completions.create(model=deployment, messages=[{"role": "user", "content": [{"type": "text", "text": "Hello?"}]}], stream=True)

    for chunk in results:
        choice = chunk.choices
        if choice == []:
            continue

        content = choice[0].delta.content
        print(content)

'''
# ===== 生成图像的函数 =====
'''
async def gen_dell3_pic():
    deployment = image_deployment
    api_version = "2024-05-01-preview"
    http_client = use_proxy()
    client = AzureOpenAI(azure_endpoint=azure_endpoint, api_key=api_key, api_version=api_version, http_client=http_client)

    # 请求
    results = client.images.generate(model=deployment, prompt="cute cat")
    print(results.data[0].url)



if __name__ == "__main__":
    asyncio.run(no_stream_chat())
    asyncio.run(stream_chat())
    asyncio.run(gen_dell3_pic())
```

### JavaScript

安装包 `npm install openai https-proxy-agent --save`, 再配置 `package.json` 如下:

```json
{
  "type": "module",
  "dependencies": {
    "https-proxy-agent": "^7.0.6",
    "openai": "^4.78.1"
  }
}
```

直接看代码吧:

```js
import { AzureOpenAI } from "openai";

const proxyUrl = "";
const endpoint = "xxxxxxxxx";
const apiKey = "xxxxxxxxx";
const chatDeployment = "xxx";
const dellDelpoyment = "xxxxxx";

/** 配置网络设置 */
async function useProxy(client) {
  if (!proxyUrl) return;

  // 动态导入 https-proxy-agent 模块
  const { HttpsProxyAgent } = await import("https-proxy-agent");

  // 使用 HttpsProxyAgent
  const agent = new HttpsProxyAgent(proxyUrl);

  const originalFetchWithTimeout = client.fetchWithTimeout;

  client.fetchWithTimeout = async (url, init, ms, controller) => {
    const { signal, ...options } = init || {};
    if (signal) signal.addEventListener("abort", () => controller.abort());

    const timeout = setTimeout(() => controller.abort(), ms);

    const fetchOptions = {
      signal: controller.signal,
      ...options,
      agent: agent,
    };
    if (fetchOptions.method) {
      // Custom methods like 'patch' need to be uppercased
      fetchOptions.method = fetchOptions.method.toUpperCase();
    }

    try {
      return await originalFetchWithTimeout.call(client, url, fetchOptions, ms, controller);
    } finally {
      clearTimeout(timeout);
    }
  };
}

/** ===== 非流式的对话测试 ===== */
async function noStreamChat() {
  const deployment = chatDeployment;
  const apiVersion = "2024-05-01-preview";
  const client = new AzureOpenAI({ endpoint, apiKey, apiVersion, deployment });
  useProxy(client);

  // 请求
  const results = await client.chat.completions.create({
    messages: [{ role: "user", content: [{ type: "text", text: "Hello?" }] }],
  });

  for (const choice of results.choices) {
    console.log(choice.message);
  }
}

/** ===== 流式的对话测试 ===== */
async function streamChat() {
  const apiVersion = "2024-05-01-preview";
  const deployment = chatDeployment;
  const client = new AzureOpenAI({ endpoint, apiKey, apiVersion, deployment });
  useProxy(client);

  // 请求
  const results = await client.chat.completions.create({
    messages: [{ role: "user", content: [{ type: "text", text: "Hello?" }] }],
    stream: true,
  });

  for await (const chunk of results) {
    console.log(chunk.choices[0]?.delta?.content || "");
  }
}

/** ===== 图片请求 ===== */
async function genDell3Pic() {
  // The prompt to generate images from
  const deployment = dellDelpoyment;
  const apiVersion = "2024-04-01-preview";
  const client = new AzureOpenAI({ endpoint, apiKey, apiVersion, deployment });
  useProxy(client);

  // 请求
  const results = await client.images.generate({ prompt: "cute cat" });
  console.log("image.url :", results.data[0].url);
}

/** ===== 测试主函数 ===== */
async function main() {
  await noStreamChat();
  await streamChat();
  await genDell3Pic();
}

main().catch((err) => {
  console.error("The sample encountered an error:", err);
});
```

## 总结

1. 对于 `JavaScript` 的代码在配置网络时候需要对原来的 `fetch` 的参数进行复写, 虽然 `openai` 的 `npm` 的包时候提供了传入自定义的 `fetch` 的值, 但是我测试发现这个传入对返回的 `response` 要做一些处理, 暂时这样操作.

2. `Python` 的库直接用 `httpx` 直接定义网络设置, 还是比较方便的.

3. 后续再介绍其他的接口.