<template>
  <!-- 移动端侧边栏 -->
  <div v-show="isMobileMenuOpen" class="mobile-overlay" @click="onCloseMobileMenu()"></div>
  <div v-show="isMobileMenuOpen" class="mobile-sidebar">
    <div class="mobile-sidebar-header">
      <div class="logo">爬楼的猪 CodeSpace</div>
      <button class="close-btn" @click="onCloseMobileMenu()">×</button>
    </div>
    <div class="mobile-sidebar-container" ref="mobileSidebarContainerRef"></div>
  </div>

  <!-- 顶部导航栏 -->
  <HeaderBar @toggle-mobile-menu="onToggleMobileMenu"></HeaderBar>

  <!-- 主体内容 -->
  <div class="main-container">
    <!-- 左侧边栏 -->
    <aside class="sidebar sidebar-sticky" ref="mainSidebarContainerRef">
      <div class="sidebar-card" ref="sidebarContentRef">
        <div class="sidebar-card-title">⚙ 菜单</div>
        <div class="sidebar-item" @click="onActiveCard('新增文章')" :style="{ background: backgroundColorList[0] }">
          <span class="sidebar-icon">➕ </span>
          新增文章
        </div>

        <div class="sidebar-item" @click="onActiveCard('专栏管理')" :style="{ background: backgroundColorList[2] }">
          <span class="sidebar-icon">📙 </span>
          专栏管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('图片管理')" :style="{ background: backgroundColorList[3] }">
          <span class="sidebar-icon">📷</span>
          图片管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('缓存管理')" :style="{ background: backgroundColorList[4] }">
          <span class="sidebar-icon">💾</span>
          缓存管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('CodeSpace管理')" :style="{ background: backgroundColorList[5] }">
          <span class="sidebar-icon">🎈</span>
          CodeSpace管理
        </div>
        <div class="sidebar-item" @click="onActiveCard('Git插件')" :style="{ background: backgroundColorList[6] }">
          <span class="sidebar-icon">🔁</span>
          Git插件
        </div>
      </div>
    </aside>

    <!-- 中间内容区 -->
    <main class="content">
      <!-- 中间内容 -->
      <!-- 新增文章 -->
      <div class="content-container" v-if="activeCard === '新增文章'">
        <div class="content-header">
          <h1>新增文章</h1>
        </div>
        <div class="content-body">
          <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
          <div class="content-item">
            <span>文章标题</span>
            <input type="text" placeholder="请输入标题" v-model="newArticleMgt.title" />
          </div>
          <div class="content-item">
            <span>文章专栏</span>
            <div class="select-wrapper">
              <select v-model="newArticleMgt.category">
                <option disabled selected>请选择专栏</option>
                <option v-for="category in allCategories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>
          </div>
          <div class="content-item">
            <button class="btn btn-primary" @click="onNewArticle">发布文章</button>
          </div>
        </div>
      </div>
      <!-- 专栏管理 -->
      <div class="content-container" v-else-if="activeCard === '专栏管理'">
        <div class="content-header">
          <h1>专栏管理</h1>
        </div>
        <div class="content-body">
          <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
          <div class="content-item">
            <span>选择专栏</span>
            <!-- 下拉菜单选择专栏 -->
            <div class="select-wrapper">
              <select v-model="categoryMgt.category" @change="onSelectArticleCategory">
                <option disabled selected>请选择专栏</option>
                <option v-for="category in allCategories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>
          </div>

          <!-- 专栏内的文章列表 -->
          <div class="card-list">
            <div v-for="article in categoryMgt.articles" :key="article.id" class="card-item">
              <div class="card-thumb">
                <img :src="article.thumbnail" />
              </div>
              <a :href="`/edit/${article.id}`" class="card-title">
                {{ article.title }}
              </a>

              <div class="card-meta">
                <div class="card-info">
                  <div class="meta-item">浏览次数: {{ article.views }}</div>
                  <div class="meta-item">序号: <input type="text" v-model="article.serialNo" @change="onEditSerialNo(article)" /></div>
                </div>
              </div>

              <div class="card-action">
                <button class="btn-danger" @click="onDeleteArticle(article.id)">删除</button>
                <button class="btn-info" @click="onSyncArticleDiff(article.id)">同步</button>
                <button class="btn-info" @click="onDownLoadMDFile(article.id, article.title)">下载</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 图片管理 -->
      <div class="content-container" v-else-if="activeCard === '图片管理'">
        <div class="content-header">
          <h1>图片管理</h1>
        </div>
        <div class="content-body">
          <!-- 📷 图像管理: 错误显示 -->
          <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
          <div class="content-item">
            <span>选择专栏</span>
            <!-- 📷 图像管理: 选择专栏 -->
            <div class="select-wrapper">
              <select v-model="imageMgt.category" @change="onSelectImageCategory">
                <option disabled selected>请选择专栏</option>
                <option v-for="category in allCategories" :key="category" :value="category">
                  {{ category }}
                </option>
              </select>
            </div>
          </div>

          <!-- 📷 图像管理: 上传图像 -->
          <div class="content-item">
            <span>上传图片</span>
            <button class="btn btn-danger" style="padding: 10px 20px" @click="onShowUploadImageDialog">选择照片</button>
            <!-- 上传图像的位置 -->
            <UploadImage
              v-if="imageMgt.upload"
              :category="imageMgt.category"
              :show-confirm-button="false"
              @upload-image-success="onUploadImageSuccess"
              @close-upload-image-dialog="onCloseUploadImageDialog"
            ></UploadImage>
          </div>

          <!-- 📷 图像管理: 图片列表 -->
          <div class="card-list">
            <div v-for="(url, index) in imageMgt.urls" :key="index" class="card-item">
              <div class="card-thumb">
                <img :src="url" />
              </div>

              <div class="card-meta">
                <div class="card-info">
                  <div class="meta-item"><input type="text" style="width: 100%" v-model="imageMgt.newImages[index]" @change="onEditImageName(index)" /></div>
                </div>
              </div>

              <div class="card-action">
                <button class="btn-danger" @click="onDeleteImage(index)">删除</button>
                <a :href="url" download class="btn-info">下载</a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 缓存管理 -->
      <div class="content-container" v-else-if="activeCard === '缓存管理'">
        <div class="content-header">
          <h1>缓存管理</h1>
        </div>
        <div class="content-body">
          <p>这里可以清理缓存。</p>
          <!-- 这里可以添加缓存管理的功能 -->
        </div>
      </div>

      <!-- CodeSpace 管理 -->
      <div class="content-container" v-else-if="activeCard === 'CodeSpace管理'">
        <div class="content-header">
          <h1>CodeSpace 管理</h1>
        </div>
        <div class="content-body">
          <p>这里可以管理 CodeSpace。</p>
          <!-- 这里可以添加 CodeSpace 管理的功能 -->
        </div>
      </div>

      <!-- 🔁 Git 插件 -->
      <div class="content-container" v-else-if="activeCard === 'Git插件'">
        <div class="content-header">
          <h1>Git 插件</h1>
        </div>
        <div class="content-body">
          <!-- 这里可以添加 Git 插件的功能 -->
          <div class="content-item">
            <span>同步全部文章</span>
            <button class="btn btn-danger" style="padding: 10px 20px" @click="onSyncAll" :disabled="isSyncing">同步</button>
          </div>
          <div class="content-item">
            <span>Git Pull</span>
            <button class="btn btn-danger" style="padding: 10px 20px" @click="onGitPull" :disabled="isSyncing">同步</button>
          </div>
          <div class="content-item">
            <span>Github 同步</span>
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
    </main>
  </div>

  <!-- 底部隐私数据 -->
  <FooterBar></FooterBar>
</template>

<script setup>
import HeaderBar from "../components/HeaderBar.vue";
import FooterBar from "../components/FooterBar.vue";
import UploadImage from "../components/UploadImage.vue";

import { useRouter } from "vue-router";
import { useStore } from "vuex";
import { ref, onMounted, onUnmounted, watch } from "vue";
import {
  getAllCategories,
  getArticlesByCategory,
  editIsExist,
  addArticle,
  editSerialNo,
  deleteArticle,
  syncArticleToFile,
  getArticleText,
  allImageInCategory,
  deleteImage,
  renameImage,
} from "../utils/apis.js";
import { syncAllArticles, syncGitPull, syncGitRepo } from "../utils/fetch-sse.js";

const store = useStore();
const router = useRouter();

const backgroundColorList = [
  "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  "linear-gradient(135deg, #4facfe, #00f2fe)",
  "linear-gradient(135deg, #ff7e5f, #feb47b)",
  "linear-gradient(135deg, #43cea2, #185a9d)",
  "linear-gradient(135deg, #f7971e, #ffd200)",
  "linear-gradient(135deg, #00c6ff, #0072ff)",
  "linear-gradient(135deg, #ff6a00, #ee0979)",
  "linear-gradient(135deg, #00c6ff, #0072ff)",
];

// 用于存储所有分类
const allCategories = ref([]);

// 用于存储错误信息
const errorMessage = ref("");

// 引用移动端和主侧边栏容器
const isMobileMenuOpen = ref(false);
const mobileSidebarContainerRef = ref(null);
const mainSidebarContainerRef = ref(null);
const sidebarContentRef = ref(null);

// 用于存储当前选中的分类
const activeCard = ref("新增文章");

/**
 * 设置当前活动分类并获取相应的文章
 * @param category {string} 选中的分类
 */
function onActiveCard(category) {
  // 如果点击的是当前分类，则不做任何操作``
  if (activeCard.value === category) return;

  // 设置当前活动分类
  activeCard.value = category;
}

/**
 * 打开移动端菜单
 */
function onToggleMobileMenu() {
  isMobileMenuOpen.value = true;
  if (mobileSidebarContainerRef.value && sidebarContentRef.value) {
    mobileSidebarContainerRef.value.appendChild(sidebarContentRef.value);
  }
}

/**
 * 关闭移动端菜单
 */
function onCloseMobileMenu() {
  isMobileMenuOpen.value = false;

  if (mainSidebarContainerRef.value && sidebarContentRef.value) {
    mainSidebarContainerRef.value.appendChild(sidebarContentRef.value);
  }
}

/**
 * ========================= 新增文章 =========================
 */

// 用于存储新文章的标题和分类
const newArticleMgt = ref({ title: "", category: "" });

/**
 * 新增文章
 * @param category {string} 文章分类
 * @param title {string} 文章标题
 */
async function onNewArticle() {
  // 检查标题和分类是否填写
  if (!newArticleMgt.value.title || !newArticleMgt.value.category) {
    errorMessage.value = "请填写文章标题和选择专栏";
    return;
  }

  const isexist = await editIsExist(newArticleMgt.value.category, newArticleMgt.value.title);
  if (isexist) {
    errorMessage.value = "文章标题已存在，请更换标题";
    return;
  }

  // 清除错误信息
  errorMessage.value = "";

  const res = await addArticle(newArticleMgt.value.category, newArticleMgt.value.title);
  if (res?.id) {
    newArticleMgt.value.title = "";
    newArticleMgt.value.category = "";
    router.push({ path: `/edit/${res.id}` });
  } else {
    errorMessage.value = "发布文章失败，请稍后再试";
  }
}

/**
 * ========================= 文章管理 =========================
 */

// 用于存储当前选中的分类下的文章
const categoryMgt = ref({ category: "", articles: [] });

/**
 * 选择分类时获取该分类下的所有文章
 */
async function onSelectArticleCategory() {
  if (!categoryMgt.value.category) return;

  // 获取该分类下的所有文章
  const res = await getArticlesByCategory(categoryMgt.value.category);
  if (res) {
    categoryMgt.value.articles = res;
  } else {
    errorMessage.value = "获取文章失败，请稍后再试";
  }
}

/**
 * 更新文章的序列号
 * @param article {Object} 文章对象，包含 id 和 serialNo
 * @returns {Promise<void>}
 * @throws {Error} 如果序号更新失败
 */
async function onEditSerialNo(article) {
  // 更新文章的序号
  const res = await editSerialNo(article.id, article.serialNo);
  if (!res) {
    errorMessage.value = "序号更新失败，请稍后再试";
  }
}

/**
 * 删除文章
 * @param articleId {string|number} 文章 ID
 * @returns {Promise<void>}
 */
async function onDeleteArticle(articleId) {
  // 删除文章
  const res = await deleteArticle(articleId);
  if (res) {
    // 成功删除后，重新获取当前分类下的文章
    await onSelectArticleCategory();
  } else {
    errorMessage.value = "删除文章失败，请稍后再试";
  }
}

/**
 * 将文章保存到缓存
 * @returns {Promise<void>}
 * @param articleId
 */
async function onSyncArticleDiff(articleId) {
  // 保存文章到缓存
  const res = await syncArticleToFile(articleId);
  if (!res) {
    errorMessage.value = "保存文章到源文件失败，请稍后再试";
  }
}

/**
 * 下载文章的 Markdown 文件
 * @param articleId {string|number} 文章 ID
 * @returns {Promise<void>}
 */
async function onDownLoadMDFile(id, title) {
  const res = await getArticleText(id);
  if (res) {
    // 创建一个 Blob 对象并下载
    const blob = new Blob([res], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } else {
    errorMessage.value = "下载文章失败，请稍后再试";
    return;
  }
}

/**
 *  ========================= 图像管理 =========================
 */

// 用于存储图片管理的分类和图片列表
const imageMgt = ref({ category: "", upload: false, urls: [], newImages: [], oldImages: [], suffix: [] });

/**
 * 选择图片分类时获取该分类下的所有图片
 */
async function onSelectImageCategory() {
  if (!imageMgt.value.category) return;

  // 获取该分类下的所有图片
  const res = await allImageInCategory(imageMgt.value.category);
  if (!Array.isArray(res)) {
    errorMessage.value = "获取图片失败，请稍后再试";
  } else {
    // 去掉后缀
    imageMgt.value.newImages = res.map((img) => img.replace(/\.(jpg|jpeg|png|gif|webp)$/, ""));
    imageMgt.value.oldImages = res.map((img) => img.replace(/\.(jpg|jpeg|png|gif|webp)$/, ""));
    imageMgt.value.suffix = res.map((img) => img.match(/\.(jpg|jpeg|png|gif|webp)$/)?.[0] || "");
    imageMgt.value.urls = res.map((img) => `/api/v1/website/image/${imageMgt.value.category}/${img}`);
  }
}

/**
 * 上传图片成功后的回调
 * @param imageUrl {string} 上传成功的图片 URL
 */
async function onShowUploadImageDialog() {
  if (!imageMgt.value.category) {
    errorMessage.value = "请先选择一个专栏";
    return;
  }

  errorMessage.value = "";
  imageMgt.value.upload = true;
  const app = document.getElementById("app");
  app.style.opacity = 0.41;
}

/**
 * 上传图片成功后的回调
 * @param imageUrl {string} 上传成功的图片 URL
 */
async function onCloseUploadImageDialog() {
  imageMgt.value.upload = false;
  const app = document.getElementById("app");
  app.style.cssText = "";
}

/**
 * 编辑图片名称
 * @param index {number} 图片索引
 */
async function onEditImageName(index) {
  const newname = imageMgt.value.newImages[index];
  const oldname = imageMgt.value.oldImages[index];
  const suffix = imageMgt.value.suffix[index];
  if (!newname) {
    errorMessage.value = "图片名称不能为空";
    return;
  }

  // 检查图片名称是否合法
  const regex = /^(?!-)[A-Za-z0-9_-]+$/;
  if (!regex.test(newname)) {
    errorMessage.value = "图片名称只能包含字母、数字和下划线和减号，且不能以减号开头";
    return;
  }

  // 检查图片是否已经存在
  const res = await renameImage(imageMgt.value.category, oldname + suffix, newname + suffix);
  if (!res.flag) {
    errorMessage.value = "修改图片名称失败，请稍后再试";
    return;
  }

  // 成功修改后，重新获取当前分类下的所有图片
  await onSelectImageCategory();
}

/**
 * 删除图片
 * @param index
 */
async function onDeleteImage(index) {
  // 删除图片
  const imageName = imageMgt.value.newImages[index];
  const suffix = imageMgt.value.suffix[index];
  const res = await deleteImage(imageMgt.value.category, imageName + suffix);
  if (!res) {
    errorMessage.value = "删除图片失败，请稍后再试";
    return;
  }

  // 成功删除后，重新获取当前分类下的所有图片
  await onSelectImageCategory();
}

/**
 * 上传图片成功后的回调
 * 重新获取当前分类下的所有图片，并关闭上传图片对话框
 */
async function onUploadImageSuccess() {
  // 重新获取当前分类下的所有图片
  await onSelectImageCategory();
  // 关闭上传图片对话框
  onCloseUploadImageDialog();
}

/**
 *  ========================= Git 操作 =========================
 */

const isSyncing = ref(false);
const log = ref("");
const gitCommit = ref("");

/**
 * 同步所有文章到源文件
 */
async function onSyncAll() {
  // 防抖——如果正在同步，就直接返回
  if (isSyncing.value) return;

  isSyncing.value = true;
  const controller = new AbortController();
  await syncAllArticles(log, controller);
  isSyncing.value = false;
}

/**
 * Git Pull
 */
async function onGitPull() {
  if (isSyncing.value) return;

  isSyncing.value = true;
  const controller = new AbortController();
  await syncGitPull(log, controller);
  isSyncing.value = false;
}

/**
 * Git同步改动到远程仓库
 * 需要填写 Git commit 信息
 * @returns {Promise<void>}
 */
async function onGitSync() {
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
}

/**
 * ========================= 组件生命周期 =========================
 */

/**
 * 在组件挂载时获取所有文章和分类数据和标签统计数据
 */
onMounted(async () => {
  // 检查是否为管理员
  const isadmin = store.state.authState.isadmin;
  if (!isadmin) {
    router.push({ path: "/" });
    return;
  }
  // 获得全部的博客文章
  const res = await getAllCategories();
  if (!res) return;

  allCategories.value = res;
});

/**
 * 监听窗口大小变化，自动关闭移动端菜单
 */
watch(
  () => window.innerWidth,
  (newWidth) => {
    if (newWidth > 768) {
      onCloseMobileMenu();
    }
  }
);

/**
 * 在组件卸载时清理资源
 */
onUnmounted(() => {});
</script>

<style scoped>
@import url("../assets/views/main-container.css");
@import url("../assets/views/mobile-overlay.css");

.sidebar-sticky {
  position: sticky;
  top: 80px;
  height: fit-content;
}

.sidebar-card {
  padding: 0 8px;
}

.sidebar-card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding: 8px;
  border-bottom: 1px solid #e4e6ea;
}

.sidebar-item {
  display: flex;
  align-items: center;
  padding: 24px 32px;
  color: #71777c;
  cursor: pointer;
  gap: 10px;
  border-radius: 16px;
  margin: 8px 0px;
  color: #171717;
  font-size: 18px;
  font-weight: 500;
}

.sidebar-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.content {
  max-width: unset;
}

.content-container {
  padding: 16px;
}

.content-header {
  margin-bottom: 24px;
  border-bottom: 1px solid #e4e6ea;
}

.content-body {
  margin: 0px 16px;
  padding: 0 20px;
}

.error-message {
  color: red;
  font-size: 14px;
  margin-bottom: 16px;
  text-align: center;
}
.content-item {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  flex-direction: row;
}
.content-item span {
  width: 100px;
  font-size: 16px;
  color: #333;
  margin-right: 10px;
}
.content-item input,
.content-item select {
  flex: 1;
  padding: 8px 12px;
  font-size: 16px;
  border: 1px solid #ccc;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s;
}
.content-item input:focus,
.content-item select:focus {
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.3);
}

.select-wrapper {
  position: relative;
}

.select-wrapper select {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  background-color: #fff;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20width='12'%20height='8'%20viewBox='0%200%2012%208'%20xmlns='http://www.w3.org/2000/svg'%3E%3Cpath%20d='M6%208L0%200h12L6%208z'%20fill='%23999'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  cursor: pointer;
  min-width: 208px;
}
.select-wrapper:hover select {
  border-color: #888;
}
/* 发布按钮样式 */
.btn {
  padding: 10px 20px;
  font-size: 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn:disabled {
  background-color: #ccc !important;
  cursor: not-allowed !important;
  color: #666 !important;
  pointer-events: none !important;
}

.btn-primary {
  background-color: #4a90e2;
  color: #fff;
}
.btn-primary:hover {
  background-color: #357ab8;
}

.card-item {
  padding: 16px;
  border-bottom: 1px solid #f1f1f1;
  display: flex;
  align-items: center;
  flex-direction: column;
  width: 232px;
  background-color: #86909c42;
  height: 256px;
  border-radius: 16px;
  gap: 8px;
  justify-content: space-between;
}

.card-item a {
  color: #171717;
  text-decoration: none;
}

.card-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

.card-title:hover {
  color: #1e80ff;
}

.card-action,
.card-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  font-size: 13px;
  color: #86909c;
  justify-content: space-between;
}

.card-info {
  display: flex;
  gap: 16px;
  flex-direction: row;
  max-height: 36px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-item input {
  width: 60px;
  padding: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 14px;
}

.card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: left;
}

.card-thumb {
  width: 120px;
  height: 80px;
  background: #f1f1f1;
  border-radius: 4px;
  background-size: cover;
  background-position: center;
  flex-shrink: 0;
}

.card-thumb img {
  height: inherit;
  width: inherit;
  object-fit: contain;
}

.btn-danger {
  background-color: #ff4d4f;
  color: #fff;
  padding: 4px 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-info {
  background-color: #1890ff;
  color: #fff !important;
  padding: 4px 8px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.log-textarea {
  flex: 1;
  height: 300px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
}

@media (max-width: 992px) {
}

@media (max-width: 768px) {
  .card-item {
    flex-direction: column;
    gap: 15px;
  }

  .card-thumb {
    margin-left: 0;
    order: -1;
  }

  .card-meta {
    flex-wrap: wrap;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .content-container {
    padding: 15px;
  }

  .card-list {
    justify-content: center;
  }

  .card-item {
    padding: 15px;
  }

  .card-title {
    font-size: 16px;
  }
}

/* 横屏小屏幕优化 */
@media (max-width: 768px) and (orientation: landscape) {
}
</style>
