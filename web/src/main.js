import "./assets/index.css";
import App from "./App.vue";
import router from "./routers";
import store from "./store";

import { createApp } from "vue";
import { refresh } from "./utils/apis.js";

import { config } from "md-editor-v3";
import { lineNumbers } from "@codemirror/view";

// 引入编辑器的全部样式
import "md-editor-v3/lib/style.css";

// 异步初始化动作
const initializeApp = async () => {
  // 配置编辑界面显示行号和字数
  config({
    codeMirrorExtensions(_theme, extensions) {
      return [...extensions, lineNumbers()];
    },
  });

  // 刷新cookie
  const res = await refresh();
  await store.dispatch("authState/update", {
    username: res?.username || "",
    avatar: res?.avatar || "",
    nickname: res?.nickname || "",
    isadmin: res?.isadmin || false,
  });
};

// 用于所有资源都加载完毕后，把进度推到 100%、移除 loading（改为隐藏）
function handleWindowLoad() {
  // 1. 把进度推到 100%
  if (window.updateProgress) {
    // 先清除那个假进度的定时器
    if (window._fakeProgressTimer) {
      clearInterval(window._fakeProgressTimer);
      window._fakeProgressTimer = null;
    }
    window.fakeProgress = 100;
    window.updateProgress(window.fakeProgress);
  }

  // 2. 给点过渡，再隐藏蒙层、显示app
  setTimeout(() => {
    const initialLoadingEl = document.getElementById("global-initial-loading");
    if (initialLoadingEl) {
      // 不要 removeChild，只是隐藏
      initialLoadingEl.style.display = "none";
    }

    const appEl = document.getElementById("app");
    if (appEl) {
      appEl.style.display = "block";
    }

    // 3. 最后挂载 Vue
    mountVueApp();
  }, 300);
}

function mountVueApp() {
  // 做我们的异步初始化
  initializeApp().then(() => {
    // 创建并挂载 Vue
    const app = createApp(App);
    app.use(store);
    app.use(router);
    app.mount("#app");
  });
}

// 如果此时文档已经加载完毕，就直接执行，否则监听一次 load
if (document.readyState === "complete") {
  handleWindowLoad();
} else {
  window.addEventListener("load", handleWindowLoad, { once: true });
}
