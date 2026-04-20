<template>
  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="onToggleMobileMenu" :route-name="'Code Space'" :show-mobile-menu="false" />

  <div class="main-container">
    <main class="livedemo-shell">
      <section class="livedemo-heading">
        <div>
          <p class="page-kicker">Code Space</p>
          <h1>项目预览</h1>
        </div>
        <span class="project-count">{{ mockData.length }} 个项目</span>
      </section>

      <section class="home-content" aria-label="项目列表">
        <!-- 卡片 -->
        <article v-for="c in mockData" :key="c.title || c.url || c.previewgif" class="code-space-card">
          <div class="card-window-bar" aria-hidden="true">
            <span></span>
            <span></span>
            <span></span>
          </div>

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
              打开预览
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
              查看源码
            </a>
            <button v-else class="btn btn-secondary" disabled title="暂无源码">查看源码</button>
          </div>
        </article>
      </section>
    </main>
  </div>

  <!-- 底部 -->
  <FooterBar />
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";

import { ref, onMounted } from "vue";
import { getAllLiveDemos } from "../utils/apis";

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
 * 获取所有的livedemo配置项
 * @returns {Promise<Array>} 返回livedemo配置项数组
 */
onMounted(async () => {
  const res = await getAllLiveDemos();
  mockData.value = res || [];
});
</script>

<style scoped>
@import url("../assets/views/main-container.css");

.main-container {
  width: min(1180px, calc(100% - 40px));
  max-width: 1180px;
  display: block;
  padding: 110px 0 72px;
}

.livedemo-shell {
  display: grid;
  gap: 26px;
}

.livedemo-heading {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 20px;
  padding-bottom: 18px;
  border-bottom: 2px solid #111827;
}

.page-kicker {
  margin: 0 0 8px;
  color: #2563eb;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.livedemo-heading h1 {
  margin: 0;
  color: #111827;
  font-size: 34px;
  line-height: 1.08;
  letter-spacing: 0;
}

.project-count {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 12px;
  border: 2px solid #111827;
  background: #facc15;
  color: #111827;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 3px 3px 0 #111827;
  white-space: nowrap;
}

.home-content {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 34px;
}

.code-space-card {
  position: relative;
  display: grid;
  grid-template-rows: auto auto auto auto 1fr auto;
  min-height: 100%;
  padding: 0;
  overflow: hidden;
  border: 2px solid #111827;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 6px 6px 0 #111827;
  transition: transform 140ms ease, box-shadow 140ms ease;
}

.code-space-card:hover {
  transform: translate(-2px, -2px);
  box-shadow: 8px 8px 0 #111827;
}

.card-window-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  height: 30px;
  padding: 0 10px;
  border-bottom: 2px solid #111827;
  background: #e2e8f0;
}

.card-window-bar span {
  width: 9px;
  height: 9px;
  border: 2px solid #111827;
  background: #ffffff;
}

.card-window-bar span:nth-child(1) {
  background: #ef4444;
}

.card-window-bar span:nth-child(2) {
  background: #facc15;
}

.card-window-bar span:nth-child(3) {
  background: #22c55e;
}

.preview-title {
  min-height: 70px;
  padding: 16px 16px 12px;
  color: #111827;
  font-size: 18px;
  font-weight: 850;
  line-height: 1.24;
  border-bottom: 1px solid #cbd5e1;
}

.preview-title span {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.preview-gif {
  width: 100%;
  margin: 0;
  padding: 12px;
  aspect-ratio: 16 / 10;
  overflow: hidden;
  border-bottom: 2px solid #111827;
  background: linear-gradient(45deg, #e2e8f0 25%, transparent 25%), linear-gradient(-45deg, #e2e8f0 25%, transparent 25%),
    linear-gradient(45deg, transparent 75%, #e2e8f0 75%), linear-gradient(-45deg, transparent 75%, #e2e8f0 75%);
  background-color: #f8fafc;
  background-position: 0 0, 0 8px, 8px -8px, -8px 0;
  background-size: 16px 16px;
}

.preview-gif img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  border: 2px solid #111827;
  border-radius: 4px;
  background: #ffffff;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 42px;
  padding: 12px 16px 0;
}

.chip {
  display: inline-flex;
  align-items: center;
  max-width: 100%;
  min-height: 24px;
  padding: 0 8px;
  overflow: hidden;
  border: 1px solid #111827;
  border-radius: 4px;
  background: #dbeafe;
  color: #111827;
  font-size: 12px;
  font-weight: 750;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chip-muted {
  background: #f1f5f9;
  color: #475569;
}

.preview-description {
  min-height: 78px;
  margin: 0;
  padding: 12px 16px 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.55;
  text-align: left;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 3;
}

.actions {
  display: flex;
  align-items: stretch;
  gap: 10px;
  padding: 16px;
}

.btn,
.btn-secondary {
  flex: 1 1 0;
  min-width: 0;
  min-height: 40px;
  padding: 0 14px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #111827;
  border-radius: 6px;
  color: #111827;
  font-size: 13px;
  font-weight: 850;
  text-decoration: none;
  cursor: pointer;
  box-shadow: 3px 3px 0 #111827;
  transition: transform 120ms ease, box-shadow 120ms ease, background-color 120ms ease, opacity 120ms ease;
}

.btn {
  background: #93c5fd;
}

.btn:hover {
  background: #bfdbfe;
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0 #111827;
}

.btn:active {
  transform: translate(2px, 2px);
  box-shadow: 1px 1px 0 #111827;
}

.btn:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.28), 3px 3px 0 #111827;
}

.btn[disabled] {
  cursor: not-allowed;
  opacity: 0.55;
  transform: none;
  box-shadow: 3px 3px 0 #111827;
}

.btn-secondary {
  background: #ffffff;
}

.btn-secondary:hover {
  background: #f8fafc;
}

@media (prefers-reduced-motion: reduce) {
  .code-space-card,
  .btn {
    transition: none;
  }
}

@media (max-width: 768px) {
  .main-container {
    width: calc(100% - 28px);
    padding-top: 92px;
    padding-bottom: 48px;
  }

  .livedemo-shell {
    gap: 18px;
  }

  .livedemo-heading {
    align-items: start;
    flex-direction: column;
    gap: 12px;
  }

  .livedemo-heading h1 {
    font-size: 28px;
  }

  .home-content {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .code-space-card {
    box-shadow: 5px 5px 0 #111827;
  }

  .code-space-card:hover {
    transform: none;
    box-shadow: 5px 5px 0 #111827;
  }

  .preview-title {
    min-height: auto;
    font-size: 17px;
  }

  .preview-gif {
    padding: 10px;
    aspect-ratio: 4 / 3;
  }

  .actions {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .main-container {
    width: calc(100% - 22px);
  }

  .code-space-card {
    border-radius: 6px;
  }

  .preview-title {
    font-size: 15px;
  }

  .preview-description {
    min-height: auto;
    font-size: 13px;
    line-height: 1.5;
  }

  .project-count {
    width: 100%;
    justify-content: center;
  }
}
</style>
