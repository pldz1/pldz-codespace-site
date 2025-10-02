<template>
  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="home">
    <div class="container">
      <div class="home-content">
        <!-- 卡片 -->
        <article v-for="c in mockData" :key="c.title || c.url || c.previewgif" class="code-space-card">
          <!-- 标题 -->
          <header class="preview-title" :title="c.title">
            <span>{{ c.title || "未命名" }}</span>
          </header>

          <!-- 媒体：缩略图 / 悬停切换 GIF -->
          <figure class="preview-gif" @mouseenter="hovered = c.url || c.previewgif || c.thumbnail" @mouseleave="hovered = null">
            <img :src="mediaSrc(c)" :alt="c.title || '预览图'" loading="lazy" decoding="async" @error="(e) => handleImgError(e, c)" />
          </figure>

          <!-- 元信息：日期 + 目录 -->
          <div class="card-meta">
            <time v-if="c.date" class="chip" :datetime="c.date">{{ fmtDate(c.date) }}</time>
            <span v-if="c.folder" class="chip chip-muted" :title="c.folder">{{ c.folder }}</span>
          </div>

          <!-- 描述 -->
          <p v-if="c.description" class="preview-description" :title="c.description">
            {{ c.description }}
          </p>

          <!-- 操作 -->
          <div class="actions">
            <button
              class="btn"
              :aria-label="`打开预览：${c.title}`"
              @click="onGoPreview(c.url)"
              :disabled="!c.url"
              :title="c.url ? '打开预览' : '暂无预览地址'"
            >
              冲 🚀
            </button>

            <a
              v-if="c.sourcelink"
              class="btn btn-secondary"
              :href="c.sourcelink"
              target="_blank"
              rel="noopener noreferrer"
              :aria-label="`查看源码：${c.title}`"
              title="查看源码"
            >
              源码 🌐
            </a>
            <button v-else class="btn btn-secondary" disabled title="暂无源码">源码 🌐</button>
          </div>
        </article>
      </div>
    </div>
  </div>

  <!-- 底部 -->
  <FooterBar />
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";

import { ref, onMounted } from "vue";
import { getAllAdBannerItem } from "../utils/apis";

/**
 * 单个配置项
 * title: 标题
 * folder: 文件夹名称
 * url: 访问链接
 * thumbnail: 缩略图链接
 * previewgif: 预览GIF链接
 * sourcelink: 源代码链接
 * description: 描述
 */
const mockData = ref([]);

const hovered = ref(null);

const onGoPreview = (url) => {
  if (!url) return;
  const final = /^https?:\/\//i.test(url) ? url : `${location.origin.replace(/\/$/, "")}/${url.replace(/^\//, "")}`;
  window.open(final, "_blank");
};

const fmtDate = (dateStr) => {
  // 兼容 YYYY-MM-DD / ISO
  const d = new Date(dateStr);
  if (isNaN(d)) return dateStr;
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const d2 = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${d2}`;
};

const handleImgError = (e, c) => {
  // 优先尝试另一个资源，最终回退 404
  const el = e.target;
  if (el.dataset.fallbackTried === "1") {
    el.src = "/404.jpg";
    return;
  }
  el.dataset.fallbackTried = "1";
  el.src = c.thumbnail && el.src !== c.thumbnail ? c.thumbnail : c.previewgif || "/404.jpg";
};

const mediaSrc = (c) => {
  // 悬停时优先 gif，否则缩略图；都没有则 404
  const preferGif = hovered.value === (c.url || c.previewgif || c.thumbnail);
  const gif = c.previewgif;
  const thumb = c.thumbnail;
  return preferGif && gif ? gif : thumb || gif || "/404.jpg";
};

const onToggleMobileMenu = () => {
  // 保留原逻辑/事件透传
};

/**
 * 获取所有的codespace配置项
 * @returns {Promise<Array>} 返回codespace配置项数组
 */
onMounted(async () => {
  const res = await getAllAdBannerItem();
  mockData.value = res || [];
});
</script>

<style scoped>
/* 设计令牌 */
:root {
  --bg: #f7f9fa;
  --text: #0f172a;
  --muted: #475569;
  --card-bg: #ffffff;
  --radius: 12px;
  --shadow: 0 6px 24px rgba(2, 6, 23, 0.08);
  --ring: 0 0 0 3px rgba(59, 130, 246, 0.35);
  --gap: 24px;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0b1220;
    --text: #e5e7eb;
    --muted: #9aa4b2;
    --card-bg: #111827;
    --shadow: 0 8px 28px rgba(0, 0, 0, 0.45);
  }
}

.home {
  min-height: 100dvh;
  background: var(--bg);
  color: var(--text);
}

.container {
  --side: 20px;
  padding: 48px var(--side);
  max-width: 1200px;
  margin: 0 auto;
  animation: fadeInUp 500ms ease both;
}

/* 默认 3 列 */
.home-content {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--gap);
  align-items: start;
}

/* 卡片 */
.code-space-card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  padding: 16px;
  display: flex;
  flex-direction: column;
  transition: transform 160ms ease, box-shadow 160ms ease;
}

.code-space-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 28px rgba(2, 6, 23, 0.12);
}

/* 标题 */
.preview-title {
  font-size: 18px;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 10px;
}

/* 媒体区：正方形/横屏自适应 */
.preview-gif {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: calc(var(--radius) - 2px);
  overflow: hidden;
  background: #e5e7eb1a;
}
.preview-gif img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* 元信息 */
.card-meta {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1;
  background: #e6eef7;
  color: #1e293b;
}
.chip-muted {
  background: #eef2f5;
  color: var(--muted);
}

/* 描述 */
.preview-description {
  margin-top: 10px;
  color: var(--muted);
  text-align: left;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2; /* 两行省略 */
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 操作区 */
.actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
  align-items: center;
}
.btn,
.btn-secondary {
  height: 40px;
  padding: 0 14px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 120ms ease, transform 120ms ease, box-shadow 120ms ease, opacity 120ms ease;
  text-decoration: none;
}
.btn {
  background-color: #e2e8f0;
  color: #0f172a;
}
.btn:hover {
  background-color: #cbd5e1;
}
.btn:active {
  transform: translateY(1px);
}
.btn:focus-visible {
  outline: none;
  box-shadow: var(--ring);
}
.btn[disabled] {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-secondary {
  background: transparent;
  border-color: rgba(148, 163, 184, 0.35);
  color: var(--text);
}
.btn-secondary:hover {
  background: rgba(148, 163, 184, 0.12);
}

/* 动画无障碍 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
@media (prefers-reduced-motion: reduce) {
  .container {
    animation: none;
  }
  .code-space-card {
    transition: none;
  }
}

/* ───── 你的断点体系 ───── */
@media (max-width: 1200px) {
  .container {
    max-width: 1064px;
  }
  .home-content {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 22px;
  }
}

@media (max-width: 992px) {
  .container {
    max-width: 920px;
    padding-top: 40px;
    padding-bottom: 40px;
  }
  .home-content {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .container {
    --side: 16px;
    padding-top: 32px;
    padding-bottom: 32px;
  }
  .home-content {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .preview-title {
    font-size: 16px;
  }
  .btn,
  .btn-secondary {
    width: 100%;
    height: 36px;
  }
  .preview-gif {
    aspect-ratio: 4 / 3;
  } /* 横屏时更扁，避免占满高度 */

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
  .article-meta {
    flex-wrap: wrap;
    row-gap: 6px;
  }
  .container {
    --side: 14px;
  }
}

@media (max-width: 768px) and (orientation: landscape) {
  .home-content {
    gap: 14px;
  }
  .code-space-card {
    box-shadow: 0 4px 16px rgba(2, 6, 23, 0.08);
  }
}
</style>
