<template>
  <header class="header">
    <div class="header-left">
      <button v-if="props.showMobileMenu" class="mobile-menu-btn" @click="toggleMobileMenu()">☰</button>
      <a class="header-logo-link" href="/">
        <!-- 使用 scoped 样式的 app-logo -->
        <div class="app-logo"></div>
        <div class="header-logo">爬楼的猪 CodeSpace</div>
      </a>

      <!-- 导航 -->
      <nav>
        <ul class="nav-menu">
          <li :class="['nav-item', routeName == '首页' ? 'active' : '']"><a href="/"> 首页 </a></li>
          <!-- 其他的导航内容 -->
          <li v-for="nav in navs" :key="nav.title" class="nav-item">
            <a :href="nav.url" target="_blank" rel="noopener noreferrer"> {{ nav.title }} <span v-if="nav.new" class="badge">new</span> </a>
          </li>
        </ul>
      </nav>
    </div>
    <div class="header-right">
      <input type="text" class="search-box" placeholder="探索文章" />
      <!-- 登录卡片 -->
      <div class="user-avatar" @click="onToggleLoginForm">
        <img v-if="avatar" :src="avatar" />
        <div v-else class="visitor-avatar"></div>
      </div>
    </div>
  </header>

  <!-- 登录表单 -->
  <LoginCard v-if="showLoginForm" @close-login-form="onCloseLoginForm"></LoginCard>
</template>

<script setup>
import LoginCard from "./LoginCard.vue";

import { useStore } from "vuex";
import { ref, computed, onMounted } from "vue";
import { getNavigation } from "../utils/apis.js";

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

// 取用户头像
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);
const navs = ref([]);

// 显示登录表单的状态
const showLoginForm = ref(false);

/**
 * 切换移动端菜单
 */
function toggleMobileMenu() {
  emit("toggle-mobile-menu");
}

/**
 * 打开登录表单
 */
function onToggleLoginForm() {
  showLoginForm.value = true;

  // 如果已经登录，则不需要加入遮罩
  if (!!username.value) {
    return;
  }
  const app = document.getElementById("app");
  app.style.opacity = 0.04;
}

/**
 * 关闭登录表单
 */
function onCloseLoginForm() {
  const app = document.getElementById("app");
  app.style.cssText = "";
  showLoginForm.value = false;
}

/**
 * 初始化时候获取导航数据
 */
onMounted(async () => {
  const res = await getNavigation();
  navs.value = res || [];
});
</script>

<style scoped>
@import url("../assets/components/header-bar.css");

.header-logo-link {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  color: unset !important;
  text-decoration: none;
}

.app-logo {
  width: 32px;
  height: 32px;
  display: inline-block;
  margin-right: 8px;
  vertical-align: middle;
  background: url("../assets/svgs/logo-32.svg") no-repeat center;
  background-size: contain;
}
</style>
