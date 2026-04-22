# pldz-dev-site

`pldz-dev-site` 是支撑 `pldz1.com` 的个人开发空间网站源码

## 项目定位

这个仓库目前承载的产品形态可以理解为：

- 个人首页：展示最近文章、项目教程、Demo、更新记录和个人入口。
- 教程/文章系统：基于 `data/articles/**/*.md` 的 Markdown + frontmatter 内容系统。
- 文章详情页：支持 Markdown 渲染、代码高亮、代码复制、目录锚点、上一篇/下一篇、评论。
- Code Space 页面：展示可预览的项目、Demo、源码链接和预览图。
- 白板页面：通过三位数字密钥临时共享文本内容。
- 管理后台：管理用户、图片、导航、横幅 配置和缓存资源。
- 登录/注册系统：基于 Cookie 中 JWT 的登录态。
- 资源服务：通过 API 读取图片、协议文本、缓存文件和站点配置。
- Demo 模板服务：当前包含 `sse-markdown` 的独立静态 Demo 服务。

## 技术栈

### 前端

- Vue `3.5.x`
- Vue Router `4.5.x`
- Vuex `4.1.x`
- Vite `6.3.x`
- marked：Markdown 解析
- highlight.js：代码块高亮
- Toastify：轻量 toast 提示
- 原生 Fetch / XMLHttpRequest：API 请求与上传进度

前端源码位于 `web/`，主要入口是：

- `web/src/main.js`
- `web/src/App.vue`
- `web/src/routers/index.js`
- `web/src/store/index.js`
- `web/src/utils/apis/*.js`
- `web/src/views/*.vue`

### 后端

- Python `3.11`
- FastAPI
- Uvicorn
- python-frontmatter
- watchdog
- PyJWT
- passlib + bcrypt
- python-dotenv
- python-multipart
- Pillow：图片压缩、缩放和 WebP/GIF 动图处理

后端源码位于 `server/`，主要入口是：

- `server/main.py`
- `server/routes/app.py`
- `server/core/config.py`
- `server/scripts/filesystem/website/article_watchdog.py`
- `server/scripts/db/connection.py`

### 部署

- Dockerfile：构建 Python 后端运行环境。
- docker-compose.yaml：同时启动 backend 与 nginx。
- Nginx：提供前端静态文件、反代 `/api/`、反代 `/io/sse-markdown`。
- 本地数据目录：`data/` 通过 volume 挂载到容器内，方便内容持久化。

## 顶层目录说明

```text
.
├── data/                      # 内容、图片、资源配置、缓存、JSON 数据库、模板产物
├── cache/                     # 图片缩放压缩后的本地缓存，运行时自动生成
├── nginx/                     # Nginx 主配置和站点配置
├── server/                    # FastAPI 后端
├── web/                       # Vue 3 前端工程
├── Dockerfile                 # backend 镜像构建文件
├── docker-compose.yaml        # backend + nginx 编排
├── entrypoint.sh              # 容器内多进程启动脚本
├── requirements.txt           # Python 依赖
├── .env.example               # 环境变量示例
└── README.md                  # 当前文档
```

## 运行模式总览

项目有两种常用运行方式。

### 方式一：Docker Compose 集成运行

这是当前仓库最接近线上形态的运行方式。

```bash
cp .env.example .env
docker compose up --build
```

启动后：

- 浏览器访问 `http://127.0.0.1:10058`
- Nginx 监听宿主机 `10058`
- Nginx 把 `/api/` 代理到 backend 容器内 `10057`
- Nginx 把 `/io/sse-markdown` 代理到 backend 容器内 `10078`
- backend 容器通过 `entrypoint.sh` 同时启动：
  - `python data/templates/sse-markdown/main.py`
  - `python server/main.py`

### 方式二：本地前后端分开开发

后端：

```bash
cp .env.example .env
pip install -r requirements.txt
python server/main.py
```

默认后端监听：

```text
SITE_HOST=127.0.0.1
SITE_PORT=10058
```

前端：

```bash
cd web
npm install
npm run dev
```

Vite 默认监听：

```text
http://127.0.0.1:10060
```

Vite 开发服务器会把 `^/(api|io)` 代理到：

```text
http://127.0.0.1:10058
```

## 端口约定

| 端口    | 使用者                        | 说明                                                     |
| ------- | ----------------------------- | -------------------------------------------------------- |
| `10058` | 宿主机 Nginx 或本地 FastAPI   | Docker 模式下是 Nginx 暴露端口；本地后端默认也用这个端口 |
| `10057` | Docker backend 中的主 FastAPI | Compose 通过环境变量覆盖 `SITE_PORT=10057`               |
| `10060` | Vite dev server               | 本地前端开发端口                                         |
| `10078` | sse-markdown Demo 服务        | `data/templates/sse-markdown/main.py`                    |

## 环境变量

`.env.example` 中定义了项目所需的运行配置。

```dotenv
ARTICLES_PATH=data/articles
IMAGES_PATH=data/images
TEMPLATES_PATH=data/templates
RESOURCES_PATH=data/resources
CACHE_PATH=data/cache
DB_PATH=data/db

SECRET_KEY=your-super-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=3600
REFRESH_TOKEN_EXPIRE_DAYS=7

ADMIN_USERNAME=admin@pldz1.com
ADMIN_PASSWORD=123

SITE_HOST=127.0.0.1
SITE_PORT=10058
SITE_NAME=爬楼的猪 Dev
SITE_COPYRIGHT=©2026 pldz1.com
SITE_ICP=京ICP备: 180xxxxx号-x
SITE_PS=京公网安备11xxxxxxxx9号
```

后端启动时会调用 `ProjectConfig.load_env()`：

- 自动定位项目根目录。
- 从项目根目录读取 `.env`。
- 如果 `.env` 不存在，后端会直接退出。
- 所有相对路径最终都会转换为项目根目录下的绝对路径。

关键路径的含义：

| 环境变量         | 默认值            | 作用                         |
| ---------------- | ----------------- | ---------------------------- |
| `ARTICLES_PATH`  | `data/articles`   | Markdown 文章目录            |
| `IMAGES_PATH`    | `data/images`     | 图片根目录                   |
| `TEMPLATES_PATH` | `data/templates`  | 前端构建产物和 Demo 模板目录 |
| `RESOURCES_PATH` | `data/resources`  | 导航、广告、协议等资源配置   |
| `CACHE_PATH`     | `data/cache`      | 管理后台缓存资源目录         |
| `DB_PATH`        | `data/db`         | JSON 数据库目录              |
| `SECRET_KEY`     | 无安全默认值      | JWT 签名密钥                 |
| `ADMIN_USERNAME` | `admin@pldz1.com` | 管理员账号                   |
| `ADMIN_PASSWORD` | `123`             | 管理员密码                   |
| `SITE_HOST`      | `127.0.0.1`       | FastAPI 绑定地址             |
| `SITE_PORT`      | `10058`           | FastAPI 绑定端口             |

## 后端启动流程

入口文件是 `server/main.py`。

启动顺序：

1. 加载 `.env`。
2. 初始化日志。
3. 开启文章目录 watchdog 线程。
4. 初始化管理员账号。
5. 启动 FastAPI 应用。

伪流程：

```text
server/main.py
  -> ProjectConfig.load_env()
  -> Logger.init_logger()
  -> threading.Thread(target=start_watch, daemon=True).start()
  -> AuthorizedHandler.init_admin()
  -> run_dev()
```

`run_dev()` 会：

- 启用 CORS。
- 允许所有 origin 正则。
- 允许携带 Cookie。
- 使用 `SITE_HOST` 和 `SITE_PORT` 启动 Uvicorn。

## FastAPI 路由总览

所有业务 API 都挂在 `/api/v1` 下。

```text
/api/v1/authorization/*
/api/v1/resource/*
/api/v1/website/article/*
/api/v1/website/image/*
/api/v1/website/comment/*
/api/v1/website/whiteboard/*
/api/v1/website/livedemo/*
```

### 通用响应格式

前端的 `apiRequest()` 默认假设后端返回：

```json
{
  "data": "..."
}
```

因此大多数 API 只会把 `payload.data` 返回给调用者。

如果后端返回非 `2xx`，前端当前会：

- 输出 debug 日志。
- 返回 `null`。

如果 JSON 解析失败，前端当前会：

- 输出错误日志。
- 返回 `null`。

## API 规格

### 授权与用户

Router:

```text
prefix = /api/v1/authorization
```

| 方法   | 路径                     | 权限          | 请求体                             | 返回                                        |
| ------ | ------------------------ | ------------- | ---------------------------------- | ------------------------------------------- |
| `GET`  | `/privacy`               | 公开          | 无                                 | `{ icp, copyright, ps }`                    |
| `POST` | `/login`                 | 公开          | `{ username, password }`           | `{ flag, user fields, log }`，并写入 Cookie |
| `POST` | `/register`              | 公开          | `{ username, password, nickname }` | `{ flag, user fields, log }`，并写入 Cookie |
| `GET`  | `/logout`                | 登录态可选    | 无                                 | `true`，并删除 Cookie                       |
| `POST` | `/refresh`               | refresh token | 无                                 | 新 access token 和用户信息                  |
| `POST` | `/update/avatar`         | 登录用户      | `{ avatar }`                       | `{ flag, log }`                             |
| `GET`  | `/usermanagement/all`    | 管理员        | 无                                 | `{ flag, data: users, log }`                |
| `POST` | `/usermanagement/delete` | 管理员        | `{ username }`                     | `{ flag, log }`                             |

登录态机制：

- 登录成功后设置 `access_token` 和 `refresh_token` Cookie。
- Cookie 属性：`httponly`, `samesite=lax`。
- `access_token` 用于普通鉴权。
- `refresh_token` 用于刷新访问令牌。
- 登出时会把 refresh token 标记为黑名单。

当前用户对象公开字段大致包括：

```json
{
  "id": "...",
  "username": "...",
  "raw_password": "...",
  "nickname": "...",
  "avatar": "...",
  "isadmin": true
}
```

注意：`password`、`token`、`blacklisted` 会在读取用户时被剔除。

### 协议、隐私与缓存资源

Router:

```text
prefix = /api/v1/resource
```

| 方法   | 路径              | 权限   | 请求体         | 返回         |
| ------ | ----------------- | ------ | -------------- | ------------ |
| `GET`  | `/privacy_policy` | 公开   | 无             | HTML 页面    |
| `GET`  | `/user_agreement` | 公开   | 无             | HTML 页面    |
| `GET`  | `/cache/all`      | 管理员 | 无             | 缓存文件列表 |
| `POST` | `/cache/download` | 管理员 | `{ filename }` | 文件下载     |
| `POST` | `/cache/delete`   | 管理员 | `{ filename }` | `true/false` |
| `POST` | `/cache/upload`   | 管理员 | multipart file | `true/false` |

协议文件来源：

```text
data/resources/privacy_policy.txt
data/resources/user_agreement.txt
```

缓存文件来源：

```text
data/cache
```

### 文章

Router:

```text
prefix = /api/v1/website/article
```

| 方法  | 路径                        | 权限 | 返回             |
| ----- | --------------------------- | ---- | ---------------- |
| `GET` | `/all/category`             | 公开 | 所有分类名       |
| `GET` | `/all/article`              | 公开 | 所有非导读文章   |
| `GET` | `/all/intro`                | 公开 | 所有导读文章     |
| `GET` | `/all/tag`                  | 公开 | 标签及文章数量   |
| `GET` | `/id/{article_id}`          | 公开 | 单篇文章完整内容 |
| `GET` | `/tag/{tag_name}`           | 公开 | 指定标签下的文章 |
| `GET` | `/category/{category_name}` | 公开 | 指定分类下的文章 |

文章列表返回的统一字段：

```json
{
  "id": "article id",
  "title": "标题",
  "category": "分类",
  "summary": "摘要",
  "serialNo": 1,
  "thumbnail": "/api/v1/website/image/category/name.png",
  "tags": ["tag"],
  "views": 0,
  "date": "2025-01-01",
  "path": "category/file.md",
  "csdn": "",
  "juejin": "",
  "github": "",
  "gitee": ""
}
```

单篇文章返回额外包含：

```json
{
  "content": "Markdown 正文"
}
```

读取单篇文章时，后端会：

- 在 `data/db/articles.json` 中把该文章 `views + 1`。
- 再从对应 Markdown 文件中读取正文内容。

### 图片

Router:

```text
prefix = /api/v1/website/image
```

| 方法   | 路径                                   | 权限     | 请求体                               | 返回                       |
| ------ | -------------------------------------- | -------- | ------------------------------------ | -------------------------- |
| `GET`  | `/{category}/{image}`                  | 公开     | 无                                   | 默认 `128x128` 压缩图片    |
| `GET`  | `/{category}/{image}@original`         | 公开     | 无                                   | 原始图片文件               |
| `GET`  | `/{category}/{image}@raw`              | 公开     | 无                                   | 原始图片文件               |
| `GET`  | `/{category}/{image}@{size}`           | 公开     | 无                                   | 宽高同值的压缩图片         |
| `GET`  | `/{category}/{image}@{width}x{height}` | 公开     | 无                                   | 指定尺寸压缩图片           |
| `POST` | `/category/all`                        | 管理员   | `{ category }`                       | 指定分类下图片文件名列表   |
| `POST` | `/rename`                              | 管理员   | `{ category, oldName, newName }`     | `{ flag, new_name }`       |
| `POST` | `/delete`                              | 管理员   | `{ category, name }`                 | `{ flag }`                 |
| `POST` | `/upload/avatar`                       | 登录用户 | multipart `file`, `name`             | `{ flag, url }`            |
| `POST` | `/upload/article`                      | 登录用户 | multipart `file`, `category`, `name` | `{ flag, url }`            |
| `POST` | `/upload/check`                        | 登录用户 | `{ category, name }`                 | `true/false`，表示是否可用 |

图片读取接口会默认压缩输出：

- 不带尺寸时默认按 `128x128` 等比缩放。
- `@original` 或 `@raw` 返回原始文件，不进行缩放、压缩和格式转换。
- `@1024` 表示宽高都按 `1024` 处理。
- `@1024x768` 表示按指定宽高处理。
- JPG / PNG / WEBP 等普通图片会保持比例缩放，不拉伸，默认输出 WebP。
- GIF 会逐帧缩放，并重新保存为 animated WebP，保留原动画帧间隔。
- 响应头包含 `Cache-Control: public, max-age=86400`。

可选 query 参数：

```text
quality=80
format=webp|jpeg
```

如果未显式传 `format`，后端会根据请求头 `Accept` 判断是否返回 WebP；不支持 WebP 的普通图片请求会返回 JPEG。GIF 为了保留动画，会统一返回 animated WebP。

尺寸限制：

- 宽高必须是合法正整数。
- 单边最大 `2000`。
- 非法尺寸、非法质量、非法格式返回 `400`。

图片实际存储在：

```text
data/images/{category}/{filename}
```

压缩后的图片会缓存在项目根目录：

```text
data/webp/{image_id}_{width}x{height}.webp
```

默认质量为 `80`，缓存存在时会直接返回缓存文件，不再处理原图。

头像固定使用：

```text
data/images/avatar
```

图片读取有路径保护：

- 通过 `os.path.abspath()` 计算真实路径。
- 要求最终路径必须位于 `IMAGES_PATH` 内。
- 文件不存在返回 `404`。

### Live Demo

Router:

```text
prefix = /api/v1/website/livedemo
```

| 方法   | 路径   | 权限   | 请求体            | 返回             |
| ------ | ------ | ------ | ----------------- | ---------------- |
| `GET`  | `/all` | 公开   | 无                | Live Demo 项列表 |
| `POST` | `/set` | 管理员 | `{ data: [...] }` | `true/false`     |

配置文件：

```text
data/resources/website/livedemo.json
```

Live Demo 项结构：

```json
{
  "title": "Markdown流渲染体验",
  "folder": "sse-markdown",
  "url": "/io/sse-markdown",
  "thumbnail": "/api/v1/website/image/chat-playground/2_markdown_sse_thumbnail.png",
  "previewgif": "/api/v1/website/image/chat-playground/2_sse_md_preview.gif",
  "sourcelink": "https://github.com/pldz1/demos/tree/main/sse_markdown",
  "date": "2025-01-15",
  "description": "用 markdown-it 动态更新 markdown 内容。"
}
```

### 评论

Router:

```text
prefix = /api/v1/website/comment
```

| 方法   | 路径      | 权限   | 请求体                               | 返回             |
| ------ | --------- | ------ | ------------------------------------ | ---------------- |
| `POST` | `/all`    | 公开   | `{ article_id }`                     | 当前文章评论列表 |
| `POST` | `/add`    | 管理员 | `{ article_id, content, parent_id }` | `true/false`     |
| `POST` | `/delete` | 管理员 | `{ article_id, comment_id }`         | `true/false`     |

评论存储在：

```text
data/db/comments.json
```

评论数据按 `article_id` 分组：

```json
{
  "article_id": [
    {
      "id": "comment-id",
      "created": "2026-01-01T00:00:00.000Z",
      "username": "user@example.com",
      "content": "评论内容",
      "avatar": "/api/v1/website/image/avatar/default.jpg",
      "replies": [],
      "replyToUsername": ""
    }
  ]
}
```

当前后端要求 `content` 字段本身就是完整评论对象，而不是纯字符串。

### 白板

Router:

```text
prefix = /api/v1/website/whiteboard
```

| 方法   | 路径          | 权限       | 请求体                     | 返回                     |
| ------ | ------------- | ---------- | -------------------------- | ------------------------ |
| `POST` | `/key`        | 公开       | `{ key }`                  | 指定 key 的白板          |
| `POST` | `/authorized` | 登录态可选 | `{ username, create_new }` | 某用户白板列表           |
| `POST` | `/update`     | 公开       | `{ key, content }`         | `{ flag, log, created }` |

白板数据结构：

```json
{
  "created": "2026-01-01T00:00:00",
  "key": "123",
  "content": "白板文本内容",
  "username": "user@example.com"
}
```

白板当前实现是内存态：

- 存储在 `WhiteBoardHandler.white_board_list`。
- 不写入数据库或文件。
- 服务重启后全部丢失。
- key 是 `100-999` 的三位数字。
- 最大容量约 900 个 key。
- 超过一天未更新的白板会被清理。
- 如果通过 key 找到过期白板，会刷新 `created` 并清空 `content`。

## 前端路由

前端使用 HTML5 History 模式。

| 路径                  | 组件                | 说明                                       |
| --------------------- | ------------------- | ------------------------------------------ |
| `/`                   | `HomePage.vue`      | 首页                                       |
| `/articles`           | `TutorialsPage.vue` | 专栏列表，展示所有 `serialNo=0` 的导读文章 |
| `/articles/:category` | `TutorialsPage.vue` | 某个分类下的系列文章                       |
| `/article/:id`        | `ArticlePage.vue`   | 文章详情                                   |
| `/livedemo`           | `LiveDemoPage.vue`  | Demo / 项目预览                            |
| `/whiteboard`         | `WhiteBoard.vue`    | 临时文本白板                               |
| `/admin/:id?`         | `AdminPage.vue`     | 管理后台                                   |
| `/404`                | `NotFound.vue`      | 404 页面                                   |
| `/:pathMatch(.*)*`    | redirect `/`        | 未匹配路径回首页                           |

Nginx 生产配置中：

```nginx
location / {
    try_files $uri $uri/ /index.html;
}
```

这保证了刷新 `/article/:id` 这类前端路由时仍然回到 `index.html`。

## 前端页面规格

### 首页

组件：

```text
web/src/views/HomePage.vue
```

首页加载时会并发请求：

- `getAllArticles()`
- `getAllALiveDemos()`

数据用途：

- 从全部文章中按日期排序，取最近文章作为项目/更新展示。
- 优先选择 `category === "code-space"` 的文章作为项目教程。
- 从 Live Demo 配置中取前 4 个作为 Demo 展示。
- 如果接口失败或无数据，则使用组件内 fallback 数据。

### 教程页

组件：

```text
web/src/views/TutorialsPage.vue
```

有两种模式：

- `/articles`：专栏模式，读取 `getArticleIntros()`，展示 `serialNo=0` 的导读文章。
- `/articles/:category`：系列模式，读取 `getArticlesByCategory(category)`，展示该分类全部文章。

排序方式：

- 按时间。
- 按浏览量。
- 系列模式额外支持按 `serialNo`。

分页：

- 每页 8 条。

### 文章详情页

组件：

```text
web/src/views/ArticlePage.vue
```

能力：

- 根据路由 `id` 请求 `getArticle(id)`。
- 使用 `renderMarkdown()` 渲染正文。
- 生成标题目录。
- 支持代码高亮。
- 支持代码块复制。
- 外链自动加 `target="_blank"` 和 `rel="noopener noreferrer"`。
- 图片自动加 `loading="lazy"` 和 `decoding="async"`。
- 展示上一篇/下一篇。
- 展示评论表单。
- 展示 CSDN、掘金、GitHub、Gitee 外部链接按钮。

Markdown 支持的高亮语言：

```text
bash, shell, sh
css
html, vue, xml
javascript, js
json
markdown, md
plaintext, text
python, py
scss
typescript, ts
yaml, yml
```

### Live Demo 页面

组件：

```text
web/src/views/LiveDemoPage.vue
```

加载：

```text
GET /api/v1/website/livedemo/all
```

展示字段：

- title
- folder
- url
- thumbnail
- previewgif
- sourcelink
- date
- description

交互：

- 卡片 hover 时优先显示 `previewgif`。
- 点击“打开预览”时，如果 `url` 是相对路径，会拼接当前 origin。
- 点击“查看源码”打开 `sourcelink`。

### 白板页

组件：

```text
web/src/views/WhiteBoard.vue
```

行为：

- 输入 key 后点击“匹配/新建”：请求 `/whiteboard/key` 匹配已有白板。
- 不输入 key 时：请求 `/whiteboard/authorized` 创建或获取当前用户/匿名用户白板。
- 选中白板后可编辑、保存、全屏预览。
- 保存调用 `/whiteboard/update`。

### 管理后台

组件：

```text
web/src/views/AdminPage.vue
```

路由：

```text
/admin/usermgt
/admin/imagemgt
/admin/navmgt
/admin/cachemgt
```

进入后台时：

- 从 Vuex 读取 `authState.isadmin`。
- 如果不是管理员，跳转回 `/`。
- 图片管理会预先读取所有分类。

后台子模块：

| key        | 组件           | 功能                                         |
| ---------- | -------------- | -------------------------------------------- |
| `usermgt`  | `UserMgt.vue`  | 用户列表、删除用户                           |
| `imagemgt` | `ImageMgt.vue` | 按分类管理文章图片，上传、重命名、下载、删除 |
| `cachemgt` | `CacheMgt.vue` | 管理缓存文件，上传、下载、删除               |

### HeaderBar

组件：

```text
web/src/components/HeaderBar.vue
```

能力：

- 固定顶部导航。
- 根据滚动方向隐藏/显示。
- 内置主导航：
  - 首页
  - 文章/教程
  - 白板
  - Demos
- 登录后显示头像。
- 未登录显示“登录 / 注册”。
- 内置搜索按钮。
- 移动端通过 `MobileDrawer` 展示导航。

### FooterBar

组件：

```text
web/src/components/FooterBar.vue
```

加载：

```text
GET /api/v1/authorization/privacy
```

展示：

- copyright
- 公安备案信息
- ICP 备案信息

### SearchOverlay

组件：

```text
web/src/components/SearchOverlay.vue
```

搜索数据来源：

```text
GET /api/v1/website/article/all/article
```

搜索字段：

- title
- summary
- tags
- category

搜索引擎：

```text
web/src/utils/search-engine.js
```

匹配逻辑：

- 字符串 normalize 为小写。
- 查询按空白切 token。
- 包含 token 得 1 分。
- 子序列匹配得 0.5 分。
- 默认阈值 `0.2`。
- 结果按 score 降序。
- title/summary 支持 `<mark>` 高亮。

## 状态管理

Vuex store 位于：

```text
web/src/store/index.js
```

包含两个 module。

### authState

字段：

```js
{
  nickname: "",
  username: "",
  avatar: "",
  isadmin: false
}
```

actions：

- `update`
- `avatar`
- `reset`

用途：

- 登录后保存用户信息。
- Header 展示头像。
- 后台判断管理员权限。
- 评论判断是否登录。
- 白板获取当前 username。

### uiState

字段：

```js
{
  loadingMap: {
  }
}
```

用途：

- 管理后台异步加载状态。
- 支持按 key 开启/关闭 loading。

## 内容系统规格

文章源文件位于：

```text
data/articles/{category}/{file}.md
```

例如：

```text
data/articles/cloud-service/ABOUT.md
data/articles/cloud-service/云服务器的选型.md
data/articles/chat-playground/Markdown的流式渲染.md
data/articles/others/Codex简单使用.md
```

### Markdown frontmatter

每篇文章通过 YAML frontmatter 描述元数据。

推荐结构：

```yaml
---
author: admin@pldz1.com
category: cloud-service
csdn: ""
date: "2025-08-15"
gitee: ""
github: ""
juejin: ""
serialNo: 0
status: publish
summary: cloud-service 的随笔
tags:
  - cloud
  - nginx
thumbnail: /api/v1/website/image/cloud-service/example.png
title: cloud-service 系列文章
---
```

字段说明：

| 字段        | 类型        | 说明                       |
| ----------- | ----------- | -------------------------- |
| `author`    | string      | 作者，一般是管理员邮箱     |
| `category`  | string      | 文章分类，也是专栏名       |
| `title`     | string      | 文章标题                   |
| `summary`   | string      | 列表页摘要                 |
| `date`      | string/date | 发布或更新日期             |
| `serialNo`  | number      | 系列序号；`0` 表示专栏导读 |
| `status`    | string      | 当前通常使用 `publish`     |
| `tags`      | array       | 标签列表                   |
| `thumbnail` | string/null | 缩略图 URL                 |
| `csdn`      | string      | CSDN 外链                  |
| `juejin`    | string      | 掘金外链                   |
| `github`    | string      | GitHub 外链                |
| `gitee`     | string      | Gitee 外链                 |

### serialNo 规则

`serialNo` 是前端组织文章的重要字段。

- `serialNo = 0`：专栏导读文章。
- `serialNo > 0`：专栏内普通文章。

接口行为：

- `/article/all/intro` 只返回 `serialNo == 0`。
- `/article/all/article` 只返回 `serialNo != 0`。
- `/articles` 页面展示导读文章，也就是专栏入口。
- `/articles/:category` 展示该分类下所有文章。

### 文章 ID 生成规则

文章 ID 不是写在 frontmatter 里的，而是由后端自动生成。

实现位置：

```text
server/scripts/filesystem/website/article_crud.py
```

生成逻辑：

```python
rel = os.path.relpath(file_path, ARTICLES_DIR)
pid = uuid.uuid5(uuid.NAMESPACE_URL, rel).hex[:16]
```

也就是说：

- ID 由 Markdown 文件相对于 `data/articles` 的相对路径决定。
- 移动文件、重命名文件会导致 ID 变化。
- ID 长度为 16 位 hex 字符。
- 原有旧路径记录会在 watchdog 的 move/delete 处理或初次同步清理中移除。

### 文章同步机制

实现位置：

```text
server/scripts/filesystem/website/article_watchdog.py
```

后端启动时会：

1. 执行 `initial_sync()`。
2. 遍历 `ARTICLES_PATH` 下所有 `.md` 文件。
3. 用 python-frontmatter 读取 metadata 和正文。
4. 将 metadata 写入 `data/db/articles.json`。
5. 清理数据库中已经不存在的文章路径。
6. 启动 watchdog 持续监听新增、修改、移动、删除。

`articles.json` 中只保存：

```json
{
  "id": "...",
  "path": "category/file.md",
  "meta": {},
  "views": 0
}
```

正文 `content` 不常驻数据库。只有请求单篇文章时，后端才从 Markdown 文件读取正文。

### 文章排序

后端排序：

- 全部文章：按 `meta.date` 倒序。
- 导读文章：按 `meta.category` 排序。

前端排序：

- 教程页默认按日期倒序。
- 可切换按浏览量。
- 系列页可切换按 `serialNo` 升序。

## 数据目录规格

`data/` 是这个项目的内容和状态中心。

```text
data
├── articles/                  # Markdown 文章
├── cache/                     # 可上传/下载/删除的缓存资源
├── db/                        # JSON 数据库
├── images/                    # 图片资源
├── resources/                 # 站点配置和协议文本
└── templates/                 # 前端构建产物和独立 Demo 模板
```

### data/db

```text
data/db/articles.json
data/db/comments.json
data/db/users.json
```

| 文件            | 说明                                     |
| --------------- | ---------------------------------------- |
| `articles.json` | 文章索引、metadata、views                |
| `comments.json` | 按文章 ID 分组的评论树                   |
| `users.json`    | 用户、密码 hash、头像、token、黑名单状态 |

JSON 数据库访问封装在：

```text
server/scripts/db/connection.py
```

读写特点：

- 使用 `threading.Lock()` 做单进程内互斥。
- 文件不存在时读取为空对象。
- JSON 解析失败时读取为空对象。
- 写入时 `ensure_ascii=False` 和 `indent=2`。

### data/images

图片按分类存放：

```text
data/images/avatar
data/images/chat-playground
data/images/cloud-service
data/images/code-space
data/images/others
```

访问 URL 规则：

```text
/api/v1/website/image/{category}/{filename}
/api/v1/website/image/{category}/{filename}@original
/api/v1/website/image/{category}/{filename}@raw
/api/v1/website/image/{category}/{filename}@{size}
/api/v1/website/image/{category}/{filename}@{width}x{height}
```

例如：

```text
/api/v1/website/image/cloud-service/cloud-service-frp-thumbnail.png
/api/v1/website/image/cloud-service/cloud-service-frp-thumbnail.png@original
/api/v1/website/image/cloud-service/cloud-service-frp-thumbnail.png@512
/api/v1/website/image/cloud-service/cloud-service-frp-thumbnail.png@1024x768
```

### data/resources

```text
data/resources/privacy_policy.txt
data/resources/user_agreement.txt
data/resources/website/livedemo.json
```

### data/templates

```text
data/templates/web
data/templates/sse-markdown
```

`data/templates/web` 是 Nginx 当前挂载的前端静态目录：

```yaml
volumes:
  - ./data/templates/web:/usr/share/nginx/html:ro
```

`data/templates/sse-markdown` 是一个独立 FastAPI 静态服务：

```text
/io/sse-markdown
```

## 本地开发流程

### 后端开发

```bash
cp .env.example .env
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server/main.py
```

启动后建议检查：

```bash
curl http://127.0.0.1:10058/api/v1/website/article/all/category
curl http://127.0.0.1:10058/api/v1/website/livedemo/all
```

### 前端开发

```bash
cd web
npm install
npm run dev
```

访问：

```text
http://127.0.0.1:10060
```

### 前端构建

```bash
cd web
npm run build
```

默认 Vite 会输出到 `web/dist`，但当前 Docker/Nginx 配置挂载的是：

```text
data/templates/web
```

因此如果要让 Nginx 服务最新前端，需要把构建产物同步到 `data/templates/web`，或调整 Vite `build.outDir` / Nginx volume。

## Docker 部署流程

### 启动

```bash
cp .env.example .env
docker compose up --build
```

### 后台启动

```bash
docker compose up -d --build
```

### 查看日志

```bash
docker compose logs -f
```

### 停止

```bash
docker compose down
```

### Compose 服务

`backend`：

- 使用本仓库 `Dockerfile` 构建。
- 工作目录 `/usr/src/app`。
- 挂载整个项目到容器。
- 只读挂载 `.env`。
- 环境变量覆盖：
  - `SITE_HOST=0.0.0.0`
  - `SITE_PORT=10057`
- 运行 `/usr/src/app/entrypoint.sh`。

`nginx`：

- 镜像 `nginx:1.25-alpine`。
- 暴露宿主端口 `10058:80`。
- 挂载：
  - `./nginx/nginx.conf`
  - `./nginx/prod.d`
  - `./data/templates/web`

### Nginx 路由

```text
/                  -> /usr/share/nginx/html/index.html
/api/*             -> http://backend:10057
/io/sse-markdown   -> http://backend:10078
```

## 管理后台使用

1. 配置 `.env` 中的管理员账号和密码。
2. 启动后端。
3. 后端会执行 `AuthorizedHandler.init_admin()` 初始化管理员。
4. 前端点击登录。
5. 使用 `ADMIN_USERNAME` 和 `ADMIN_PASSWORD` 登录。
6. 点击头像卡片中的“管理员”进入后台，或访问 `/admin`。

后台页面会根据路由跳转到：

```text
/admin/usermgt
```

如果 `authState.isadmin` 为 false，会自动跳转回首页。

## 安全与权限模型

当前权限模型比较简单：

- 用户身份依赖 `access_token` Cookie。
- 管理员判断依赖 `username == ADMIN_USERNAME`。
- 多数后台写操作需要登录且为管理员。
- 图片上传头像只要求登录用户。
- 白板更新当前不要求登录。
- 评论新增/删除后端要求管理员。

需要管理员权限的能力：

- 获取全部用户。
- 删除用户。
- 获取、上传、下载、删除缓存文件。
- 获取指定分类图片列表。
- 重命名/删除文章图片。
- 新增/删除评论。

公开能力：

- 读取文章列表和文章详情。
- 读取图片。
- 读取导航。
- 读取横幅。
- 读取 Live Demo.
- 读取评论。
- 读取协议/隐私页面。
- 读取/创建/更新白板。

## 当前实现注意事项

这些不是文档推测，而是当前代码实现中值得 AI 或维护者特别注意的点。

### 用户密码处理存在实现风险

`AuthorizedHandler.add_user()` 当前会始终使用 `ADMIN_PASSWORD` 生成 `password` hash：

```python
hash_password = cls.hash_password(ADMIN_PASSWORD)
```

同时 `register()` 调用时传入的是：

```python
AuthorizedHandler.hash_password(data.password)
```

但这个值只会被作为 `raw_password` 保存，实际 password hash 仍然来自 `ADMIN_PASSWORD`。这意味着普通注册用户的登录校验可能会受管理员密码影响，而不是自己的注册密码。

如果要修复，建议重新梳理：

- `add_user(username, raw_password, nickname, avatar)` 只接受明文输入或只接受 hash 输入，二选一。
- 不要保存 `raw_password`。
- 管理后台不展示明文密码。

### 前端协议链接路径可能不匹配

`LoginCard.vue` 中协议链接写成：

```text
/api/v1/website/resource/user_agreement
/api/v1/website/resource/privacy_policy
```

但后端实际路由是：

```text
/api/v1/resource/user_agreement
/api/v1/resource/privacy_policy
```

如果点击协议 404，应优先检查这个路径。

### 白板不持久化

白板只存在于 Python 进程内存中：

- 重启丢失。
- 多进程部署时不同进程不可共享。
- 多容器横向扩展时不可共享。

如果需要可靠协作或持久保存，应迁移到 `data/db`、Redis 或数据库。

### JSON 数据库只保证单进程内互斥

`threading.Lock()` 只能保护单个 Python 进程内的并发写入。

如果未来改成多 worker、多进程或多个 backend 容器同时写同一份 `data/db/*.json`，会有写入竞争风险。

### 文章 ID 与文件路径强绑定

文章 ID 由相对路径生成。改文件名或目录会导致文章 ID 改变。

影响：

- 旧文章链接失效。
- 对应评论不会自动迁移。
- views 统计会重新开始。

如果未来需要稳定 URL，应考虑在 frontmatter 中显式增加 `id` 或 `slug`。

### `navigation.json` 当前示例中存在空对象

`data/resources/website/navigation.json` 的 `data` 数组当前包含一个空对象。后端读取时会跳过缺少 `title` 或 `url` 的项，并输出 warning。

### 前端构建产物目录需要明确

Vite 默认输出 `web/dist`，Nginx 当前服务 `data/templates/web`。如果部署时发现页面不是最新版本，要检查构建产物是否同步到了 Nginx 挂载目录。

## 常见维护任务

### 新增一篇文章

1. 在 `data/articles/{category}/` 下新增 `.md` 文件。
2. 填写 frontmatter。
3. 保存文件。
4. 后端 watchdog 会自动同步到 `data/db/articles.json`。
5. 访问 `/articles/{category}` 或 `/article/{id}` 查看。

如果后端没运行，启动后会做初次全量同步。

### 新增一个专栏

1. 新建目录：

```text
data/articles/new-category
```

2. 创建导读文章，例如：

```text
data/articles/new-category/ABOUT.md
```

3. 设置：

```yaml
category: new-category
serialNo: 0
```

4. 添加普通文章：

```yaml
category: new-category
serialNo: 1
```

5. 如需配图，把图片放到：

```text
data/images/new-category
```

6. 在文章中引用：

```markdown
![说明](/api/v1/website/image/new-category/example.png)
```

### 管理图片

图片管理入口：

```text
/admin/imagemgt
```

图片分类来自文章分类接口：

```text
GET /api/v1/website/article/all/category
```

因此某个分类要出现在图片管理下拉框中，通常需要先存在对应文章分类。

### 管理缓存文件

缓存管理入口：

```text
/admin/cachemgt
```

实际目录：

```text
data/cache
```

支持：

- 上传。
- 下载。
- 删除。
- 查看大小和更新时间。

## 故障排查

### `.env` 未找到

现象：

```text
环境变量文件 .env 未找到
```

处理：

```bash
cp .env.example .env
```

### Docker 镜像拉取失败

如果 `nginx:1.25-alpine` 或 Python 基础镜像拉取失败，可以先使用镜像代理拉取，再重新 tag。

示例：

```bash
docker pull docker.m.daocloud.io/library/nginx:1.25-alpine
docker tag docker.m.daocloud.io/library/nginx:1.25-alpine nginx:1.25-alpine
docker rmi docker.m.daocloud.io/library/nginx:1.25-alpine
```

### 前端接口 404

检查顺序：

1. 前端请求是否以 `/api/v1` 开头。
2. 本地 Vite 代理是否指向 `http://127.0.0.1:10058`。
3. Docker 模式下 Nginx 是否已启动。
4. Nginx `/api/` 是否代理到 `backend:10057`。
5. backend 容器中 `SITE_PORT` 是否为 `10057`。

### 文章列表为空

检查：

1. `data/articles` 是否存在。
2. Markdown 文件是否以 `.md` 结尾。
3. frontmatter 是否可被 python-frontmatter 解析。
4. 后端启动日志中是否出现初次同步。
5. `data/db/articles.json` 是否生成。
6. `serialNo` 是否符合页面预期：
   - `/articles` 只展示 `serialNo=0`。
   - 首页项目优先取 `category=code-space`，没有则回退到最近文章。

### 图片无法显示

检查：

1. URL 是否为 `/api/v1/website/image/{category}/{filename}`。
2. 文件是否实际存在于 `data/images/{category}/{filename}`。
3. 文件名大小写是否一致。
4. category 是否包含非法路径。
5. 后端日志是否出现 “图片未找到”。

### 后台无法进入

检查：

1. 是否已登录。
2. 登录用户是否等于 `.env` 中的 `ADMIN_USERNAME`。
3. Vuex `authState.isadmin` 是否为 true。
4. 后端是否初始化了管理员账号。

### 白板内容丢失

这是当前设计结果。白板不持久化，重启后会丢失。

## 开发约定

### 后端约定

- 所有 API 统一挂载在 `/api/v1`。
- 路由定义放在 `server/routes/`。
- 文件系统操作放在 `server/scripts/filesystem/`。
- JSON 数据库操作放在 `server/scripts/db/`。
- 配置路径统一通过 `ProjectConfig` 获取。
- API 返回尽量包裹在 `{ "data": ... }` 中，保持前端请求工具兼容。

### 前端约定

- 页面级组件放在 `web/src/views/`。
- 可复用组件放在 `web/src/components/`。
- API 封装放在 `web/src/utils/apis/`。
- 全局用户状态放在 Vuex `authState`。
- 页面路由使用 history mode。
- 所有 API 请求默认使用相对路径，让 Vite/Nginx 代理处理环境差异。

### 内容约定

- 一篇 Markdown 就是一篇文章。
- 一个 `category` 就是一个专栏。
- `serialNo=0` 是专栏导读。
- 图片按文章分类目录存放。
- 文章图片优先使用 `/api/v1/website/image/...` 形式引用。

## 适合 AI 继续开发时的项目理解

如果 AI 需要继续修改这个项目，可以先建立以下 mental model：

1. 这是一个内容站，不是传统数据库驱动的 CMS。
2. 文章的事实来源是 `data/articles` 下的 Markdown。
3. `data/db/articles.json` 是 Markdown 的索引缓存，不是文章正文主存储。
4. 用户、评论、文章 views 当前存在 JSON 文件里。
5. 管理后台写的是本地 JSON 配置和本地文件。
6. 生产入口是 Nginx，前端静态文件来自 `data/templates/web`。
7. 主后端和 `sse-markdown` Demo 在同一个 backend 容器内由 `entrypoint.sh` 同时启动。
8. 前端请求工具默认只返回后端 `data` 字段。
9. 管理员权限只由用户名是否等于 `ADMIN_USERNAME` 决定。
10. 白板是临时内存功能，不应假设它可靠持久。

优先阅读顺序：

```text
server/main.py
server/routes/app.py
server/core/config.py
server/scripts/filesystem/website/article_watchdog.py
server/scripts/filesystem/website/article_crud.py
server/scripts/db/connection.py
server/scripts/db/authorization.py
server/routes/website/*.py
web/src/routers/index.js
web/src/utils/apis/request.js
web/src/store/index.js
web/src/views/*.vue
```

## License

本仓库包含 `LICENSE` 文件，使用前请阅读其中的许可条款。
