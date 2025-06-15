import { createRouter, createWebHistory } from "vue-router";
import HomePage from "../views/HomePage.vue";
import ArticlePage from "../views/ArticlePage.vue";
import EditorPage from "../views/EditorPage.vue";
import NotFound from "../views/NotFound.vue";
import AdminPage from "../views/AdminPage.vue";

const router = createRouter({
  // 使用 HTML5 的 History 模式
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: HomePage,
    },
    {
      path: "/admin",
      component: AdminPage,
    },
    {
      // 动态路由，用 :id 捕获文章 ID
      path: "/article/:id",
      component: ArticlePage,
      // 将路由参数作为 props 传入组件
      props: true,
    },
    {
      path: "/edit/:id",
      component: EditorPage,
      props: true,
    },
    {
      path: "/404",
      component: NotFound,
    },
    {
      // 通配所有未匹配的路径
      path: "/:pathMatch(.*)*",
      redirect: "/",
    },
  ],
});

export default router;
