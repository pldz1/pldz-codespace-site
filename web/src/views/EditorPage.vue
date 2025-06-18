<template>
  <div class="meta-setting-overlay" @click="closeMetaSetting" v-show="isShowMetaSetting"></div>
  <div class="meta-setting-sidebar" v-show="isShowMetaSetting">
    <div class="meta-setting-sidebar-header">
      <div>
        <a href="/"><div class="app-logo"></div></a>
        <span>爬楼的猪 CodeSpace</span>
      </div>
      <button class="close-btn" @click="closeMetaSetting">×</button>
    </div>
    <!-- 侧边栏内容 -->
    <div class="meta-setting-sidebar-container">
      <div class="meta-setting-item">
        <span>专栏</span>
        <input class="meta-setting-input" v-model="articleMeta.category" placeholder="请输入专栏" />
      </div>
      <div class="meta-setting-item">
        <span>日期</span>
        <input class="meta-setting-input" v-model="articleMeta.date" type="date" />
      </div>
      <div class="meta-setting-item">
        <span>排序</span>
        <input class="meta-setting-input" type="number" v-model="articleMeta.serialNo" placeholder="数字排序" />
      </div>
      <div class="meta-setting-item">
        <span>标签</span>
        <input class="meta-setting-input" v-model="articleTags" placeholder="逗号分隔" @change="onTagsChange" />
      </div>
      <div class="meta-setting-item">
        <span>总结</span>
        <textarea class="meta-setting-textarea" v-model="articleMeta.summary" placeholder="一句话总结" type="textarea" rows="4"></textarea>
      </div>
      <div class="meta-setting-item">
        <span>封面</span>
        <div class="thumbnail-container" @click="onShowUploadImageDialog(false)">
          <img class="thumbnail-image" :src="articleMeta.thumbnail" />
          <div class="overlay-button">+</div>
        </div>
      </div>
      <div class="meta-setting-item">
        <span>图像源</span>
        <input class="meta-setting-input" v-model="articleMeta.thumbnail" placeholder="有效的图片路径" />
      </div>
    </div>
  </div>

  <!-- 头部导航, 但是不显示移动菜单 -->
  <HeaderBar :show-mobile-menu="false" />

  <!-- 编辑器标题和操作按钮 -->
  <div class="edit-header">
    <div class="edit-title"><input placeholder="输入标题" v-model="articleMeta.title" @change="saveMeta" /></div>
    <div class="edit-header-actions">
      <button class="btn btn-primary" @click="closeMetaSetting">设置元数据</button>
      <button class="btn btn-primary" ref="saveBtn">已保存</button>
    </div>
  </div>

  <!-- 工具栏 -->
  <div class="toolbar">
    <div class="toolbar-left">
      <button class="toolbar-btn image" @click="onShowUploadImageDialog(true)" title="图片"></button>
      <div class="separator"></div>
      <button class="toolbar-btn bold" @click="insertText('**', '**')" title="粗体"></button>
      <button class="toolbar-btn italic" @click="insertText('*', '*')" title="斜体"></button>
      <button class="toolbar-btn quote" @click="insertText('> ', '')" title="引用"></button>
      <button class="toolbar-btn link" @click="insertText('[]()', '')" title="链接"></button>
      <div class="separator"></div>
      <button class="toolbar-btn code" @click="insertText('`', '`')" title="代码"></button>
      <button class="toolbar-btn unorder-list" @click="insertText('- ', '')" title="无序列表"></button>
      <button class="toolbar-btn order-list" @click="insertText('1. ', '')" title="有序列表"></button>
      <button class="toolbar-btn strikethrough" @click="insertText('~~', '~~')" title="删除线"></button>
      <button class="toolbar-btn task" @click="insertText('- [ ] ', '')" title="任务列表"></button>
      <button class="toolbar-btn table" @click="insertText('| 表头1 | 表头2 |\n|-------|-------|\n| 内容1 | 内容2 |', '')" title="表格"></button>
      <button class="toolbar-btn divide" @click="insertText('---\n', '')" title="分割线"></button>
    </div>
    <div class="toolbar-right">
      <button class="toolbar-btn preview-switch" @click="closeOpenPreview" title="打开/关闭预览"></button>
      <div class="separator"></div>
    </div>
  </div>

  <!-- 主界面 -->
  <div class="main-container">
    <!-- 编辑器区域 -->
    <div class="editor-panel">
      <div class="panel-header">编辑界面</div>
      <textarea
        ref="editorRef"
        v-model="editorText"
        class="editor"
        placeholder="在这里输入Markdown内容..."
        @input="onEditorInput"
        @keydown.tab.prevent="insertTab"
      ></textarea>
    </div>

    <!-- 预览区域 -->
    <div class="preview-panel" v-show="isShowPreviw">
      <div class="panel-header">预览界面</div>
      <div ref="previewRef" class="article-content"></div>
    </div>
  </div>

  <!-- 上传图像的位置 -->
  <teleport to="body">
    <div v-if="isShowImageUpload" class="image-upload-overlay">
      <div class="image-upload-container">
        <div class="image-upload-header">
          <h2>上传专栏图片</h2>
          <div class="image-upload-close" @click="onCloseUploadImageDialog"></div>
        </div>
        <div class="image-upload-content">
          <div class="image-upload-item">
            <span class="label">专栏:</span>
            <span>{{ articleMeta.category }}</span>
          </div>
          <div class="image-upload-item">
            <span class="label">名称* :</span>
            <input type="text" placeholder="请输入名称" @change="onCheckImageName" v-model="imageName" />
          </div>
          <div :style="{ color: 'red', fontSize: '16px', maxHeight: '32px' }">
            {{ imageUploadError }}
          </div>
          <div class="image-upload-item upload-image-preview" @click="onUploadImage">
            <img v-if="imagePreviewUrl" :src="imagePreviewUrl" alt="Image Preview" />
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import { ref, watch, nextTick, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { renderMdBlock } from "../utils/md-render.js";
import { getArticle, editArticle, editMeta, checkImageExit } from "../utils/apis.js";
import { uploadArticleImage } from "../utils/image-upload.js";

const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
});

const router = useRouter();
const store = useStore();

// 控制元数据设置和预览的显示状态
const isShowMetaSetting = ref(false);
const isShowPreviw = ref(true);
const isShowImageUpload = ref(false);

// 编辑器和预览的引用
const editorRef = ref(null);
const previewRef = ref(null);

// 编辑器内容和文章元数据
const editorText = ref("");
const articleID = ref("");
const articleMeta = ref({ title: "", thumbnail: "", category: "", tags: "", date: "", serialNo: 0, summary: "" });
const articleTags = ref("");

// 上传的图像的URL
const imageName = ref("");
const imagePreviewUrl = ref("");
const imageUploadError = ref("图像名称只能包含字母、数字和下划线");
const editContentImg = ref(true);

/**
 * 校验上传的图像名字
 */
async function onCheckImageName() {
  // 只支持字母数字下划线
  const regex = /^[a-zA-Z0-9_]+$/;
  if (!regex.test(imageName.value)) {
    imageUploadError.value = "图像名称只能包含字母、数字和下划线";
    return;
  } else {
    imageUploadError.value = "";
  }

  const res = await checkImageExit(articleMeta.value.category, imageName.value);
  if (!res) {
    imageUploadError.value = "图像已经存在！";
    return;
  }
}

/**
 *
 */
async function onUploadImage() {
  if (!imageUploadError.value) {
    try {
      const res = await uploadArticleImage(articleMeta.value.category, imageName.value);
      if (res.data && res.url) {
        imagePreviewUrl.value = res.url;
        if (editContentImg.value) {
          insertText(`![${imageName.value}](${imagePreviewUrl.value})`, "");
          await editArticle(articleID.value, editorText.value);
        } else {
          articleMeta.value.thumbnail = res.url;
          await saveMeta();
        }
        imageUploadError.value = "";
      } else {
        imageUploadError.value = "上传失败！";
      }
    } catch (e) {
      imageUploadError.value = String(e);
      return;
    }
  } else {
    imageUploadError.value = "图像已经存在, 重新命名之后再上传!";
    return;
  }
}

/**
 * 显示上传图片对话框
 */
function onShowUploadImageDialog(isContent = true) {
  isShowImageUpload.value = true;
  imageName.value = "";
  imagePreviewUrl.value = "";
  imageUploadError.value = "图像名称只能包含字母、数字和下划线";
  editContentImg.value = isContent;
}

/**
 * 关闭上传图片对话框
 */
function onCloseUploadImageDialog() {
  isShowImageUpload.value = false;
}

/**
 * 打开/关闭元数据设置
 */
async function closeMetaSetting() {
  isShowMetaSetting.value = !isShowMetaSetting.value;
  if (!isShowMetaSetting.value) {
    await saveMeta();
  }
}

/**
 * 打开/关闭预览
 */
function closeOpenPreview() {
  isShowPreviw.value = !isShowPreviw.value;
}

/**
 * 处理标签变化
 */
function onTagsChange() {
  articleMeta.value.tags = JSON.parse(articleTags.value) || "";
}

/**
 * 保存文章元数据
 */
async function saveMeta() {
  await editMeta(articleID.value, articleMeta.value);
}

const saveBtnText = ref("已保存");
const saveBtn = ref(null);
let saveTimeout = null;

// 更新预览内容
function updatePreview() {
  const previewEl = previewRef.value;
  if (!previewEl) return;

  if (editorText.value.trim() === "") {
    previewEl.innerHTML = `
      <h1>MARKDOWN 实时编辑</h1>
      <p>开始在左侧编辑器中输入Markdown内容，右侧将实时显示预览效果。</p>
    `;
  } else {
    renderMdBlock("article-content", previewEl, editorText.value);
  }
}

// 处理编辑器输入：更新预览并模拟自动保存
function onEditorInput() {
  updatePreview();

  // 自动保存按钮逻辑
  clearTimeout(saveTimeout);
  saveBtnText.value = "已保存";
  saveTimeout = setTimeout(async () => {
    saveBtnText.value = "保存中...";
    await editArticle(articleID.value, editorText.value);
    setTimeout(() => {
      saveBtnText.value = "已保存";
    }, 1000);
  }, 1000);
}

// 插入文本（前后缀）
function insertText(before = "", after = "") {
  const el = editorRef.value;
  if (!el) return;

  const start = el.selectionStart;
  const end = el.selectionEnd;
  const selected = editorText.value.substring(start, end);
  const newContent = before + selected + after;

  editorText.value = editorText.value.substring(0, start) + newContent + editorText.value.substring(end);

  nextTick(async () => {
    // 更新光标位置
    const pos = start + before.length + selected.length;
    el.focus();
    el.setSelectionRange(pos, pos);
    await editArticle(articleID.value, editorText.value);
  });
}

// 处理 Tab 键
function insertTab(e) {
  const el = editorRef.value;
  if (!el) return;

  const start = el.selectionStart;
  const end = el.selectionEnd;
  editorText.value = editorText.value.substring(0, start) + "    " + editorText.value.substring(end);

  nextTick(() => {
    el.selectionStart = el.selectionEnd = start + 4;
  });
}

/**
 * 编辑器的初始化函数
 * 在组件挂载时调用，获取文章内容并初始化编辑器
 * @returns {void}
 */
onMounted(async () => {
  // 检查是否为管理员
  const isadmin = store.state.authState.isadmin;
  if (!isadmin) {
    router.push({ path: "/" });
    return;
  }

  // 检查文章ID是否存在
  const res = await getArticle(props.id);
  if (!res) {
    router.push({ path: "/" });
    return;
  }

  // 初始化内容和预览
  articleID.value = res.id;
  editorText.value = res.content;

  articleMeta.value.title = res.meta.title;
  articleMeta.value.thumbnail = res.meta.thumbnail;
  articleMeta.value.category = res.meta.category;
  articleTags.value = JSON.stringify(res.meta.tags);
  articleMeta.value.tags = res.meta.tags || [];
  articleMeta.value.date = res.meta.date;
  articleMeta.value.serialNo = res.meta.serialNo;
  articleMeta.value.summary = res.meta.summary;

  updatePreview();
});

// 监听保存按钮文本变化，同步到按钮
watch(saveBtnText, (val) => {
  if (saveBtn.value) {
    saveBtn.value.textContent = val;
  }
});
</script>

<style scoped>
@import url("../assets/views/article-content.css");

.app-logo {
  width: 32px;
  height: 32px;
  display: inline-block;
  margin-right: 8px;
  vertical-align: middle;
  background: url("../assets/svgs/logo-32.svg") no-repeat center;
  background-size: contain;
}

.edit-header {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 48px;
}

.edit-title {
  font-weight: 500;
  flex: 1;
  padding: 4px 4px 4px 4px;
}

.edit-title input {
  font-size: 18px;
  height: 100%;
  width: 100%;
  border: none;
  padding: 8px;
  font-weight: 600;
}

.edit-header-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 6px 12px;
  border: 1px solid #d0d7de;
  background: white;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn:hover {
  background: #f3f4f6;
}

.btn-primary {
  background: #0969da;
  color: white;
  border-color: #0969da;
}

.btn-primary:hover {
  background: #0860ca;
}

.toolbar {
  background: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 4px;
  flex-wrap: wrap;
  min-height: 40px;
  justify-content: space-between;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 8px;
}

.toolbar-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: background 0.2s;
}

.toolbar-btn:hover {
  background-color: #d0d7de !important;
}

.toolbar .bold {
  display: inline-block;
  background: url("../assets/svgs/bold-16.svg") no-repeat center;
}

.toolbar .italic {
  display: inline-block;
  background: url("../assets/svgs/italic-16.svg") no-repeat center;
}

.toolbar .quote {
  display: inline-block;
  background: url("../assets/svgs/quote-16.svg") no-repeat center;
}

.toolbar .link {
  display: inline-block;
  background: url("../assets/svgs/link-16.svg") no-repeat center;
}

.toolbar .image {
  display: inline-block;
  background: url("../assets/svgs/img-gray-16.svg") no-repeat center;
}

.toolbar .code {
  display: inline-block;
  background: url("../assets/svgs/code-16.svg") no-repeat center;
}

.toolbar .unorder-list {
  display: inline-block;
  background: url("../assets/svgs/unorder-list-16.svg") no-repeat center;
}

.toolbar .order-list {
  display: inline-block;
  background: url("../assets/svgs/order-list-16.svg") no-repeat center;
}

.toolbar .strikethrough {
  display: inline-block;
  background: url("../assets/svgs/strikethrough-16.svg") no-repeat center;
}

.toolbar .task {
  display: inline-block;
  background: url("../assets/svgs/task-16.svg") no-repeat center;
}

.toolbar .table {
  display: inline-block;
  background: url("../assets/svgs/table-16.svg") no-repeat center;
}

.toolbar .divide {
  display: inline-block;
  background: url("../assets/svgs/divide-16.svg") no-repeat center;
}

.toolbar .preview-switch {
  display: inline-block;
  background: url("../assets/svgs/preview-16.svg") no-repeat center;
}

.separator {
  width: 1px;
  height: 20px;
  background: #e0e0e0;
  margin: 0 4px;
}

.main-container {
  display: flex;
  height: calc(100vh - 156px);
  overflow: hidden;
}

.editor-panel,
.preview-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-panel {
  max-width: 50%;
}

.panel-header {
  background: #f6f8fa;
  border-bottom: 1px solid #e0e0e0;
  padding: 8px 16px;
  font-size: 13px;
  color: #586069;
  display: flex;
  align-items: center;
  gap: 8px;
}

.panel-header .icon {
  width: 16px;
  height: 16px;
  color: #0969da;
}

.editor-panel {
  border-right: 1px solid #e0e0e0;
}

.editor {
  flex: 1;
  border: none;
  outline: none;
  padding: 16px;
  font-family: "SFMono-Regular", Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: none;
  background: white;
}

.preview {
  flex: 1;
  padding: 16px;
  background: white;
  overflow-y: auto;
  font-size: 16px;
  line-height: 1.6;
}

.article-content {
  overflow-y: auto;
  padding: 8px;
}

.meta-setting-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
}

.meta-setting-sidebar {
  position: fixed;
  top: 0;
  left: 0;
  width: 368px;
  height: 100vh;
  background: white;
  z-index: 1000;
  transition: left 0.3s ease;
  overflow-y: auto;
}

.meta-setting-sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e6ea;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #71777c;
}

.meta-setting-sidebar-container {
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
}

.meta-setting-item {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.meta-setting-item span {
  width: 80px;
  flex-shrink: 0;
  font-size: 14px;
  color: #333;
}

.meta-setting-input,
.meta-setting-textarea {
  flex: 1;
  padding: 6px 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 4px;
  outline: none;
  transition: border-color 0.2s;
}

.meta-setting-textarea {
  height: 126px;
  max-height: 196px;
}

.meta-setting-input:focus {
  border-color: #409eff;
}

.thumbnail-container {
  position: relative;
  display: inline-block;
  width: 248px;
  height: 168px;
}

.thumbnail-image {
  width: 248px;
  height: 168px;
  border: 1px solid #ddd;
  border-radius: 4px;
  object-fit: contain;
}

/* 按钮初始隐藏 */
.overlay-button {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0;
  border: none;
  background-color: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: 24px;
  line-height: 1;
  padding: 8px 12px;
  border-radius: 50%;
  cursor: pointer;
  transition: opacity 0.3s ease;
}

/* hover 效果 */
.thumbnail-container:hover .thumbnail-image {
  opacity: 0.5;
}

.thumbnail-container:hover .overlay-button {
  opacity: 1;
}

.image-upload-overlay {
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

.image-upload-container {
  width: 360px;
  margin: 80px auto;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
}

.image-upload-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.image-upload-close {
  height: 32px;
  width: 32px;

  display: inline-block;
  background: url("../assets/svgs/close-24.svg") no-repeat center;
}

.image-upload-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.image-upload-item {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.image-upload-item:last-child {
  margin-bottom: 0;
}

.image-upload-item .label {
  flex: 0 0 100px;
  font-weight: 500;
  color: #333;
}

.image-upload-item span:not(.label) {
  flex: 1;
  color: #555;
}

.image-upload-item input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.image-upload-item input:focus {
  border-color: #66afe9;
  box-shadow: 0 0 5px rgba(102, 175, 233, 0.6);
}

.upload-image-preview {
  width: 280px;
  height: 150px;
  margin-left: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  object-fit: cover;
  background-color: #f0f0f0;
  cursor: pointer;
  display: flex;
  justify-content: center;
}

.upload-image-preview img {
  max-height: 100%;
  max-width: 100%;
  object-fit: contain;
}

/* 移动端响应式设计 */
@media (max-width: 768px) {
  .main-container {
    flex-direction: column;
  }

  .editor-panel {
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
    height: 50%;
    max-width: 100%;
  }

  .preview-panel {
    height: 50%;
    max-width: 100%;
  }

  .toolbar {
    overflow-x: auto;
  }

  .edit-header-actions {
    gap: 4px;
  }

  .btn {
    padding: 4px 8px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .edit-header {
    padding: 4px 8px;
  }

  .toolbar {
    padding: 4px 8px;
  }

  .editor,
  .preview {
    padding: 12px;
  }

  .panel-header {
    padding: 6px 12px;
    font-size: 12px;
  }
}
</style>
