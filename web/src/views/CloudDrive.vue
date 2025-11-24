<template>
  <HeaderBar :route-name="'云盘共享'" :show-mobile-menu="false" />
  <div class="drive-page">
    <div class="progress-toast-container" v-if="activeTransfers.length">
      <div
        v-for="item in activeTransfers"
        :key="item.name"
        :class="['progress-toast', 'progress-toast--' + item.state]"
      >
        <div class="progress-toast-title">{{ item.name }}</div>
        <div class="progress-toast-bar">
          <div
            class="progress-toast-bar-inner"
            :style="{ width: item.state === 'error' ? '100%' : (item.percent || 0) + '%' }"
          ></div>
        </div>
        <div class="progress-toast-percent">{{ formatProgressText(item) }}</div>
      </div>
    </div>

    <div class="panel token-panel">
      <h1>云盘共享</h1>
      <p class="subtitle">输入管理员提供的口令，在 7 天有效期内上传或下载文件。</p>
      <div class="token-input">
        <input
          v-model="tokenInput"
          type="text"
          placeholder="输入云盘口令"
          @keyup.enter="handleVerify"
        />
        <button class="btn btn-primary" @click="handleVerify" :disabled="!tokenInput || verifying">
          {{ verifying ? "验证中…" : "验证口令" }}
        </button>
      </div>
      <div v-if="tokenData" class="token-result">
        <div class="token-meta">
          <div class="meta-row">
            <span class="label">口令</span>
            <code class="value">{{ tokenData.token }}</code>
          </div>
          <div class="meta-grid">
            <div>
              <span class="label">有效期至</span>
              <span class="value">{{ formatDate(tokenData.expires_at) }}</span>
            </div>
            <div>
              <span class="label">允许上传</span>
              <span class="value">{{ tokenData.allow_upload ? "是" : "否" }}</span>
            </div>
            <div>
              <span class="label">允许下载</span>
              <span class="value">{{ tokenData.allow_download ? "是" : "否" }}</span>
            </div>
            <div>
              <span class="label">文件状态</span>
              <span class="value">{{ currentFileLabel }}</span>
            </div>
          </div>
        </div>
        <div class="action-buttons">
          <button class="btn btn-primary" @click="handleUpload" :disabled="!canUpload">
            {{ uploadBusy ? "上传中…" : "上传文件" }}
          </button>
          <button class="btn btn-info" @click="handleDownload" :disabled="!canDownload">
            {{ downloadBusy ? "下载中…" : "下载文件" }}
          </button>
          <button class="btn btn-outline" type="button" @click="refreshTokenInfo" :disabled="verifying">
            刷新状态
          </button>
        </div>
        <p v-if="downloadTip" class="tip">{{ downloadTip }}</p>
      </div>
    </div>

    <div v-if="isAdmin" class="panel admin-entry">
      <div class="admin-entry-text">
        <h2>管理员工具</h2>
        <p>生成云盘口令并管理已有口令。</p>
      </div>
      <button class="btn btn-primary admin-entry-button" type="button" @click="openAdminOverlay">
        管理
      </button>
    </div>
  </div>

  <div
    v-if="isAdmin && showAdminOverlay"
    class="admin-overlay-mask"
    @click.self="closeAdminOverlay"
  >
    <div class="panel admin-panel admin-overlay-card" @click.stop>
      <div class="admin-overlay-header">
        <h2>生成云盘口令（管理员）</h2>
        <button class="admin-overlay-close" type="button" @click="closeAdminOverlay">
          关闭
        </button>
      </div>
      <div class="admin-form">
        <label>
          <input type="checkbox" v-model="adminForm.allowUpload" />
          允许上传
        </label>
        <label>
          <input type="checkbox" v-model="adminForm.allowDownload" />
          允许下载
        </label>
        <div class="cache-select">
          <select
            v-model="adminForm.filename"
            :disabled="!adminForm.allowDownload || cacheLoading"
          >
            <option value="">
              选择下载文件（可选）
            </option>
            <option
              v-for="file in cacheFiles"
              :key="file.filename"
              :value="file.filename"
            >
              {{ file.filename }} · {{ formatFileSize(file.size || 0) }}
            </option>
          </select>
          <button
            class="btn btn-outline btn-small"
            type="button"
            @click="loadCacheFiles"
            :disabled="cacheLoading"
          >
            {{ cacheLoading ? "加载中…" : "刷新缓存" }}
          </button>
        </div>
        <p v-if="cacheError" class="cache-error">{{ cacheError }}</p>
        <input v-model="adminForm.description" type="text" placeholder="备注（可选）" />
        <button class="btn btn-primary" type="button" @click="handleGenerateToken" :disabled="generating">
          {{ generating ? "生成中…" : "生成口令" }}
        </button>
      </div>
      <div v-if="generatedToken" class="generated-token">
        <div class="token-display">
          <span class="token-value">{{ generatedToken.token }}</span>
          <button class="btn btn-info" type="button" @click="copyGeneratedToken">复制口令</button>
        </div>
        <div class="token-summary">
          <span>有效期至 {{ formatDate(generatedToken.expires_at) }}</span>
          <span>允许上传: {{ generatedToken.allow_upload ? "是" : "否" }}</span>
          <span>允许下载: {{ generatedToken.allow_download ? "是" : "否" }}</span>
        </div>
        <p v-if="generatedToken.description" class="token-desc">备注: {{ generatedToken.description }}</p>
      </div>

      <div class="token-list-header">
        <h3>已生成口令</h3>
        <button class="btn btn-outline" type="button" @click="loadAdminTokens" :disabled="tokensLoading">
          {{ tokensLoading ? "刷新中…" : "刷新列表" }}
        </button>
      </div>

      <div v-if="tokensError" class="error-banner">{{ tokensError }}</div>
      <div v-else>
        <div v-if="tokensLoading" class="loading-stack">
          <div v-for="n in 4" :key="`token-loading-${n}`" class="loading-card">
            <div class="skeleton-line w-60"></div>
            <div class="skeleton-line w-40"></div>
          </div>
        </div>
        <div v-else-if="adminTokens.length" class="token-table-wrapper">
          <table class="token-table">
            <thead>
              <tr>
                <th>口令</th>
                <th>有效期</th>
                <th>上传</th>
                <th>下载</th>
                <th>文件</th>
                <th>备注</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="token in adminTokens" :key="token.token">
                <td class="mono">{{ token.token }}</td>
                <td>{{ formatDate(token.expires_at) }}</td>
                <td>{{ token.allow_upload ? "是" : "否" }}</td>
                <td>{{ token.allow_download ? "是" : "否" }}</td>
                <td>
                  <span v-if="token.has_file">
                    {{ token.original_filename || token.filename }} · {{ formatFileSize(token.size || 0) }}
                  </span>
                  <span v-else>暂无文件</span>
                </td>
                <td>{{ token.description || "-" }}</td>
                <td class="actions">
                  <button class="btn btn-outline btn-small" type="button" @click="copyExistingToken(token.token)">
                    复制
                  </button>
                  <button class="btn btn-danger btn-small" type="button" @click="openDeleteDialog(token)">
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="empty-state">
          <div class="empty-icon">🔐</div>
          <p>暂无可用口令，点击上方按钮生成或刷新。</p>
        </div>
      </div>
    </div>
  </div>

  <div v-if="showDeleteDialog" class="dialog-mask">
    <div class="dialog-card">
      <h3>删除口令</h3>
      <p class="dialog-desc">
        确认要删除口令
        <code>{{ tokenToDelete?.token }}</code>
        吗？删除后使用该口令的上传/下载链接将失效。
      </p>
      <div class="dialog-actions">
        <button class="btn btn-outline" type="button" @click="closeDeleteDialog" :disabled="deletingToken">
          取消
        </button>
        <button class="btn btn-danger" type="button" @click="confirmDeleteToken" :disabled="deletingToken">
          {{ deletingToken ? "删除中…" : "确认删除" }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useStore } from "vuex";
import HeaderBar from "../components/HeaderBar.vue";
import Toast from "../utils/toast.js";
import { createDriveToken, verifyDriveToken, listDriveTokens, deleteDriveToken } from "../utils/apis/cloud-drive.js";
import { getAllCache } from "../utils/apis/cache-post.js";

const store = useStore();
const isAdmin = computed(() => !!store.state.authState.isadmin);

const tokenInput = ref("");
const tokenData = ref(null);
const verifying = ref(false);
const uploadBusy = ref(false);
const downloadBusy = ref(false);

const transferProgress = reactive({});
const activeTransfers = computed(() =>
  Object.entries(transferProgress)
    .filter(([, item]) => item.state !== "hidden")
    .map(([key, item]) => ({ name: item.label || key, ...item }))
);

const adminForm = reactive({
  allowUpload: true,
  allowDownload: false,
  filename: "",
  description: "",
});
const generating = ref(false);
const generatedToken = ref(null);

const adminTokens = ref([]);
const tokensLoading = ref(false);
const tokensError = ref("");
const showDeleteDialog = ref(false);
const tokenToDelete = ref(null);
const deletingToken = ref(false);
const cacheFiles = ref([]);
const cacheLoading = ref(false);
const cacheError = ref("");
const showAdminOverlay = ref(false);

watch(isAdmin, (value) => {
  if (!value) {
    adminTokens.value = [];
    cacheFiles.value = [];
    showAdminOverlay.value = false;
  }
});

watch(showAdminOverlay, (value) => {
  if (value && isAdmin.value) {
    loadAdminTokens();
    if (!cacheFiles.value.length || cacheError.value) {
      loadCacheFiles();
    }
  }

  if (typeof document !== "undefined") {
    if (value) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
  }
});

watch(
  () => adminForm.allowDownload,
  (value) => {
    if (!value) {
      adminForm.filename = "";
      return;
    }
    if (isAdmin.value && showAdminOverlay.value && !cacheFiles.value.length) {
      loadCacheFiles();
    }
  }
);

const canUpload = computed(() => {
  if (!tokenData.value) return false;
  if (!tokenData.value.allow_upload) return false;
  return !uploadBusy.value;
});

const canDownload = computed(() => {
  if (!tokenData.value) return false;
  if (!tokenData.value.allow_download) return false;
  if (!tokenData.value.has_file) return false;
  return !downloadBusy.value;
});

const downloadTip = computed(() => {
  if (!tokenData.value) return "";
  if (!tokenData.value.allow_download) {
    return "该口令未开启下载权限。";
  }
  if (!tokenData.value.has_file) {
    return "暂未找到可下载的文件，请先上传或联系管理员。";
  }
  return "";
});

const currentFileLabel = computed(() => {
  if (!tokenData.value || !tokenData.value.has_file) {
    return "暂无文件";
  }
  const name = tokenData.value.original_filename || tokenData.value.filename || "文件";
  const size = formatFileSize(tokenData.value.size || 0);
  return `${name} · ${size}`;
});

function formatDate(iso) {
  if (!iso) return "-";
  try {
    const date = new Date(iso);
    return date.toLocaleString();
  } catch {
    return iso;
  }
}

function formatFileSize(bytes) {
  const value = Number(bytes);
  if (!Number.isFinite(value) || value <= 0) return "0 B";
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = value;
  let idx = 0;
  while (size >= 1024 && idx < units.length - 1) {
    size /= 1024;
    idx += 1;
  }
  const precision = size >= 10 || idx === 0 ? 0 : 1;
  return `${size.toFixed(precision)} ${units[idx]}`;
}

function formatProgressText(item) {
  if (!item) return "";
  if (item.state === "error") {
    return item.mode === "upload" ? "上传失败" : "下载失败";
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

function completeTransfer(key, total) {
  if (!transferProgress[key]) return;
  const entry = transferProgress[key];
  const finalTotal = total || entry.total || entry.loaded || 0;
  entry.total = finalTotal;
  entry.loaded = finalTotal;
  entry.percent = 100;
  entry.state = "done";
  setTimeout(() => {
    if (transferProgress[key]) {
      transferProgress[key].state = "hidden";
    }
    setTimeout(() => {
      delete transferProgress[key];
    }, 200);
  }, 800);
}

function markTransferFailed(key) {
  if (!transferProgress[key]) return;
  transferProgress[key].state = "error";
  setTimeout(() => {
    if (transferProgress[key]) {
      transferProgress[key].state = "hidden";
    }
    setTimeout(() => {
      delete transferProgress[key];
    }, 200);
  }, 1600);
}

async function fetchTokenInfo(token) {
  const trimmed = (token || "").trim();
  if (!trimmed) {
    throw new Error("口令不能为空");
  }
  try {
    const info = await verifyDriveToken(trimmed);
    tokenData.value = info;
    tokenInput.value = info.token;
    return info;
  } catch (error) {
    tokenData.value = null;
    throw error;
  }
}

async function handleVerify() {
  if (!tokenInput.value.trim()) {
    Toast.error("请输入口令");
    return;
  }
  verifying.value = true;
  try {
    await fetchTokenInfo(tokenInput.value);
    Toast.success("口令验证成功");
    if (isAdmin.value) {
      await loadAdminTokens();
    }
  } catch (error) {
    Toast.error(error.message || "口令验证失败");
  } finally {
    verifying.value = false;
  }
}

async function refreshTokenInfo() {
  if (!tokenData.value) return;
  verifying.value = true;
  try {
    await fetchTokenInfo(tokenData.value.token);
    Toast.success("已刷新状态");
    if (isAdmin.value) {
      await loadAdminTokens();
    }
  } catch (error) {
    Toast.error(error.message || "刷新失败");
  } finally {
    verifying.value = false;
  }
}

async function loadAdminTokens() {
  if (!isAdmin.value) return;
  tokensLoading.value = true;
  tokensError.value = "";
  try {
    const list = await listDriveTokens();
    adminTokens.value = Array.isArray(list) ? list : [];
  } catch (error) {
    tokensError.value = error.message || "加载口令列表失败";
    Toast.error(tokensError.value);
  } finally {
    tokensLoading.value = false;
  }
}

async function loadCacheFiles() {
  if (!isAdmin.value) return;
  cacheLoading.value = true;
  cacheError.value = "";
  try {
    const list = await getAllCache();
    cacheFiles.value = Array.isArray(list) ? list : [];
  } catch (error) {
    cacheError.value = error.message || "加载缓存文件列表失败";
    Toast.error(cacheError.value);
  } finally {
    cacheLoading.value = false;
  }
}

async function handleGenerateToken() {
  if (!adminForm.allowUpload && !adminForm.allowDownload) {
    Toast.error("请至少开启上传或下载中的一项权限");
    return;
  }
  generating.value = true;
  try {
    const payload = {
      allow_upload: adminForm.allowUpload,
      allow_download: adminForm.allowDownload,
      filename: adminForm.filename.trim() || undefined,
      description: adminForm.description.trim() || undefined,
    };
    const token = await createDriveToken(payload);
    generatedToken.value = token;
    tokenInput.value = token.token;
    Toast.success("口令生成成功");
    try {
      await fetchTokenInfo(token.token);
    } catch (error) {
      console.error("口令生成后验证失败:", error);
    }
    await loadAdminTokens();
  } catch (error) {
    Toast.error(error.message || "口令生成失败");
  } finally {
    generating.value = false;
  }
}

async function copyText(value) {
  if (!value) return false;
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(value);
    } else {
      const textarea = document.createElement("textarea");
      textarea.value = value;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "absolute";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
    Toast.success("已复制到剪贴板");
    return true;
  } catch (error) {
    console.error(error);
    Toast.error("复制失败，请手动复制");
    return false;
  }
}

function copyGeneratedToken() {
  if (!generatedToken.value) return;
  copyText(generatedToken.value.token);
}

function copyExistingToken(value) {
  copyText(value);
}

function openAdminOverlay() {
  if (!isAdmin.value) return;
  showAdminOverlay.value = true;
}

function closeAdminOverlay() {
  showAdminOverlay.value = false;
  closeDeleteDialog();
}

function openDeleteDialog(token) {
  tokenToDelete.value = token;
  showDeleteDialog.value = true;
}

function closeDeleteDialog() {
  showDeleteDialog.value = false;
  deletingToken.value = false;
  tokenToDelete.value = null;
}

async function confirmDeleteToken() {
  if (!tokenToDelete.value) return;
  deletingToken.value = true;
  try {
    await deleteDriveToken(tokenToDelete.value.token);
    Toast.success("口令已删除");
    closeDeleteDialog();
    await loadAdminTokens();
  } catch (error) {
    Toast.error(error.message || "删除失败");
  } finally {
    deletingToken.value = false;
  }
}

function selectLocalFile() {
  return new Promise((resolve) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "*/*";
    input.style.display = "none";
    document.body.appendChild(input);
    input.addEventListener("change", () => {
      const file = input.files && input.files[0] ? input.files[0] : null;
      document.body.removeChild(input);
      resolve(file);
    });
    input.click();
  });
}

async function handleUpload() {
  if (!tokenData.value || !tokenData.value.token) return;
  const file = await selectLocalFile();
  if (!file) return;

  const progressKey = `upload-${Date.now()}-${file.name}`;
  transferProgress[progressKey] = {
    label: `上传 ${file.name}`,
    percent: 0,
    loaded: 0,
    total: file.size || 0,
    state: "uploading",
    mode: "upload",
  };

  uploadBusy.value = true;
  const formData = new FormData();
  formData.append("token", tokenData.value.token);
  formData.append("file", file);

  const xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/v1/website/cloud-drive/upload");

  xhr.upload.onprogress = (event) => {
    const entry = transferProgress[progressKey];
    if (!entry) return;
    if (event.lengthComputable) {
      entry.total = event.total;
    }
    entry.loaded = event.loaded;
    const total = entry.total || file.size || 0;
    entry.percent = total ? Math.min(100, (entry.loaded / total) * 100) : 0;
  };

  xhr.onload = async () => {
    uploadBusy.value = false;
    if (xhr.status >= 200 && xhr.status < 300) {
      completeTransfer(progressKey, transferProgress[progressKey]?.total || file.size || 0);
      Toast.success("文件上传成功");
      try {
        await fetchTokenInfo(tokenData.value?.token || tokenInput.value);
      } catch (error) {
        console.error("刷新令牌信息失败:", error);
      }
      if (isAdmin.value) {
        await loadAdminTokens();
      }
    } else {
      markTransferFailed(progressKey);
      const message = xhr.statusText || "上传失败";
      Toast.error(message);
    }
  };

  xhr.onerror = () => {
    uploadBusy.value = false;
    markTransferFailed(progressKey);
    Toast.error("上传过程中发生错误");
  };

  xhr.send(formData);
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
  URL.revokeObjectURL(url);
}

async function handleDownload() {
  if (!tokenData.value || !tokenData.value.token) return;

  const filename = tokenData.value.original_filename || tokenData.value.filename || "下载文件";
  const progressKey = `download-${Date.now()}-${filename}`;
  transferProgress[progressKey] = {
    label: `下载 ${filename}`,
    percent: 0,
    loaded: 0,
    total: tokenData.value.size || 0,
    state: "downloading",
    mode: "download",
  };

  downloadBusy.value = true;
  try {
    const response = await fetch("/api/v1/website/cloud-drive/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token: tokenData.value.token }),
    });

    if (!response.ok) {
      let message = `${response.status} ${response.statusText}`;
      try {
        const payload = await response.json();
        message = payload?.detail || message;
      } catch {
        // ignore parse error
      }
      throw new Error(message);
    }

    const entry = transferProgress[progressKey];
    if (entry) {
      const total = Number(response.headers.get("content-length")) || entry.total;
      if (total) {
        entry.total = total;
      }
    }

    if (response.body && response.body.getReader) {
      const reader = response.body.getReader();
      const chunks = [];
      let loaded = 0;
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        chunks.push(value);
        loaded += value.length;
        const entryLoop = transferProgress[progressKey];
        if (entryLoop) {
          entryLoop.loaded = loaded;
          const total = entryLoop.total || tokenData.value.size || 0;
          entryLoop.percent = total ? Math.min(100, (loaded / total) * 100) : 0;
        }
      }
      const blob = new Blob(chunks, { type: "application/octet-stream" });
      triggerDownload(blob, filename);
      completeTransfer(progressKey, transferProgress[progressKey]?.total || loaded);
    } else {
      const blob = await response.blob();
      triggerDownload(blob, filename);
      const entrySimple = transferProgress[progressKey];
      if (entrySimple) {
        entrySimple.loaded = blob.size;
        entrySimple.total = blob.size;
      }
      completeTransfer(progressKey, blob.size);
    }

    Toast.success("文件下载完成");
    try {
      await fetchTokenInfo(tokenData.value.token);
    } catch (error) {
      console.error("刷新令牌信息失败:", error);
    }
    if (isAdmin.value) {
      await loadAdminTokens();
    }
  } catch (error) {
    markTransferFailed(progressKey);
    Toast.error(error.message || "下载失败");
  } finally {
    downloadBusy.value = false;
  }
}
</script>

<style scoped>
.drive-page {
  padding: 72px 16px 24px;
  min-height: calc(100vh - 64px);
  background: #f3f4f6;
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: center;
}

.panel {
  width: 100%;
  max-width: 1040px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08);
  padding: 24px;
  box-sizing: border-box;
}

.token-panel h1 {
  font-size: 1.8rem;
  margin-bottom: 8px;
  color: #111827;
}

.subtitle {
  margin: 0 0 20px;
  color: #6b7280;
}

.token-input {
  display: flex;
  gap: 12px;
  align-items: center;
}

.token-input input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s ease;
}

.token-input input:focus {
  border-color: #2563eb;
  outline: none;
}

.btn {
  padding: 10px 22px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #6366f1);
  color: #ffffff;
}

.btn-info {
  background: #e0e7ff;
  color: #1d4ed8;
}

.btn-outline {
  background: transparent;
  color: #2563eb;
  border: 1px solid #2563eb;
}

.btn-danger {
  background: #ef4444;
  color: #ffffff;
}

.btn-small {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.token-result {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.token-meta {
  background: #f9fafb;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #e5e7eb;
}

.meta-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-family: "Fira Code", Consolas, monospace;
}

.meta-row code {
  background: rgba(37, 99, 235, 0.08);
  padding: 6px 10px;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #1d4ed8;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.label {
  display: block;
  font-size: 0.85rem;
  color: #6b7280;
}

.value {
  display: block;
  margin-top: 4px;
  font-weight: 600;
  color: #111827;
  word-break: break-all;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.tip {
  margin: 0;
  color: #ef4444;
  font-size: 0.9rem;
}

.admin-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.admin-entry-text h2 {
  margin: 0;
  font-size: 1.3rem;
  color: #111827;
}

.admin-entry-text p {
  margin: 6px 0 0;
  color: #6b7280;
  font-size: 0.95rem;
}

.admin-entry-button {
  min-width: 120px;
}

.admin-overlay-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding: 64px 16px;
  z-index: 1100;
  overflow-y: auto;
}

.admin-overlay-card {
  max-width: 1040px;
  width: 100%;
  max-height: calc(100vh - 128px);
  overflow-y: auto;
}

.admin-overlay-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.admin-overlay-close {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 0.95rem;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 6px;
  transition: background 0.2s ease, color 0.2s ease;
}

.admin-overlay-close:hover {
  background: rgba(37, 99, 235, 0.08);
  color: #2563eb;
}

.admin-panel h2 {
  margin: 0 0 16px;
  color: #111827;
  font-size: 1.4rem;
}

.admin-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
}

.admin-form label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #374151;
  font-size: 0.95rem;
}

.admin-form input[type="text"] {
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
}

.admin-form select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 0.95rem;
  background: #ffffff;
  appearance: none;
  transition: border-color 0.2s ease;
}

.admin-form select:focus {
  border-color: #2563eb;
  outline: none;
}

.cache-select {
  display: flex;
  gap: 8px;
  align-items: center;
}

.cache-select select:disabled {
  background: #f3f4f6;
  color: #9ca3af;
}

.cache-error {
  grid-column: 1 / -1;
  margin: 0;
  font-size: 0.85rem;
  color: #b91c1c;
}

.generated-token {
  margin-bottom: 24px;
  background: #f9fafb;
  border-radius: 10px;
  padding: 16px;
  border: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.token-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-family: "Fira Code", Consolas, monospace;
}

.token-display .token-value {
  font-size: 1.1rem;
  color: #1d4ed8;
}

.token-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 0.9rem;
  color: #4b5563;
}

.token-desc {
  margin: 0;
  font-size: 0.9rem;
  color: #374151;
}

.token-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.token-list-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #111827;
}

.token-table-wrapper {
  overflow-x: auto;
}

.token-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.95rem;
}

.token-table th,
.token-table td {
  padding: 12px 14px;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
  vertical-align: top;
}

.token-table th {
  background: #f3f4f6;
  font-weight: 600;
  color: #111827;
}

.token-table td.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.token-table td.mono {
  font-family: "Fira Code", Consolas, monospace;
  color: #1d4ed8;
}

.empty-state {
  margin-top: 12px;
  padding: 24px;
  text-align: center;
  color: #6b7280;
  border: 1px dashed #cbd5f5;
  border-radius: 12px;
  background: #f9fafc;
}

.empty-icon {
  font-size: 1.5rem;
  margin-bottom: 8px;
}

.error-banner {
  background: rgba(248, 113, 113, 0.12);
  color: #b91c1c;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid rgba(248, 113, 113, 0.4);
  margin-bottom: 16px;
}

.loading-stack {
  display: grid;
  gap: 12px;
}

.loading-card {
  background: #f1f5f9;
  border-radius: 10px;
  padding: 16px;
  display: grid;
  gap: 12px;
}

.skeleton-line {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #e2e8f0 0%, #f8fafc 50%, #e2e8f0 100%);
  background-size: 200% 100%;
  animation: shimmer 1.2s infinite;
}

.w-60 {
  width: 60%;
}

.w-40 {
  width: 40%;
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.progress-toast-container {
  position: fixed;
  top: 88px;
  right: 24px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  z-index: 1000;
}

.progress-toast {
  min-width: 220px;
  max-width: 280px;
  background: rgba(15, 23, 42, 0.85);
  color: #f8fafc;
  box-shadow: 0 14px 40px -20px rgba(15, 23, 42, 0.6);
  border-radius: 12px;
  padding: 14px 16px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  backdrop-filter: blur(14px);
}

.progress-toast-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  word-break: break-all;
}

.progress-toast-bar {
  position: relative;
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.16);
  border-radius: 4px;
  overflow: hidden;
}

.progress-toast-bar-inner {
  height: 100%;
  background: linear-gradient(135deg, #38bdf8 0%, #6366f1 100%);
  transition: width 0.2s ease;
}

.progress-toast-percent {
  margin-top: 8px;
  text-align: right;
  font-size: 12px;
  color: rgba(248, 250, 252, 0.8);
  font-weight: 500;
}

.progress-toast--done {
  border-color: rgba(52, 211, 153, 0.45);
}

.progress-toast--done .progress-toast-bar-inner {
  background: linear-gradient(135deg, #10b981 0%, #22d3ee 100%);
}

.progress-toast--error {
  border-color: rgba(248, 113, 113, 0.6);
}

.progress-toast--error .progress-toast-bar-inner {
  background: linear-gradient(135deg, #f87171 0%, #ef4444 100%);
}

.dialog-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1200;
  padding: 16px;
}

.dialog-card {
  width: 100%;
  max-width: 420px;
  background: #ffffff;
  border-radius: 14px;
  box-shadow: 0 24px 60px -30px rgba(15, 23, 42, 0.6);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dialog-card h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #111827;
}

.dialog-desc {
  margin: 0;
  color: #4b5563;
  line-height: 1.6;
}

.dialog-desc code {
  background: rgba(37, 99, 235, 0.12);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: "Fira Code", Consolas, monospace;
  color: #1d4ed8;
}

.dialog-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

@media (max-width: 640px) {
  .token-input {
    flex-direction: column;
    align-items: stretch;
  }

  .action-buttons {
    flex-direction: column;
  }

  .admin-form {
    grid-template-columns: 1fr;
  }

  .admin-entry {
    flex-direction: column;
    align-items: flex-start;
  }

  .admin-entry-button {
    width: 100%;
  }

  .admin-overlay-card {
    max-height: calc(100vh - 80px);
  }

  .token-table th,
  .token-table td {
    padding: 10px 12px;
  }

  .dialog-card {
    padding: 20px;
  }
}
</style>
