<template>
  <ModalToolbar
    :visible="modalState.modalVisible"
    :isFullscreen="modalState.modalFullscreen"
    showAdjust
    title="编辑元数据"
    modalTitle="编辑元数据"
    width="870px"
    height="600px"
    @onClick="onClick"
    @onClose="onClose"
    @onAdjust="modalState.modalFullscreen = !modalState.modalFullscreen"
  >
    <div class="meta-setting-sidebar-container">
      <div class="meta-setting-item">
        <span>专栏</span>
        <input class="meta-setting-input" v-model="articleMeta.category" placeholder="请输入专栏" />
      </div>
      <div class="meta-setting-item">
        <span>文章标题</span>
        <input class="meta-setting-input" v-model="articleMeta.title" placeholder="请输入文章标题" />
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
        <div class="thumbnail-container" @click="onShowUploadImageDialog">
          <img class="thumbnail-image" :src="articleMeta.thumbnail" />
          <div class="overlay-button">+</div>
        </div>
      </div>
      <div class="meta-setting-item">
        <span>图像源</span>
        <input class="meta-setting-input" v-model="articleMeta.thumbnail" placeholder="有效的图片路径" />
      </div>
    </div>
    <template #trigger>
      <FolderPen class="md-editor-icon" />
    </template>
  </ModalToolbar>

  <UploadImage v-if="showUploadImageDialog" :category="articleMeta.category" @on-close="onCloseUploadImageDialog" @on-upload="onUploadImage"></UploadImage>
</template>

<script setup>
import { reactive, ref } from "vue";
import { FolderPen } from "lucide-vue-next";
import { ModalToolbar } from "md-editor-v3";
import UploadImage from "../UploadImage.vue";

const emit = defineEmits(["on-update"]);

const props = defineProps({
  meta: {
    type: Object,
    default: () => ({
      title: "",
      thumbnail: "",
      category: "",
      tags: "",
      date: "",
      serialNo: 0,
      summary: "",
    }),
  },
});

/**
 * 弹窗的状态数据
 */
const modalState = reactive({
  modalVisible: false,
  modalFullscreen: false,
});

const articleTags = ref("");
const articleMeta = ref({ ...props.meta });
const showUploadImageDialog = ref(false);

/**
 * 处理标签变化
 */
function onTagsChange() {
  articleMeta.value.tags = JSON.parse(articleTags.value) || "";
}

/**
 * 显示上传图像对话框
 */
function onShowUploadImageDialog() {
  showUploadImageDialog.value = true;
  const app = document.getElementById("app");
  if (app) app.style.opacity = "0.04";
}

/**
 * 关闭上传图像对话框
 */
function onCloseUploadImageDialog() {
  showUploadImageDialog.value = false;
  const app = document.getElementById("app");
  if (app) app.style.cssText = "";
}
/**
 * 上传图像回调
 * @param data 上传的图像数据
 */
function onUploadImage(data) {
  articleMeta.value.thumbnail = data?.url;
  showUploadImageDialog.value = false;
}

/**
 * 监听元数据变化
 * 更新本地状态
 */
function onClick() {
  articleMeta.value = { ...props.meta };
  articleTags.value = JSON.stringify(props.meta?.tags || []);
  modalState.modalVisible = true;
}

/**
 * 关闭对话框
 */
function onClose() {
  modalState.modalVisible = false;
  emit("on-update", articleMeta.value);
}
</script>

<style scoped>
.meta-setting-sidebar-container {
  margin: 0 auto;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  max-height: 100%;
  overflow-y: auto;
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
</style>
