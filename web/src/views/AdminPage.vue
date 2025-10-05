<template>
  <!-- 移动端侧边栏 -->
  <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="onCloseMobileMenu()"></div>
  <div v-show="isMobileMenuOpen" class="mobile-sidebar">
    <div class="mobile-sidebar-header">
      <div class="logo">爬楼的猪 CodeSpace</div>
      <button class="close-btn" @click="onCloseMobileMenu()">×</button>
    </div>
    <div class="nav-placeholder"></div>
    <div class="mobile-sidebar-container" ref="mobileSidebarContainerRef"></div>
  </div>

  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="onToggleMobileMenu"></HeaderBar>

  <!-- 主体内容 -->
  <div class="main-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar sidebar-sticky" ref="mainSidebarContainerRef">
      <div class="sidebar-card" ref="sidebarContentRef">
        <div class="sidebar-card-title">⚙ 菜单</div>

        <div class="sidebar-item" @click="onActiveCard('用户管理')" :style="{ background: backgroundColorList[0] }">
          <span class="sidebar-icon">🤠 </span>
          用户管理
        </div>

        <div class="sidebar-item" @click="onActiveCard('新增文章')" :style="{ background: backgroundColorList[1] }">
          <span class="sidebar-icon">➕ </span>
          新增文章
        </div>

        <div class="sidebar-item" @click="onActiveCard('专栏管理')" :style="{ background: backgroundColorList[2] }">
          <span class="sidebar-icon">📙 </span>
          专栏管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('图片管理')" :style="{ background: backgroundColorList[3] }">
          <span class="sidebar-icon">📷</span>
          图片管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('网站导航管理')" :style="{ background: backgroundColorList[4] }">
          <span class="sidebar-icon">🌐</span>
          网站导航管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('缓存资源管理')" :style="{ background: backgroundColorList[5] }">
          <span class="sidebar-icon">💾</span>
          缓存资源管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('Git插件')" :style="{ background: backgroundColorList[6] }">
          <span class="sidebar-icon">🔁</span>
          Git插件
        </div>
      </div>
    </aside>

    <!-- 中间内容区 -->
    <main class="content">
      <!-- 用户管理 -->
      <UserMgt v-if="activeCard === '用户管理'"></UserMgt>
      <!-- 新增文章 -->
      <ArticleMgt v-if="activeCard === '新增文章'" :all-categories="allCategories"></ArticleMgt>
      <!-- 专栏管理 -->
      <CategoryMgt v-if="activeCard === '专栏管理'" :all-categories="allCategories" @on-update-categories="onOnUpdateCategories"> </CategoryMgt>
      <!-- 图片管理 -->
      <ImageMgt v-if="activeCard === '图片管理'" :all-categories="allCategories"></ImageMgt>
      <!-- 网站导航管理 -->
      <NavMgt v-if="activeCard === '网站导航管理'"></NavMgt>
      <!-- 缓存资源管理 -->
      <CacheMgt v-if="activeCard === '缓存资源管理'"></CacheMgt>
      <!-- 🔁 Git 插件 -->
      <GitPlugin v-if="activeCard === 'Git插件'"></GitPlugin>
    </main>
  </div>

  <!-- 底部隐私数据 -->
  <FooterBar></FooterBar>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";

import UserMgt from "../components/admin-page/UserMgt.vue";
import ArticleMgt from "../components/admin-page/ArticleMgt.vue";
import CategoryMgt from "../components/admin-page/CategoryMgt.vue";
import ImageMgt from "../components/admin-page/ImageMgt.vue";
import NavMgt from "../components/admin-page/NavMgt.vue";
import CacheMgt from "../components/admin-page/CacheMgt.vue";
import GitPlugin from "../components/admin-page/GitPlugin.vue";

import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import { ref, onMounted, watch } from "vue";
import { getAllCategories } from "../utils/apis";

const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
});

const routeMap = {
  usermgt: "用户管理",
  articlemgt: "新增文章",
  categorymgt: "专栏管理",
  imagemgt: "图片管理",
  navmgt: "网站导航管理",
  cachemgt: "缓存资源管理",
  gitplugin: "Git插件",
};

const store = useStore();
const route = useRoute();
const router = useRouter();

const backgroundColorList = [
  "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  "linear-gradient(135deg, #4facfe, #00f2fe)",
  "linear-gradient(135deg, #ff7e5f, #feb47b)",
  "linear-gradient(135deg, #43cea2, #185a9d)",
  "linear-gradient(135deg, #f7971e, #ffd200)",
  "linear-gradient(135deg, #00c6ff, #0072ff)",
  "linear-gradient(135deg, #ff6a00, #ee0979)",
  "linear-gradient(135deg, #00c6ff, #0072ff)",
];

// 用于存储所有分类
const allCategories = ref([]);

// 引用移动端和主侧边栏容器
const isMobileMenuOpen = ref(false);
const mobileSidebarContainerRef = ref(null);
const mainSidebarContainerRef = ref(null);
const sidebarContentRef = ref(null);

// 用于存储当前选中的分类
const activeCard = ref("用户管理");

/**
 * 设置当前活动分类并获取相应的文章
 * @param category {string} 选中的分类
 */
function onActiveCard(category) {
  // 如果点击的是当前分类，则不做任何操作``
  if (activeCard.value === category) return;

  // 设置当前活动分类
  activeCard.value = category;
  const key = Object.keys(routeMap).find((k) => routeMap[k] === category);
  router.push(`/admin/${key}`);
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
 * 更新所有分类数据
 */
async function onOnUpdateCategories() {
  const res = await getAllCategories();
  if (res) {
    allCategories.value = res;
    Toast.success("分类数据更新成功");
  } else {
    Toast.error("分类数据更新失败，请稍后再试");
  }
}

// --- 监听路由参数变化 ---
function syncActiveFromRoute(id) {
  if (id && routeMap[id]) {
    activeCard.value = routeMap[id];
  } else {
    activeCard.value = "用户管理";
    // 保持 URL 规范
    router.replace("/admin/usermgt");
  }
}

watch(
  () => route.params.id,
  (newId) => {
    syncActiveFromRoute(newId);
  },
  { immediate: true }
);

/**
 * 在组件激活时获取所有文章和分类数据和标签统计数据
 */
onMounted(async () => {
  // 检查是否为管理员
  const isadmin = store.state.authState.isadmin;
  if (!isadmin) {
    router.push({ path: "/" });
    return;
  }
  // 获得全部的博客文章
  let res = await getAllCategories();
  if (!res) return;

  allCategories.value = res;
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
  padding: 16px 32px;
  color: #71777c;
  cursor: pointer;
  gap: 10px;
  border-radius: 16px;
  margin: 8px 0px;
  color: #171717;
  font-size: 18px;
  font-weight: 500;
}

.sidebar-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content {
  max-width: unset;
}
</style>
