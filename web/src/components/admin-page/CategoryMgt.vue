<template>
  <div class="content-container">
    <div class="content-header">
      <h1>专栏管理</h1>
    </div>
    <div class="content-body">
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
      <div class="content-item">
        <span>新建专栏</span>
        <input type="text" placeholder="请输入专栏名称" v-model="categoryMgt.newCategoryName" />
        <button class="btn btn-primary" @click="onNewCategory">新增专栏</button>
      </div>
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
</template>

<script setup>
import { ref } from "vue";
import { getArticlesByCategory, editSerialNo, deleteArticle, syncArticleToFile, getArticleText } from "../../utils/apis";
import Toast from "../../utils/toast.js";

const props = defineProps({
  allCategories: {
    type: Array,
    required: true,
    default: () => [],
  },
});

const errorMessage = ref("");
// 用于存储当前选中的分类下的文章
const categoryMgt = ref({ newCategoryName: "", category: "", articles: [] });

/**
 * 选择分类时获取该分类下的所有文章
 */
async function onSelectArticleCategory() {
  if (!categoryMgt.value.category) return;

  // 获取该分类下的所有文章
  const res = await getArticlesByCategory(categoryMgt.value.category);
  if (res) {
    categoryMgt.value.articles = res;
    Toast.success("文章数据加载成功");
  } else {
    errorMessage.value = "获取文章失败，请稍后再试";
    Toast.error("获取文章失败，请稍后再试");
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
    Toast.error("序号更新失败，请稍后再试");
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
    Toast.error("删除文章失败，请稍后再试");
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
    Toast.error("保存文章到源文件失败，请稍后再试");
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
    Toast.error("下载文章失败，请稍后再试");
    return;
  }
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: left;
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
</style>
