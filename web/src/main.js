import "./assets/index.css";
import App from "./App.vue";
import router from "./routers";
import store from "./store";

import { createApp } from "vue";
import { refresh } from "./utils/apis";

const refreshAuthState = async () => {
  try {
    const res = await refresh();

    await store.dispatch("authState/update", {
      username: res?.username || "",
      avatar: res?.avatar || "",
      nickname: res?.nickname || "",
      isadmin: res?.isadmin || false,
    });
  } catch (error) {
    console.error("refreshAuthState error:", error);
  } finally {
    await store.dispatch("authState/ready", true);
  }
};

const bootstrap = () => {
  try {
    window.loading?.set(98);

    const app = createApp(App);
    app.use(store);
    app.use(router);
    app.mount("#app");

    refreshAuthState();
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
