---
title: 使用VUE3创建个人静态主页
category: CodeSpace_Blog
serialNo: 1
tags: [VUE3]
date: 2025-01-08
thumbnail: /images/CodeSpace_Blog/v3_sbw_static_website_thumbnail.png
summary: VUE3 来做这个静态的网站.
---

# 🌟 前言

作为开发者或者内容创作者，我们经常需要创建静态网页，用来展示个人博客、作品集，甚至是小型的文档网站。🎨

- **传统工具如 Jekyll、Hexo、Hugo 等很强大**：但是这些框架专注于静态站点生成，功能完善，但大多基于特定的模板语言或非前端框架，这对于大家有一些前端的基础，发现还是需要时间去了解这些工具。

- **VUE3 上手快入门简单** 所以用 VUE3 来做这个静态的网站管理 应该会很方便，主要是减少要学习技术栈 😂

---

# 😎 体验

👉 **项目源码: [VUE3 Static Blog WebSite](https://github.com/pldz1/VUE3_Static_Blog_WebSite)**

👉 **预览它造出来的 Git Page: [pldz1.github.io](https://pldz1.github.io)**

> **🎉 欢迎一起交流！💬 (⭐️ start 和 🍴 fork，感谢大家的支持！🙏)**

- 主页预览

![主页预览](/images/CodeSpace_Blog/v3_sbw_home_preview.gif)

- 博客页预览

![博客页预览](/images/CodeSpace_Blog/v3_sbw_preview_blog.gif)

# 🔨 具体实现

这个项目我在做的时候用的是 `node-v16` 因为里面有用到 `crypto` 这个库，对大于`17` 版本的`node`有加密的不一样的哈希报错

## ✨ 核心功能

1. **Markdown 支持** 📝  
   通过 `markdown-it` 这个 **Markdown 渲染库**将这些内容转成 HTML 并在页面中展示

2. **静态内容管理**
   博客文章内容和元数据（比如标题、作者、日期等）都被保存在 **JSON 文件** 页面加载时，项目会通过 `axios` 请求 直接拉取这些静态文件内容，但是条件是 你先执行了 `npm run update`的操作，这个操作也被写在了 `npm run serve`脚本里，目的是为了模仿 VUE3 的服务流程 把`public`当成服务器的开放资源位置，同时对博客内容加密（如果你在`.env`设置了要加密)

---

## 🏗️ 项目结构

- **`src/`**：主要代码的核心目录。
  - **`components/`**：复用组件（比如文章列表、导航等）。
  - **`views/`**：各页面视图组件，比如首页、文章详情页。
  - **`router/`**：定义路由规则的地方。
  - **`styles/`**：存放 SCSS 样式文件。
  - **`assets/`**：静态资源（图片、图标等）。
- **`public/`**：用于存博客资源。

## 🚀 用这个项目部署 Git Page

具体的操作 可以等待作者后续更新 参考例子: [https://pldz1.github.io](https://pldz1.github.io)

1. 创建一个 Git Page 的代码仓库: [creating-a-github-pages-site](https://docs.github.com/zh/pages/getting-started-with-github-pages/creating-a-github-pages-site)

2. 利用本项目打包出你自己的静态网页: `npm run build` 得到 `dist` 文件夹

3. 将 `dist` 文件夹的内容 全部拷贝到你的 Git Page 仓库, 注意检查是不是有 `.nojekyll` 文件, 这个文件必须存在, 表示我们 发布静态网页的工作流

4. 推送到你的远程 Git Page 仓库

5. 配置你的 Git Page 仓库的 `settings`, 其实就是直接打开 Git Page 这个选项, [configuring-a-publishing-source-for-your-github-pages-site](https://docs.github.com/zh/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)

6. 等待 流程跑完 几分钟后 查看你的 `https:/xxxx.github.io` 😎

---

# 📖 参考

- 参考了 GitHub 项目： [https://github.com/zhiyiYo/KilaKila-Blog](https://github.com/zhiyiYo/KilaKila-Blog)

---
