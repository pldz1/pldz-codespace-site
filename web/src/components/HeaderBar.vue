<template>
  <header :class="['header', { 'header--hidden': !isHeaderVisible }]">
    <div class="header-inner">
      <div class="header-left">
        <button v-if="showMobileMenu" class="mobile-menu-btn" type="button" aria-label="打开导航菜单" @click="toggleMobileMenu()"></button>
        <a class="brand-link" href="/">
          <span class="app-logo"></span>
          <span class="brand-copy">
            <span class="brand-name">CodeSpace</span>
            <span class="brand-subtitle">Projects, tutorials, demos</span>
          </span>
        </a>
      </div>

      <nav class="header-nav" aria-label="主导航">
        <ul ref="navAllRef" class="nav-menu">
          <li v-for="item in navItems" :key="item.label" :class="['nav-item', { active: isActive(item) }]">
            <a :href="item.href">{{ item.label }}</a>
          </li>
          <li v-for="nav in navs" :key="nav.title" class="nav-item nav-item--external">
            <a :href="nav.url" target="_blank" rel="noopener noreferrer">
              {{ nav.title }}
              <span v-if="nav.new" class="nav-badge">new</span>
            </a>
          </li>
        </ul>
      </nav>

      <div class="header-right">
        <button class="search-trigger" type="button" aria-label="打开搜索" title="搜索" @click="onOpenSearch">
          <span class="search-trigger__icon"></span>
          <span class="search-trigger__text">搜索</span>
          <span class="search-trigger__key">/</span>
        </button>

        <a class="github-link" :href="githubLink" target="_blank" rel="noopener noreferrer" aria-label="GitHub">
          <span class="github-icon"></span>
        </a>

        <div v-if="avatar" class="user-avatar" @click="onToggleLoginForm">
          <img :src="avatar" alt="avatar" />
        </div>
        <button v-else class="login-register-btn" @click="onToggleLoginForm">登录 / 注册</button>
      </div>
    </div>
  </header>

  <LoginCard v-if="showLoginForm" @close-login-form="onCloseLoginForm" />
  <SearchOverlay v-model="searchOpen" />
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useStore } from "vuex";

import { getNavigation } from "../utils/apis";
import Toast from "../utils/toast.js";
import LoginCard from "./LoginCard.vue";
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
  scroll: {
    type: Boolean,
    required: false,
    default: true,
  },
});

const emit = defineEmits(["toggle-mobile-menu"]);

const store = useStore();
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);

const navAllRef = ref(null);
const navs = ref([]);
const showLoginForm = ref(false);
const searchOpen = ref(false);
const isHeaderVisible = ref(true);
const activeAnchor = ref("");

const githubLink = computed(() => {
  const githubNav = navs.value.find((item) => /github/i.test(item.title || "") || /github\.com/i.test(item.url || ""));
  return githubNav?.url || "https://github.com";
});

const navItems = [
  { label: "首页", href: "/", anchor: "" },
  { label: "教程", href: "/404", anchor: "/404" },
  { label: "白板", href: "/whiteboard", anchor: "/whiteboard" },
  { label: "Demos", href: "/Demos", anchor: "/Demos" },
];

let lastScrollY = 0;
let ticking = false;
let accumulatedUp = 0;
let accumulatedDown = 0;
let scrollListenerActive = false;
let keydownHandler = null;
let hashchangeHandler = null;

function isActive(item) {
  if (props.routeName !== "首页") {
    return item.label === routeNameToNavLabel[props.routeName];
  }

  if (!activeAnchor.value) {
    return item.label === "首页";
  }

  return item.anchor === activeAnchor.value;
}

const routeNameToNavLabel = {
  首页: "首页",
  "Code Space": "Projects",
  白板: "Demo",
};

function handleScroll() {
  const currentY = window.scrollY;
  const diff = currentY - lastScrollY;

  if (Math.abs(diff) < 1) {
    lastScrollY = currentY;
    return;
  }

  if (diff > 0) {
    accumulatedDown += diff;
    accumulatedUp = 0;
    if (accumulatedDown > 10 && currentY > 80 && isHeaderVisible.value) {
      isHeaderVisible.value = false;
      accumulatedDown = 0;
    }
  } else {
    accumulatedUp += -diff;
    accumulatedDown = 0;
    if (accumulatedUp > 40 && !isHeaderVisible.value) {
      isHeaderVisible.value = true;
      accumulatedUp = 0;
    }
  }

  lastScrollY = currentY;
}

function onScrollThrottled() {
  if (ticking) return;
  ticking = true;
  window.requestAnimationFrame(() => {
    handleScroll();
    ticking = false;
  });
}

function enableScrollHide() {
  if (scrollListenerActive) return;
  lastScrollY = window.scrollY;
  window.addEventListener("scroll", onScrollThrottled, { passive: true });
  scrollListenerActive = true;
}

function disableScrollHide() {
  if (!scrollListenerActive) return;
  window.removeEventListener("scroll", onScrollThrottled);
  scrollListenerActive = false;
  isHeaderVisible.value = true;
  accumulatedUp = 0;
  accumulatedDown = 0;
}

function toggleMobileMenu() {
  const placeholders = document.querySelectorAll(".nav-placeholder");
  if (placeholders.length && navAllRef.value) {
    placeholders.forEach((item) => {
      item.innerHTML = "";
      item.appendChild(navAllRef.value.cloneNode(true));
    });
  }
  emit("toggle-mobile-menu");
}

function onToggleLoginForm() {
  showLoginForm.value = true;
  if (username.value) return;

  Toast.info("登录后可以注册aigc账号, 评论文章, 缓存白板内容");
  const app = document.getElementById("app");
  if (app) app.style.opacity = "0.04";
}

function onCloseLoginForm() {
  const app = document.getElementById("app");
  if (app) app.style.cssText = "";
  showLoginForm.value = false;
}

function onOpenSearch() {
  searchOpen.value = true;
}

function syncActiveAnchor() {
  activeAnchor.value = window.location.hash || "";
}

onMounted(async () => {
  if (props.scroll) {
    enableScrollHide();
  }

  watch(
    () => props.scroll,
    (shouldScroll) => {
      if (shouldScroll) {
        enableScrollHide();
      } else {
        disableScrollHide();
      }
    }
  );

  keydownHandler = (e) => {
    if (e.key !== "/" || searchOpen.value) return;
    const tag = e.target && e.target.tagName;
    const isTyping = tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || (e.target && e.target.isContentEditable);
    if (isTyping) return;
    e.preventDefault();
    searchOpen.value = true;
  };
  window.addEventListener("keydown", keydownHandler);
  hashchangeHandler = () => syncActiveAnchor();
  window.addEventListener("hashchange", hashchangeHandler);
  syncActiveAnchor();

  const res = await getNavigation();
  navs.value = res || [];
});

onBeforeUnmount(() => {
  disableScrollHide();
  if (keydownHandler) {
    window.removeEventListener("keydown", keydownHandler);
  }
  if (hashchangeHandler) {
    window.removeEventListener("hashchange", hashchangeHandler);
  }
});
</script>

<style scoped>
.header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 10005;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid rgba(229, 231, 235, 0.85);
  backdrop-filter: blur(12px);
  transition: transform 0.25s ease, opacity 0.25s ease, border-color 0.25s ease;
}

.header--hidden {
  transform: translateY(-100%);
  pointer-events: none;
}

.header-inner {
  width: min(1180px, calc(100% - 32px));
  height: 68px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 28px;
}

.header-left {
  display: flex;
  align-items: center;
  min-width: 0;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  color: inherit;
  text-decoration: none;
  min-width: 0;
}

.app-logo {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: #ffffff url("../assets/svgs/logo-32.svg") no-repeat center;
  background-size: 22px;
  border: 1px solid #dbe3ef;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
  flex-shrink: 0;
}

.brand-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}

.brand-name {
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.1;
}

.brand-subtitle {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1;
  white-space: nowrap;
}

.header-nav {
  min-width: 0;
}

.nav-menu {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  position: relative;
}

.nav-item a {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  height: 38px;
  padding: 0 12px;
  border-radius: 10px;
  color: #475569;
  text-decoration: none;
  font-size: 14px;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.nav-item a:hover {
  color: #0f172a;
  background: #f8fafc;
}

.nav-item.active a {
  color: #2563eb;
  background: #eff6ff;
}

.nav-item--external a {
  color: #64748b;
}

.nav-badge {
  font-size: 10px;
  line-height: 1;
  color: #2563eb;
  background: #dbeafe;
  border-radius: 999px;
  padding: 3px 6px;
}

.header-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
}

.search-trigger {
  height: 38px;
  padding: 0 12px;
  border-radius: 10px;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  color: #475569;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  transition: border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.search-trigger:hover {
  border-color: #cbd5e1;
  color: #0f172a;
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.search-trigger__icon {
  width: 16px;
  height: 16px;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Ccircle cx='11' cy='11' r='7'/%3E%3Cline x1='21' y1='21' x2='16.65' y2='16.65'/%3E%3C/svg%3E")
    no-repeat center / contain;
}

.search-trigger__text {
  font-size: 14px;
}

.search-trigger__key {
  font-size: 12px;
  color: #94a3b8;
  padding-left: 4px;
}

.github-link {
  width: 38px;
  height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #ffffff;
  transition: border-color 0.2s ease, transform 0.2s ease, box-shadow 0.2s ease;
}

.github-link:hover {
  border-color: #cbd5e1;
  transform: translateY(-1px);
  box-shadow: 0 10px 24px rgba(15, 23, 42, 0.06);
}

.github-icon {
  width: 18px;
  height: 18px;
  background: url("../assets/svgs/github-48.svg") no-repeat center / contain;
}

.login-register-btn {
  height: 38px;
  padding: 0 14px;
  border-radius: 10px;
  border: 1px solid #dbe3ef;
  background: #ffffff;
  color: #2563eb;
  font-size: 14px;
  cursor: pointer;
  transition: border-color 0.2s ease, background-color 0.2s ease, transform 0.2s ease;
}

.login-register-btn:hover {
  border-color: #bfdbfe;
  background: #eff6ff;
  transform: translateY(-1px);
}

.user-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  border: 1px solid #dbe3ef;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}

.user-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.mobile-menu-btn {
  display: none;
  width: 38px;
  height: 38px;
  margin-right: 10px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  background: #ffffff url("../assets/svgs/menu-32.svg") no-repeat center;
  cursor: pointer;
}

@media (max-width: 1080px) {
  .header-inner {
    grid-template-columns: auto 1fr auto;
    gap: 18px;
  }

  .nav-menu {
    gap: 2px;
  }

  .nav-item a {
    padding: 0 10px;
  }

  .nav-item--external {
    display: none;
  }
}

@media (max-width: 840px) {
  .header-inner {
    width: min(100%, calc(100% - 24px));
    height: 64px;
    grid-template-columns: auto auto;
    justify-content: space-between;
  }

  .header-nav {
    display: none;
  }

  .mobile-menu-btn {
    display: inline-flex;
    flex-shrink: 0;
  }

  .brand-subtitle {
    display: none;
  }
}

@media (max-width: 640px) {
  .search-trigger {
    width: 38px;
    padding: 0;
    justify-content: center;
  }

  .search-trigger__text,
  .search-trigger__key {
    display: none;
  }

  .login-register-btn {
    padding: 0 12px;
    font-size: 13px;
  }
}

@media (max-width: 480px) {
  .header-inner {
    width: min(100%, calc(100% - 16px));
  }

  .brand-name {
    font-size: 15px;
  }

  .github-link {
    display: none;
  }
}
</style>

<style>
.nav-placeholder {
  width: 100%;
}

.nav-placeholder .nav-menu {
  display: flex !important;
  flex-direction: column !important;
  align-items: stretch !important;
  gap: 6px !important;
  padding: 8px 0 !important;
}

.nav-placeholder .nav-item {
  width: 100%;
}

.nav-placeholder .nav-item a {
  display: flex !important;
  width: 100%;
  justify-content: space-between;
  box-sizing: border-box;
}

.nav-placeholder .nav-item--external {
  display: block !important;
}
</style>
