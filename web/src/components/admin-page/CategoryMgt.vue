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
          <div class="card-thumb" title="编辑文章" @click="onEditArticle(article.id)">
            <img :src="article.thumbnail" />
          </div>

          <div class="card-meta">
            <div class="card-info">
              <div class="card-option-name">标题:</div>
              <input class="card-input-editor" type="text" v-model="article.title" @change="onEditTitle(article.id, article.title)" />
            </div>
            <div class="card-info">
              <div class="card-option-name">文件名:</div>
              <input class="card-input-editor" type="text" v-model="article.path" @change="onEditFileName(article.id, article.path)" />
            </div>
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
import {
  getArticlesByCategory,
  editSerialNo,
  deleteArticle,
  syncArticleToFile,
  getArticleText,
  editTitle,
  renameArticleFile,
  editIsExist,
  addCategory,
} from "../../utils/apis";
import Toast from "../../utils/toast.js";

const emit = defineEmits(["on-update-categories"]);

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
  if (Array.isArray(res)) {
    categoryMgt.value.articles = [];
    res.forEach((article) => {
      // 对文章路径进行处理，去掉 .md 后缀, 保留有效的文件的名字
      const path = article.path;
      const match = path.match(/([^/]+)\.md$/);
      if (match) {
        article.path = match[1];
      }
      categoryMgt.value.articles.push(article);
    });
    Toast.success("文章数据加载成功");
  } else {
    errorMessage.value = "获取文章失败，请稍后再试";
    Toast.error("获取文章失败，请稍后再试");
  }
}

/**
 * 新建分类
 */
async function onNewCategory() {
  if (!categoryMgt.value.newCategoryName) {
    errorMessage.value = "请输入分类名称";
    Toast.error("请输入分类名称");
    return;
  }

  if (props.allCategories.includes(categoryMgt.value.newCategoryName)) {
    errorMessage.value = "分类名称已存在，请使用其他名称";
    Toast.error("分类名称已存在，请使用其他名称");
    return;
  }

  // 新分类名字只能是数字和字母和下划线的组合并且下划线不能开头
  const regex = /^[a-zA-Z0-9_]+$/;
  if (!regex.test(categoryMgt.value.newCategoryName) || categoryMgt.value.newCategoryName.startsWith("_")) {
    errorMessage.value = "分类名称只能包含字母、数字和下划线，且不能以下划线开头";
    Toast.error("分类名称只能包含字母、数字和下划线，且不能以下划线开头");
    return;
  }

  const res = await addCategory(categoryMgt.value.newCategoryName);
  if (res) {
    Toast.success("新分类创建成功");
    categoryMgt.value.newCategoryName = "";
    emit("on-update-categories");
  } else {
    errorMessage.value = "新分类创建失败，请稍后再试";
    Toast.error("新分类创建失败，请稍后再试");
  }
}

/**
 * 跳转到编辑文章页面
 * @param articleId {string|number} 文章 ID
 * @returns {void}
 */
function onEditArticle(articleId) {
  window.location.href = `/edit/${articleId}`;
}

/**
 * 修改文章标题
 * @param id
 * @param title
 */
async function onEditTitle(id, title) {
  // 更新文章的标题
  const res = await editTitle(id, title);
  if (!res) {
    errorMessage.value = "标题更新失败，请稍后再试";
    Toast.error("标题更新失败，请稍后再试");
  } else {
    Toast.success("标题更新成功");
  }
}

/**
 * 修改文章文件名
 * @param articleId {string|number} 文章 ID
 * @param filename {string} 新的文件名
 * @returns {Promise<void>}
 */
async function onEditFileName(articleId, filename) {
  // 检查文件名是否已存在
  const isExist = await editIsExist(categoryMgt.value.category, filename);
  if (isExist) {
    errorMessage.value = "文件名已存在，请使用其他名称";
    Toast.error("文件名已存在，请使用其他名称");
    return;
  }

  // 更新文章的文件名
  const res = await renameArticleFile(articleId, filename);
  if (!res) {
    errorMessage.value = "文件名更新失败，请稍后再试";
    Toast.error("文件名更新失败，请稍后再试");
  } else {
    Toast.success("文件名更新成功");
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
  padding: 8px;
  border-bottom: 1px solid #f1f1f1;
  display: flex;
  align-items: center;
  flex-direction: column;
  width: 232px;
  background-color: #86909c42;
  height: 256px;
  border-radius: 16px;
  gap: 4px;
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
  cursor: pointer;
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
  gap: 8px;
  font-size: 12px;
  color: #86909c;
  justify-content: space-between;
}

.card-meta {
  flex-direction: column;
}

.card-action {
  flex-direction: row;
}

.card-info {
  display: flex;
  gap: 8px;
  flex-direction: row;
  max-height: 36px;
  justify-content: center;
  align-items: center;
}

.card-option-name {
  font-weight: bold;
  color: #333;
  max-width: 42px;
  width: 42px;
}

.card-input-editor {
  height: 24px;
  max-width: 154px;
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
