<template>
  <div class="content-container">
    <div class="content-header">
      <h1>图片管理</h1>
      <p>上传、重命名并下载各专栏的配图资源</p>
    </div>

    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="content-item">
        <span>选择专栏</span>
        <div class="select-wrapper">
          <select v-model="imageMgt.category" @change="onSelectImageCategory" :disabled="isLoading || isImageLoading">
            <option value="" disabled>请选择专栏</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
        <button class="btn btn-outline" type="button" @click="onRefreshImages" :disabled="!imageMgt.category || isImageLoading">刷新列表</button>
      </div>

      <div class="content-item">
        <span>上传图片</span>
        <div class="inline-actions">
          <button class="btn btn-primary" type="button" @click="onShowUploadImageDialog" :disabled="!imageMgt.category">选择照片</button>
          <span class="helper-text">支持 jpg / jpeg / png / gif / webp</span>
        </div>
      </div>

      <UploadImage
        v-if="imageMgt.upload"
        :category="imageMgt.category"
        :show-confirm-button="false"
        @on-upload="onUploadImageSuccess"
        @on-close="onCloseUploadImageDialog"
      ></UploadImage>

      <div v-if="isImageLoading" class="loading-stack">
        <div v-for="n in 6" :key="`image-skeleton-${n}`" class="loading-card">
          <div class="skeleton-line w-80"></div>
          <div class="skeleton-line w-40" style="margin-top: 12px"></div>
        </div>
      </div>

      <div v-else-if="imageMgt.urls.length" class="list-block">
        <div class="list-row image-row" v-for="(url, index) in imageMgt.urls" :key="url">
          <div class="thumbnail">
            <img :src="url" alt="图片缩略图" />
          </div>
          <div class="field field-grow">
            <span class="field-label">图片名称</span>
            <input class="field-input" type="text" v-model="imageMgt.newImages[index]" @change="onEditImageName(index)" />
          </div>
          <div class="inline-actions">
            <a class="btn btn-outline" :href="url" download>下载</a>
            <button class="btn btn-danger" @click="onDeleteImage(index)" :disabled="isImageLoading">删除</button>
          </div>
        </div>
      </div>

      <div v-else-if="imageMgt.category" class="empty-state">
        <div class="empty-icon">🖼️</div>
        <p>当前专栏暂未上传图片。</p>
        <button class="btn btn-outline" @click="onRefreshImages" :disabled="isImageLoading">重新加载</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import UploadImage from "../UploadImage.vue";
import { ref, computed } from "vue";
import { allImageInCategory, deleteImage, renameImage } from "../../utils/apis";
import Toast from "../../utils/toast.js";
import { useLoading } from "../../utils/use-loading";

const props = defineProps({
  allCategories: {
    type: Array,
    required: true,
    default: () => [],
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const errorMessage = ref("");
const imageMgt = ref({ category: "", upload: false, urls: [], newImages: [], oldImages: [], suffix: [] });
const { isLoading: isImageLoading, start: startImageLoading, stop: stopImageLoading } = useLoading("admin.image.list");

const IMAGE_SUFFIX_REG = /\.(jpg|jpeg|png|gif|webp)$/i;
const categories = computed(() => props.allCategories || []);

function mapImageResponse(res) {
  imageMgt.value.newImages = res.map((img) => img.replace(IMAGE_SUFFIX_REG, ""));
  imageMgt.value.oldImages = [...imageMgt.value.newImages];
  imageMgt.value.suffix = res.map((img) => img.match(IMAGE_SUFFIX_REG)?.[0] || "");
  imageMgt.value.urls = res.map((img) => `/api/v1/website/image/${imageMgt.value.category}/${img}`);
}

async function onSelectImageCategory() {
  if (!imageMgt.value.category) return;
  await fetchImageList();
}

async function onRefreshImages() {
  if (!imageMgt.value.category) return;
  await fetchImageList();
}

async function fetchImageList() {
  startImageLoading();
  try {
    const res = await allImageInCategory(imageMgt.value.category);
    if (!Array.isArray(res)) {
      throw new Error("获取图片失败");
    }
    mapImageResponse(res);
    errorMessage.value = "";
    Toast.success("图片数据加载成功");
  } catch (error) {
    console.error("获取图片失败:", error);
    imageMgt.value.urls = [];
    errorMessage.value = "获取图片失败，请稍后再试";
    Toast.error("获取图片失败，请稍后再试");
  } finally {
    stopImageLoading();
  }
}

function onShowUploadImageDialog() {
  if (!imageMgt.value.category) {
    errorMessage.value = "请先选择一个专栏";
    Toast.warning("请先选择一个专栏");
    return;
  }

  errorMessage.value = "";
  imageMgt.value.upload = true;
}

function onCloseUploadImageDialog() {
  imageMgt.value.upload = false;
}

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

  const regex = /^(?!-)[A-Za-z0-9_-]+$/;
  if (!regex.test(newname)) {
    errorMessage.value = "图片名称只能包含字母、数字和下划线和减号，且不能以减号开头";
    Toast.error("图片名称只能包含字母、数字和下划线和减号，且不能以减号开头");
    imageMgt.value.newImages[index] = imageMgt.value.oldImages[index];
    return;
  }

  const res = await renameImage(imageMgt.value.category, oldname + suffix, newname + suffix);
  if (!res.flag) {
    errorMessage.value = "修改图片名称失败，请稍后再试";
    Toast.error("修改图片名称失败，请稍后再试");
    imageMgt.value.newImages[index] = imageMgt.value.oldImages[index];
    return;
  }

  await fetchImageList();
  Toast.success("图片名称修改成功");
}

async function onDeleteImage(index) {
  if (!confirm("确定要删除这张图片吗？")) return;
  const imageName = imageMgt.value.newImages[index];
  const suffix = imageMgt.value.suffix[index];
  const res = await deleteImage(imageMgt.value.category, imageName + suffix);
  if (!res) {
    errorMessage.value = "删除图片失败，请稍后再试";
    Toast.error("删除图片失败，请稍后再试");
    return;
  }

  await fetchImageList();
  Toast.success("图片删除成功");
}

async function onUploadImageSuccess() {
  await fetchImageList();
  onCloseUploadImageDialog();
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.thumbnail {
  width: 72px;
  height: 72px;
  border-radius: 6px;
  overflow: hidden;
  background: #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.helper-text {
  color: #6b7280;
  font-size: 13px;
}
</style>
