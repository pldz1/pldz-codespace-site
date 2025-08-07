<template>
  <teleport to="body">
    <div class="image-upload-overlay">
      <div class="image-upload-container">
        <div class="image-upload-header">
          <h2>上传专栏图片</h2>
          <div class="image-upload-close" @click="onClose"></div>
        </div>
        <div class="image-upload-content">
          <!-- 专栏信息 -->
          <div class="image-upload-item">
            <span class="label">专栏:</span>
            <span>{{ props.category }}</span>
          </div>
          <!-- 名称输入框 -->
          <div class="image-upload-item">
            <span class="label">名称* :</span>
            <input type="text" placeholder="请输入名称" @input="onCheckImageName" v-model="imageName" />
          </div>
          <!-- 错误提示 -->
          <div :style="{ color: 'red', fontSize: '16px', maxHeight: '32px' }">
            {{ imageUploadError }}
          </div>
          <!-- 图片预览 -->
          <div v-if="!imageUploadError && !showConfirmButton" class="image-upload-item upload-image-preview" @click="onUploadImage">
            <img v-if="imagePreviewUrl" :src="imagePreviewUrl" alt="Image Preview" />
          </div>
          <!-- 确认上传按钮 -->
          <div v-if="showConfirmButton" class="image-upload-item" style="justify-content: flex-end">
            <button class="confirm-button" @click="onUploadImageFromCopy">确认</button>
          </div>
        </div>
      </div>
    </div>
  </teleport>
</template>

<script setup>
import { ref } from "vue";
import { checkImageExit } from "../utils/apis";
import { uploadArticleImage, uploadArticleImageFromCopy } from "../utils/file-upload.js";

const emit = defineEmits(["on-close", "on-upload"]);
const props = defineProps({
  category: {
    type: String,
    default: "",
    required: true,
  },
  showConfirmButton: {
    type: Boolean,
    default: false,
  },
});

// 上传的图像的URL
const imageName = ref("");
const imagePreviewUrl = ref("");
const imageUploadError = ref("图像名称不能为空！");
let checkNameTimer = null;

/**
 * 校验上传的图像名字
 */
async function onCheckImageName() {
  if (!imageName.value) {
    imageUploadError.value = "图像名称不能为空！";
    return;
  }

  clearTimeout(checkNameTimer);

  checkNameTimer = setTimeout(async () => {
    // 只支持字母数字下划线和减号, 减号不能开头
    const regex = /^(?!-)[A-Za-z0-9_-]+$/;
    if (!regex.test(imageName.value)) {
      imageUploadError.value = "图像名称只能包含字母、数字和下划线和减号，且不能以减号开头";
      return;
    } else {
      imageUploadError.value = "";
    }

    const res = await checkImageExit(props.category, imageName.value);
    if (!res) {
      imageUploadError.value = "图像已经存在！";
      return;
    }
  }, 500);
}

/**
 * 处理上传图像的返回结果
 * @param res 上传图像的返回结果
 */
function afterUploadImage(res) {
  // 检查返回结果
  if (!res || !res?.data || !res.data.flag || !res.data.url) {
    imageUploadError.value = "上传失败！";
    return;
  }

  imagePreviewUrl.value = res.data.url;
  imageUploadError.value = "";

  // 触发上传成功事件
  emit("on-upload", { url: res.data.url, name: imageName.value });
}

/**
 * 上传图像
 */
async function onUploadImage() {
  // 图像有错误不能删除
  if (imageUploadError.value) return;

  const res = await uploadArticleImage(props.category, imageName.value);
  // 检查返回结果
  afterUploadImage(res);
}

/**
 * 从剪贴板上传图像
 */
async function onUploadImageFromCopy() {
  // 图像有错误不能删除
  if (imageUploadError.value) return;

  const res = await uploadArticleImageFromCopy(props.category, imageName.value);
  // 检查返回结果
  afterUploadImage(res);
}

/**
 * 关闭上传图像对话框
 */
function onClose() {
  emit("on-close");
  imageName.value = "";
  imagePreviewUrl.value = "";
  imageUploadError.value = "图像名称不能为空！";
  clearTimeout(checkNameTimer);
}
</script>

<style scoped>
.image-upload-overlay {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 100009;
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

.image-upload-close:hover {
  cursor: pointer;
  border-radius: 50%;
  border: 1px solid #ccc;
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

.confirm-button {
  background-color: #4caf50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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
</style>
