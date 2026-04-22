<template>
  <MobileDrawer v-model="isMobileMenuOpen" subtitle="Whiteboard, notes, cache">
    <p>白板页</p>
    <p>通过密钥匹配或创建临时白板。</p>
  </MobileDrawer>

  <HeaderBar :route-name="'白板'" @toggle-mobile-menu="onToggleMobileMenu"></HeaderBar>

  <div class="whiteboard-page">
    <main class="main-container whiteboard-main">
      <section class="whiteboard-heading">
        <div class="hero-copy">
          <p class="page-kicker">Tools / Whiteboard</p>
          <p class="page-description">临时白板</p>
        </div>
        <span class="board-count">{{ boards.length }} 个白板</span>
      </section>

      <section class="input-area" aria-label="白板匹配">
        <div class="input-wrapper">
          <input v-model="key" type="text" placeholder="输入密钥" @keyup.enter="handleClick" />
          <button v-if="key" class="clear-btn" type="button" @click="clearKey" aria-label="清除密钥">×</button>
        </div>
        <button @click="handleClick">匹配/新建</button>
      </section>

      <section v-if="boards.length" class="board-selector" aria-label="已关联白板">
        <span class="selector-label">已关联白板</span>
        <div class="key-list">
          <button v-for="item in boards" :key="item.key" class="key-chip" :class="{ active: item.key === key }" @click="selectBoard(item.key)">
            {{ item.key }}
          </button>
        </div>
      </section>

      <section class="board" aria-label="白板内容">
        <article class="card" :class="{ empty: !selectedBoard }">
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
          <textarea
            v-if="isEditing"
            ref="editorRef"
            v-model="content"
            :disabled="!selectedBoard"
            placeholder="请先匹配或创建白板"
            @paste="handlePaste"
          ></textarea>
          <div v-else class="content-preview" :class="{ empty: !selectedBoard || !content }">
            <template v-if="selectedBoard && content">
              <template v-for="(block, index) in contentBlocks" :key="`${block.type}-${index}`">
                <img v-if="block.type === 'image'" class="preview-image" :src="block.value" alt="白板图片" loading="lazy" decoding="async" />
                <pre v-else class="preview-text">{{ block.value }}</pre>
              </template>
            </template>
            <span v-else>请先匹配或创建白板</span>
          </div>
          <div class="timestamp">上次更新: {{ formatTimestamp(created) }}</div>
        </article>
      </section>
    </main>

    <div v-if="showFullscreen" class="fullscreen-overlay" @click.self="closeFullscreen">
      <div class="fullscreen-panel" role="dialog" aria-modal="true">
        <div class="fullscreen-header">
          <span class="fullscreen-title">白板内容预览</span>
          <button class="close-btn" type="button" @click="closeFullscreen" aria-label="关闭全屏">×</button>
        </div>
        <div class="fullscreen-body">
          <template v-if="content">
            <template v-for="(block, index) in contentBlocks" :key="`fullscreen-${block.type}-${index}`">
              <img v-if="block.type === 'image'" class="preview-image" :src="block.value" alt="白板图片" loading="lazy" decoding="async" />
              <pre v-else class="preview-text">{{ block.value }}</pre>
            </template>
          </template>
          <pre v-else class="preview-text">（暂无内容）</pre>
        </div>
        <div class="fullscreen-footer">
          <button type="button" class="exit-btn" @click="closeFullscreen">退出全屏</button>
        </div>
      </div>
    </div>

    <FooterBar></FooterBar>
  </div>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import MobileDrawer from "../components/MobileDrawer.vue";
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
const isMobileMenuOpen = ref(false);
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
const contentBlocks = computed(() => {
  const value = content.value || "";
  const imagePattern = /data:image\/[a-zA-Z0-9.+-]+;base64,[a-zA-Z0-9+/=]+/g;
  const blocks = [];
  let lastIndex = 0;
  let match;

  while ((match = imagePattern.exec(value)) !== null) {
    if (match.index > lastIndex) {
      const text = value.slice(lastIndex, match.index);
      if (text) {
        blocks.push({ type: "text", value: text });
      }
    }

    blocks.push({ type: "image", value: match[0] });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < value.length) {
    blocks.push({ type: "text", value: value.slice(lastIndex) });
  }

  return blocks.length ? blocks : [{ type: "text", value }];
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

const onToggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value;
};

const insertAtCursor = (value) => {
  const editor = editorRef.value;
  if (!editor) {
    content.value += value;
    return;
  }

  const start = editor.selectionStart ?? content.value.length;
  const end = editor.selectionEnd ?? start;
  content.value = `${content.value.slice(0, start)}${value}${content.value.slice(end)}`;

  nextTick(() => {
    editor.focus();
    const cursor = start + value.length;
    editor.setSelectionRange(cursor, cursor);
  });
};

const handlePaste = async (event) => {
  if (!isEditing.value || !selectedBoard.value) {
    return;
  }

  const items = Array.from(event.clipboardData?.items || []);
  const imageItems = items.filter((item) => item.type.startsWith("image/"));

  if (!imageItems.length) {
    return;
  }

  event.preventDefault();

  const readImage = (item) =>
    new Promise((resolve, reject) => {
      const file = item.getAsFile();
      if (!file) {
        reject(new Error("无法读取剪贴板图片"));
        return;
      }

      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result || ""));
      reader.onerror = () => reject(reader.error || new Error("图片读取失败"));
      reader.readAsDataURL(file);
    });

  try {
    const images = await Promise.all(imageItems.map(readImage));
    const imageText = images.filter(Boolean).join("\n\n");
    if (imageText) {
      insertAtCursor(imageText);
      Toast.success("图片已转为 Base64");
    }
  } catch (error) {
    console.error("粘贴图片失败:", error);
    Toast.error("图片转换失败，请重试");
  }
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
@import url("../assets/views/main-container.css");

.whiteboard-page {
  min-height: 100vh;
  background: #f8fafc;
}

.main-container {
  width: min(1120px, calc(100% - 40px));
  max-width: 1120px;
  display: block;
  padding: 110px 0 72px;
  min-height: auto;
}

.whiteboard-main {
  display: grid;
  gap: 24px;
  min-width: 0;
}

.whiteboard-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  padding-bottom: 18px;
  border-bottom: 1px solid #e7edf5;
}

.hero-copy {
  display: grid;
  gap: 6px;
}

.page-kicker {
  margin: 0 0 12px;
  color: #2563eb;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.page-description {
  margin: 0;
  color: #0f172a;
  font-size: 18px;
  line-height: 1.45;
  font-weight: 600;
}

.board-count {
  display: inline-flex;
  align-items: center;
  height: 38px;
  padding: 0 14px;
  border: 1px solid #d9e4f0;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.75);
  color: #475569;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.input-area {
  display: flex;
  gap: 10px;
  align-items: center;
  padding: 18px;
  border: 1px solid #dce6f2;
  border-radius: 8px;
  background: #ffffff;
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
}

.input-wrapper {
  position: relative;
  flex: 1;
  display: flex;
  min-width: 0;
}

.input-area input {
  flex: 1;
  height: 42px;
  min-width: 0;
  padding: 0 42px 0 14px;
  font-size: 14px;
  border: 1px solid #d9e4f0;
  border-radius: 8px;
  background: #f8fafc;
  color: #0f172a;
  transition: background-color 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.input-area input:focus {
  background: #ffffff;
  border-color: #bfd4ff;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
  outline: none;
}

.input-area > button {
  height: 42px;
  padding: 0 18px;
  font-size: 14px;
  font-weight: 600;
  background-color: #2563eb;
  color: #ffffff;
  border: 1px solid #2563eb;
  border-radius: 999px;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
}

.input-area > button:hover {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
  transform: translateY(-1px);
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border: 1px solid transparent;
  border-radius: 999px;
  background: transparent;
  color: #94a3b8;
  font-size: 18px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.clear-btn:hover {
  background: #eef4f9;
  color: #475569;
}

.board-selector {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.selector-label {
  font-size: 13px;
  font-weight: 600;
  color: #64748b;
}

.key-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.key-chip {
  height: 32px;
  padding: 0 13px;
  font-size: 13px;
  border-radius: 999px;
  border: 1px solid #d9e4f0;
  background: rgba(255, 255, 255, 0.75);
  color: #475569;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.key-chip:hover {
  background: #ffffff;
  border-color: #bfd4ff;
  color: #1d4ed8;
}

.key-chip.active {
  background: #eff6ff;
  border-color: #bfd4ff;
  color: #1d4ed8;
}

.board {
  display: grid;
  grid-template-columns: 1fr;
}

.card {
  display: flex;
  flex-direction: column;
  min-height: 540px;
  border: 1px solid #dce6f2;
  border-radius: 8px;
  overflow: hidden;
  background: #ffffff;
  box-shadow: 0 14px 36px rgba(15, 23, 42, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  background-color: #ffffff;
  border-bottom: 1px solid #e7edf5;
}

.card-meta {
  display: flex;
  flex-direction: column;
  gap: 4px;
  color: #94a3b8;
  font-size: 13px;
  min-width: 0;
}

.card-key {
  font-weight: 600;
  color: #0f172a;
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.card-actions button {
  height: 36px;
  padding: 0 14px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 999px;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.card-actions .primary {
  background-color: #2563eb;
  color: #ffffff;
  border: 1px solid #2563eb;
}

.card-actions .primary:disabled {
  background-color: #bfdbfe;
  border-color: #bfdbfe;
  cursor: not-allowed;
}

.card-actions .primary:not(:disabled):hover {
  background-color: #1d4ed8;
}

.card-actions .secondary {
  background-color: #ffffff;
  color: #475569;
  border: 1px solid #d9e4f0;
}

.card-actions .secondary:disabled {
  color: #94a3b8;
  border-color: #e7edf5;
  cursor: not-allowed;
}

.card-actions .secondary:not(:disabled):hover {
  border-color: #bfd4ff;
  color: #1d4ed8;
}

.card textarea {
  flex: 1;
  min-height: 420px;
  padding: 18px;
  font-size: 15px;
  line-height: 1.7;
  border: none;
  resize: none;
  outline: none;
  background-color: #ffffff;
  color: #0f172a;
}

.card textarea:disabled {
  background-color: #f8fafc;
  color: #94a3b8;
}

.content-preview {
  flex: 1;
  min-height: 420px;
  padding: 18px;
  overflow: auto;
  background: #fbfdff;
  color: #0f172a;
}

.content-preview.empty {
  display: grid;
  place-items: center;
  color: #94a3b8;
  background: #f8fafc;
}

.preview-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: "SFMono-Regular", Menlo, Consolas, "Liberation Mono", Courier, monospace;
  font-size: 14px;
  line-height: 1.7;
  color: #0f172a;
}

.preview-image {
  display: block;
  max-width: min(100%, 860px);
  max-height: 70vh;
  margin: 10px 0;
  border: 1px solid #e2eaf3;
  border-radius: 8px;
  background: #ffffff;
  object-fit: contain;
}

.timestamp {
  padding: 10px 18px;
  font-size: 13px;
  color: #94a3b8;
  background-color: #fbfdff;
  text-align: right;
  border-top: 1px solid #e7edf5;
}

.fullscreen-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.58);
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
  border-radius: 8px;
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
  border-bottom: 1px solid #e7edf5;
  position: sticky;
  top: 0;
  background-color: #ffffff;
  z-index: 5;
}
.fullscreen-title {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.close-btn {
  line-height: 1;
  width: 36px;
  height: 36px;
  border: 1px solid #d9e4f0;
  border-radius: 999px;
  background: #ffffff;
  font-size: 22px;
  cursor: pointer;
  color: #475569;
  padding: 0;
}

.close-btn:hover {
  border-color: #bfd4ff;
  color: #1d4ed8;
}

.fullscreen-body {
  padding: 20px;
  overflow: auto;
  flex: 1;
  background-color: #f8fafc;
}

.fullscreen-footer {
  padding: 16px 20px;
  border-top: 1px solid #e7edf5;
  background-color: #ffffff;
  display: flex;
  justify-content: flex-end;
}

.exit-btn {
  height: 38px;
  padding: 0 18px;
  background-color: #2563eb;
  color: #ffffff;
  border: 1px solid #2563eb;
  border-radius: 999px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: background-color 0.2s ease;
}

.exit-btn:hover {
  background-color: #1d4ed8;
}

@media (max-width: 900px) {
  .main-container {
    width: min(100% - 28px, 980px);
    padding-top: 102px;
  }
}

@media (max-width: 640px) {
  .main-container {
    width: calc(100% - 24px);
    padding: 92px 0 54px;
  }

  .whiteboard-main {
    gap: 18px;
  }

  .whiteboard-heading {
    align-items: start;
    flex-direction: column;
    gap: 14px;
    padding-bottom: 14px;
  }

  .page-kicker {
    margin-bottom: 6px;
    font-size: 11px;
  }

  .page-description {
    font-size: 16px;
  }

  .input-area {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 14px;
  }
  .input-wrapper {
    width: 100%;
  }
  .input-area > button {
    width: 100%;
  }

  .key-list {
    gap: 6px;
  }

  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
    padding: 14px;
  }

  .card {
    min-height: 460px;
  }

  .card textarea {
    min-height: 320px;
    padding: 14px;
    font-size: 14px;
  }

  .content-preview {
    min-height: 320px;
    padding: 14px;
  }

  .preview-image {
    max-width: 100%;
    max-height: 62vh;
  }

  .timestamp {
    padding: 8px 14px;
    font-size: 12px;
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
