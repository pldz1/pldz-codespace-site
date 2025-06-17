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
          <li :class="['nav-item', routeName == 'Code Space' ? 'active' : '']"><a href="/codespace"> Code Space </a></li>
          <li class="nav-item">
            <a href="https://aigc.pldz1.com/auth" target="_blank"> open-webui demo <span class="badge">new</span> </a>
          </li>
        </ul>
      </nav>
    </div>
    <div class="header-right">
      <input type="text" class="search-box" placeholder="探索文章" />
      <!-- 登录卡片 -->
      <div class="user-avatar" @click="onToggleLoginForm">
        <img v-if="avatar" :src="avatar" />
        <div v-else>游客</div>
      </div>
    </div>
  </header>

  <teleport to="body">
    <div v-if="showLoginForm" class="auth-overlay" @click="onClickOverlay">
      <!-- 已经登录的卡片信息 -->
      <div v-if="!!username" class="info-card">
        <!-- 头像 -->
        <div class="info-avatar">
          <img :src="avatar" alt="头像" />
          <div class="avatar-overlay">+</div>
        </div>

        <!-- 其他信息 -->
        <p class="info-item">
          昵称：<span>{{ nickname }}</span>
        </p>
        <p class="info-item">
          用户名：<span>{{ username }}</span>
        </p>
        <!-- 用户角色 -->
        <p class="info-admin">{{ isadmin ? "管理员" : "普通用户" }}</p>
        <!-- 退出登录 -->
        <div class="btn-logout">
          <button @click="onLogout" class="btn-logout">退出</button>
        </div>
      </div>

      <!-- 登录/注册 表单 -->
      <div v-else class="auth-container">
        <div class="auth-header">
          <h2>{{ showRegister ? "注册" : "登录" }}</h2>
          <div class="auth-close" @click="onCloseLoginForm"></div>
        </div>

        <!-- 错误提示 -->
        <div class="error">{{ error }}</div>
        <!-- 表单 -->
        <form method="post" @submit.prevent="onLoginOrRegister">
          <!-- 注册头像 -->
          <div v-if="showRegister" class="register-avatar">
            <div class="info-avatar">
              <img v-if="ava" :src="ava" />
              <div class="avatar-overlay">+</div>
            </div>
          </div>
          <!-- 用户名 -->
          <input type="text" placeholder="邮箱地址(示例:user@example.com)" required v-model="name" @change="onCheckName" />
          <!-- 密码 -->
          <input type="password" placeholder="请输入密码" required v-model="pwd" />
          <!-- 昵称，仅在注册时显示 -->
          <input v-if="showRegister" type="text" placeholder="昵称" required v-model="nick" />
          <div class="action-buttons">
            <button type="button" class="btn-register" @click="onSwitchRegister">{{ showRegister ? "返回登录" : "注册" }}</button>
            <button type="submit" class="btn-login">{{ showRegister ? "注册" : "登录" }}</button>
          </div>
          <!-- 条款 -->
          <div class="agreement">
            注册/登录即表示同意 <a href="/api/v1/resource/user_agreement" target="_blank" rel="noopener noreferrer">用户协议</a> 和
            <a href="/api/v1/resource/privacy_policy" target="_blank" rel="noopener noreferrer">隐私政策</a>
          </div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { useStore } from "vuex";
import { ref, computed, onMounted } from "vue";
import { login, register, logout } from "../utils/apis.js";

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
const emit = defineEmits(["toggle-mobile-menu", "invalid-login"]);

// 引入 Vuex store
const store = useStore();

// 取用户头像
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);
const nickname = computed(() => store.state.authState.nickname);
const isadmin = computed(() => store.state.authState.isadmin);

// 用户名和密码的响应式引用
const name = ref("");
const pwd = ref("");
const nick = ref("");
const error = ref("");
const ava = ref("");

// 显示登录表单的状态
const showLoginForm = ref(false);

// 显示是注册界面的状态
const showRegister = ref(false);

/**
 * 检查用户名是否符合要求
 * @returns {boolean} 是否符合要求
 */
function onCheckName() {
  // 检查用户名是否符合要求
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailPattern.test(name.value)) {
    error.value = "请输入合法的邮箱地址（示例：user@example.com）";
    return false;
  } else {
    error.value = "";
    return true;
  }
}

/**
 * 切换注册界面
 */
function onSwitchRegister() {
  showRegister.value = !showRegister.value;
}

/**
 * 登录或注册操作
 */
async function onLoginOrRegister() {
  const isValid = onCheckName();
  if (!isValid) {
    return;
  }

  // 如果是注册界面，则调用注册接口
  if (showRegister.value) {
    const res = await register(name.value, pwd.value);
    if (res.flag) {
      await store.dispatch("authState/update", {
        username: name.value,
        isAdmin: false,
      });
      onCloseLoginForm();
    } else {
      error.value = res.log || "注册失败，请稍后再试";
    }
  } else {
    const res = await login(name.value, pwd.value);
    await store.dispatch("authState/update", {
      username: name.value || "",
      isadmin: res.isadmin || false,
      avatar: res.avatar || "",
      nickname: res.nickname || "",
    });

    if (res.flag) {
      error.value = "";
      onCloseLoginForm();
    } else {
      error.value = res.log || "登录失败，请稍后再试";
    }
  }
}

/**
 * 退出操作
 */
async function onLogout() {
  await logout();
  await store.dispatch("authState/update", {
    username: "",
    avatar: "",
    nickname: "",
    isadmin: false,
  });
  onCloseLoginForm();
}

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
  showLoginForm.value = false;

  const app = document.getElementById("app");
  app.style.cssText = "";
}

function onClickOverlay(event) {
  // 点击遮罩时关闭登录表单
  if (event.target.classList.contains("auth-overlay") && !!username.value) {
    onCloseLoginForm();
  }
}

/**
 * 组件挂载时刷新登录状态
 */
onMounted(async () => {
  // 关闭登录表单充值样式
  onCloseLoginForm();
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

.auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.auth-container {
  width: 360px;
  margin: 80px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.auth-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.auth-close {
  height: 32px;
  width: 32px;

  display: inline-block;
  background: url("../assets/svgs/close-24.svg") no-repeat center;
}

.auth-close:hover {
  border: 1px solid #ddd;
  border-radius: 50%;
}

.auth-container h2 {
  margin-bottom: 16px;
  color: #333;
}
.auth-container input {
  width: 100%;
  padding: 8px;
  margin: 8px 0;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.auth-container button {
  width: 48%;
  padding: 10px;
  margin-top: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.register-avatar {
  display: flex;
  justify-content: center;
  margin-bottom: 16px;
}

.action-buttons {
  display: flex;
  flex-direction: row;
  gap: 8px;
}
.auth-container .btn-register {
  background: #fff;
  color: #007bff;
  border: 1px solid #007bff;
}
.auth-container .btn-login {
  background: #007bff;
  color: #fff;
}

.auth-container .error {
  color: #e74c3c;
  margin-top: 8px;
}

.auth-container .agreement {
  font-size: 12px;
  color: #666;
  margin-top: 16px;
}
.auth-container .agreement a {
  color: #007bff;
  text-decoration: none;
}
</style>
