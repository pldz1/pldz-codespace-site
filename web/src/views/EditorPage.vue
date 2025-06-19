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
@import url("../assets/views/editor-content.css");
</style>
