<template>
  <div class="admin-page">
    <MobileDrawer v-if="hasInitializedAdmin" v-model="isMobileMenuOpen" subtitle="Admin, assets, navigation" :show-nav-placeholder="false">
      <nav class="sidebar-nav admin-sidebar-card admin-sidebar-card--mobile">
        <button
          v-for="item in menuItems"
          :key="item.key"
          class="sidebar-link"
          :class="{ active: activeMenuKey === item.key }"
          type="button"
          @click="onActiveCard(item.key)"
        >
          <span class="sidebar-link-label">{{ item.name }}</span>
        </button>
      </nav>
    </MobileDrawer>

    <HeaderBar @toggle-mobile-menu="onToggleMobileMenu"></HeaderBar>

    <div v-if="hasInitializedAdmin" class="main-container admin-main" :class="{ 'mobile-menu-open': isMobileMenuOpen }">
      <aside class="sidebar sidebar-sticky admin-sidebar">
        <nav class="sidebar-nav admin-sidebar-card">
          <button
            v-for="item in menuItems"
            :key="item.key"
            class="sidebar-link"
            :class="{ active: activeMenuKey === item.key }"
            type="button"
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

          <CacheMgt v-if="activeMenuKey === 'cachemgt'"></CacheMgt>
        </section>
      </main>
    </div>

    <div v-else class="admin-auth-loading">
      <div class="loading-spinner"></div>
      <p>权限确认中...</p>
    </div>

    <FooterBar></FooterBar>
  </div>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";

import UserMgt from "../components/admin-page/UserMgt.vue";
import ImageMgt from "../components/admin-page/ImageMgt.vue";
import CacheMgt from "../components/admin-page/CacheMgt.vue";

import { useRoute, useRouter } from "vue-router";
import { useStore } from "vuex";
import { ref, computed, onMounted, watch } from "vue";
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
const hasInitializedAdmin = ref(false);

const { isLoading: isCategoriesLoading, start: startCategoriesLoading, stop: stopCategoriesLoading } = useLoading("admin.categories");

const activeMenu = computed(() => routeMap[activeMenuKey.value] || routeMap[defaultMenuKey]);
const showLoadingOverlay = computed(() => isCategoriesLoading.value && categoriesDependentMenu.has(activeMenuKey.value));
const isAuthReady = computed(() => store.state.authState.ready);
const isAdmin = computed(() => store.state.authState.isadmin);

function onActiveCard(key) {
  if (activeMenuKey.value === key) {
    onCloseMobileMenu();
    return;
  }
  activeMenuKey.value = key;
  onCloseMobileMenu();
  if (route.params.id !== key) {
    router.push(`/admin/${key}`);
  }
}

function onToggleMobileMenu() {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
}

function onCloseMobileMenu() {
  isMobileMenuOpen.value = false;
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

async function initializeAdminPage() {
  if (!isAuthReady.value) {
    return;
  }

  if (!isAdmin.value) {
    hasInitializedAdmin.value = false;
    router.replace({ path: "/" });
    return;
  }

  if (hasInitializedAdmin.value) {
    return;
  }

  hasInitializedAdmin.value = true;
  await fetchCategories();
  syncActiveFromRoute(props.id || route.params.id);
}

onMounted(() => {
  initializeAdminPage();
});

watch([isAuthReady, isAdmin], initializeAdminPage);

watch(
  () => route.params.id,
  (newId) => {
    if (!hasInitializedAdmin.value) {
      return;
    }
    syncActiveFromRoute(newId);
  }
);

watch(
  () => props.id,
  (newId) => {
    if (!hasInitializedAdmin.value) {
      return;
    }
    if (newId) {
      syncActiveFromRoute(newId);
    }
  }
);
</script>

<style scoped>
@import url("../assets/views/main-container.css");

.admin-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}

.admin-main {
  flex: 1;
  display: flex;
  gap: 28px;
  padding: 92px 28px 40px;
  min-height: calc(100vh - 112px);
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  min-width: 0;
  overflow: visible;
  transition: filter 0.3s ease, transform 0.3s ease;
}

.admin-auth-loading {
  min-height: calc(100vh - 112px);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #475569;
}

.admin-sidebar {
  width: 224px;
  flex: 0 0 224px;
  display: flex;
  background: transparent;
  border-radius: 0;
  padding: 0;
}

.admin-sidebar-card {
  width: 100%;
  padding: 4px 0;
  border-radius: 0;
  background: transparent;
  border: none;
  box-shadow: none;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 2px;
  width: 100%;
  padding: 0;
}

.sidebar-link {
  text-align: left;
  position: relative;
  padding: 14px 4px 14px 18px;
  border: none;
  border-radius: 0;
  background: transparent;
  font-size: 15px;
  color: #475569;
  cursor: pointer;
  transition: color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
}

.sidebar-link:hover {
  color: #0f172a;
  background: rgba(255, 255, 255, 0.35);
  transform: none;
}

.sidebar-link.active {
  background: linear-gradient(90deg, rgba(255, 255, 255, 0.62), rgba(255, 255, 255, 0));
}

.sidebar-link.active::before {
  content: "";
  position: absolute;
  left: 0;
  top: 50%;
  width: 3px;
  height: 24px;
  border-radius: 999px;
  background: #2563eb;
  transform: translateY(-50%);
}

.sidebar-link.active > span {
  color: #2563eb;
  font-weight: 700;
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
  overflow: visible;
  background: transparent;
  border-radius: 0;
}

.admin-content-body {
  position: relative;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 0 0 32px;
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
  background: rgba(248, 250, 252, 0.82);
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

.admin-sidebar-card--mobile {
  padding: 0;
}

@media (max-width: 1024px) {
  .admin-main {
    padding: 84px 20px 28px;
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
    padding: 0;
    background: transparent;
    box-shadow: none;
  }

  .sidebar-nav {
    gap: 10px;
  }

  .admin-sidebar-card {
    background: transparent;
    border: none;
    box-shadow: none;
    padding: 0;
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
  .admin-content-header {
    margin-bottom: 20px;
  }

  .admin-main.mobile-menu-open {
    filter: blur(2.4px) brightness(0.88);
    transform: scale(0.99);
  }
}
</style>
