import "./assets/index.css";
import App from "./App.vue";
import router from "./routers";
import store from "./store";

import { createApp } from "vue";
import { refresh } from "./utils/apis";

// 异步初始化
const initializeApp = async () => {
  try {
    window.loading?.set(96);

    const res = await refresh();

    window.loading?.set(98);

    await store.dispatch("authState/update", {
      username: res?.username || "",
      avatar: res?.avatar || "",
      nickname: res?.nickname || "",
      isadmin: res?.isadmin || false,
    });
  } catch (error) {
    console.error("initializeApp error:", error);
  }
};

const bootstrap = async () => {
  try {
    await initializeApp();

    const app = createApp(App);
    app.use(store);
    app.use(router);
    app.mount("#app");
  } finally {
    window.loading?.done();
  }
};

// 等页面资源加载完后再启动
if (document.readyState === "complete") {
  bootstrap();
} else {
  window.addEventListener("load", bootstrap, { once: true });
}
