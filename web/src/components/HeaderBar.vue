<template>
  <header :class="['header', { 'header--hidden': !isHeaderVisible }]">
    <div class="header-left">
      <button v-if="showMobileMenu" class="mobile-menu-btn" @click="toggleMobileMenu()"></button>
      <a class="header-logo-link" href="/">
        <!-- 使用 scoped 样式的 app-logo -->
        <div class="app-logo"></div>
        <div class="header-logo">爬楼的猪 CodeSpace</div>
      </a>

      <!-- 导航 -->
      <nav>
        <ul class="nav-menu" ref="navAllRef">
          <li :class="['nav-item', routeName === '首页' ? 'active' : '']">
            <a href="/"> 首页 </a>
          </li>
          <li :class="['nav-item', routeName === 'Code Space' ? 'active' : '']">
            <a href="/codespace"> Code Space </a>
          </li>
          <li :class="['nav-item', routeName === '白板' ? 'active' : '']">
            <a href="/whiteboard"> 白板 </a>
          </li>
          <li v-for="nav in navs" :key="nav.title" class="nav-item">
            <a :href="nav.url" target="_blank" rel="noopener noreferrer">
              {{ nav.title }}
              <span v-if="nav.new" class="badge">new</span>
            </a>
          </li>
        </ul>
      </nav>
    </div>
    <div class="header-right">
      <input type="search" class="search-box" placeholder="探索文章" readonly @focus="onOpenSearch" @click="onOpenSearch" />
      <!-- 窄屏下显示的放大镜按钮，点击打开搜索 -->
      <button class="search-icon-btn" type="button" aria-label="打开搜索" title="搜索" @click="onOpenSearch"></button>
      <!-- 登录卡片 -->
      <div v-if="avatar" class="user-avatar" @click="onToggleLoginForm">
        <img :src="avatar" alt="avatar" />
      </div>
      <button v-else class="login-register-btn" @click="onToggleLoginForm">登录 | 注册</button>
    </div>
  </header>

  <!-- 登录表单 -->
  <LoginCard v-if="showLoginForm" @close-login-form="onCloseLoginForm" />
  <!-- 搜索 -->
  <SearchOverlay v-model="searchOpen" />
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";

import { useStore } from "vuex";
import { getNavigation } from "../utils/apis";

import LoginCard from "./LoginCard.vue";
import Toast from "../utils/toast.js";
import SearchOverlay from "./SearchOverlay.vue";

const props = defineProps({
  routeName: {
    type: String,
    required: false,
    default: "",
  },
  showMobileMenu: {
    type: Boolean,
    required: false,
    default: true,
  },
});

const emit = defineEmits(["toggle-mobile-menu"]);

// 引入 Vuex store
const store = useStore();

const navAllRef = ref("navAllRef");

// 取用户头像
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);
const navs = ref([]);
const showLoginForm = ref(false);
const searchOpen = ref(false);

// header 显示/隐藏控制
const isHeaderVisible = ref(true);
let lastScrollY = 0;
let ticking = false;
const deltaToShow = 50; // 向上滚动多少再出现
const deltaToHide = 5; // 向下滚动多少才隐藏
let accumulatedUp = 0;
let accumulatedDown = 0;

function handleScroll() {
  const currentY = window.scrollY;
  const diff = currentY - lastScrollY;

  if (Math.abs(diff) < 1) {
    lastScrollY = currentY;
    return;
  }

  if (diff > 0) {
    // 向下
    accumulatedDown += diff;
    accumulatedUp = 0;
    if (accumulatedDown > deltaToHide && isHeaderVisible.value) {
      isHeaderVisible.value = false;
      accumulatedDown = 0;
    }
  } else {
    // 向上
    accumulatedUp += -diff;
    accumulatedDown = 0;
    if (accumulatedUp > deltaToShow && !isHeaderVisible.value) {
      isHeaderVisible.value = true;
      accumulatedUp = 0;
    }
  }

  lastScrollY = currentY;
}

function onScrollThrottled() {
  if (!ticking) {
    window.requestAnimationFrame(() => {
      handleScroll();
      ticking = false;
    });
    ticking = true;
  }
}

/**
 * 切换移动端菜单
 */
function toggleMobileMenu() {
  const placeholders = document.querySelectorAll(".nav-placeholder");
  if (placeholders && navAllRef.value) {
    const copyNav = navAllRef.value.cloneNode(true);
    placeholders.forEach((item) => {
      item.innerHTML = "";
      item.appendChild(copyNav);
    });
  }
  emit("toggle-mobile-menu");
}

/**
 * 打开登录表单
 */
function onToggleLoginForm() {
  showLoginForm.value = true;
  if (!!username.value) return;

  Toast.info("登录后可以注册aigc账号, 评论文章, 缓存白板内容");
  const app = document.getElementById("app");
  if (app) app.style.opacity = "0.04";
}

/**
 * 关闭登录表单
 */
function onCloseLoginForm() {
  const app = document.getElementById("app");
  if (app) app.style.cssText = "";
  showLoginForm.value = false;
}
function onOpenSearch() {
  searchOpen.value = true;
}

/**
 * 初始化时候获取导航数据
 */
onMounted(async () => {
  lastScrollY = window.scrollY;
  window.addEventListener("scroll", onScrollThrottled, { passive: true });
  // 快捷键：按下 / 打开搜索
  window.addEventListener("keydown", (e) => {
    if (e.key === "/" && !searchOpen.value) {
      const tag = e.target && e.target.tagName;
      const isTyping = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (e.target && e.target.isContentEditable);
      if (!isTyping) {
        e.preventDefault();
        searchOpen.value = true;
      }
    }
  });
  const res = await getNavigation();
  navs.value = res || [];
});

onBeforeUnmount(() => {
  window.removeEventListener("scroll", onScrollThrottled);
});
</script>

<style scoped>
@import url("../assets/components/header-bar.css");

.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  transition: transform 0.25s ease, opacity 0.25s ease;
  z-index: 50;
  background: white;
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 60px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  z-index: 10005;
}

.header--hidden {
  transform: translateY(-100%);
  pointer-events: none;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-logo-link {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: unset !important;
  text-decoration: none;
  /* 允许在小屏上收缩，避免与右侧重叠 */
  min-width: 0;
  flex-shrink: 1;
}

.app-logo {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  margin-right: 8px;
  vertical-align: middle;
  background: url("../assets/svgs/logo-32.svg") no-repeat center;
  background-size: contain;
  /* 防止在窄屏下因 flex 收缩而形变 */
  white-space: nowrap;
  flex-shrink: 0;
  box-sizing: border-box;
}

.login-register-btn {
  display: inline-block;
  padding: 8px 16px;
  border: 1px solid #51a6ff;
  border-radius: 3px;
  background-color: #ffffff;
  color: #51a6ff;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
  text-decoration: none;
}
</style>

<style>
.nav-placeholder {
  width: 100%;
  height: auto;
}

.nav-placeholder .nav-menu {
  display: flex !important;
  flex-direction: column !important;
  padding: 8px !important;
  gap: 16px !important;
  border-bottom: 1px solid #eee !important;
}

.nav-placeholder .badge {
  right: 100px !important;
}
</style>
