<template>
  <div class="content-container">
    <div class="content-header">
      <h1>缓存资源管理</h1>
    </div>
    <div class="content-body">
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
      <div class="content-item">
        <span>上传缓存资源</span>
        <button class="btn btn-primary" @click="onUploadCacheFile">上传</button>
        <div class="content-item" style="border-top: 1px solid #e4e6ea; margin-top: 8px"></div>
      </div>
      <!-- 广告的列表 -->
      <div class="row-list">
        <div class="row-item" v-for="(cache, index) in cacheMgt" :key="index" style="flex: 1; flex-direction: row">
          <!-- 序号 -->
          <div class="row-serial">{{ index + 1 }}</div>
          <!-- 缓存文件名字 -->
          <div class="row-content" style="flex-direction: row">
            <input type="text" :value="cache" readonly />
            <div class="item-actions" style="justify-content: right">
              <button @click="onDownloadCacheFile(cache)" style="padding: 8px; width: 54px; background-color: #1890ff">下载</button>
              <button @click="onDeleteCacheFile(cache)" style="padding: 8px; width: 54px; margin-left: 8px">删除</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getAllCache, deleteCacheFile, downloadCacheFile } from "../../utils/apis";
import { uploadCacheFile } from "../../utils/file-upload.js";
import Toast from "../../utils/toast.js";

// 用于存储缓存资源管理的数据
const cacheMgt = ref([]);

/**
 * 删除缓存文件
 * @param filename {string} 缓存文件名
 * @returns {Promise<void>}
 */
async function onDeleteCacheFile(filename) {
  // 删除缓存文件
  const res = await deleteCacheFile(filename);
  if (res) {
    // 成功删除后，重新获取所有缓存数据
    await onSelectCacheManagement();
  } else {
    errorMessage.value = "删除缓存文件失败，请稍后再试";
    Toast.error("删除缓存文件失败，请稍后再试");
    return;
  }
}

/**
 * 下载缓存文件
 * @param filename {string} 缓存文件名
 */
async function onDownloadCacheFile(filename) {
  // 下载缓存文件
  const res = await downloadCacheFile(filename);
  if (res) {
    // 创建一个 Blob 对象并下载
    const blob = new Blob([res], { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } else {
    errorMessage.value = "下载缓存文件失败，请稍后再试";
    Toast.error("下载缓存文件失败，请稍后再试");
    return;
  }
  Toast.success("缓存文件下载成功");
  errorMessage.value = "";
}

/**
 * 上传缓存文件
 */
async function onUploadCacheFile() {
  const res = await uploadCacheFile();
  if (res) {
    // 成功上传后，重新获取所有缓存数据
    await onSelectCacheManagement();
    Toast.success("缓存文件上传成功");
    errorMessage.value = "";
  } else {
    errorMessage.value = "上传缓存文件失败，请稍后再试";
    Toast.error("上传缓存文件失败，请稍后再试");
  }
}

/**
 * 获取所有缓存数据
 */
async function onSelectCacheManagement() {
  const res = await getAllCache();
  if (res) {
    cacheMgt.value = res;
    Toast.success("缓存数据加载成功");
    errorMessage.value = "";
  } else {
    errorMessage.value = "获取缓存数据失败，请稍后再试";
    Toast.error("获取缓存数据失败，请稍后再试");
  }
}

/**
 * 初始化时获取所有缓存数据
 */
onMounted(async () => {
  // 初始化时获取所有缓存数据
  await onSelectCacheManagement();
});
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.row-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.row-item {
  display: flex;
  align-items: center;
  padding: 8px;
  background: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.row-serial {
  font-size: 18px;
  font-weight: bold;
  color: #555;
  width: 24px;
  text-align: center;
  margin-right: 8px;
  border-right: 2px solid #e0e0e0;
}

.row-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.row-content input[type="text"],
.row-content input[type="url"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.item-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  justify-content: right;
}

.item-actions label {
  display: flex;
  align-items: center;
  font-size: 14px;
  cursor: pointer;
}

.item-actions button {
  padding: 8px 14px;
  font-size: 14px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  background: #e74c3c;
  color: #fff;
  transition: background 0.2s;
}

.item-actions button:hover {
  background: #c0392b;
}
</style>
