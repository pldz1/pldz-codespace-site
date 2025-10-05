<template>
  <!-- 移动端侧边栏 -->
  <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="closeMobileMenu"></div>
  <div v-show="isMobileMenuOpen" class="mobile-sidebar">
    <div class="mobile-sidebar-header">
      <div class="logo">爬楼的猪 CodeSpace</div>
      <button class="close-btn" @click="closeMobileMenu">×</button>
    </div>
    <div class="mobile-sidebar-container" ref="mobileSidebarContainerRef"></div>
  </div>

  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="toggleMobileMenu"></HeaderBar>

  <!-- 主体内容 -->
  <div class="main-container" id="article-main-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar sidebar-sticky" ref="mainSidebarContainerRef">
      <div class="sidebar-item sidebar-article-chapter" ref="articleChapterRef">
        <ChapterBlock :editor-id="state.id" :theme="state.theme"></ChapterBlock>
      </div>

      <div class="sidebar-item sidebar-article-related">
        <RelatedRecom :article="article"></RelatedRecom>
      </div>
    </aside>
    <!-- 中间内容区 -->
    <main class="content">
      <div class="article-header">
        <h1 class="article-title">{{ article.meta.title }}</h1>
        <div class="article-meta">
          <span class="article-meta-item"> 最新日期: {{ article.meta.date }}</span>
          <span>👀 {{ article.views }} 次</span>
          <span>🏷️ 专栏：{{ article.meta.category }}</span>
          <span v-if="isadmin" class="article-edit" @click="onEditArticle"> 重新编辑 </span>
        </div>
      </div>

      <div class="article-content">
        <MdPreview :id="state.id" :theme="state.theme" :codeFoldable="false" v-model="article.content" />
      </div>
      <div class="next-previous-article">
        <span>其他文章</span>
        <PrevNext :id="article.id" :category="article.meta.category"></PrevNext>
      </div>
      <div class="comments-content">
        <span> 评论留言 </span>
        <CommentForm :article-id="article.id"></CommentForm>
      </div>
    </main>

    <!-- 右侧边栏 -->
    <aside class="right-sidebar sidebar-sticky">
      <AdBanner></AdBanner>
    </aside>
  </div>

  <!-- 反馈按钮 -->
  <div class="to-top top-icon" id="to-top" @click="onToTop"></div>
  <div class="to-bottom message-icon" id="to-bottom" @click="onToBottom"></div>
  <div v-show="article.meta.csdn" class="to-csdn csdn-icon" id="to-csdn" @click="onToCsdn"></div>
  <div v-show="article.meta.juejin" class="to-juejin juejin-icon" id="to-juejin" @click="onToJuejin"></div>
  <div v-show="article.meta.github" class="to-github github-icon" id="to-github" @click="onToGithub"></div>
  <div v-show="article.meta.gitee" class="to-gitee gitee-icon" id="to-gitee" @click="onToGitee"></div>

  <!-- 底部的信息栏 -->
  <FooterBar></FooterBar>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import AdBanner from "../components/AdBanner.vue";

import ChapterBlock from "../components/article-page/ChapterBlock.vue";
import PrevNext from "../components/article-page/PrevNext.vue";
import CommentForm from "../components/article-page/CommentForm.vue";
import RelatedRecom from "../components/article-page/RelatedRecom.vue";

import ToolTip from "../utils/tooltip.js";

import { ref, onActivated, watch, computed, reactive } from "vue";
import { useRouter } from "vue-router";
import { getArticle } from "../utils/apis";
import { useStore } from "vuex";

import { MdPreview } from "md-editor-v3";

const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
});

const router = useRouter();

const state = reactive({
  theme: "light",
  id: "my-editor",
});

const isMobileMenuOpen = ref(false);
const mainSidebarContainerRef = ref(null);
const mobileSidebarContainerRef = ref(null);
const articleChapterRef = ref(null);

// 引入 Vuex store
const store = useStore();
const isadmin = computed(() => store.state.authState.isadmin);

const article = ref({ id: "", content: "", meta: { title: "", date: "", category: "", csdn: "", juejin: "", github: "", gitee: "" }, views: 0 });

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

function onEditArticle() {
  router.push({ path: `/edit/${article.value.id}` });
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

/**
 * 组件激活时获取文章内容
 */
onActivated(async () => {
  const res = await getArticle(props.id);
  if (!res) return;

  article.value = res;

  ToolTip.loadArticleTooltip();
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
</script>

<style scoped>
@import url("../assets/views/main-container.css");
@import url("../assets/views/mobile-overlay.css");

.sidebar-sticky {
  position: sticky;
  top: 80px;
  height: calc(100vh - 80px);
}

.sidebar-article-chapter {
  max-height: calc(100vh - 386px);
}

.sidebar-article-related {
  margin-top: 24px;
}

.article-header {
  margin-bottom: 20px;
}

.article-title {
  font-size: 32px;
  font-weight: bold;
  color: #252933;
  margin-bottom: 16px;
  line-height: 1.2;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  color: #86909c;
  font-size: 14px;
  margin-bottom: 20px;
}

.article-meta-item {
  color: #515767;
}

.article-edit {
  color: #1e80ff;
  cursor: pointer;
}

.article-content {
  line-height: 1.8;
  font-size: 16px;
}

.next-previous-article {
  margin-top: 16px;
  margin-bottom: 16px;
}

.comments-content {
  min-height: 600px;
}

.comments-content span,
.next-previous-article span {
  font-size: 18px;
  font-weight: 900;
}

.sidebar-card-right {
  background-color: transparent;
  display: flex;
  justify-content: flex-end;
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

/* 响应式设计 */
@media (max-width: 1200px) {
}

@media (max-width: 992px) {
}

@media (max-width: 768px) {
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
  }
}

/* 横屏小屏幕优化 */
@media (max-width: 768px) and (orientation: landscape) {
}
</style>
