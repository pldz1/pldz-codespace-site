<template>
  <div class="content-container">
    <div class="content-header">
      <h1>缓存资源管理</h1>
    </div>
    <div class="progress-toast-container" v-if="activeDownloads.length">
      <div v-for="item in activeDownloads" :key="item.name" :class="['progress-toast', 'progress-toast--' + item.state]">
        <div class="progress-toast-title">{{ item.name }}</div>
        <div class="progress-toast-bar">
          <div class="progress-toast-bar-inner" :style="{ width: item.state === 'error' ? '100%' : (item.percent || 0) + '%' }"></div>
        </div>
        <div class="progress-toast-percent">{{ formatProgressText(item) }}</div>
      </div>
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
            <input type="text" :value="cache.modified_time + ' | ' + cache.filename" readonly />
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
import { ref, onMounted, reactive, computed } from "vue";
import { getAllCache, deleteCacheFile } from "../../utils/apis";
import { uploadCacheFile } from "../../utils/file-upload.js";
import Toast from "../../utils/toast.js";

const errorMessage = ref("");
// 用于存储缓存资源管理的数据
const cacheMgt = ref([]);
// 下载进度: { [filename]: { percent: number, loaded: number, total: number, state: 'downloading'|'done'|'error' } }
const downloadProgress = reactive({});

const activeDownloads = computed(() =>
  Object.entries(downloadProgress)
    .filter(([, item]) => item.state !== "hidden")
    .map(([name, item]) => ({ name, ...item }))
);

/**
 * 删除缓存文件
 * @param filename {string} 缓存文件名
 * @returns {Promise<void>}
 */
async function onDeleteCacheFile(filename) {
  if (!confirm(`确定要删除${filename.filename}吗？`)) return;
  // 删除缓存文件
  const res = await deleteCacheFile(filename.filename);
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
async function onDownloadCacheFile(fileObj) {
  const fname = fileObj.filename;
  // 初始化进度
  downloadProgress[fname] = { percent: 0, loaded: 0, total: 0, state: "downloading" };

  try {
    const res = await fetch("/api/v1/resource/cache/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ filename: fname }),
    });
    if (!res.ok) {
      throw new Error(`${res.status} ${res.statusText}`);
    }

    const total = Number(res.headers.get("content-length")) || 0;
    downloadProgress[fname].total = total;

    if (!res.body || !res.body.getReader) {
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = fname;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      if (downloadProgress[fname]) {
        downloadProgress[fname].loaded = total || downloadProgress[fname].loaded || 0;
        downloadProgress[fname].percent = 100;
        downloadProgress[fname].state = "done";
      }
      setTimeout(() => {
        if (downloadProgress[fname]) {
          downloadProgress[fname].state = "hidden";
        }
        setTimeout(() => {
          delete downloadProgress[fname];
        }, 200);
      }, 800);
      Toast.success("缓存文件下载成功");
      errorMessage.value = "";
      return;
    }

    const reader = res.body.getReader();
    const chunks = [];
    let loaded = 0;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      chunks.push(value);
      loaded += value.length;
      downloadProgress[fname].loaded = loaded;
      if (total > 0) {
        downloadProgress[fname].percent = Math.min(100, (loaded / total) * 100);
      } else {
        // 无总长度时，仅展示已下载字节数
        downloadProgress[fname].percent = 0;
      }
    }

    const blob = new Blob(chunks, { type: "application/octet-stream" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fname;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    if (downloadProgress[fname]) {
      downloadProgress[fname].loaded = total || downloadProgress[fname].loaded;
      downloadProgress[fname].percent = 100;
      downloadProgress[fname].state = "done";
    }
    setTimeout(() => {
      if (downloadProgress[fname]) {
        downloadProgress[fname].state = "hidden";
      }
      setTimeout(() => {
        delete downloadProgress[fname];
      }, 200);
    }, 800);
    Toast.success("缓存文件下载成功");
    errorMessage.value = "";
  } catch (err) {
    console.error("下载缓存文件失败:", err);
    if (downloadProgress[fname]) {
      downloadProgress[fname].state = "error";
    }
    setTimeout(() => {
      if (downloadProgress[fname]) {
        downloadProgress[fname].state = "hidden";
      }
      setTimeout(() => {
        delete downloadProgress[fname];
      }, 200);
    }, 1600);
    errorMessage.value = "下载缓存文件失败，请稍后再试";
    Toast.error("下载缓存文件失败，请稍后再试");
  }
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
  if (Array.isArray(res)) {
    // 把res里的对象的根据modified_time按照日期排序,并且改成年-月-日 时:分:秒格式
    res
      .sort((a, b) => b.modified_time - a.modified_time)
      .forEach((item) => {
        const d = new Date(item.modified_time * 1000);
        item.modified_time = d.toISOString().replace("T", " ").split(".")[0];
        // 结果: 2025-08-15 21:53:17
      });
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

function formatProgressText(item) {
  if (!item) return "";
  if (item.state === "error") {
    return "下载失败";
  }
  if (item.state === "done") {
    return "100%";
  }
  if (item.total > 0) {
    const percent = item.percent || 0;
    return `${Math.min(100, percent).toFixed(0)}%`;
  }

  const loaded = item.loaded || 0;
  if (!loaded) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = loaded;
  let unitIndex = 0;
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }
  const precision = size >= 10 || unitIndex === 0 ? 0 : 1;
  return `${size.toFixed(precision)} ${units[unitIndex]}`;
}
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
.progress-toast-container {
  position: fixed;
  top: 64px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1000;
}

.progress-toast {
  min-width: 220px;
  max-width: 280px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
}

.progress-toast-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
  word-break: break-all;
}

.progress-toast-bar {
  position: relative;
  width: 100%;
  height: 6px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-toast-bar-inner {
  height: 100%;
  background: #1890ff;
  transition: width 0.2s ease;
}

.progress-toast-percent {
  margin-top: 8px;
  text-align: right;
  font-size: 12px;
  color: #555;
  font-weight: 500;
}

.progress-toast--done {
  border-color: #52c41a;
}

.progress-toast--done .progress-toast-bar-inner {
  background: #52c41a;
}

.progress-toast--error {
  border-color: #ff4d4f;
}

.progress-toast--error .progress-toast-bar-inner {
  background: #ff4d4f;
}
</style>
