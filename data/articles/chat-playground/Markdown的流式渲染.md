---
author: admin@pldz1.com
category: chat-playground
csdn: 'https://blog.csdn.net/qq_42727752/article/details/145092638'
date: '2025-01-12'
gitee: ''
github: 'https://github.com/pldz1/demos/tree/main/sse_markdown'
juejin: 'https://juejin.cn/post/7458656534718316595'
serialNo: 2
status: publish
summary: 用 markdown-it 这个库在 HTML 上动态更新 markdown 内容(不是重新刷新).
tags:
- AIGC
- Playground
- SSE
- JavaScript
thumbnail: /api/v1/website/image/chat-playground/2_markdown_sse_thumbnail.png
title: Markdown的流式渲染
---

# 0️⃣ 前言

`GPT` 的流输出还是要渲染成 `markdown`, 网络上的教程还是蛮多的,个人打算用 `VUE3` 创建一个调用 `GPT` 的 `stream` 对话的网页,但是查阅了很多资料,**发现大部分的处理方法都是用`v-html`或者是`innerHTML`的强制刷新,这样导致文本在框选了的时候,就没有办法保证框选中的文本一直是标记的(因为这样会造成浏览器重新刷新一次内容), 但是`ChatGPT`的是动态递增的,是不会影响之前的内容的选中的**, 那么这里给出一个简单的这样的实现思路.

总的来说就是这个博客介绍一个 在 `HTML` 上**动态更新**markdown 内容(不是重新刷新)

## 🔍 开发平台

- 框架是 `VUE3` 和 `vite`
- `node` 版本是 `v20.15.1`
- `markdown` 渲染核心工具是`markdown-it`
- 参考了我之前用的做静态个人网页的项目的 `markdown` 的渲染方法: [VUE3_Static_Blog_WebSite](https://github.com/pldz1/VUE3_Static_Blog_WebSite)

## 😎 体验预览

👉 在线体验: [https://pldz1.github.io/\_codespace/sse_markdown/index.html](https://pldz1.github.io/_codespace/sse_markdown/index.html)

👉 下面的代码源码被放在了: [chat-playground/samples/sse_markdown](https://github.com/pldz1/chat-playground)

拉取下来输入 `npm run dev` 运行查看效果.

预览的效果如下所示:

![预览效果](/api/v1/website/image/chat-playground/2_sse_md_preview.gif)

# 1️⃣ 实现介绍

## 🏠 用到的库

`package.json` 如下所示:

```json
"clipboard": "^2.0.10",
"highlight.js": "^11.4.0",
"jquery": "^3.6.0",
"markdown-it": "^12.3.2",
"markdown-it-abbr": "^1.0.4",
"markdown-it-container": "^3.0.0",
"markdown-it-deflist": "^2.1.0",
"markdown-it-emoji": "^2.0.0",
"markdown-it-footnote": "^3.0.3",
"markdown-it-ins": "^3.0.1",
"markdown-it-mark": "^3.0.1",
"markdown-it-sub": "^1.0.0",
"markdown-it-sup": "^1.0.0",
"markdown-it-task-lists": "^2.1.1",
"markdown-it-toc": "^1.1.0",
"markdown-it-toc-done-right": "^4.2.0",
"@DatatracCorporation/markdown-it-mermaid": "npm:@datatraccorporation/markdown-it-mermaid@^0.5.0"
```

## 📻 用 JavaScript 模仿 SSE

JavaScript 模仿 SSE 的返回代码:

```js
export const codeContent = "xxxxxxxxxxxxxxxxxxxxxx";

/** SSE 生成器 */
export function* yieldContent() {
  let i = 0;
  while (i < codeContent.length) {
    // 随机生成 1 到 20 之间的数
    const chunkSize = Math.floor(Math.random() * 20) + 1;
    // 获取一个片段
    const chunk = codeContent.slice(i, i + chunkSize);
    yield chunk; // 一次性返回这部分字符
    i += chunkSize; // 更新索引，跳过已经返回的字符
    // 休眠 20ms
    yield new Promise((resolve) => setTimeout(resolve, 20));
  }
}
```

JavaScript 接收 SSE 的结果的例子:

```js
/** Step 1. 处理 SSE 返回的内容. */
const processStep = (generator) => {
  // 获取生成迭代对象
  const result = generator.next();

  // 生成器结束
  if (result.done) return;

  if (result.value instanceof Promise) {
    // 如果值是 Promise，等待它完成再继续
    result.value
      .then(() => {
        // 无意义的结果, 继续执行下一个步骤
        processStep(generator);
      })
      .catch((error) => {
        console.error("Error occurred during promise resolution:", error);
      });
  } else {
    // 将当前的部分内容加入队列进行渲染
    // 这个时候拿到的 result.value 是 string 是有意义的结果,用来处理具体逻辑
    // <ANY FUNCTION>(result.value);
    // Input your code under here.
    // ................
    //
    // 继续下一步
    processStep(generator);
  }
};

/** Step 0. 开始 SSE 模拟 */
const yieldedSSEContent = () => {
  const generator = yieldContent();
  // 开始处理生成器的每一步
  processStep(generator);
};
```

## 📕 markdown-it 插件配置

用法还是蛮简单的, 用 `use` 方法可以直接使用这个插件.

```js
import MarkdownIt from "markdown-it";
import emoji from "markdown-it-emoji";
import deflist from "markdown-it-deflist";
import abbr from "markdown-it-abbr";
import footnote from "markdown-it-footnote";
import ins from "markdown-it-ins";
import mark from "markdown-it-mark";
import taskLists from "markdown-it-task-lists";
import container from "markdown-it-container";
import toc from "markdown-it-toc-done-right";
import mermaid from "@DatatracCorporation/markdown-it-mermaid";

var config = {
  html: true,
  xhtmlOut: true,
  breaks: true,
  langPrefix: "lang-",
  linkify: false,
  typographer: true,
  quotes: "“”‘’",
};
let markdownIt = new MarkdownIt(config);

markdownIt
  .use(emoji)
  .use(deflist)
  .use(abbr)
  .use(footnote)
  .use(ins)
  .use(mark)
  .use(taskLists)
  .use(container)
  .use(container, "hljs-left")
  .use(container, "hljs-center")
  .use(container, "hljs-right")
  .use(toc)
  .use(mermaid);

export default markdownIt;
```

## 💼 Code Block 的渲染

这个主要是对要放入 `markdown` 内容的 `div` 的内容进行额外的样式处理

```js
import "highlight.js/styles/atom-one-dark.css";
import $ from "jquery";
import hljs from "highlight.js/lib/core";
import javascript from "highlight.js/lib/languages/javascript";
import vbscript from "highlight.js/lib/languages/vbscript";
import python from "highlight.js/lib/languages/python";
import matlab from "highlight.js/lib/languages/matlab";
import csharp from "highlight.js/lib/languages/csharp";
import shell from "highlight.js/lib/languages/shell";
import vhdl from "highlight.js/lib/languages/vhdl";
import java from "highlight.js/lib/languages/java";
import css from "highlight.js/lib/languages/css";
import xml from "highlight.js/lib/languages/xml";
import sql from "highlight.js/lib/languages/sql";
import cpp from "highlight.js/lib/languages/cpp";
import c from "highlight.js/lib/languages/c";
import ClipboardJS from "clipboard";

hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("vbscript", vbscript);
hljs.registerLanguage("python", python);
hljs.registerLanguage("matlab", matlab);
hljs.registerLanguage("csharp", csharp);
hljs.registerLanguage("shell", shell);
hljs.registerLanguage("vhdl", vhdl);
hljs.registerLanguage("java", java);
hljs.registerLanguage("html", xml);
hljs.registerLanguage("xml", xml);
hljs.registerLanguage("css", css);
hljs.registerLanguage("sql", sql);
hljs.registerLanguage("cpp", cpp);
hljs.registerLanguage("c", c);

hljs.configure({ ignoreUnescapedHTML: true });

/**
 * 高亮代码块
 * @param {Element} element 包含 pre code 代码块的元素
 */
function highlightCode(element) {
  const codeEls = element.querySelectorAll("pre code");
  codeEls.forEach((el) => {
    hljs.highlightElement(el);
  });
}

/**
 * 给代码块添加复制按钮
 * @param {Element} element 包含 pre code 代码块的元素
 */
function buildCopyButton(element) {
  let $pres = $(element).find("pre");
  if (!$pres.length) return;

  $pres.each(function () {
    var t = $(this).children("code").text();

    // 创建按钮
    var btn = $('<span class="copy">复制</span>').attr("data-clipboard-text", t);

    $(this).prepend(btn);

    var c = new ClipboardJS(btn[0]);
    c.on("success", function () {
      btn.addClass("copyed").text("复制成功");
      setTimeout(function () {
        btn.text("复制").removeClass("copyed");
      }, 1000);
    });
    c.on("error", function () {
      btn.text("复制失败");
    });
  });
}

/** 构建生成中的 markdown 的内容 */
export function buildCodeBlock(element) {
  highlightCode(element);
  buildCopyButton(element);
}
```

## ✨ 动态渲染 markdown

对比两个 `html div` 的 `DOM` 树, 对比各种属性和层级变化, 动态的更新

这个函数有一个硬代码, 因为 `root` 节点要被保护一下, 所以加入了判断里.

```js
/** 核心函数, 对比节点的内容 实现动态更新 markdown 的 div 而不是用 innerHTML 的属性全部刷新 */
export function deepCloneAndUpdate(div1, div2) {
  // 递归比较和更新 div1 和 div2 的子节点
  function compareAndUpdate(node1, node2) {
    // 情况 1：node1 是文本节点，更新文本内容
    if (node1 && node1.nodeType === Node.TEXT_NODE && node2.nodeType === Node.TEXT_NODE) {
      if (node1.nodeValue !== node2.nodeValue) {
        // 更新文本内容
        node1.nodeValue = node2.nodeValue;
      }
      return;
    }

    // 情况 2：node1 和 node2 的标签名不同，替换整个节点
    if (!node1 || node1.tagName !== node2.tagName) {
      // 克隆 node2 节点
      const newNode = node2.cloneNode(true);
      if (node1) {
        // 替换旧节点
        node1.parentNode.replaceChild(newNode, node1);
      } else {
        // 如果 node1 不存在，直接新增
        node2.parentNode.appendChild(newNode);
      }
      return;
    }

    // 情况 3：节点的 class 或其他属性更新, 注意对root节点的保护
    if (node1.className !== "article-content" && node1.className !== node2.className) {
      // 3.1 更新 className
      node1.className = node2.className;
    }

    // 3.2 对 id 的更新 注意对root节点的保护
    if (node1.id !== "article-content" && node1.id !== node2.id) {
      node1.id = node2.id;
    }

    //  3.3 对 style 的更新
    if (node1.style.cssText !== node2.style.cssText) {
      node1.style.cssText = node2.style.cssText;
    }

    // 情况 4：递归对比和更新子节点
    const children1 = Array.from(node1.childNodes); // node1 的所有子节点
    const children2 = Array.from(node2.childNodes); // node2 的所有子节点

    // 遍历 node2 的子节点，逐个与 node1 的对应子节点比较
    children2.forEach((child2, index) => {
      const child1 = children1[index];
      if (!child1) {
        // 如果 child1 不存在，直接克隆 child2 并添加到 node1
        const newChild = child2.cloneNode(true);
        node1.appendChild(newChild);
      } else {
        // 如果 child1 存在，递归比较和更新
        compareAndUpdate(child1, child2);
      }
    });

    // 删除 node1 中多余的子节点
    if (children1.length > children2.length) {
      for (let i = children2.length; i < children1.length; i++) {
        node1.removeChild(children1[i]);
      }
    }
  }

  // 从 div2 根节点开始与 div1 比较
  compareAndUpdate(div1, div2);
}
```

## 💡 主页渲染

主页渲染很重要, 因为要处理 `SSE` 的生成速度比 `markdown` 的动态渲染快, 要用异步队列来处理这个频率.

```html
<template>
  <div class="article-details">
    <div class="container">
      <button class="start-btn" @click="yieldedSSEContent">开始模仿SSE</button>
      <div class="post-body">
        <div class="article-content" id="article-content"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import markdownIt from "./module/markdown-it";
  import { deepCloneAndUpdate, buildCodeBlock } from "./module/code-block.js";
  import { yieldContent } from "./module/server.js";

  let htmlData = "";
  let el = null;
  let isRendering = false;
  const renderQueue = [];

  /** Step 4. 渲染markdown的 HTML Element. */
  const renderMarkdown = (data) => {
    if (!el) el = document.getElementById("article-content");
    if (!el) return;

    const tmpDiv = document.createElement("div");
    tmpDiv.innerHTML = markdownIt.render(data); // 只渲染当前的块
    buildCodeBlock(tmpDiv);

    // 这里不再拼接 htmlData，而是每次渲染独立的块
    deepCloneAndUpdate(el, tmpDiv);
  };

  /** Step 3. 处理异步渲染 */
  const processRenderQueue = () => {
    if (renderQueue.length === 0) {
      isRendering = false; // 队列为空时标记渲染完成
      return;
    }

    const data = renderQueue.shift(); // 获取并移除队列中的第一个渲染任务
    renderMarkdown(data); // 执行渲染操作

    // 继续处理下一个渲染任务
    setTimeout(processRenderQueue, 0);
  };

  /** Step 2. 异步队列控制渲染 */
  const enqueueRender = (data) => {
    htmlData += data;
    renderQueue.push(htmlData);
    // 如果当前没有渲染任务在进行，启动渲染队列
    if (!isRendering) {
      isRendering = true;
      processRenderQueue();
    }
  };

  /** Step 1. 处理 SSE 返回的内容. */
  const processStep = (generator) => {
    // 获取下一个值
    const result = generator.next();

    // 如果生成器结束，停止并设置 state 为 "done"
    if (result.done) {
      // 渲染生成器最后的值
      enqueueRender("");
      return;
    }

    if (result.value instanceof Promise) {
      // 如果值是 Promise，等待它完成再继续
      result.value
        .then(() => {
          // 继续执行下一个步骤
          processStep(generator);
        })
        .catch((error) => {
          console.error("Error occurred during promise resolution:", error);
        });
    } else {
      // 将当前的部分内容加入队列进行渲染
      enqueueRender(result.value);
      // 继续下一步
      processStep(generator);
    }
  };

  /** Step 0. 开始 SSE 模拟 */
  const yieldedSSEContent = () => {
    // 重置 Demo 的div
    const el = document.getElementById("article-content");
    if (el) {
      htmlData = "";
      el.innerHTML = "";
    }

    // 正式的 DEMO 开始, 获取生成器
    const generator = yieldContent();
    // 开始处理生成器的每一步
    processStep(generator);
  };
</script>
```

# ✏️ 总结

1. **性能优化：**

   - 使用 **生成器 (`yield`)** 和 **异步队列** 控制数据的分块渲染，避免一次性渲染过多内容导致卡顿。
   - 渲染过程中，通过 **`setTimeout`** 控制任务的执行频率，减轻浏览器渲染压力。

2. **动态节点对比：**
   - 通过 **`deepCloneAndUpdate`** 实现 DOM 节点的精准比较与更新，避免直接使用 `innerHTML`。该方法递归地比较并更新元素的文本、属性和子节点，最大限度减少不必要的 DOM 操作，提高性能。