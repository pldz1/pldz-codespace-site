<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="项目、教程、仓库和 Live Demo">
    <p>欢迎来到「爬楼的猪 Dev」</p>
    <p>这里放项目、教程、仓库、Live Demo 和一些零散记录。</p>
  </MobileDrawer>

  <HeaderBar :route-name="'首页'" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="home-page">
    <main class="home-main">
      <section class="hero-section">
        <div class="hero-copy card-surface">
          <p class="hero-kicker">Dev Space</p>
          <h1>🎉 欢迎来到 <span class="hero-brand-pixel">爬楼的猪 Dev</span></h1>
          <p class="hero-description">
            项目教程 & Live Demo<br />
            分享和记录一些我个人在做的, 感兴趣的工具和内容 😁
          </p>
          <div class="hero-actions">
            <a class="button-primary" href="/codespace">查看项目教程</a>
            <a class="button-secondary" href="/codespace">查看 Demo / GitHub</a>
          </div>
          <!-- TODO 后续用接口换成热点内容... -->
          <ul class="hero-points">
            <li>开发里的零散内容，慢慢放到这里</li>
            <li>能复用的、能跑的、顺手能查的，会优先留下来</li>
          </ul>
        </div>

        <div class="hero-preview">
          <article class="preview-card preview-card--feature card-surface">
            <div class="preview-card__header">
              <span class="preview-card__eyebrow">Latest tutorial</span>
              <span class="preview-status">持续维护</span>
            </div>
            <h2>{{ featuredProject.title }}</h2>
            <p>{{ featuredProject.description }}</p>
            <div class="preview-tags">
              <span v-for="tag in featuredProject.tags" :key="tag">{{ tag }}</span>
            </div>
            <a class="text-link" :href="featuredProject.tutorialLink">进入教程</a>
          </article>

          <div class="preview-grid">
            <article class="preview-card card-surface">
              <div class="preview-inline-meta">
                <span class="preview-card__eyebrow">Live demo</span>
                <span class="preview-status preview-status--muted">{{ featuredDemo.status === "done" ? "在线可用" : "查看详情" }}</span>
              </div>
              <h3>{{ featuredDemo.title }}</h3>
              <p>{{ featuredDemo.description }}</p>
              <a class="text-link" :href="featuredDemo.demoLink" target="_blank" rel="noopener noreferrer">在线体验</a>
            </article>

            <article class="preview-card card-surface">
              <div class="preview-inline-meta">
                <span class="preview-card__eyebrow">More reading</span>
                <span class="preview-status preview-status--muted">{{ secondaryProject.tags?.[0] || "文章" }}</span>
              </div>
              <h3>{{ secondaryProject.title }}</h3>
              <p>{{ secondaryProject.description }}</p>
              <a class="text-link" :href="secondaryProject.tutorialLink">查看文章</a>
            </article>
          </div>
        </div>
      </section>

      <section class="content-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Articles / Notes</p>
            <h2>项目教程 / 开发记录</h2>
          </div>
          <div class="section-heading-side">
            <p class="section-intro">主要是一些项目过程、配置折腾、工具记录，还有少量偏实验性的内容。</p>
            <a class="section-link" href="/codespace">查看全部项目</a>
          </div>
        </div>

        <div class="projects-grid">
          <ProjectCard v-for="project in projects" :key="project.id" :project="project" />
        </div>
      </section>

      <section class="content-section demo-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Demo / Repo</p>
            <h2>一些可直接打开的内容</h2>
          </div>
          <p class="section-intro">偏轻一点，适合先点开看看。源码、预览和相关文章都尽量放在一起。</p>
        </div>

        <div class="demo-grid">
          <DemoCard v-for="demo in demos" :key="demo.id" :demo="demo" />
        </div>
      </section>

      <section class="content-section updates-and-about">
        <div class="updates-panel">
          <div class="section-heading section-heading--compact">
            <div>
              <p class="section-kicker">Updates / Timeline</p>
              <h2>最近更新</h2>
            </div>
            <a class="section-link" href="/codespace">阅读更新</a>
          </div>

          <ul class="updates-list">
            <TimelineItem v-for="item in updates" :key="item.id" :item="item" />
          </ul>
        </div>

        <section class="about-panel card-surface">
          <div class="about-avatar">
            <img :src="'/api/v1/website/image/avatar/admin@pldz1_com_00000001.jpg'" alt="about avatar" />
          </div>
          <div class="about-copy">
            <p class="section-kicker">About</p>
            <h2>一个长期维护的小空间</h2>
            <p>平时写点项目实现、工具脚本、页面实验和部署记录。没有特别严格的边界，想到什么就慢慢补进来。</p>
            <a class="button-ghost button-small" href="/">About me / 了解更多</a>
          </div>
        </section>
      </section>
    </main>

    <FooterBar />
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from "vue";

import FooterBar from "../components/FooterBar.vue";
import HeaderBar from "../components/HeaderBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
import DemoCard from "../components/home-page/DemoCard.vue";
import ProjectCard from "../components/home-page/ProjectCard.vue";
import TimelineItem from "../components/home-page/TimelineItem.vue";
import { getAllACodeSpace, getAllArticles } from "../utils/apis";

const isMobileMenuOpen = ref(false);

const fallbackProjects = [
  {
    id: 1,
    title: "在线白板项目：从 0 实现实时协作",
    description: "从房间同步、画布事件到持久化存储，逐步把多人协作白板拆开实现。",
    cover: "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=960&q=80",
    tags: ["Vue 3", "Canvas", "WebSocket"],
    tutorialLink: "/whiteboard",
    repoLink: "https://github.com/example/realtime-whiteboard",
  },
  {
    id: 2,
    title: "Docker 部署博客系统",
    description: "把博客拆成镜像、配置、数据卷和反向代理，记录一套能稳定复用的部署流程。",
    cover: "https://images.unsplash.com/photo-1605745341112-85968b19335b?auto=format&fit=crop&w=960&q=80",
    tags: ["Docker", "Nginx", "Linux"],
    tutorialLink: "/codespace",
    repoLink: "https://github.com/example/docker-blog-stack",
  },
  {
    id: 3,
    title: "用 frp 打通内网访问",
    description: "把一台局域网服务暴露到公网，顺手整理配置、权限和常见故障排查。",
    cover: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=960&q=80",
    tags: ["frp", "Server", "Network"],
    tutorialLink: "/codespace",
    repoLink: "https://github.com/example/frp-notes",
  },
];

const fallbackDemos = [
  {
    id: 1,
    title: "Realtime Whiteboard",
    description: "支持多房间协作、基础绘图和状态同步的在线白板 Demo。",
    status: "done",
    demoLink: "/whiteboard",
    repoLink: "https://github.com/example/realtime-whiteboard",
    thumbnail: "",
    previewgif: "",
  },
  {
    id: 2,
    title: "CodeSpace Playground",
    description: "放一些小型实验和过程性页面，用来验证交互和布局想法。",
    status: "building",
    demoLink: "/codespace",
    repoLink: "https://github.com/example/codespace-playground",
    thumbnail: "",
    previewgif: "",
  },
  {
    id: 3,
    title: "Prompt Lab",
    description: "整理一些实验性工具和脚手架，边做边记录可行的交互方式。",
    status: "done",
    demoLink: "https://example.com/demo/prompt-lab",
    repoLink: "https://github.com/example/prompt-lab",
    thumbnail: "",
    previewgif: "",
  },
  {
    id: 4,
    title: "CodeSpace Notes",
    description: "把一些实验项目、教程页面和可复用思路汇总成轻量入口。",
    status: "experimental",
    demoLink: "/codespace",
    repoLink: "https://github.com/example/codespace-notes",
    thumbnail: "",
    previewgif: "",
  },
];

const fallbackUpdates = [
  {
    id: 1,
    title: "补完白板房间同步和重连处理",
    date: "2026-04-08",
    type: "教程",
    link: "/whiteboard",
  },
  {
    id: 2,
    title: "Codespace Playground 增加一版新的预览页",
    date: "2026-04-05",
    type: "demo",
    link: "/codespace",
  },
  {
    id: 3,
    title: "整理 Docker 部署博客系统的仓库结构",
    date: "2026-04-01",
    type: "repo",
    link: "https://github.com/example/docker-blog-stack",
  },
];

const projects = ref([]);
const demos = ref([]);
const updates = ref([]);

const featuredProject = computed(() => projects.value[0] || fallbackProjects[0]);
const secondaryProject = computed(() => projects.value[1] || fallbackProjects[1]);
const featuredDemo = computed(() => demos.value[0] || fallbackDemos[0]);

function normalizeTags(tags) {
  if (Array.isArray(tags)) return tags.filter(Boolean).slice(0, 4);
  if (typeof tags === "string") {
    return tags
      .split(/[,\s]+/)
      .map((item) => item.trim())
      .filter(Boolean)
      .slice(0, 4);
  }
  return [];
}

function normalizeArticleProject(article, index) {
  return {
    id: article?.id || `project-${index}`,
    title: article?.title || "未命名文章",
    description: article?.summary || "暂无描述",
    cover: article?.thumbnail || "",
    tags: normalizeTags(article?.tags),
    tutorialLink: article?.id ? `/article/${article.id}` : "/",
    repoLink: article?.github || article?.gitee || article?.csdn || `/article/${article?.id || ""}`,
  };
}

function normalizeCodeSpaceDemo(item, index) {
  const url = item?.url || "";
  const sourceLink = item?.sourcelink || item?.url || "https://github.com";
  return {
    id: item?.folder || item?.title || `demo-${index}`,
    title: item?.title || "未命名 Demo",
    description: item?.description || "暂无描述",
    status: "done",
    demoLink: url,
    repoLink: sourceLink,
    thumbnail: item?.thumbnail || "",
    previewgif: item?.previewgif || "",
  };
}

function normalizeUpdate(article, index) {
  return {
    id: article?.id || `update-${index}`,
    title: article?.title || "未命名文章",
    date: article?.date || "",
    type: article?.category || "article",
    link: article?.id ? `/article/${article.id}` : "/",
  };
}

async function loadHomeData() {
  const [articlesRes, codeSpaceRes] = await Promise.allSettled([getAllArticles(), getAllACodeSpace()]);

  const articles = articlesRes.status === "fulfilled" && Array.isArray(articlesRes.value) ? articlesRes.value : [];
  const codeSpaces = codeSpaceRes.status === "fulfilled" && Array.isArray(codeSpaceRes.value) ? codeSpaceRes.value : [];

  const sortedArticles = [...articles].sort((a, b) => String(b?.date || "").localeCompare(String(a?.date || "")));
  const preferredProjectArticles = sortedArticles.filter((article) => article?.category === "code-space");

  const projectArticles = (preferredProjectArticles.length ? preferredProjectArticles : sortedArticles)
    .filter((article) => article?.id && article?.title)
    .slice(0, 3)
    .map(normalizeArticleProject);

  const updateArticles = sortedArticles
    .filter((article) => article?.id && article?.title)
    .slice(0, 5)
    .map(normalizeUpdate);

  const codeSpaceDemos = codeSpaces.slice(0, 4).map(normalizeCodeSpaceDemo);

  projects.value = projectArticles.length ? projectArticles : fallbackProjects;
  updates.value = updateArticles.length ? updateArticles : fallbackUpdates;
  demos.value = codeSpaceDemos.length ? codeSpaceDemos : fallbackDemos;
}

function onToggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

function onCloseMobileMenu() {
  isMobileMenuOpen.value = false;
}

function onResize() {
  if (window.innerWidth > 840) {
    onCloseMobileMenu();
  }
}

onMounted(() => {
  window.addEventListener("resize", onResize);
  loadHomeData();
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", onResize);
});
</script>

<style scoped>
:global(body) {
  background: #f8fafc;
  color: #0f172a;
}

.home-page {
  min-height: 100vh;
}

.home-main {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: 108px 0 56px;
}

.card-surface {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid #edf2f7;
  border-radius: 24px;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.025);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
}

.card-surface:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.04);
  border-color: #e2e8f0;
  background: rgba(255, 255, 255, 0.95);
}

.hero-copy.card-surface,
.about-panel.card-surface {
  background: transparent;
  border-color: transparent;
  box-shadow: none;
}

.hero-copy.card-surface:hover,
.about-panel.card-surface:hover {
  transform: none;
  box-shadow: none;
  border-color: transparent;
  background: transparent;
}

.hero-section {
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
  gap: 24px;
  margin-bottom: 72px;
  align-items: start;
}

.hero-copy {
  padding: 28px 12px 28px 0;
}

.hero-kicker,
.section-kicker {
  margin: 0 0 10px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #2563eb;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(32px, 4vw, 46px);
  line-height: 1.1;
  letter-spacing: -0.03em;
}

.hero-brand-pixel {
  display: inline-block;
  margin-left: 0.12em;
  padding: 0.08em 0.26em 0.14em;
  border: 2px solid #0f172a;
  border-radius: 8px;
  background: linear-gradient(180deg, #fefefe 0%, #eef5ff 100%);
  box-shadow: 4px 4px 0 #93c5fd;
  font-family: "Press Start 2P", "Microsoft YaHei", monospace;
  font-size: 0.92em;
  letter-spacing: 0.02em;
  text-shadow: 1px 0 0 currentColor, 0 1px 0 currentColor;
  vertical-align: 0.06em;
  white-space: nowrap;
}

.hero-description {
  margin: 18px 0 0;
  font-size: 16px;
  line-height: 1.8;
  color: #475569;
}

.hero-actions,
.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.hero-actions {
  margin-top: 28px;
}

.hero-points {
  margin: 30px 0 0;
  padding: 0;
  list-style: none;
  display: grid;
  gap: 12px;
}

.hero-points li {
  position: relative;
  padding-left: 18px;
  color: #64748b;
  line-height: 1.7;
}

.hero-points li::before {
  content: "";
  position: absolute;
  top: 10px;
  left: 0;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #93c5fd;
}

.hero-preview {
  display: grid;
  gap: 18px;
}

.preview-card {
  padding: 24px;
  border: 1px solid #e7edf5;
  border-radius: 26px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.06);
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease, background-color 0.22s ease;
}

.preview-card--feature {
  padding: 30px 30px 28px;
}

.preview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.09);
  border-color: #d7e3f1;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
}

.preview-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 18px;
}

.preview-card__eyebrow {
  font-size: 12px;
  color: #64748b;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.preview-inline-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.preview-status {
  padding: 6px 10px;
  border-radius: 999px;
  background: #f4f8ff;
  color: #2563eb;
  border: 1px solid #d8e7ff;
  font-size: 12px;
}

.preview-status--muted {
  background: #fbfcfd;
  color: #475569;
  border-color: #e8edf3;
}

.preview-card h2,
.preview-card h3,
.project-card h3,
.demo-card h3,
.about-copy h2,
.section-heading h2 {
  margin: 0;
  color: #0f172a;
}

.preview-card h2 {
  font-size: 24px;
  line-height: 1.35;
}

.preview-card h3,
.project-card h3,
.demo-card h3 {
  font-size: 20px;
  line-height: 1.35;
}

.preview-card p,
.project-card p,
.demo-card p,
.about-copy p,
.section-intro {
  color: #475569;
  line-height: 1.75;
}

.preview-tags,
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.preview-tags {
  margin: 20px 0;
}

.preview-tags span,
.tag-chip {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid #e6edf5;
  background: #fbfcfd;
  color: #475569;
  font-size: 12px;
}

.preview-tags span {
  background: #ffffff;
  border-color: #dbe3ef;
}

.tag-chip--muted {
  background: #ffffff;
}

.text-link {
  display: inline-flex;
  align-items: center;
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
}

.preview-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px;
}

.preview-screenshot {
  height: 152px;
  margin-bottom: 18px;
  border-radius: 18px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
  position: relative;
  background: #f8fafc;
}

.preview-screenshot span {
  position: absolute;
  inset: 14px;
  border-radius: 14px;
}

.preview-screenshot--code span {
  background: linear-gradient(#0f172a, #0f172a) 18px 20px / 42% 6px no-repeat, linear-gradient(#2563eb, #2563eb) 18px 42px / 68% 6px no-repeat,
    linear-gradient(#cbd5e1, #cbd5e1) 18px 64px / 54% 6px no-repeat, linear-gradient(#e2e8f0, #e2e8f0) 18px 86px / 74% 6px no-repeat,
    linear-gradient(135deg, #f8fafc, #eff6ff);
}

.preview-screenshot--board span {
  background: radial-gradient(circle at 22% 26%, #2563eb 0 10px, transparent 11px), radial-gradient(circle at 55% 40%, #93c5fd 0 14px, transparent 15px),
    radial-gradient(circle at 74% 68%, #0f172a 0 8px, transparent 9px), linear-gradient(#dbeafe, #dbeafe) 22% 26% / 34% 2px no-repeat,
    linear-gradient(#dbeafe, #dbeafe) 55% 40% / 26% 2px no-repeat, linear-gradient(180deg, #f8fafc, #eff6ff);
}

.content-section {
  margin-bottom: 72px;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 24px;
  margin-bottom: 28px;
}

.section-heading h2 {
  font-size: 28px;
  line-height: 1.2;
}

.section-intro {
  max-width: 520px;
  margin: 0;
  font-size: 15px;
}

.section-heading-side {
  display: grid;
  justify-items: end;
  gap: 10px;
}

.section-heading--compact {
  margin-bottom: 18px;
}

.section-link {
  color: #2563eb;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.projects-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 20px;
}

.about-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.demo-section {
  padding: 12px 0 0;
  border-radius: 0;
  background: transparent;
  border: none;
}

.demo-grid {
  display: grid;
  gap: 14px;
}

.updates-and-about {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.72fr);
  gap: 20px;
  align-items: start;
}

.updates-panel {
  padding: 0;
}

.about-panel {
  padding: 12px 0 0 24px;
  border-left: 1px solid #e9eef5;
  border-radius: 0;
}

.updates-panel,
.about-panel {
  align-self: start;
}

.updates-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  border-top: 1px solid #e5e7eb;
}

.about-panel {
  display: grid;
  grid-template-columns: 88px 1fr;
  gap: 18px;
}

.about-avatar {
  width: 88px;
  height: 88px;
  overflow: hidden;
  border-radius: 24px;
  background: #e2e8f0;
}

.about-copy {
  display: grid;
  gap: 14px;
}

.button-primary,
.button-secondary,
.button-ghost {
  height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s ease, background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.button-small {
  height: 38px;
  padding: 0 14px;
  font-size: 14px;
}

.button-primary {
  background: #2563eb;
  color: #ffffff;
  border: 1px solid #2563eb;
}

.button-primary:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
  transform: translateY(-1px);
}

.button-secondary {
  background: #eff6ff;
  color: #2563eb;
  border: 1px solid #bfdbfe;
}

.button-secondary:hover {
  background: #dbeafe;
  transform: translateY(-1px);
}

.button-ghost {
  background: #ffffff;
  color: #334155;
  border: 1px solid #e5e7eb;
}

.button-ghost:hover {
  background: #f8fafc;
  transform: translateY(-1px);
}

@media (max-width: 1080px) {
  .hero-section,
  .updates-and-about {
    grid-template-columns: 1fr;
  }

  .about-panel {
    grid-template-columns: 72px 1fr;
  }

  .about-avatar {
    width: 72px;
    height: 72px;
    border-radius: 20px;
  }
}

@media (max-width: 840px) {
  .home-main {
    width: min(100%, calc(100% - 24px));
    padding-top: 94px;
  }

  .hero-section,
  .projects-grid,
  .preview-grid {
    grid-template-columns: 1fr;
  }

  .section-heading {
    align-items: start;
    flex-direction: column;
  }

  .section-heading-side {
    justify-items: start;
  }
}

@media (max-width: 640px) {
  .home-main {
    width: min(100%, calc(100% - 16px));
    padding-bottom: 40px;
  }

  .hero-copy,
  .preview-card,
  .preview-card--feature,
  .about-panel {
    padding: 22px;
  }

  .hero-copy h1 {
    font-size: 30px;
  }

  .section-heading h2 {
    font-size: 24px;
  }

  .about-panel {
    grid-template-columns: 72px 1fr;
  }
}
</style>
