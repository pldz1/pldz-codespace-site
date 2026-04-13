<template>
  <!-- 移动端侧边栏 -->
  <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="closeMobileMenu"></div>
  <div v-show="isMobileMenuOpen" class="mobile-sidebar">
    <div class="mobile-sidebar-header">
      <div class="logo">爬楼的猪 Dev</div>
      <button class="close-btn" @click="closeMobileMenu">×</button>
    </div>
    <div class="nav-placeholder"></div>
    <div class="mobile-sidebar-container" ref="mobileSidebarContainerRef"></div>
  </div>

  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="toggleMobileMenu"></HeaderBar>

  <!-- 主体内容 -->
  <div class="main-container article-layout" id="article-main-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar sidebar-sticky" ref="mainSidebarContainerRef">
      <div class="sidebar-item sidebar-card sidebar-article-chapter" ref="articleChapterRef">
        <ChapterBlock :headings="headings"></ChapterBlock>
      </div>
    </aside>
    <!-- 中间内容区 -->
    <main class="content article-shell">
      <div class="article-header card-surface">
        <h1 class="article-title">{{ article.meta.title }}</h1>
        <div class="article-meta">
          <span class="article-meta-item"> 最新日期: {{ article.meta.date }}</span>
          <span>👀 {{ article.views }} 次</span>
          <span>🏷️ 专栏：{{ article.meta.category }}</span>
        </div>
      </div>

      <div class="article-content card-surface">
        <article class="markdown-body" v-html="renderedHtml"></article>
      </div>
      <div class="next-previous-article card-surface">
        <span>其他文章</span>
        <PrevNext :id="article.id" :category="article.meta.category"></PrevNext>
      </div>
      <div class="comments-content card-surface">
        <span> 评论留言 </span>
        <CommentForm :article-id="article.id"></CommentForm>
      </div>
    </main>
  </div>

  <!-- 反馈按钮 -->
  <div class="to-top top-icon" id="to-top" @click="onToTop"></div>
  <div class="to-bottom message-icon" id="to-bottom" @click="onToBottom"></div>
  <div v-show="article.meta.csdn" class="to-csdn csdn-icon" id="to-csdn" @click="onGotoLink(article.meta.csdn)"></div>
  <div v-show="article.meta.juejin" class="to-juejin juejin-icon" id="to-juejin" @click="onGotoLink(article.meta.juejin)"></div>
  <div v-show="article.meta.github" class="to-github github-icon" id="to-github" @click="onGotoLink(article.meta.github)"></div>
  <div v-show="article.meta.gitee" class="to-gitee gitee-icon" id="to-gitee" @click="onGotoLink(article.meta.gitee)"></div>

  <div class="fab-container">
    <div class="fab-actions">
      <div class="fab-item message-icon" @click="onToBottom" id="to-bottom" title="到底部"></div>
      <div class="fab-item top-icon" @click="onToTop" id="to-top" title="到顶部"></div>
      <div v-show="article.meta.csdn" class="fab-item csdn-icon" id="to-csdn" @click="onGotoLink(article.meta.csdn)" title="CSDN"></div>
      <div v-show="article.meta.juejin" class="fab-item juejin-icon" id="to-juejin" @click="onGotoLink(article.meta.juejin)" title="掘金"></div>
      <div v-show="article.meta.github" class="fab-item github-icon" id="to-github" @click="onGotoLink(article.meta.github)" title="GitHub"></div>
      <div v-show="article.meta.gitee" class="fab-item gitee-icon" id="to-gitee" @click="onGotoLink(article.meta.gitee)" title="Gitee"></div>
    </div>
  </div>

  <!-- 底部的信息栏 -->
  <FooterBar></FooterBar>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";

import ChapterBlock from "../components/article-page/ChapterBlock.vue";
import PrevNext from "../components/article-page/PrevNext.vue";
import CommentForm from "../components/article-page/CommentForm.vue";

import { ref, onActivated, watch } from "vue";
import { getArticle } from "../utils/apis";
import { renderMarkdown } from "../utils/markdown.js";

const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
});

const isMobileMenuOpen = ref(false);
const mainSidebarContainerRef = ref(null);
const mobileSidebarContainerRef = ref(null);
const articleChapterRef = ref(null);

const article = ref({ id: "", content: "", meta: { title: "", date: "", category: "", tags: [], csdn: "", juejin: "", github: "", gitee: "" }, views: 0 });
const renderedHtml = ref("");
const headings = ref([]);

function closeMobileMenu() {
  isMobileMenuOpen.value = false;
  if (mainSidebarContainerRef.value && articleChapterRef.value) {
    mainSidebarContainerRef.value.appendChild(articleChapterRef.value);
  }
}

function toggleMobileMenu() {
  isMobileMenuOpen.value = true;
  if (mobileSidebarContainerRef.value && articleChapterRef.value) {
    mobileSidebarContainerRef.value.appendChild(articleChapterRef.value);
  }
}

/**
 * 滚动到页面顶部
 * @returns {void}
 */
function onToTop() {
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/**
 * 滚动到页面底部
 * @returns {void}
 */
function onToBottom() {
  window.scrollTo({ top: document.body.scrollHeight, behavior: "smooth" });
}

function onGotoLink(url) {
  window.open(url, "_blank");
}

function updateRenderedContent() {
  const result = renderMarkdown(article.value.content || "");
  renderedHtml.value = result.html;
  headings.value = result.headings;
}

/**
 * 组件激活时获取文章内容
 */
onActivated(async () => {
  const res = await getArticle(props.id);
  if (!res) return;

  article.value = res;
  updateRenderedContent();
});

/**
 * 监听窗口大小变化，自动关闭移动端菜单
 */
watch(
  () => window.innerWidth,
  (newWidth) => {
    if (newWidth > 768) {
      closeMobileMenu();
    }
  }
);

watch(
  () => article.value.content,
  () => {
    updateRenderedContent();
  }
);
</script>

<style scoped>
@import url("../assets/views/main-container.css");
@import url("../assets/views/mobile-overlay.css");

:global(body) {
  background: #f8fafc;
  color: #0f172a;
}

.article-layout {
  max-width: 1240px;
  padding-top: 88px;
  padding-left: 20px;
  padding-right: 20px;
  padding-bottom: 40px;
  gap: 28px;
  align-items: flex-start;
}

.card-surface,
.sidebar-card,
.article-shell {
  background: transparent;
  border: none;
  border-radius: 0;
  box-shadow: none;
}

.sidebar {
  width: 232px;
  box-sizing: border-box;
  background: transparent;
  border-radius: 0;
  padding: 8px 28px 0 0;
  border-right: 1px solid #e2e8f0;
}

.sidebar-sticky {
  position: sticky;
  top: 92px;
  height: calc(100vh - 92px);
}

.sidebar-article-chapter {
  max-height: calc(100vh - 120px);
}

.article-shell {
  background: transparent;
  border: none;
  box-shadow: none;
  display: grid;
  gap: 24px;
  max-width: none;
  min-width: 0;
  padding-left: 4px;
}

.content.article-shell {
  max-width: 880px;
}

.article-header {
  padding: 8px 0 0;
  background: transparent;
  border: none;
  border-radius: 0;
  box-shadow: none;
  max-width: 780px;
}

.article-title {
  font-size: clamp(34px, 5vw, 52px);
  font-weight: 800;
  color: #0f172a;
  margin: 0 0 16px;
  line-height: 1.04;
  letter-spacing: -0.05em;
}

.article-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  color: #5b687c;
  font-size: 13px;
}

.article-meta span {
  display: inline-flex;
  align-items: center;
  min-height: 30px;
  padding: 0 11px;
  border-radius: 999px;
  border: 1px solid rgba(203, 213, 225, 0.8);
  background: rgba(255, 255, 255, 0.7);
}

.article-meta-item {
  color: #334155;
}

.article-content {
  padding: 0;
  line-height: 1.8;
  font-size: 16px;
  max-width: 780px;
}

.next-previous-article {
  padding: 22px 0 0;
  background: transparent;
  border: none;
  border-top: 1px solid #e2e8f0;
  border-radius: 0;
  max-width: 780px;
}

.comments-content {
  padding: 22px 0 0;
  min-height: 600px;
  background: transparent;
  border: none;
  border-top: 1px solid #e2e8f0;
  border-radius: 0;
  max-width: 780px;
}

.comments-content span,
.next-previous-article span {
  display: inline-block;
  margin-bottom: 18px;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #0f172a;
}

.sidebar-card {
  overflow: hidden;
}

.markdown-body {
  color: #334155;
  font-size: 18px;
  line-height: 1.95;
  word-break: break-word;
  max-width: 100%;
}

.markdown-body :deep(*) {
  box-sizing: border-box;
}

.markdown-body :deep(> *:first-child) {
  margin-top: 0;
}

.markdown-body :deep(> *:last-child) {
  margin-bottom: 0;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  color: #0f172a;
  line-height: 1.12;
  letter-spacing: -0.04em;
  margin-top: 2.1em;
  margin-bottom: 0.9em;
  scroll-margin-top: 96px;
}

.markdown-body :deep(h1) {
  font-size: 2.4rem;
}

.markdown-body :deep(h2) {
  font-size: 1.9rem;
  padding-bottom: 0.42em;
  border-bottom: 1px solid rgba(226, 232, 240, 0.95);
}

.markdown-body :deep(h3) {
  font-size: 1.5rem;
}

.markdown-body :deep(h4) {
  font-size: 1.22rem;
}

.markdown-body :deep(p),
.markdown-body :deep(ul),
.markdown-body :deep(ol),
.markdown-body :deep(blockquote),
.markdown-body :deep(table),
.markdown-body :deep(pre) {
  margin: 1em 0;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 1.4em;
}

.markdown-body :deep(li + li) {
  margin-top: 0.4em;
}

.markdown-body :deep(a) {
  color: #2563eb;
  text-decoration: none;
}

.markdown-body :deep(a:hover) {
  text-decoration: underline;
}

.markdown-body :deep(code) {
  padding: 0.16em 0.42em;
  border-radius: 8px;
  background: #eef2ff;
  color: #3347c7;
  font-size: 0.92em;
  font-family: "JetBrains Mono", "SFMono-Regular", Consolas, monospace;
}

.markdown-body :deep(pre) {
  padding: 22px 24px;
  border-radius: 16px;
  background: linear-gradient(180deg, #0f172a 0%, #111827 100%);
  color: #e2e8f0;
  overflow-x: auto;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.12);
}

.markdown-body :deep(pre code) {
  padding: 0;
  background: transparent;
  color: inherit;
}

.markdown-body :deep(blockquote) {
  padding: 16px 18px;
  border-left: 3px solid #60a5fa;
  border-radius: 0 18px 18px 0;
  background: linear-gradient(90deg, rgba(241, 245, 249, 0.92), rgba(248, 250, 252, 0.98));
  color: #475569;
}

.markdown-body :deep(hr) {
  border: none;
  height: 1px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0), rgba(148, 163, 184, 0.7), rgba(148, 163, 184, 0));
  margin: 2em 0;
}

.markdown-body :deep(img) {
  display: block;
  max-width: 100%;
  height: auto;
  margin: 1.6em auto;
  border-radius: 16px;
  box-shadow: none;
}

.markdown-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid #e5e7eb;
}

.markdown-body :deep(thead) {
  background: #f8fafc;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 12px 14px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}

.markdown-body :deep(tr:last-child td) {
  border-bottom: none;
}

.to-top,
.to-bottom,
.to-csdn,
.to-juejin,
.to-github,
.to-gitee {
  position: fixed;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 30;
}

.to-top {
  right: 20px;
  bottom: 20px;
}

.top-icon {
  background: url("../assets/svgs/top-48.svg") no-repeat center;
  background-size: 60%;
}

.to-bottom {
  right: 20px;
  bottom: 80px;
}

.message-icon {
  background: url("../assets/svgs/message-48.svg") no-repeat center;
  background-size: 60%;
}

.to-csdn {
  right: 20px;
  bottom: 140px;
}

.csdn-icon {
  background: url("../assets/svgs/csdn-48.svg") no-repeat center;
  background-size: 60%;
}

.to-juejin {
  right: 20px;
  bottom: 200px;
}

.juejin-icon {
  background: url("../assets/svgs/juejin-48.svg") no-repeat center;
  background-size: 60%;
}

.to-github {
  right: 20px;
  bottom: 260px;
}

.github-icon {
  background: url("../assets/svgs/github-48.svg") no-repeat center;
  background-size: 60%;
}

.to-gitee {
  right: 20px;
  bottom: 320px;
}

.gitee-icon {
  background: url("../assets/svgs/gitee-48.svg") no-repeat center;
  background-size: 60%;
}

/* 使用 FAB 后，默认隐藏原有固定按钮（所有屏幕尺寸） */
.to-bottom,
.to-top,
.to-csdn,
.to-juejin,
.to-github,
.to-gitee {
  display: none !important;
}

.fab-container {
  position: fixed;
  right: 18px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.fab-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.fab-item {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  background-size: 60% !important;
  background-position: center !important;
  background-repeat: no-repeat !important;
}

/* 响应式设计 */
@media (max-width: 1200px) {
}

@media (max-width: 992px) {
}

@media (max-width: 768px) {
  .article-layout {
    padding-top: 78px;
    padding-left: 14px;
    padding-right: 14px;
    gap: 16px;
    max-width: 100%;
  }

  .sidebar-sticky {
    position: static;
    height: auto;
  }

  .sidebar {
    width: 100%;
    padding: 0 0 12px;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }

  .article-title {
    font-size: 34px;
  }

  .article-header,
  .article-content,
  .next-previous-article,
  .comments-content {
    padding-left: 0;
    padding-right: 0;
    max-width: none;
  }

  .to-bottom,
  .to-top {
    width: 45px;
    height: 45px;
  }

  .to-top {
    right: 15px;
    bottom: 15px;
  }

  .to-bottom {
    right: 15px;
    bottom: 80px;
  }
}

@media (max-width: 480px) {
  .article-title {
    font-size: 28px;
  }
}

/* 横屏小屏幕优化 */
@media (max-width: 768px) and (orientation: landscape) {
}
</style>
  .fab-container {
    right: 14px;
  }
