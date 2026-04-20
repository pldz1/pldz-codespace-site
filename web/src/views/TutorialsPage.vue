<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="Articles, notes, demos">
    <p>教程页</p>
    <p>{{ isSeriesView ? "当前专栏的系列文章。" : "按专栏整理全部教程。" }}</p>
  </MobileDrawer>

  <HeaderBar :route-name="'教程'" @toggle-mobile-menu="onToggleMobileMenu" />

  <div class="tutorials-page">
    <main class="tutorials-main">
      <section class="tutorials-hero">
        <div class="hero-copy">
          <p class="page-kicker">Articles / Tutorials</p>
          <p class="page-description">{{ pageTitle }}</p>
        </div>

        <div class="toolbar">
          <a v-if="isSeriesView" class="back-link" href="/articles">返回专栏</a>
          <button
            v-for="option in sortOptions"
            :key="option.value"
            :class="['sort-chip', { active: sortBy === option.value }]"
            type="button"
            @click="sortBy = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </section>

      <section class="tutorials-summary">
        <span>共 {{ sortedArticles.length }} {{ isSeriesView ? "篇" : "个专栏" }}</span>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
      </section>

      <section class="article-list" :aria-label="isSeriesView ? '系列文章列表' : '专栏列表'">
        <article v-for="article in pagedArticles" :key="article.id" class="article-row">
          <a class="article-cover" :href="getArticleLink(article)" :aria-label="article.title">
            <img :src="article.thumbnail || defaultCover" :alt="article.title" loading="lazy" decoding="async" />
          </a>

          <div class="article-copy">
            <div class="article-meta">
              <span class="meta-pill">{{ article.category || "others" }}</span>
              <span v-if="isSeriesView">第 {{ article.serialNo }} 篇</span>
              <span>{{ article.date || "暂无日期" }}</span>
              <span>{{ article.views || 0 }} 次浏览</span>
            </div>

            <h2>
              <a :href="getArticleLink(article)">{{ article.title }}</a>
            </h2>

            <p>{{ article.summary || "暂无摘要。" }}</p>

            <div class="article-footer">
              <div class="tag-list">
                <span v-for="tag in article.tags || []" :key="tag" class="tag-chip">{{ tag }}</span>
              </div>

              <a class="article-link" :href="getArticleLink(article)">{{ isSeriesView ? "查看文章" : "进入系列" }}</a>
            </div>
          </div>
        </article>
      </section>

      <nav v-if="totalPages > 1" class="pagination" aria-label="文章分页">
        <button class="page-button" type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">上一页</button>
        <button v-for="page in visiblePages" :key="page" :class="['page-number', { active: page === currentPage }]" type="button" @click="goToPage(page)">
          {{ page }}
        </button>
        <button class="page-button" type="button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">下一页</button>
      </nav>
    </main>

    <FooterBar />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";

import FooterBar from "../components/FooterBar.vue";
import HeaderBar from "../components/HeaderBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
import { getArticleIntros, getArticlesByCategory } from "../utils/apis";

const defaultCover = "/404.jpg";
const isMobileMenuOpen = ref(false);
const route = useRoute();

const sortBy = ref("date");
const articles = ref([]);
const currentPage = ref(1);
const pageSize = 8;

const activeCategory = computed(() => {
  const value = route.params.category;
  return Array.isArray(value) ? value[0] || "" : value || "";
});

const isSeriesView = computed(() => Boolean(activeCategory.value));
const pageTitle = computed(() => (isSeriesView.value ? `${activeCategory.value} 系列` : "教程专栏"));
const sortOptions = computed(() => {
  const options = [
    { label: "按时间", value: "date" },
    { label: "按浏览", value: "views" },
  ];

  if (isSeriesView.value) {
    return [{ label: "按序号", value: "serial" }, ...options];
  }

  return options;
});

const parseDate = (value) => {
  const time = new Date(value || "").getTime();
  return Number.isNaN(time) ? 0 : time;
};

const sortedArticles = computed(() => {
  const cloned = [...articles.value];

  if (sortBy.value === "views") {
    return cloned.sort((a, b) => (b.views || 0) - (a.views || 0) || parseDate(b.date) - parseDate(a.date));
  }

  if (sortBy.value === "serial") {
    return cloned.sort((a, b) => (a.serialNo || 0) - (b.serialNo || 0) || parseDate(b.date) - parseDate(a.date));
  }

  return cloned.sort((a, b) => parseDate(b.date) - parseDate(a.date) || (b.views || 0) - (a.views || 0));
});

const totalPages = computed(() => Math.max(1, Math.ceil(sortedArticles.value.length / pageSize)));

const pagedArticles = computed(() => {
  const start = (currentPage.value - 1) * pageSize;
  return sortedArticles.value.slice(start, start + pageSize);
});

const visiblePages = computed(() => {
  const pages = [];
  const start = Math.max(1, currentPage.value - 2);
  const end = Math.min(totalPages.value, start + 4);

  for (let page = start; page <= end; page += 1) {
    pages.push(page);
  }

  return pages;
});

const getArticleLink = (article) => {
  if (isSeriesView.value) {
    return `/article/${article.id}`;
  }

  return `/articles/${encodeURIComponent(article.category || "")}`;
};

const goToPage = (page) => {
  currentPage.value = Math.min(totalPages.value, Math.max(1, page));
  window.scrollTo({ top: 0, behavior: "smooth" });
};

const onToggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const loadArticles = async () => {
  sortBy.value = isSeriesView.value ? "serial" : sortBy.value === "serial" ? "date" : sortBy.value;
  const res = isSeriesView.value ? await getArticlesByCategory(activeCategory.value) : await getArticleIntros();
  articles.value = Array.isArray(res) ? res : [];
  currentPage.value = 1;
};

onMounted(loadArticles);

watch(sortBy, () => {
  currentPage.value = 1;
});

watch(activeCategory, loadArticles);
</script>

<style scoped>
.tutorials-page {
  min-height: 100vh;
  background: #f8fafc;
}

.tutorials-main {
  width: min(1120px, calc(100% - 40px));
  margin: 0 auto;
  padding: 118px 0 72px;
}

.tutorials-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid #e7edf5;
}

.hero-copy {
  display: grid;
  gap: 6px;
}

.page-kicker {
  margin: 0 0 12px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #2563eb;
}

.page-description {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  line-height: 1.45;
  font-weight: 600;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}

.back-link {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 14px;
  border: 1px solid #d9e4f0;
  border-radius: 999px;
  background: #ffffff;
  color: #0f172a;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
}

.back-link:hover {
  border-color: #bfd4ff;
  color: #1d4ed8;
}

.sort-chip {
  height: 38px;
  padding: 0 16px;
  border: 1px solid #d9e4f0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  color: #475569;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, transform 0.2s ease;
}

.sort-chip:hover {
  background: #ffffff;
  border-color: #cbd8e6;
  color: #0f172a;
  transform: translateY(-1px);
}

.sort-chip.active {
  background: #eff6ff;
  border-color: #bfd4ff;
  color: #1d4ed8;
}

.tutorials-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 18px 0 8px;
  color: #94a3b8;
  font-size: 14px;
}

.article-list {
  display: grid;
}

.article-row {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 20px;
  padding: 20px 0;
  border-top: 1px solid #e7edf5;
}

.article-cover {
  display: block;
  overflow: hidden;
  border-radius: 18px;
  background: #eef4f9;
  aspect-ratio: 16 / 10;
}

.article-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.article-copy {
  min-width: 0;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px 14px;
  color: #94a3b8;
  font-size: 12px;
}

.meta-pill,
.tag-chip {
  display: inline-flex;
  align-items: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid #e2eaf3;
  background: rgba(255, 255, 255, 0.7);
  color: #475569;
  font-size: 12px;
}

.article-copy h2 {
  margin: 10px 0 0;
  font-size: 21px;
  line-height: 1.28;
}

.article-copy h2 a {
  color: #0f172a;
  text-decoration: none;
}

.article-copy h2 a:hover {
  color: #1d4ed8;
}

.article-copy p {
  margin: 10px 0 0;
  color: #475569;
  font-size: 14px;
  line-height: 1.72;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-footer {
  margin-top: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.article-link {
  color: #2563eb;
  text-decoration: none;
  font-weight: 600;
  white-space: nowrap;
  font-size: 14px;
}

.article-link:hover {
  color: #1d4ed8;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 28px;
  border-top: 1px solid #e7edf5;
}

.page-button,
.page-number {
  height: 40px;
  min-width: 40px;
  padding: 0 14px;
  border: 1px solid #d9e4f0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  color: #475569;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.page-button:hover,
.page-number:hover {
  background: #ffffff;
  border-color: #cbd8e6;
  color: #0f172a;
}

.page-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.page-number.active {
  background: #eff6ff;
  border-color: #bfd4ff;
  color: #1d4ed8;
}

@media (max-width: 900px) {
  .tutorials-main {
    width: min(100% - 28px, 980px);
    padding-top: 102px;
  }

  .tutorials-hero {
    align-items: start;
    flex-direction: column;
  }

  .article-row {
    grid-template-columns: 1fr;
    gap: 18px;
  }
}

@media (max-width: 640px) {
  .tutorials-main {
    width: calc(100% - 24px);
    padding-top: 92px;
  }

  .tutorials-hero {
    gap: 14px;
    padding-bottom: 14px;
  }

  .page-kicker {
    margin-bottom: 6px;
    font-size: 11px;
  }

  .page-description {
    font-size: 16px;
  }

  .toolbar {
    width: 100%;
  }

  .sort-chip {
    flex: 1 1 calc(50% - 5px);
    justify-content: center;
  }

  .tutorials-summary,
  .article-footer {
    align-items: start;
    flex-direction: column;
  }

  .tutorials-summary {
    padding-top: 14px;
    gap: 6px;
    font-size: 13px;
  }

  .article-row {
    gap: 14px;
    padding: 16px 0;
  }

  .article-cover {
    border-radius: 16px;
  }

  .article-meta {
    gap: 8px 10px;
    font-size: 11px;
  }

  .meta-pill,
  .tag-chip {
    height: 24px;
    padding: 0 9px;
    font-size: 11px;
  }

  .article-copy h2 {
    font-size: 18px;
    line-height: 1.34;
  }

  .article-copy p {
    font-size: 13px;
    line-height: 1.7;
  }

  .article-link {
    font-size: 13px;
  }

  .pagination {
    gap: 8px;
    padding-top: 22px;
    justify-content: flex-start;
  }

  .page-button,
  .page-number {
    height: 36px;
    min-width: 36px;
    padding: 0 12px;
    font-size: 13px;
  }
}
</style>
