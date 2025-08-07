<template>
  <!-- 移动端侧边栏 -->
  <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="onCloseMobileMenu()"></div>
  <div v-show="isMobileMenuOpen" class="mobile-sidebar">
    <div class="mobile-sidebar-header">
      <div class="logo">爬楼的猪 CodeSpace</div>
      <button class="close-btn" @click="onCloseMobileMenu()">×</button>
    </div>
    <div class="mobile-sidebar-container" ref="mobileSidebarContainerRef"></div>
  </div>

  <!-- 顶部导航栏 -->
  <HeaderBar :route-name="'首页'" @toggle-mobile-menu="onToggleMobileMenu"></HeaderBar>

  <!-- 主体内容 -->
  <div class="main-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar sidebar-sticky" ref="mainSidebarContainerRef">
      <div class="sidebar-card" ref="sidebarContentRef">
        <div class="sidebar-card-title">专栏</div>
        <div :class="['sidebar-item', { active: activeCategory === '全部文章' }]" @click="onActiveCategory('全部文章')">
          <span class="sidebar-icon">📃</span>
          全部文章
        </div>
        <div
          v-for="(category, index) in allCategories"
          :key="category"
          :class="['sidebar-item', { active: activeCategory === category }]"
          @click="onActiveCategory(category)"
        >
          <span class="sidebar-icon">{{ emojiList[index % emojiList.length] }}</span>
          {{ category }}
        </div>
      </div>
      <div class="sidebar-card">
        <TagsCloud @toggle-tag-filter="onActiveTag" :active-tag="activeTag"></TagsCloud>
      </div>
    </aside>

    <!-- 中间内容区 -->
    <main class="content">
      <!-- 如果显示分类 -->
      <div class="content-tabs">
        <div :class="['tab', sortMode === 'date' ? 'active' : '']" @click="onSortArticles('date')">日期排序</div>
        <div :class="['tab', sortMode === 'serial' ? 'active' : '']" @click="onSortArticles('serial')">序列排序</div>
        <div :class="['tab', sortMode === 'views' ? 'active' : '']" @click="onSortArticles('views')">访问排序</div>
      </div>
      <!-- 中间内容 -->
      <div class="article-list">
        <article v-for="article in allArticles" :key="article.id" class="article-item">
          <div class="article-content">
            <a :href="`/article/${article.id}`" class="article-title">
              {{ article.title }}
            </a>
            <p class="article-excerpt">{{ article.summary }}</p>
            <div class="article-meta">
              <div class="article-info">
                <span class="meta-item">浏览次数: {{ article.views }}</span>
                <span class="meta-item"> 专栏: {{ article.category }}</span>
              </div>
              <div class="article-tags">
                <span v-for="tag in article.tags" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </div>
          <div class="article-thumb">
            <img :src="article.thumbnail" />
          </div>
        </article>
      </div>
    </main>

    <!-- 右侧边栏 -->
    <aside class="right-sidebar sidebar-sticky">
      <div class="sidebar-card">
        <!-- 广告位 -->
        <AdBanner></AdBanner>
      </div>
    </aside>
  </div>

  <!-- 底部隐私数据 -->
  <FooterBar></FooterBar>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import AdBanner from "../components/AdBanner.vue";

import TagsCloud from "../components/home-page/TagsCloud.vue";

import { ref, onMounted, onUnmounted, watch } from "vue";
import { sortByDate, sortByViews, sortBySerialNo } from "../utils/sort.js";
import { getAllArticles, getAllCategories, getArticlesByCategory, getArticlesByTag } from "../utils/apis";

// 用于存储所有文章
const allArticles = ref([]);

// 用于存储所有分类
const allCategories = ref([]);

// 引用移动端和主侧边栏容器
const isMobileMenuOpen = ref(false);
const mobileSidebarContainerRef = ref(null);
const mainSidebarContainerRef = ref(null);
const sidebarContentRef = ref(null);

// 默认排序方式
const sortMode = ref("date");

// 用于存储当前选中的分类
const activeCategory = ref("全部文章");

// 用于存储当前选中的标签
const activeTag = ref("");

// 预定义一些表情符号，用于分类图标
const emojiList = ["⭐", "💡", "🔍", "🌟", "🚀", "💬", "📅"];

/**
 * 处理文章排序事件
 * @param mode {string} 排序模式
 */

function onSortArticles(mode) {
  // 如果当前模式已是所选模式，则不做任何操作
  if (sortMode.value === mode) return;
  sortMode.value = mode;

  sortArticles();
}

function onActiveTag(tag) {
  // 如果点击的是当前标签，则不做任何操作
  if (activeTag.value === tag) return;

  // 设置当前活动标签
  activeTag.value = tag;

  // 根据标签获取文章
  getArticlesByTag(tag).then((res) => {
    allArticles.value = res;
  });

  // 文章排序
  sortArticles();

  // 清除当前活动分类
  activeCategory.value = "";
}

/**
 * 对文章进行排序
 * @param mode {string} 排序模式
 */
function sortArticles() {
  // 根据所选模式对文章进行排序
  if (sortMode.value === "date") {
    allArticles.value = sortByDate(allArticles.value);
  }

  if (sortMode.value === "serial") {
    allArticles.value = sortBySerialNo(allArticles.value);
  }

  if (sortMode.value === "views") {
    allArticles.value = sortByViews(allArticles.value);
  }
}

/**
 * 设置当前活动分类并获取相应的文章
 * @param category {string} 选中的分类
 */
function onActiveCategory(category) {
  // 如果点击的是当前分类，则不做任何操作``
  if (activeCategory.value === category) return;

  // 设置当前活动分类
  activeCategory.value = category;

  // 如果是全部文章，直接获取所有文章
  if (category === "全部文章") {
    getAllArticles().then((res) => {
      allArticles.value = res;
    });
  } else {
    // 否则根据分类获取文章
    getArticlesByCategory(category).then((res) => {
      allArticles.value = res;
    });
  }

  // 清除当前活动分类
  activeTag.value = "";

  // 文章排序
  sortArticles();
}

/**
 * 打开移动端菜单
 */
function onToggleMobileMenu() {
  isMobileMenuOpen.value = true;
  if (mobileSidebarContainerRef.value && sidebarContentRef.value) {
    mobileSidebarContainerRef.value.appendChild(sidebarContentRef.value);
  }
}

/**
 * 关闭移动端菜单
 */
function onCloseMobileMenu() {
  isMobileMenuOpen.value = false;

  if (mainSidebarContainerRef.value && sidebarContentRef.value) {
    mainSidebarContainerRef.value.appendChild(sidebarContentRef.value);
  }
}

/**
 * 在组件挂载时获取所有文章和分类数据和标签统计数据
 */
onMounted(async () => {
  // 获得全部的博客文章
  const res = await getAllArticles();
  if (!res) return;

  allArticles.value = res;

  // 获取所有分类
  const categoryRes = await getAllCategories();
  if (!categoryRes) return;
  allCategories.value = categoryRes;
});

/**
 * 监听窗口大小变化，自动关闭移动端菜单
 */
watch(
  () => window.innerWidth,
  (newWidth) => {
    if (newWidth > 768) {
      onCloseMobileMenu();
    }
  }
);

/**
 * 在组件卸载时清理资源
 */
onUnmounted(() => {});
</script>

<style scoped>
@import url("../assets/views/main-container.css");
@import url("../assets/views/mobile-overlay.css");

.sidebar-sticky {
  position: sticky;
  top: 80px;
  height: fit-content;
}

.sidebar-card {
  padding: 0 8px;
}

.sidebar-card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding: 8px;
  border-bottom: 1px solid #e4e6ea;
}

.sidebar-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  color: #71777c;
  cursor: pointer;
  gap: 10px;
}

.sidebar-item:hover {
  background: #f2f3f5;
}

.sidebar-item.active {
  background: #e8f4ff;
  color: #1e80ff;
}

.sidebar-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content-tabs {
  display: flex;
  border-bottom: 1px solid #e4e6ea;
  padding: 0 20px;
}

.tab {
  padding: 16px 0;
  margin-right: 32px;
  color: #71777c;
  cursor: pointer;
  border-bottom: 2px solid transparent;
}

.tab.active {
  color: #1e80ff;
  border-bottom-color: #1e80ff;
}

.article-list {
  padding: 16px;
}

.article-item {
  padding: 16px;
  border-bottom: 1px solid #f1f1f1;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.article-content {
  flex: 1;
}

.article-content a {
  color: #171717;
  text-decoration: none;
}

.article-title {
  font-size: 18px;
  font-weight: 600;
}

.article-title:hover {
  color: #1e80ff;
}

.article-excerpt {
  color: #86909c;
  font-size: 14px;
  line-height: 1.6;
  margin-bottom: 12px;
  margin-top: 8px;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 13px;
  color: #86909c;
  flex-wrap: wrap;
  justify-content: space-between;
}

.article-info,
.article-tags {
  display: flex;
  gap: 16px;
  flex-direction: row;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tag {
  background: #f2f3f5;
  color: #86909c;
  padding: 4px 8px;
  border-radius: 2px;
  font-size: 12px;
}

.article-thumb {
  width: 120px;
  height: 80px;
  background: #f1f1f1;
  border-radius: 4px;
  margin-left: 20px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}

.article-thumb img {
  height: inherit;
  width: inherit;
  object-fit: contain;
}

/* 响应式设计 */
@media (max-width: 1200px) {
}

@media (max-width: 992px) {
}

@media (max-width: 768px) {
  .article-item {
    flex-direction: column;
    gap: 15px;
  }

  .article-thumb {
    width: 100%;
    height: 160px;
    margin-left: 0;
    order: -1;
  }

  .article-meta {
    flex-wrap: wrap;
    gap: 10px;
  }

  .article-tags {
    margin-left: 0;
    margin-top: 8px;
    width: 100%;
  }
}

@media (max-width: 480px) {
  .article-list {
    padding: 15px;
  }

  .article-item {
    padding: 15px;
  }

  .article-title {
    font-size: 16px;
  }

  .article-excerpt {
    font-size: 13px;
  }
}

/* 横屏小屏幕优化 */
@media (max-width: 768px) and (orientation: landscape) {
}
</style>
