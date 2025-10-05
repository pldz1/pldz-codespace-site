<template>
  <div class="content-container">
    <div class="content-header">
      <h1>Git 插件</h1>
    </div>
    <div class="content-body">
      <!-- 这里可以添加 Git 插件的功能 -->
      <div class="content-item">
        <span>Git Pull</span>
        <button class="btn btn-danger" style="padding: 10px 20px" @click="onGitPull" :disabled="isSyncing">PULL</button>
      </div>
      <div class="content-item">
        <span>同步全部文章</span>
        <button class="btn btn-danger" style="padding: 10px 20px" @click="onSyncAll" :disabled="isSyncing">同步</button>
      </div>
      <div class="content-item">
        <span>Github Push</span>
        <input type="text" placeholder="请输入 Git commit" v-model="gitCommit" />
        <button class="btn btn-danger" style="padding: 10px 20px; margin-left: 16px" @click="onGitSync" :disabled="isSyncing">同步</button>
      </div>
      <div class="content-item">
        <span>日志</span>
      </div>
      <div class="content-item">
        <textarea class="log-textarea" readonly v-model="log"></textarea>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { syncAllArticles, syncGitPull, syncGitRepo } from "../../utils/fetch-sse.js";

import Toast from "../../utils/toast.js";

const isSyncing = ref(false);
const log = ref("");
const gitCommit = ref("");

/**
 * 同步所有文章到源文件
 */
async function onSyncAll() {
  if (!confirm("确定要将所有文章保存到源文件吗？")) return;

  // 防抖——如果正在同步，就直接返回
  if (isSyncing.value) return;

  isSyncing.value = true;
  const controller = new AbortController();
  await syncAllArticles(log, controller);
  isSyncing.value = false;
  Toast.success("同步所有文章成功");
}

/**
 * Git Pull
 */
async function onGitPull() {
  if (!confirm("确定要执行 Git Pull 操作吗？请确保已经备份好本地改动！")) return;
  if (isSyncing.value) return;

  isSyncing.value = true;
  const controller = new AbortController();
  await syncGitPull(log, controller);
  isSyncing.value = false;
  Toast.success("Git Pull 执行完成");
}

/**
 * Git同步改动到远程仓库
 * 需要填写 Git commit 信息
 * @returns {Promise<void>}
 */
async function onGitSync() {
  if (!confirm("确定要将本地改动同步到远程仓库吗？")) return;

  if (isSyncing.value) return;
  // 检查是否填写了 Git commit

  if (!gitCommit.value) {
    log.value += "[ERROR] 请填写 Git commit\n";
    return;
  }

  isSyncing.value = true;
  const controller = new AbortController();
  await syncGitRepo(log, controller, gitCommit.value);
  isSyncing.value = false;
  Toast.success("Git 同步到远程仓库成功");
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.log-textarea {
  flex: 1;
  height: 300px;
}
</style>
