<template>
  <teleport to="body">
    <div class="auth-overlay" @click="onClickOverlay">
      <!-- 已经登录的卡片信息 -->
      <div v-if="!!username" class="info-card">
        <div class="auth-window-bar" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </div>
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
        <div class="auth-window-bar" aria-hidden="true">
          <span></span>
          <span></span>
          <span></span>
        </div>
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

import { ref, computed, onMounted, onBeforeUnmount } from "vue";
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
let previousBodyOverflow = "";

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
  if (event.target.classList.contains("auth-overlay")) {
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

onMounted(() => {
  previousBodyOverflow = document.body.style.overflow || "";
  document.body.style.overflow = "hidden";
});

onBeforeUnmount(() => {
  document.body.style.overflow = previousBodyOverflow;
});
</script>

<style scoped>
.auth-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 10030;
  min-height: 100vh;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(rgba(15, 23, 42, 0.62), rgba(15, 23, 42, 0.62)), linear-gradient(45deg, rgba(255, 255, 255, 0.08) 25%, transparent 25%),
    linear-gradient(-45deg, rgba(255, 255, 255, 0.08) 25%, transparent 25%);
  background-size: auto, 18px 18px, 18px 18px;
  overflow: auto;
  padding: 32px 18px;
}

.auth-container,
.info-card {
  position: relative;
  width: min(420px, 100%);
  margin: auto;
  overflow: hidden;
  border: 2px solid #111827;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 8px 8px 0 #111827;
  z-index: 10031;
}

.flex-center {
  display: flex;
  justify-content: center;
  align-items: center;
}

.loading {
  position: absolute;
  inset: auto;
  min-height: 330px;
  z-index: 10032;
  background: rgba(255, 255, 255, 0.9);
}

.auth-window-bar {
  display: flex;
  align-items: center;
  gap: 7px;
  height: 32px;
  padding: 0 12px;
  border-bottom: 2px solid #111827;
  background: #e2e8f0;
}

.auth-window-bar span {
  width: 10px;
  height: 10px;
  border: 2px solid #111827;
  background: #ffffff;
}

.auth-window-bar span:nth-child(1) {
  background: #ef4444;
}

.auth-window-bar span:nth-child(2) {
  background: #facc15;
}

.auth-window-bar span:nth-child(3) {
  background: #22c55e;
}

.auth-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 20px 22px 8px;
}

.auth-close {
  flex: 0 0 auto;
  height: 34px;
  width: 34px;
  border: 2px solid #111827;
  border-radius: 6px;
  background: #ffffff url("../assets/svgs/close-24.svg") no-repeat center;
  background-size: 18px;
  box-shadow: 3px 3px 0 #111827;
  cursor: pointer;
}

.auth-close:hover {
  background-color: #f8fafc;
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0 #111827;
}

.auth-container h2 {
  margin: 0;
  color: #111827;
  font-size: 24px;
  line-height: 1.1;
  letter-spacing: 0;
}

.auth-container form {
  padding: 0 22px 22px;
}

.auth-container input {
  width: 100%;
  height: 44px;
  padding: 0 12px;
  margin: 10px 0 0;
  border: 2px solid #111827;
  border-radius: 6px;
  background: #f8fafc;
  color: #111827;
  font: inherit;
  box-shadow: inset 3px 3px 0 rgba(15, 23, 42, 0.08);
}

.auth-container input:focus {
  outline: none;
  background: #ffffff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.22), inset 3px 3px 0 rgba(15, 23, 42, 0.08);
}

.auth-container button {
  min-height: 42px;
  padding: 0 14px;
  margin-top: 0;
  border: 2px solid #111827;
  border-radius: 6px;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 3px 3px 0 #111827;
  transition: transform 120ms ease, box-shadow 120ms ease, background-color 120ms ease;
}

.auth-container button:hover {
  transform: translate(-1px, -1px);
  box-shadow: 4px 4px 0 #111827;
}

.auth-container button:active {
  transform: translate(2px, 2px);
  box-shadow: 1px 1px 0 #111827;
}

.action-buttons {
  display: flex;
  flex-direction: row;
  gap: 12px;
  margin-top: 16px;
}

.auth-container .btn-register {
  background: #fff;
  color: #111827;
}

.auth-container .btn-login {
  background: #93c5fd;
  color: #111827;
}

.auth-container .error {
  min-height: 22px;
  padding: 0 22px;
  color: #dc2626;
  font-size: 13px;
  font-weight: 700;
}

.auth-container .agreement {
  font-size: 12px;
  color: #475569;
  margin-top: 16px;
  line-height: 1.6;
}

.auth-container .agreement a {
  color: #2563eb;
  font-weight: 700;
  text-decoration: none;
}

.info-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 0 22px 22px;
}

.info-avatar {
  position: relative;
  width: 96px;
  height: 96px;
  margin-top: 24px;
  border: 3px solid #111827;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #f8fafc;
  box-shadow: 5px 5px 0 #111827;
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
  color: #ffffff;
  opacity: 0;
  transition: opacity 0.2s ease;
  font-weight: 700;
  user-select: none;
  cursor: pointer;
}

.info-avatar:hover .avatar-overlay {
  opacity: 1;
}

.info-content {
  text-align: center;
  width: 100%;
}

.info-item {
  width: 100%;
  min-height: 38px;
  padding: 0 10px;
  border: 2px solid #111827;
  border-radius: 6px;
  background: #f8fafc;
  color: #475569;
  font-size: 0.9rem;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.info-item span {
  min-width: 0;
  overflow: hidden;
  color: #111827;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-admin {
  display: inline-block;
  min-height: 32px;
  padding: 5px 12px;
  border: 2px solid #111827;
  border-radius: 6px;
  color: #111827;
  background: #facc15;
  box-shadow: 3px 3px 0 #111827;
  font-size: 0.78rem;
  font-weight: 800;
  cursor: pointer;
  width: 100%;
}

.btn-logout {
  display: flex;
  justify-content: center;
  width: 100%;
  background: transparent;
}

.btn-logout button,
button.btn-logout {
  min-height: 40px;
  width: 100%;
  border: 2px solid #111827;
  border-radius: 6px;
  background: #fecaca;
  color: #111827;
  font-weight: 800;
  cursor: pointer;
  box-shadow: 3px 3px 0 #111827;
}

@media (max-width: 480px) {
  .auth-overlay {
    align-items: flex-start;
    padding-top: 92px;
  }

  .auth-header,
  .auth-container form {
    padding-left: 16px;
    padding-right: 16px;
  }

  .auth-container .error {
    padding-left: 16px;
    padding-right: 16px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .auth-container button {
    width: 100%;
  }
}
</style>
