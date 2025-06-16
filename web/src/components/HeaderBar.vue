<template>
  <header class="header">
    <div class="header-left">
      <button v-if="props.showMobileMenu" class="mobile-menu-btn" @click="toggleMobileMenu()">☰</button>
      <a class="header-logo-link" href="/">
        <!-- 使用 scoped 样式的 app-logo -->
        <div class="app-logo"></div>
        <div class="header-logo">爬楼的猪 CodeSpace</div>
      </a>

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
      <div class="user-avatar" @click="onToggleLoginForm">{{ usernameChar }}</div>
    </div>
  </header>

  <teleport to="body">
    <div v-if="showLoginForm" class="auth-overlay">
      <div class="auth-container">
        <div class="auth-header">
          <h2>{{ showRegister ? "注册" : "登录" }}</h2>
          <div class="auth-close" @click="onCloseLoginForm"></div>
        </div>

        <div class="error">{{ error }}</div>
        <div v-if="usernameChar !== '游客'" class="action-buttons">
          <button @click="onLogout" class="btn-logout">注销</button>
        </div>
        <form v-else method="post" @submit.prevent="onLoginOrRegister">
          <input type="text" name="username" placeholder="邮箱地址(示例:user@example.com)" required v-model="username" @change="onCheckUsername" />
          <input type="password" name="password" placeholder="请输入密码" required v-model="password" />
          <div class="action-buttons">
            <button type="button" class="btn-register" @click="onSwitchRegister">{{ showRegister ? "返回登录" : "注册" }}</button>
            <button type="submit" class="btn-login">{{ showRegister ? "注册" : "登录" }}</button>
          </div>
          <div class="agreement" v-if="false">注册/登录即表示同意 <a href="#">用户协议</a> 和 <a href="#">隐私政策</a></div>
        </form>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useStore } from "vuex";
import { login, register, logout, refresh } from "../utils/apis.js";

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

// 取用户首字母
const usernameChar = computed(() => {
  const authState = store.state.authState;
  if (authState.username && authState.username.length > 0) {
    return authState.username.charAt(0).toUpperCase();
  }
  return "游客";
});

// 用户名和密码的响应式引用
const username = ref("");
const password = ref("");
const error = ref("");

// 显示登录表单的状态
const showLoginForm = ref(false);

// 显示是注册界面的状态
const showRegister = ref(false);

/**
 * 检查用户名是否符合要求
 * @returns {boolean} 是否符合要求
 */
function onCheckUsername() {
  // 检查用户名是否符合要求
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailPattern.test(username.value)) {
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
  const isValid = onCheckUsername();
  if (!isValid) {
    return;
  }

  // 如果是注册界面，则调用注册接口
  if (showRegister.value) {
    const res = await register(username.value, password.value);
    if (res.flag) {
      await store.dispatch("authState/update", {
        username: username.value,
        isAdmin: false,
      });
      onCloseLoginForm();
    } else {
      error.value = res.log || "注册失败，请稍后再试";
    }
  } else {
    const res = await login(username.value, password.value);
    if (res.flag) {
      await store.dispatch("authState/update", {
        username: username.value,
        isAdmin: res.isAdmin,
      });
      onCloseLoginForm();
    } else {
      error.value = res.log || "登录失败，请稍后再试";
    }
  }
}

/**
 * 注销操作
 */
async function onLogout() {
  console.log("Logging out...");
  await logout();
  await store.dispatch("authState/update", {
    username: "",
    isAdmin: false,
  });
  onCloseLoginForm();
  emit("invalid-login");
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

  const app = document.getElementById("app");
  app.style.opacity = 0.46;
}

/**
 * 关闭登录表单
 */
function onCloseLoginForm() {
  showLoginForm.value = false;

  const app = document.getElementById("app");
  app.style.cssText = "";
}

/**
 * 组件挂载时刷新登录状态
 */
onMounted(async () => {
  // 关闭登录表单充值样式
  onCloseLoginForm();

  // 如果已经登录，则不需要刷新
  if (usernameChar.value !== "游客") {
    return;
  }

  // 尝试刷新登录状态
  const res = await refresh();
  await store.dispatch("authState/update", {
    username: res?.username || "",
    isAdmin: res?.isAdmin || false,
  });

  if (!res) {
    emit("invalid-login");
  }
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
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
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

.auth-container .btn-logout {
  background: #f44336;
  color: #fff;
  border: none;
  width: 100%;
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
