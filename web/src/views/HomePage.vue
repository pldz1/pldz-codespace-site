<template>
  <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="onCloseMobileMenu()"></div>
  <div v-show="isMobileMenuOpen" class="mobile-sidebar">
    <div class="mobile-sidebar-header">
      <div class="mobile-sidebar-brand">
        <span class="mobile-sidebar-logo"></span>
        <div>
          <div class="mobile-sidebar-title">CodeSpace</div>
          <div class="mobile-sidebar-subtitle">项目、教程、仓库与 Demo</div>
        </div>
      </div>
      <button class="close-btn" @click="onCloseMobileMenu()">×</button>
    </div>
    <div class="mobile-sidebar-body">
      <div class="nav-placeholder"></div>
      <div class="mobile-sidebar-note">
        <p>这里整理我做过的项目和实现过程。</p>
        <p>有些项目附了教程，有些可以直接在线体验。</p>
      </div>
    </div>
  </div>

  <HeaderBar :route-name="'首页'" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="home-page">
    <main class="home-main">
      <section class="hero-section">
        <div class="hero-copy card-surface">
          <p class="hero-kicker">Personal project archive</p>
          <h1>项目、教程、仓库与 Demo</h1>
          <p class="hero-description">
            记录我做过的项目，以及它们的实现过程。<br />
            每个项目尽量附上教程、源码和可运行示例。
          </p>
          <div class="hero-actions">
            <a class="button-primary" href="#tutorials">查看项目教程</a>
            <a class="button-secondary" href="#demo">查看 Demo / GitHub</a>
          </div>
          <ul class="hero-points">
            <li>从想法到实现，尽量把过程留下来</li>
            <li>优先展示能复用、能运行、能讲清楚的项目</li>
          </ul>
        </div>

        <div class="hero-preview">
          <article class="preview-card preview-card--feature card-surface">
            <div class="preview-card__header">
              <span class="preview-card__eyebrow">Latest tutorial</span>
              <span class="preview-status">持续维护</span>
            </div>
            <h2>在线白板项目：从 0 实现实时协作</h2>
            <p>拆开同步、画布、房间和部署流程，保留每一步的实现记录。</p>
            <div class="preview-tags">
              <span v-for="tag in projects[0].tags" :key="tag">{{ tag }}</span>
            </div>
            <a class="text-link" :href="projects[0].tutorialLink">进入教程</a>
          </article>

          <div class="preview-grid">
            <article class="preview-card card-surface">
              <div class="preview-screenshot preview-screenshot--code">
                <span></span>
              </div>
              <h3>Demo 可直接体验</h3>
              <p>把仓库入口和在线示例放在一起，先看效果，再看实现。</p>
            </article>

            <article class="preview-card card-surface">
              <div class="preview-screenshot preview-screenshot--board">
                <span></span>
              </div>
              <h3>过程比结果更重要</h3>
              <p>除了项目本身，也保留部署、排坑和重构过程。</p>
            </article>
          </div>
        </div>
      </section>

      <section id="projects" class="content-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Projects</p>
            <h2>Projects / 项目教程</h2>
          </div>
          <div class="section-heading-side">
            <p class="section-intro">挑几篇最值得展开讲的项目。重点不是归档，而是把做法和取舍写清楚。</p>
            <a class="section-link" href="/codespace#projects">查看全部项目</a>
          </div>
        </div>

        <div id="tutorials" class="projects-grid">
          <ProjectCard v-for="project in projects" :key="project.id" :project="project" />
        </div>
      </section>

      <section id="demo" class="content-section demo-section">
        <div class="section-heading">
          <div>
            <p class="section-kicker">Demo / Repo</p>
            <h2>可体验的项目入口</h2>
          </div>
          <p class="section-intro">这里是更直接的入口。先点开用，再决定要不要继续看实现。</p>
        </div>

        <div class="demo-grid">
          <DemoCard v-for="demo in demos" :key="demo.id" :demo="demo" />
        </div>
      </section>

      <section class="content-section updates-and-about">
        <div class="updates-panel">
          <div class="section-heading section-heading--compact">
            <div>
              <p class="section-kicker">Blog / Timeline</p>
              <h2>最近更新</h2>
            </div>
            <a class="section-link" href="/codespace#updates">阅读更新</a>
          </div>

          <ul class="updates-list">
            <TimelineItem v-for="item in updates" :key="item.id" :item="item" />
          </ul>
        </div>

        <section id="about" class="about-panel card-surface">
          <div class="about-avatar">
            <img src="https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=320&q=80" alt="about avatar" />
          </div>
          <div class="about-copy">
            <p class="section-kicker">About</p>
            <h2>一个长期维护的小站</h2>
            <p>
              平时会写项目实现、部署过程和一些能复用的小工具。更新不追求频率，尽量让每一篇都能回头再用。
            </p>
            <a class="button-ghost button-small" href="/#about">About me / 了解更多</a>
          </div>
        </section>
      </section>
    </main>

    <FooterBar />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";

import FooterBar from "../components/FooterBar.vue";
import HeaderBar from "../components/HeaderBar.vue";
import DemoCard from "../components/home-page/DemoCard.vue";
import ProjectCard from "../components/home-page/ProjectCard.vue";
import TimelineItem from "../components/home-page/TimelineItem.vue";

const isMobileMenuOpen = ref(false);

const projects = ref([
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
    tutorialLink: "/codespace#projects",
    repoLink: "https://github.com/example/frp-notes",
  },
]);

const demos = ref([
  {
    id: 1,
    title: "Realtime Whiteboard",
    description: "支持多房间协作、基础绘图和状态同步的在线白板 Demo。",
    status: "done",
    demoLink: "/whiteboard",
    repoLink: "https://github.com/example/realtime-whiteboard",
  },
  {
    id: 2,
    title: "CodeSpace Playground",
    description: "放一些小型实验和过程性页面，用来验证交互和布局想法。",
    status: "building",
    demoLink: "/codespace",
    repoLink: "https://github.com/example/codespace-playground",
  },
  {
    id: 3,
    title: "Cloud Drive Share",
    description: "一个轻量共享页，记录文件上传、访问和基础权限控制的实现方式。",
    status: "done",
    demoLink: "/clouddrive",
    repoLink: "https://github.com/example/cloud-drive-share",
  },
  {
    id: 4,
    title: "Prompt Lab",
    description: "整理一些实验性工具和脚手架，边做边记录可行的交互方式。",
    status: "experimental",
    demoLink: "https://example.com/demo/prompt-lab",
    repoLink: "https://github.com/example/prompt-lab",
  },
]);

const updates = ref([
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
]);

function onToggleMobileMenu() {
  isMobileMenuOpen.value = true;
  document.body.style.overflow = "hidden";
}

function onCloseMobileMenu() {
  isMobileMenuOpen.value = false;
  document.body.style.overflow = "";
}

function onResize() {
  if (window.innerWidth > 840) {
    onCloseMobileMenu();
  }
}

onMounted(() => {
  window.addEventListener("resize", onResize);
});

onBeforeUnmount(() => {
  document.body.style.overflow = "";
  window.removeEventListener("resize", onResize);
});
</script>

<style scoped>
@import url("../assets/views/mobile-overlay.css");

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
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.card-surface:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
  border-color: #d7dfe8;
}

.hero-section {
  display: grid;
  grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.98fr);
  gap: 24px;
  margin-bottom: 72px;
}

.hero-copy {
  padding: 40px;
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
}

.preview-card--feature {
  padding: 28px;
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
}

.preview-status {
  padding: 6px 10px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
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
  border: 1px solid #dbe3ef;
  background: #f8fafc;
  color: #475569;
  font-size: 12px;
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
  background:
    linear-gradient(#0f172a, #0f172a) 18px 20px / 42% 6px no-repeat,
    linear-gradient(#2563eb, #2563eb) 18px 42px / 68% 6px no-repeat,
    linear-gradient(#cbd5e1, #cbd5e1) 18px 64px / 54% 6px no-repeat,
    linear-gradient(#e2e8f0, #e2e8f0) 18px 86px / 74% 6px no-repeat,
    linear-gradient(135deg, #f8fafc, #eff6ff);
}

.preview-screenshot--board span {
  background:
    radial-gradient(circle at 22% 26%, #2563eb 0 10px, transparent 11px),
    radial-gradient(circle at 55% 40%, #93c5fd 0 14px, transparent 15px),
    radial-gradient(circle at 74% 68%, #0f172a 0 8px, transparent 9px),
    linear-gradient(#dbeafe, #dbeafe) 22% 26% / 34% 2px no-repeat,
    linear-gradient(#dbeafe, #dbeafe) 55% 40% / 26% 2px no-repeat,
    linear-gradient(180deg, #f8fafc, #eff6ff);
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
  padding: 26px;
  border-radius: 28px;
  background: #f8fafc;
  border: 1px solid #eef2f7;
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
  padding: 28px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 24px;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.04);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.about-panel:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.08);
  border-color: #d7dfe8;
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

.mobile-sidebar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-sidebar-logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #ffffff url("../assets/svgs/logo-32.svg") no-repeat center / 22px;
  border: 1px solid #dbe3ef;
}

.mobile-sidebar-title {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.mobile-sidebar-subtitle {
  margin-top: 2px;
  font-size: 12px;
  color: #94a3b8;
}

.mobile-sidebar-body {
  padding: 14px 18px 24px;
}

.mobile-sidebar-note {
  margin-top: 18px;
  padding-top: 18px;
  border-top: 1px solid #e5e7eb;
  color: #64748b;
  line-height: 1.7;
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
