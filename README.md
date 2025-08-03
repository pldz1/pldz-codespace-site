# pldz-codespace-site — pldz1.com 代码站

这是支撑 https://pldz1.com 的源码仓。开发、改动、跑起来、部署，都从这里开始。  
适配 Codespaces / Docker，想要「拉下来直接跑」的体验就做到极致。

## 核心亮点

- 🐍 后端用 Python，依赖集中在 `requirements.txt`
- 🧰 前端按需混合（静态 + JS），结构直观不搞花活
- 🐳 Docker + Compose 一键搞定开发环境，Codespace 友好
- ⚙️ 推荐用 VS Code（`.vscode/` 配置在仓里），开箱即用
- 🔒 环境变量通过 `.env` 管理，真实部署不硬编码
- 🔁 可复现：Dockerfile + compose 保证本地/线上一致

## 开发快跑（最少动作启动）

```bash
git clone https://github.com/pldz1/pldz-codespace-site.git
cd pldz-codespace-site
cp .env.example .env          # 改你自己的配置
docker compose up --build     # 构建并启动
```
