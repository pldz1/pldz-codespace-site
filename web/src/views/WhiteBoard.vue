<template>
  <!-- 顶部导航栏 -->
  <HeaderBar :route-name="'白板'" :show-mobile-menu="false" :scroll="false"></HeaderBar>

  <!-- 主内容区 -->
  <div class="main-container">
    <div class="whiteboard-wrapper">
      <div class="input-area">
        <div class="input-wrapper">
          <input v-model="key" type="text" placeholder="输入密钥" @keyup.enter="handleClick" />
          <button v-if="key" class="clear-btn" type="button" @click="clearKey" aria-label="清除密钥">×</button>
        </div>
        <button @click="handleClick">匹配/新建</button>
      </div>
      <div v-if="boards.length" class="board-selector">
        <span class="selector-label">已关联白板</span>
        <div class="key-list">
          <button v-for="item in boards" :key="item.key" class="key-chip" :class="{ active: item.key === key }" @click="selectBoard(item.key)">
            {{ item.key }}
          </button>
        </div>
      </div>
      <div class="board">
        <div class="card" :class="{ empty: !selectedBoard }">
          <div class="card-header">
            <div class="card-meta">
              <div class="card-key">密钥: {{ selectedBoard?.key || "-" }}</div>
              <div class="card-owner">创建者: {{ displayUsername }}</div>
            </div>
            <div class="card-actions">
              <button class="secondary" @click="startEditing" :disabled="!canEdit">编辑</button>
              <button class="primary" @click="updateRecord" :disabled="!canSave">保存</button>
              <button class="secondary" @click="openFullscreen" :disabled="!selectedBoard">全屏</button>
            </div>
          </div>
          <textarea ref="editorRef" v-model="content" :readonly="!isEditing" :disabled="!selectedBoard" placeholder="请先匹配或创建白板"></textarea>
          <div class="timestamp">上次更新: {{ formatTimestamp(created) }}</div>
        </div>
      </div>
    </div>
    <div v-if="showFullscreen" class="fullscreen-overlay" @click.self="closeFullscreen">
      <div class="fullscreen-panel" role="dialog" aria-modal="true">
        <div class="fullscreen-header">
          <span class="fullscreen-title">白板内容预览</span>
          <button class="close-btn" type="button" @click="closeFullscreen" aria-label="关闭全屏">×</button>
        </div>
        <div class="fullscreen-body">
          <pre>{{ content || "（暂无内容）" }}</pre>
        </div>
        <div class="fullscreen-footer">
          <button type="button" class="exit-btn" @click="closeFullscreen">退出全屏</button>
        </div>
      </div>
    </div>
  </div>
  <!-- 底部隐私数据 -->
  <FooterBar></FooterBar>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import { computed, nextTick, onBeforeUnmount, ref, watch } from "vue";
import { useStore } from "vuex";
import Toast from "../utils/toast.js";
import { getWhiteBoardByKey, getWhiteBoardByUser, updateWhiteBoardContent } from "../utils/apis";

const store = useStore();
const username = computed(() => store.state.authState.username || "");

const boards = ref([]);
const key = ref("");
const content = ref("");
const created = ref("");
const isEditing = ref(false);
const editorRef = ref(null);
const showFullscreen = ref(false);
const originalBodyOverflow = ref("");
const keydownHandler = (event) => {
  if (event.key === "Escape") {
    event.preventDefault();
    closeFullscreen();
  }
};

const selectedBoard = computed(() => boards.value.find((item) => item.key === key.value) || null);
const canEdit = computed(() => !!selectedBoard.value && !isEditing.value);
const canSave = computed(() => !!selectedBoard.value && isEditing.value);
const displayUsername = computed(() => {
  const owner = selectedBoard.value?.username || "";
  return owner || "匿名";
});

const formatTimestamp = (ts) => (ts ? new Date(ts).toLocaleString() : "-");

const selectBoardByKey = (boardKey) => {
  const match = boards.value.find((item) => item.key === boardKey);
  if (!match) {
    return;
  }
  key.value = match.key;
  content.value = match.content || "";
  created.value = match.created || "";
  isEditing.value = false;
};

const selectBoard = (boardKey) => {
  selectBoardByKey(boardKey);
};

const startEditing = () => {
  if (!selectedBoard.value) {
    Toast.error("请先匹配白板");
    return;
  }
  if (isEditing.value) {
    return;
  }
  isEditing.value = true;
  nextTick(() => {
    editorRef.value?.focus();
  });
};

const clearKey = () => {
  key.value = "";
  content.value = "";
  created.value = "";
  isEditing.value = false;
};

const openFullscreen = () => {
  if (!selectedBoard.value && !content.value) {
    Toast.info("暂无白板内容可查看");
    return;
  }
  showFullscreen.value = true;
};

const closeFullscreen = () => {
  showFullscreen.value = false;
};

const handleClick = async () => {
  const trimmedKey = key.value.trim();
  isEditing.value = false;

  if (trimmedKey) {
    const res = await getWhiteBoardByKey(trimmedKey);
    if (!res) {
      Toast.error("未找到对应的白板");
      boards.value = [];
      content.value = "";
      created.value = "";
      return;
    }
    boards.value = [res];
    selectBoardByKey(res.key);
    Toast.success("匹配成功");
    return;
  }

  const res = await getWhiteBoardByUser(username.value, true);
  if (!res || !res.length) {
    Toast.error("创建白板失败，请稍后再试");
    return;
  }
  boards.value = [...res];
  selectBoardByKey(boards.value[0].key);
  Toast.success("已为你创建新的白板");
};

const updateRecord = async () => {
  if (!selectedBoard.value) {
    Toast.error("请选择要更新的白板");
    return;
  }
  if (!isEditing.value) {
    Toast.error("请先点击编辑按钮");
    return;
  }
  const res = await updateWhiteBoardContent(key.value, content.value);
  if (!res || res.flag === false) {
    Toast.error(res?.log || "更新失败，请稍后再试");
    return;
  }
  const timestamp = res.created || new Date().toISOString();
  created.value = timestamp;
  const target = boards.value.find((item) => item.key === key.value);
  if (target) {
    target.content = content.value;
    target.created = timestamp;
  }
  boards.value = [...boards.value].sort((a, b) => (b.created || "").localeCompare(a.created || ""));
  isEditing.value = false;
  Toast.success("更新成功");
};

watch(
  showFullscreen,
  (value) => {
    if (typeof document !== "undefined") {
      if (value) {
        originalBodyOverflow.value = document.body.style.overflow;
        document.body.style.overflow = "hidden";
      } else {
        document.body.style.overflow = originalBodyOverflow.value || "";
      }
    }
    if (typeof window !== "undefined") {
      if (value) {
        window.addEventListener("keydown", keydownHandler);
      } else {
        window.removeEventListener("keydown", keydownHandler);
      }
    }
  },
  { flush: "post" }
);

onBeforeUnmount(() => {
  if (typeof document !== "undefined") {
    document.body.style.overflow = originalBodyOverflow.value || "";
  }
  if (typeof window !== "undefined") {
    window.removeEventListener("keydown", keydownHandler);
  }
});
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
  align-items: flex-start;
}
.input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
}
.input-area input {
  flex: 1;
  padding: 12px 16px;
  padding-right: 40px;
  font-size: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  transition: border-color 0.2s;
}
.input-area input:focus {
  border-color: #3b82f6;
  outline: none;
}
.input-area > button {
  padding: 12px 24px;
  font-size: 1rem;
  background-color: #3b82f6;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}
.input-area > button:hover {
  background-color: #2563eb;
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: #9ca3af;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.clear-btn:hover {
  color: #4b5563;
}

.board-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.selector-label {
  font-weight: 600;
  color: #374151;
}
.key-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.key-chip {
  padding: 6px 14px;
  font-size: 0.875rem;
  border-radius: 999px;
  border: 1px solid #d1d5db;
  background-color: #ffffff;
  color: #374151;
  cursor: pointer;
  transition: all 0.2s ease;
}
.key-chip:hover {
  border-color: #3b82f6;
  color: #2563eb;
}
.key-chip.active {
  background-color: #3b82f6;
  border-color: #2563eb;
  color: #ffffff;
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
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}
.card-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #4b5563;
  font-size: 0.875rem;
}
.card-key {
  font-weight: 600;
  color: #111827;
}
.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.card-actions button {
  padding: 8px 16px;
  font-size: 0.875rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}
.card-actions .primary {
  background-color: #3b82f6;
  color: #ffffff;
  border: 1px solid #2563eb;
}
.card-actions .primary:disabled {
  background-color: #bfdbfe;
  border-color: #bfdbfe;
  cursor: not-allowed;
}
.card-actions .primary:not(:disabled):hover {
  background-color: #2563eb;
}
.card-actions .secondary {
  background-color: #ffffff;
  color: #374151;
  border: 1px solid #d1d5db;
}
.card-actions .secondary:disabled {
  color: #9ca3af;
  border-color: #e5e7eb;
  cursor: not-allowed;
}
.card-actions .secondary:not(:disabled):hover {
  border-color: #3b82f6;
  color: #2563eb;
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
.card textarea:disabled {
  background-color: #f3f4f6;
  color: #9ca3af;
}
.timestamp {
  padding: 8px 16px;
  font-size: 0.875rem;
  color: #6b7280;
  background-color: #f9fafb;
  text-align: right;
  border-top: 1px solid #e5e7eb;
}
.fullscreen-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10006;
  padding: 24px;
}
.fullscreen-panel {
  width: min(1200px, 100%);
  max-height: 100%;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 24px 48px rgba(15, 23, 42, 0.25);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.fullscreen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  background-color: #ffffff;
  z-index: 5;
}
.fullscreen-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}
.close-btn {
  line-height: 1;
  border: none;
  background: transparent;
  font-size: 24px;
  cursor: pointer;
  color: #4b5563;
  padding: 4px;
}
.close-btn:hover {
  color: #111827;
}
.fullscreen-body {
  padding: 20px;
  overflow: auto;
  flex: 1;
  background-color: #f9fafb;
}
.fullscreen-body pre {
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", Courier, monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #1f2937;
}
.fullscreen-footer {
  padding: 16px 20px;
  border-top: 1px solid #e5e7eb;
  background-color: #ffffff;
  display: flex;
  justify-content: flex-end;
}
.exit-btn {
  padding: 10px 20px;
  background-color: #111827;
  color: #ffffff;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background-color 0.2s ease;
}
.exit-btn:hover {
  background-color: #1f2937;
}
@media (max-width: 640px) {
  .whiteboard-wrapper {
    padding: 16px;
    gap: 20px;
  }
  .input-area {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .input-wrapper {
    width: 100%;
  }
  .input-area > button {
    width: 100%;
    padding: 12px;
  }
  .key-list {
    gap: 6px;
  }
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  .card-actions {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .card-actions button {
    width: 100%;
  }
  .fullscreen-overlay {
    padding: 12px;
  }
  .fullscreen-panel {
    max-height: calc(100vh - 24px);
  }
  .fullscreen-header {
    padding: 12px 16px;
  }
  .fullscreen-body {
    padding: 16px;
  }
  .fullscreen-footer {
    padding: 12px 16px 16px;
    justify-content: center;
  }
  .exit-btn {
    width: 100%;
  }
}
</style>
