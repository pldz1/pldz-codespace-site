<template>
  <teleport to="body">
    <div class="auth-overlay" @click="onClickOverlay">
      <!-- 已经登录的卡片信息 -->
      <div v-if="!!username" class="info-card">
        <!-- 头像 -->
        <div class="info-avatar">
          <img :src="avatar" alt="头像" />
          <div class="avatar-overlay" @click="onUploadAvatar($event)">+</div>
        </div>

        <!-- 其他信息 -->
        <p class="info-item">
          昵称：<span>{{ nickname }}</span>
        </p>
        <p class="info-item">
          用户名：<span>{{ username }}</span>
        </p>
        <!-- 用户角色 -->
        <p class="info-admin" @click="onAdminClick">{{ isadmin ? "管理员" : "普通用户" }}</p>
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
            注册/登录即表示同意 <a href="/api/v1/website/resource/user_agreement" target="_blank" rel="noopener noreferrer">用户协议</a> 和
            <a href="/api/v1/website/resource/privacy_policy" target="_blank" rel="noopener noreferrer">隐私政策</a>
          </div>
        </form>
      </div>
      <div class="auth-container flex-center loading" v-if="showLoginCss">
        <div class="my-loader"></div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { useStore } from "vuex";
import { useRouter } from "vue-router";

import { ref, computed } from "vue";
import { login, register, logout, updateAvatar } from "../utils/apis";
import { uploadAvatar } from "../utils/file-upload.js";
import Toast from "../utils/toast.js";

const emit = defineEmits(["close-login-form"]);

// 引入 Vuex store
const store = useStore();
// 引入 Vue Router
const router = useRouter();

// 取用户头像
const avatar = computed(() => store.state.authState.avatar);
const username = computed(() => store.state.authState.username);
const nickname = computed(() => store.state.authState.nickname);
const isadmin = computed(() => store.state.authState.isadmin);

// 用户名和密码的响应式引用
const name = ref("");
const pwd = ref("");
const nick = ref("");
const ava = ref("");
const error = ref("");

// 显示是注册界面的状态
const showRegister = ref(false);

// 显示登陆css
const showLoginCss = ref(false);

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
  showLoginCss.value = true;
  const isValid = onCheckName();
  if (!isValid) {
    showLoginCss.value = false;
    return;
  }

  // 如果是注册界面，则调用注册接口
  let res;
  if (showRegister.value) {
    res = await register(name.value, pwd.value, nick.value);
  } else {
    res = await login(name.value, pwd.value);
  }

  if (res.flag) {
    await store.dispatch("authState/update", {
      username: res.username || "",
      isadmin: res.isadmin || false,
      avatar: res.avatar || "",
      nickname: res.nickname || "",
    });
    onCloseLoginForm();
    Toast.success("登录成功!");
  } else {
    error.value = res.log || "操作失败，请稍后再试";
    Toast.error(`登录失败: ${error.value}`);
  }
  showLoginCss.value = false;
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
  Toast.success("退出成功!");
}

/**
 * 关闭登录表单
 */
function onCloseLoginForm() {
  emit("close-login-form");
}

/**
 * 处理点击遮罩事件
 * @param event
 */
function onClickOverlay(event) {
  // 点击遮罩时关闭登录表单
  if (event.target.classList.contains("auth-overlay") && !!username.value) {
    onCloseLoginForm();
  }
}

/**
 * 如果是管理员，点击管理员信息时跳转到管理页面
 */
function onAdminClick() {
  // 如果是管理员，则跳转到管理页面
  if (isadmin.value) {
    router.push({ path: "/admin" });
  }
}

/**
 * 上传头像
 * @returns {Promise<void>}
 */
async function onUploadAvatar(event) {
  // 阻止事件冒泡，避免触发关闭登录表单
  event.stopPropagation();

  const res = await uploadAvatar(username.value);
  if (res?.data && res.data?.flag && res.data?.url) {
    ava.value = res.data.url;

    // 更新 中的头像
    await store.dispatch("authState/avatar", res.data.url);
    await updateAvatar(res.data.url);
  } else {
    error.value = "头像上传失败，请稍后再试";
  }
}
</script>

<style scoped>
.auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 999;
  height: 100vh;
  width: 100vw;
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
  box-shadow: 0 2px 8px rgba(124, 122, 122, 0.4);
  z-index: 900;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading {
  position: absolute;
  height: 360px;
  z-index: 1000;
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

.info-card {
  position: absolute;
  width: 240px;
  right: 0px;
  top: 48px;
  background-color: #f9f9f9;
  border: 1px solid rgba(0, 0, 0, 0.08);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  border-radius: 8px;
  padding: 16px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.info-avatar {
  position: relative;
  width: 80px;
  height: 80px;
  border: 3px solid #4a90e2;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.info-avatar img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  background: rgba(0, 0, 0, 0.4);
  opacity: 0;
  border-radius: 50%;
  transition: opacity 0.2s ease;
  font-weight: 700;
  user-select: none;
}

.info-avatar:hover .avatar-overlay {
  opacity: 1;
}

.info-content {
  text-align: center;
  width: 100%;
}

.info-item {
  font-size: 0.9rem;
  display: flex;
  flex-direction: row;
  justify-content: center;
  gap: 8px;
}

.info-item span {
  font-weight: 500;
}

.info-admin {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  background: #4a90e2;
  border-radius: 8px;
  cursor: pointer;
}

.btn-logout {
  background: #f44336;
  color: #fff;
  border: none;
  width: 60px;
  border-radius: 8px;
  cursor: pointer;
}
</style>
