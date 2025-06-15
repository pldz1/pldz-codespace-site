import { fetchEventSource } from "@microsoft/fetch-event-source";

/**
 * 通用的 SSE 请求函数
 * @param {string} url - 请求的 URL
 * @param {Ref} refLog - 用于存储日志的响应式引用
 * @param {AbortController} controller - 用于控制请求的中止
 * @param {Object} payload - 请求的负载数据，默认为空对象
 * @returns {Promise<void>} - 返回一个 Promise，表示请求的完成
 */
async function fetchSSE(url, refLog, controller, payload = {}) {
  try {
    await fetchEventSource(url, {
      method: "POST",
      signal: controller.signal,
      retry: 0, // 关闭自动重连
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
      openWhenHidden: true, // 即使页面不可见也保持连接
      onopen() {
        refLog.value += "[INFO] 连接已打开\n";
      },
      onmessage(evt) {
        const data = JSON.parse(evt.data);
        const message = data.message || "";
        const status = data.status || "error";

        refLog.value += `[INFO] ${message}\n`;
        // 如果后端告诉我们 “done”，就主动中断
        if (status === "done" || status === "error") {
          refLog.value += "[INFO] 同步完成\n";
          controller.abort();
        }
      },
      onerror(err) {
        refLog.value += `[ERROR] ${err.message || err}\n`;
        // 这里也可以选择中断或重连，视需求而定
        controller.abort();
      },
    });
  } catch (e) {
    // 这里捕获到的是 AbortController 抛出的异常
    refLog.value += `[ERROR] 流已关闭 ${String(e)} \n`;
  }
}

/**
 * 同步所有文章的函数
 * @param {Ref} refLog - 用于存储日志的响应式引用
 * @param {AbortController} controller - 用于控制请求的中止
 * @returns {Promise<void>} - 返回一个 Promise，表示同步操作的完成
 */
export async function syncAllArticles(refLog, controller) {
  await fetchSSE("/api/v1/website/article/file/syncall", refLog, controller);
}

/**
 * Git 拉取到本地
 * @param {Ref} refLog - 用于存储日志的响应式引用
 */
export async function syncGitPull(refLog, controller) {
  await fetchSSE("/api/v1/website/article/plugin/gitpull", refLog, controller);
}

/**
 * Git 同步函数
 * @param {Ref} refLog - 用于存储日志的响应式引用
 */
export async function syncGitRepo(refLog, controller, commit = "✨ Sync articles") {
  await fetchSSE("/api/v1/website/article/plugin/gitsync", refLog, controller, { commit });
}
