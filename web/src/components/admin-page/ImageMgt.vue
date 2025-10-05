<template>
  <div class="content-container">
    <div class="content-header">
      <h1>图片管理</h1>
    </div>
    <div class="content-body">
      <!-- 📷 图像管理: 错误显示 -->
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
      <div class="content-item">
        <span>选择专栏</span>
        <!-- 📷 图像管理: 选择专栏 -->
        <div class="select-wrapper">
          <select v-model="imageMgt.category" @change="onSelectImageCategory">
            <option disabled selected>请选择专栏</option>
            <option v-for="category in allCategories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
      </div>

      <!-- 📷 图像管理: 上传图像 -->
      <div class="content-item">
        <span>上传图片</span>
        <button class="btn btn-danger" style="padding: 10px 20px" @click="onShowUploadImageDialog">选择照片</button>
        <!-- 上传图像的位置 -->
        <UploadImage
          v-if="imageMgt.upload"
          :category="imageMgt.category"
          :show-confirm-button="false"
          @on-upload="onUploadImageSuccess"
          @on-close="onCloseUploadImageDialog"
        ></UploadImage>
      </div>

      <!-- 📷 图像管理: 图片列表 -->
      <div class="card-list">
        <div v-for="(url, index) in imageMgt.urls" :key="index" class="card-item">
          <div class="card-thumb">
            <img :src="url" />
          </div>

          <div class="card-meta">
            <div class="card-info">
              <div class="meta-item"><input type="text" style="width: 100%" v-model="imageMgt.newImages[index]" @change="onEditImageName(index)" /></div>
            </div>
          </div>

          <div class="card-action">
            <button class="btn-danger" @click="onDeleteImage(index)">删除</button>
            <a :href="url" download class="btn-info">下载</a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import UploadImage from "../UploadImage.vue";

import { ref } from "vue";
import { allImageInCategory, deleteImage, renameImage } from "../../utils/apis";

import Toast from "../../utils/toast.js";

const props = defineProps({
  allCategories: {
    type: Array,
    required: true,
    defualt: () => [],
  },
});

const errorMessage = ref("");

// 用于存储图片管理的分类和图片列表
const imageMgt = ref({ category: "", upload: false, urls: [], newImages: [], oldImages: [], suffix: [] });

/**
 * 选择图片分类时获取该分类下的所有图片
 */
async function onSelectImageCategory() {
  if (!imageMgt.value.category) return;

  // 获取该分类下的所有图片
  const res = await allImageInCategory(imageMgt.value.category);
  if (!Array.isArray(res)) {
    errorMessage.value = "获取图片失败，请稍后再试";
    Toast.error("获取图片失败，请稍后再试");
  } else {
    // 去掉后缀
    imageMgt.value.newImages = res.map((img) => img.replace(/\.(jpg|jpeg|png|gif|webp)$/, ""));
    imageMgt.value.oldImages = res.map((img) => img.replace(/\.(jpg|jpeg|png|gif|webp)$/, ""));
    imageMgt.value.suffix = res.map((img) => img.match(/\.(jpg|jpeg|png|gif|webp)$/)?.[0] || "");
    imageMgt.value.urls = res.map((img) => `/api/v1/website/image/${imageMgt.value.category}/${img}`);
    errorMessage.value = "";
    Toast.success("图片数据加载成功");
  }
}

/**
 * 上传图片成功后的回调
 * @param imageUrl {string} 上传成功的图片 URL
 */
async function onShowUploadImageDialog() {
  if (!imageMgt.value.category) {
    errorMessage.value = "请先选择一个专栏";
    Toast.warning("请先选择一个专栏");
    return;
  }

  errorMessage.value = "";
  imageMgt.value.upload = true;
}

/**
 * 上传图片成功后的回调
 * @param imageUrl {string} 上传成功的图片 URL
 */
async function onCloseUploadImageDialog() {
  imageMgt.value.upload = false;
}

/**
 * 编辑图片名称
 * @param index {number} 图片索引
 */
async function onEditImageName(index) {
  if (!confirm("确定要修改这张图片的名称吗？")) return;

  const newname = imageMgt.value.newImages[index];
  const oldname = imageMgt.value.oldImages[index];
  const suffix = imageMgt.value.suffix[index];
  if (!newname) {
    errorMessage.value = "图片名称不能为空";
    Toast.error("图片名称不能为空");
    return;
  }

  // 检查图片名称是否合法
  const regex = /^(?!-)[A-Za-z0-9_-]+$/;
  if (!regex.test(newname)) {
    errorMessage.value = "图片名称只能包含字母、数字和下划线和减号，且不能以减号开头";
    return;
  }

  // 检查图片是否已经存在
  const res = await renameImage(imageMgt.value.category, oldname + suffix, newname + suffix);
  if (!res.flag) {
    errorMessage.value = "修改图片名称失败，请稍后再试";
    Toast.error("修改图片名称失败，请稍后再试");
    return;
  }

  // 成功修改后，重新获取当前分类下的所有图片
  await onSelectImageCategory();
}

/**
 * 删除图片
 * @param index
 */
async function onDeleteImage(index) {
  if (!confirm("确定要删除这张图片吗？")) return;
  // 删除图片
  const imageName = imageMgt.value.newImages[index];
  const suffix = imageMgt.value.suffix[index];
  const res = await deleteImage(imageMgt.value.category, imageName + suffix);
  if (!res) {
    errorMessage.value = "删除图片失败，请稍后再试";
    Toast.error("删除图片失败，请稍后再试");
    return;
  }

  // 成功删除后，重新获取当前分类下的所有图片
  await onSelectImageCategory();
}

/**
 * 上传图片成功后的回调
 * 重新获取当前分类下的所有图片，并关闭上传图片对话框
 */
async function onUploadImageSuccess() {
  // 重新获取当前分类下的所有图片
  await onSelectImageCategory();
  // 关闭上传图片对话框
  onCloseUploadImageDialog();
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: left;
}

.card-item {
  padding: 16px;
  border-bottom: 1px solid #f1f1f1;
  display: flex;
  align-items: center;
  flex-direction: column;
  width: 232px;
  background-color: #86909c42;
  height: 256px;
  border-radius: 16px;
  gap: 8px;
  justify-content: space-between;
}

.card-item a {
  color: #171717;
  text-decoration: none;
}

.card-thumb {
  width: 120px;
  height: 80px;
  background: #f1f1f1;
  border-radius: 4px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}

.card-thumb img {
  height: inherit;
  width: inherit;
  object-fit: contain;
}

.card-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.card-title:hover {
  color: #1e80ff;
}

.card-action,
.card-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 13px;
  color: #86909c;
  justify-content: space-between;
}

.card-info {
  display: flex;
  gap: 16px;
  flex-direction: row;
  max-height: 36px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item input {
  width: 60px;
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}
</style>
