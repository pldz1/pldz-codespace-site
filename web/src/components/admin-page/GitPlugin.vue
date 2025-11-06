<template>
  <div class="content-container">
    <div class="content-header">
      <h1>Git 插件</h1>
      <p>同步文章内容与仓库代码，保持线上线下版本一致</p>
    </div>

    <div class="content-body">
      <div class="content-item action-row">
        <span>Git Pull</span>
        <button
          class="btn btn-info"
          :class="{ 'is-loading': activeAction === 'pull' }"
          @click="onGitPull"
          :disabled="isSyncing"
        >
          执行 Pull
        </button>
      </div>

      <div class="content-item action-row">
        <span>同步全部文章</span>
        <button
          class="btn btn-info"
          :class="{ 'is-loading': activeAction === 'sync-all' }"
          @click="onSyncAll"
          :disabled="isSyncing"
        >
          同步缓存
        </button>
      </div>

      <div class="content-item action-row">
        <span>Git Push</span>
        <input type="text" placeholder="请输入 Git commit" v-model.trim="gitCommit" />
        <button
          class="btn btn-primary"
          :class="{ 'is-loading': activeAction === 'push' }"
          @click="onGitSync"
          :disabled="isSyncing"
        >
          推送到远程
        </button>
      </div>

      <div class="log-card">
        <div class="log-card-header">
          <div>
            <span class="label-sm">运行日志</span>
          </div>
          <div class="inline-actions">
            <button class="btn btn-outline" type="button" @click="clearLog" :disabled="!log">
              清空日志
            </button>
          </div>
        </div>
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
const activeAction = ref("");
const log = ref("");
const gitCommit = ref("");

async function runWithSyncing(actionKey, task) {
  if (isSyncing.value) return false;
  activeAction.value = actionKey;
  isSyncing.value = true;
  try {
    await task();
    return true;
  } finally {
    isSyncing.value = false;
    activeAction.value = "";
  }
}

async function onSyncAll() {
  if (!confirm("确定要将所有文章保存到源文件吗？")) return;
  await runWithSyncing("sync-all", async () => {
    const controller = new AbortController();
    await syncAllArticles(log, controller);
    Toast.success("同步所有文章成功");
  });
}

async function onGitPull() {
  if (!confirm("确定要执行 Git Pull 操作吗？请确保已经备份好本地改动！")) return;
  await runWithSyncing("pull", async () => {
    const controller = new AbortController();
    await syncGitPull(log, controller);
    Toast.success("Git Pull 执行完成");
  });
}

async function onGitSync() {
  if (!confirm("确定要将本地改动同步到远程仓库吗？")) return;
  if (!gitCommit.value) {
    log.value += "[ERROR] 请填写 Git commit\n";
    Toast.error("请填写 Git commit 信息");
    return;
  }
  await runWithSyncing("push", async () => {
    const controller = new AbortController();
    await syncGitRepo(log, controller, gitCommit.value);
    Toast.success("Git 同步到远程仓库成功");
  });
}

function clearLog() {
  log.value = "";
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.action-row {
  justify-content: space-between;
  gap: 16px;
}

.action-row input {
  max-width: 280px;
}

.log-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  background: #fff;
}

.log-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.log-textarea {
  width: 100%;
  min-height: 240px;
  resize: vertical;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  background: #fff;
  color: #0f172a;
  font-family: "Fira Code", SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
  font-size: 13px;
}

@media (max-width: 768px) {
  .action-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
