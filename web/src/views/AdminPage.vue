<template>
  <div class="admin-page">
    <transition name="fade">
      <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="onCloseMobileMenu()"></div>
    </transition>

    <transition name="slide-in">
      <div v-show="isMobileMenuOpen" class="mobile-sidebar modern-mobile-sidebar">
        <div class="mobile-sidebar-header">
          <div class="logo">
            <div class="logo-icon"></div>
            <span>爬楼的猪 Dev</span>
          </div>
          <button class="close-btn" @click="onCloseMobileMenu()">×</button>
        </div>
        <div class="nav-placeholder"></div>
        <div class="mobile-sidebar-container" ref="mobileSidebarContainerRef"></div>
      </div>
    </transition>

    <HeaderBar @toggle-mobile-menu="onToggleMobileMenu"></HeaderBar>

    <div class="main-container admin-main" :class="{ 'mobile-menu-open': isMobileMenuOpen }">
      <aside class="sidebar sidebar-sticky admin-sidebar" ref="mainSidebarContainerRef">
        <nav class="sidebar-nav admin-sidebar-card" ref="sidebarContentRef">
          <button
            v-for="item in menuItems"
            :key="item.key"
            class="sidebar-link"
            :class="{ active: activeMenuKey === item.key }"
            @click="onActiveCard(item.key)"
          >
            <span class="sidebar-link-label">{{ item.name }}</span>
          </button>
        </nav>
      </aside>

      <main class="content admin-content">
        <section class="admin-content-body" :class="{ 'is-dimmed': showLoadingOverlay }">
          <transition name="fade">
            <div v-if="showLoadingOverlay" class="loading-overlay">
              <div class="loading-spinner"></div>
              <p>数据加载中，请稍候...</p>
            </div>
          </transition>

          <UserMgt v-if="activeMenuKey === 'usermgt'"></UserMgt>
          <ImageMgt v-if="activeMenuKey === 'imagemgt'" :all-categories="allCategories" :is-loading="isCategoriesLoading"></ImageMgt>
          <NavMgt v-if="activeMenuKey === 'navmgt'"></NavMgt>
          <CacheMgt v-if="activeMenuKey === 'cachemgt'"></CacheMgt>
        </section>
      </main>
    </div>

    <FooterBar></FooterBar>
  </div>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";

import UserMgt from "../components/admin-page/UserMgt.vue";
import ImageMgt from "../components/admin-page/ImageMgt.vue";
import NavMgt from "../components/admin-page/NavMgt.vue";
import CacheMgt from "../components/admin-page/CacheMgt.vue";

import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { getAllCategories } from "../utils/apis";
import Toast from "../utils/toast.js";
import { useLoading } from "../utils/use-loading";

const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
});

const menuItems = [
  {
    key: "usermgt",
    name: "用户管理",
    icon: "🤠",
    caption: "管理后台用户权限与基础资料",
    gradient: "linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)",
    requiresCategories: false,
  },
  {
    key: "imagemgt",
    name: "图片管理",
    icon: "📷",
    caption: "上传与维护内容配图",
    gradient: "linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%)",
    requiresCategories: true,
  },
  {
    key: "navmgt",
    name: "网站导航管理",
    icon: "🌐",
    caption: "配置站点导航与展示位",
    gradient: "linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)",
    requiresCategories: false,
  },
  {
    key: "cachemgt",
    name: "缓存资源管理",
    icon: "💾",
    caption: "维护静态缓存与资源文件",
    gradient: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
    requiresCategories: false,
  },
];

const routeMap = menuItems.reduce((map, item) => {
  map[item.key] = item;
  return map;
}, {});

const categoriesDependentMenu = new Set(menuItems.filter((item) => item.requiresCategories).map((item) => item.key));

const defaultMenuKey = menuItems[0].key;

const store = useStore();
const route = useRoute();
const router = useRouter();

const allCategories = ref([]);
const activeMenuKey = ref(defaultMenuKey);

const isMobileMenuOpen = ref(false);
const mobileSidebarContainerRef = ref(null);
const mainSidebarContainerRef = ref(null);
const sidebarContentRef = ref(null);

const { isLoading: isCategoriesLoading, start: startCategoriesLoading, stop: stopCategoriesLoading } = useLoading("admin.categories");

const activeMenu = computed(() => routeMap[activeMenuKey.value] || routeMap[defaultMenuKey]);
const showLoadingOverlay = computed(() => isCategoriesLoading.value && categoriesDependentMenu.has(activeMenuKey.value));

function onActiveCard(key) {
  if (activeMenuKey.value === key) return;
  activeMenuKey.value = key;
  if (route.params.id !== key) {
    router.push(`/admin/${key}`);
  }
}

function onToggleMobileMenu() {
  if (isMobileMenuOpen.value) {
    onCloseMobileMenu();
    return;
  }

  if (mobileSidebarContainerRef.value && sidebarContentRef.value) {
    mobileSidebarContainerRef.value.appendChild(sidebarContentRef.value);
  }
  isMobileMenuOpen.value = true;
}

function onCloseMobileMenu() {
  isMobileMenuOpen.value = false;
  if (mainSidebarContainerRef.value && sidebarContentRef.value && !mainSidebarContainerRef.value.contains(sidebarContentRef.value)) {
    mainSidebarContainerRef.value.appendChild(sidebarContentRef.value);
  }
}

function handleResize() {
  if (window.innerWidth > 768 && isMobileMenuOpen.value) {
    onCloseMobileMenu();
  }
}

async function fetchCategories({ showSuccessToast = false } = {}) {
  startCategoriesLoading();
  try {
    const res = await getAllCategories();
    if (res) {
      allCategories.value = res;
      if (showSuccessToast) {
        Toast.success("分类数据更新成功");
      }
      return true;
    }
    Toast.error("分类数据获取失败，请稍后再试");
    return false;
  } catch (error) {
    console.error("获取分类数据失败:", error);
    Toast.error("分类数据获取失败，请稍后再试");
    return false;
  } finally {
    stopCategoriesLoading();
  }
}

function syncActiveFromRoute(id) {
  if (id && routeMap[id]) {
    activeMenuKey.value = id;
    return;
  }

  const routeId = route.params.id;
  if (routeId && routeMap[routeId]) {
    activeMenuKey.value = routeId;
    return;
  }

  activeMenuKey.value = defaultMenuKey;
  if (route.params.id !== defaultMenuKey) {
    router.replace(`/admin/${defaultMenuKey}`);
  }
}

onMounted(async () => {
  window.addEventListener("resize", handleResize);

  const isadmin = store.state.authState.isadmin;
  if (!isadmin) {
    router.push({ path: "/" });
    return;
  }

  await fetchCategories();
  syncActiveFromRoute(props.id || route.params.id);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", handleResize);
});

watch(
  () => route.params.id,
  (newId) => {
    syncActiveFromRoute(newId);
  }
);

watch(
  () => props.id,
  (newId) => {
    if (newId) {
      syncActiveFromRoute(newId);
    }
  }
);
</script>

<style scoped>
@import url("../assets/views/main-container.css");
@import url("../assets/views/mobile-overlay.css");

.admin-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f7f8fa;
}

.admin-main {
  flex: 1;
  display: flex;
  gap: 24px;
  padding: 88px 24px 32px;
  min-height: calc(100vh - 112px);
  width: 100%;
  max-width: none;
  min-width: 0;
  overflow: hidden;
  transition: filter 0.3s ease, transform 0.3s ease;
}

.admin-sidebar {
  width: 240px;
  flex: 0 0 240px;
  display: flex;
}

.admin-sidebar-card {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 6px;
  width: 100%;
  padding: 8px;
}

.sidebar-link {
  text-align: left;
  padding: 10px 4px;
  border: none;
  background: none;
  font-size: 15px;
  color: #1f2937;
  border-bottom: 1px solid transparent;
  cursor: pointer;
  transition: color 0.2s ease;
}

.sidebar-link:hover {
  color: #2563eb;
}

.sidebar-link.active > span {
  color: #1d4ed8;
  border-bottom: 2px solid currentColor;
  font-weight: 600;
}

.admin-content {
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  padding: 0;
  max-width: none;
  width: 100%;
  min-width: 0;
  overflow: hidden;
}

.admin-content-body {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0 8px 32px;
  transition: filter 0.25s ease, opacity 0.25s ease;
}

.admin-content-body.is-dimmed {
  pointer-events: none;
  filter: blur(1px);
  opacity: 0.6;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 4;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  gap: 12px;
  color: #475569;
}

.loading-spinner {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  border: 4px solid rgba(99, 102, 241, 0.16);
  border-top-color: #6366f1;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-in-enter-active,
.slide-in-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.slide-in-enter-from,
.slide-in-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}

.modern-mobile-sidebar {
  color: #fff;
}

.mobile-sidebar-header .logo {
  color: black;
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
}

.mobile-sidebar-header .logo .logo-icon {
  width: 32px;
  height: 32px;
  background: url("../assets/svgs/logo-32.svg") center;
}

@media (max-width: 1024px) {
  .admin-main {
    padding: 80px 20px 28px;
    gap: 20px;
  }

  .admin-sidebar {
    width: 200px;
    flex-basis: 200px;
  }

  .admin-content {
    padding: 0;
  }
}

@media (max-width: 768px) {
  .admin-main {
    padding: 88px 16px 32px;
    overflow-y: auto;
    gap: 20px;
  }

  .admin-sidebar {
    display: none;
  }

  .admin-content {
    padding: 24px 20px;
    backdrop-filter: none;
    background: rgba(255, 255, 255, 0.98);
    box-shadow: 0 18px 36px -24px rgba(15, 23, 42, 0.25);
  }

  .sidebar-nav {
    gap: 10px;
  }

  .admin-sidebar-card {
    backdrop-filter: none;
    background: rgba(255, 255, 255, 0.95);
  }

  .admin-content-header h1 {
    font-size: 24px;
  }

  .admin-main.mobile-menu-open {
    filter: blur(2px) brightness(0.92);
    transform: scale(0.995);
    transition: filter 0.3s ease, transform 0.3s ease;
  }
}

@media (max-width: 480px) {
  .admin-content {
    padding: 20px 16px;
  }

  .admin-content-header {
    margin-bottom: 20px;
  }

  .admin-main.mobile-menu-open {
    filter: blur(2.4px) brightness(0.88);
    transform: scale(0.99);
  }
}
</style>
