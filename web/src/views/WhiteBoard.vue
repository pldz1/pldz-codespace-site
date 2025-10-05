<template>
  <!-- 移动端侧边栏 -->
  <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="onCloseMobileMenu()"></div>
  <div v-show="isMobileMenuOpen" class="mobile-sidebar">
    <div class="mobile-sidebar-header">
      <div class="logo">爬楼的猪 CodeSpace</div>
      <button class="close-btn" @click="onCloseMobileMenu()">×</button>
    </div>
    <div class="mobile-sidebar-container" ref="mobileSidebarContainerRef"></div>
  </div>

  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="onToggleMobileMenu" :route-name="'白板'" :show-mobile-menu="false"></HeaderBar>

  <!-- 主内容区 -->
  <div class="main-container">
    <div class="whiteboard-wrapper">
      <div class="input-area">
        <input v-model="key" type="text" placeholder="输入密钥" @keyup.enter="handleClick" />
        <button @click="handleClick">匹配/新建</button>
      </div>
      <div class="board">
        <div class="card">
          <textarea v-model="content" @blur="updateRecord" :disabled="!active"></textarea>
          <div class="timestamp">上次更新: {{ formatTimestamp(created) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import { ref } from "vue";
import Toast from "../utils/toast.js";
import { getWhiteBoardByKey, getWhiteBoardByUser, updateWhiteBoardContent } from "../utils/apis";

// 引用移动端和主侧边栏容器
const isMobileMenuOpen = ref(false);
const mobileSidebarContainerRef = ref(null);
const mainSidebarContainerRef = ref(null);
const sidebarContentRef = ref(null);

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

// 白板交互
const active = ref(false);
const key = ref("");
const content = ref("");
const created = ref("");

const formatTimestamp = (ts) => (ts ? new Date(ts).toLocaleString() : "-");

const updateRecord = async () => {
  if (!key.value.trim()) {
    Toast.error("无效的密钥");
    return;
  }
  const res = await updateWhiteBoardContent(key.value, content.value);
  if (res) {
    Toast.success("更新成功");
    created.value = res.created || new Date().toISOString();
  } else {
    Toast.error("更新失败，请稍后再试");
  }
};

const handleClick = async () => {
  let res = null;
  if (!key.value.trim()) res = await getWhiteBoardByUser();
  else res = await getWhiteBoardByKey(key.value);

  if (!res) {
    Toast.error("请登录/注册获得正确的key!");
    active.value = false;
    return;
  }
  key.value = res.key;
  content.value = res.content;
  created.value = res.created;
  active.value = true;
};
</script>

<style scoped>
/* 主容器 */
.main-container {
  display: flex;
  justify-content: center;
  padding: 68px 16px 16px 16px;
  background-color: #f9fafb;
  min-height: calc(100vh - 64px);
}
.whiteboard-wrapper {
  width: 100%;
  max-width: 960px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.05);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 输入区 */
.input-area {
  display: flex;
  gap: 8px;
}
.input-area input {
  flex: 1;
  padding: 12px 16px;
  font-size: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  transition: border-color 0.2s;
}
.input-area input:focus {
  border-color: #3b82f6;
  outline: none;
}
.input-area button {
  padding: 12px 24px;
  font-size: 1rem;
  background-color: #3b82f6;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.input-area button:hover {
  background-color: #2563eb;
}

/* 画板区 */
.board {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr;
  grid-auto-rows: 1fr;
  gap: 16px;
}
.card {
  display: flex;
  flex-direction: column;
  height: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.card textarea {
  flex: 1;
  padding: 16px;
  font-size: 1rem;
  border: none;
  resize: none;
  outline: none;
  background-color: #fefefe;
}
.timestamp {
  padding: 8px 16px;
  font-size: 0.875rem;
  color: #6b7280;
  background-color: #f9fafb;
  text-align: right;
  border-top: 1px solid #e5e7eb;
}
</style>
