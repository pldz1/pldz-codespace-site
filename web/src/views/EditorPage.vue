<template>
  <!-- 头部导航, 但是不显示移动菜单 -->
  <HeaderBar :show-mobile-menu="false" />

  <!-- 主界面 -->
  <MdEditor
    class="md-editor-v3-container"
    ref="editorRef"
    :codeFoldable="false"
    :pageFullscreen="true"
    :noUploadImg="true"
    :toolbars="toolbars"
    :footers="footers"
    :toolbarsExclude="['image', 'previewOnly', 'htmlPreview', 'pageFullscreen', 'fullscreen', 'github']"
    @on-save="onSaveArticleContent"
    @on-change="onChange"
    @on-error="onError"
    v-model="editorText"
  >
    <template #defToolbars>
      <NormalToolbar title="上传图像" @onClick="onShowUploadImageDialog">
        <Image class="md-editor-icon" />
      </NormalToolbar>
      <NormalToolbar title="设置元数据" @onClick="onShowMetaDialog">
        <Settings2 class="md-editor-icon" />
      </NormalToolbar>
      <NormalToolbar title="查看文章" @onClick="onGotoArticle">
        <BookOpen class="md-editor-icon" />
      </NormalToolbar>
    </template>

    <template #defFooters>
      <NormalFooterToolbar>上次更新: {{ updateTime }}</NormalFooterToolbar>
    </template>
  </MdEditor>

  <MetaDialog v-if="showMetaDialog" :meta="articleMeta" @on-update="onCloseMetaDialog" />

  <UploadImage
    v-if="showUploadImageDialog"
    :category="articleMeta.category"
    :show-confirm-button="showImageUploadConfirm"
    @on-close="onCloseUploadImageDialog"
    @on-upload="onUploadImage"
  />
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import UploadImage from "../components/UploadImage.vue";
import MetaDialog from "../components/edit-page/MetaDialog.vue";

import { BookOpen, Image, Settings2 } from "lucide-vue-next";
import { MdEditor, NormalToolbar, NormalFooterToolbar } from "md-editor-v3";

import { ref, onActivated, onDeactivated } from "vue";
import { useRouter } from "vue-router";
import { useStore } from "vuex";

import { toolbars, footers } from "../utils/md-editor.js";
import { getArticle, editArticle, editMeta } from "../utils/apis";
import { setCopyImageFile } from "../utils/file-upload.js";
import Toast from "../utils/toast.js";

const props = defineProps({
  id: {
    type: String,
    required: true,
    default: "",
  },
});

const router = useRouter();
const store = useStore();

// 编辑器引用
const editorRef = ref(null);
const codemirror = ref(null);
const updateTime = ref("");

// 编辑器内容和文章元数据
const editorText = ref("");
const articleID = ref("");
const articleMeta = ref({ title: "", thumbnail: "", category: "", tags: "", date: "", serialNo: 0, summary: "" });

/**
 * 更新保存时间
 * 格式化日期为 YYYY/MM/DD HH:mm:ss
 */
function updateSaveTime(date = new Date()) {
  const pad = (n) => String(n).padStart(2, "0");
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  const seconds = pad(date.getSeconds());

  updateTime.value = `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
}

/**
 * 保存文章内容
 * @param showToast 是否显示保存成功的提示
 */
async function onSaveArticleContent(showToast = true) {
  await editArticle(articleID.value, editorText.value);
  updateSaveTime();

  if (showToast) {
    Toast.success("文章已保存！");
  }
}

/**
 * 编辑器错误处理函数
 * @param error 处理编辑器错误
 */
async function onError(error) {
  Toast.error(`Markdown 编辑器存在错误: ${String(error)}`);
}

// 定时器
let renderTimer = null;

/**
 * 编辑器内容发生变化, 自动保存.
 */
async function onChange() {
  // 如果有定时器，清除它
  if (renderTimer) {
    clearTimeout(renderTimer);
  }

  // 设置一个新的定时器
  renderTimer = setTimeout(async () => {
    await onSaveArticleContent(false);
  }, 1000);
}

/**
 * 跳转到文章详情页
 * 使用路由跳转到指定文章的详情页面
 */
async function onGotoArticle() {
  // 跳转到文章详情页
  await onForceUpdate();
  router.push({ path: `/article/${articleID.value}` });
}

/**
 * 强制更新文章内容
 * 保存元数据和文章内容，并显示保存状态
 * @returns {Promise<void>}
 */
async function onForceUpdate() {
  await editMeta(articleID.value, articleMeta.value);
  await editArticle(articleID.value, editorText.value);
  updateSaveTime();
}

/**
 * 更新文章元数据
 * @param data 更新文章元数据
 */
function _updateArticleMeta(data = {}) {
  Object.entries(data).forEach(([k, v]) => {
    if (v !== undefined && k in articleMeta.value) {
      articleMeta.value[k] = v;
    }
  });
}
/**
 * ========================= UploadImage 相关 =========================
 */
const showImageUploadConfirm = ref(false);
const showUploadImageDialog = ref(false);

/**
 * 显示上传图像对话框
 * 设置对话框的状态和样式
 */
function onShowUploadImageDialog() {
  showUploadImageDialog.value = true;
  showImageUploadConfirm.value = false;
}

/**
 * 关闭上传图像对话框
 */
function onCloseUploadImageDialog() {
  showUploadImageDialog.value = false;
  showImageUploadConfirm.value = false;
}

/**
 * 上传图像
 * @param data 上传的图像数据
 *
 */
function onUploadImage(data) {
  if (editorRef.value) {
    editorRef.value?.insert(() => {
      return {
        targetValue: `![${data?.name}](${data?.url})`,
        select: true,
        deviationStart: 0,
        deviationEnd: 0,
      };
    });
  }
  showImageUploadConfirm.value = false;
  showUploadImageDialog.value = false;
}

/**
 * 处理粘贴事件
 * 检查剪贴板中的文件，如果是图片则显示上传对话框
 */
function _handleCodemirrorCopy(e) {
  // 获取真正要插入的文件列表
  const files = (e.clipboardData || window.clipboardData).files;
  // 如果有文件，并且第一个是 image 类型
  if (files.length > 0 && files[0].type.startsWith("image/")) {
    showUploadImageDialog.value = true;
    showImageUploadConfirm.value = true;
    setCopyImageFile(files[0]);
    // 阻止默认粘贴行为
    e.preventDefault();
  }
}

/**
 * ========================= Meta数据设置相关 =========================
 */

// 显示元数据对话框
const showMetaDialog = ref(false);

/**
 * 显示元数据对话框
 */
function onShowMetaDialog() {
  showMetaDialog.value = true;
}

/**
 * 保存文章元数据
 */
async function onSaveMeta(data) {
  _updateArticleMeta(data);
  await editMeta(articleID.value, articleMeta.value);
}

/**
 * 关闭元数据对话框
 */
async function onCloseMetaDialog() {
  Toast.info("正在保存元数据...");
  showMetaDialog.value = false;
  await onSaveMeta();
  Toast.success("元数据已保存！");
}

/**
 * 编辑器的初始化函数
 * 在组件挂载时调用，获取文章内容并初始化编辑器
 * @returns {void}
 */
onActivated(async () => {
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
  _updateArticleMeta(res.meta);

  codemirror.value = editorRef.value?.getEditorView()?.contentDOM;
  if (codemirror.value instanceof HTMLElement) {
    codemirror.value.addEventListener("paste", (e) => _handleCodemirrorCopy(e));
  }

  updateSaveTime();
});

/**
 * 组件卸载时的清理工作
 * 移除事件监听器
 */
onDeactivated(() => {
  // 清理事件监听器
  if (codemirror.value instanceof HTMLElement) {
    codemirror.value.removeEventListener("paste", (e) => _handleCodemirrorCopy(e));
    codemirror.value = null;
  }

  console.log("EditorPage 组件已卸载");
});
</script>

<style scoped>
.md-editor-v3-container {
  position: absolute;
  top: 60px;
  left: 0;
  right: 0;
  bottom: 0;
  height: calc(100vh - 60px);
}
</style>
