<template>
  <div class="content-container">
    <div class="content-header">
      <h1>专栏管理</h1>
      <p>维护专栏结构、调整文章顺序并同步文件信息</p>
    </div>

    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <div class="content-item">
        <span>新建专栏</span>
        <input
          type="text"
          placeholder="请输入专栏名称（字母、数字、下划线，且不能以下划线开头）"
          v-model.trim="categoryMgt.newCategoryName"
          :disabled="isCreatingCategory"
        />
        <button class="btn btn-primary" :class="{ 'is-loading': isCreatingCategory }" @click="onNewCategory" :disabled="isCreatingCategory">新增专栏</button>
      </div>

      <div class="content-item">
        <span>选择专栏</span>
        <div class="select-wrapper">
          <select v-model="categoryMgt.category" @change="onSelectArticleCategory" :disabled="isLoading || isArticleLoading">
            <option value="" disabled>请选择专栏</option>
            <option v-for="category in categories" :key="category" :value="category">
              {{ category }}
            </option>
          </select>
        </div>
        <button class="btn btn-outline" type="button" @click="onRefreshArticles" :disabled="!categoryMgt.category || isArticleLoading">刷新列表</button>
      </div>

      <div v-if="isArticleLoading" class="loading-stack">
        <div v-for="n in 4" :key="`article-list-skeleton-${n}`" class="loading-card">
          <div class="skeleton-line w-60"></div>
          <div class="skeleton-line w-40" style="margin-top: 12px"></div>
          <div class="skeleton-line w-80" style="margin-top: 12px"></div>
        </div>
      </div>

      <div v-else-if="categoryMgt.category && categoryMgt.articles.length" class="list-block">
        <div class="list-row article-row" v-for="article in categoryMgt.articles" :key="article.id">
          <div class="field field-grow article-title">
            <span class="field-label">标题</span>
            <strong @click="onEditArticle(article.id)" class="article-link">
              {{ article.title || article.id }}
            </strong>
          </div>
          <div class="field field-grow">
            <span class="field-label">文件名</span>
            <input class="field-input" type="text" v-model="article.path" @change="onEditFileName(article.id, article.path)" />
          </div>
          <div class="field field-compact">
            <span class="field-label">浏览</span>
            <span class="field-value">{{ article.views }}</span>
          </div>
          <div class="field field-compact">
            <span class="field-label">序号</span>
            <input type="number" class="field-input field-input--xs" v-model.number="article.serialNo" @change="onEditSerialNo(article)" />
          </div>
          <div class="inline-actions">
            <button class="btn btn-info" @click="onSyncArticleDiff(article.id)" :disabled="isArticleLoading">同步</button>
            <button class="btn btn-outline" @click="onDownLoadMDFile(article.id, article.title)" :disabled="isArticleLoading">下载</button>
            <button class="btn btn-danger" @click="onDeleteArticle(article.id)" :disabled="isArticleLoading">删除</button>
          </div>
        </div>
      </div>

      <div v-else-if="categoryMgt.category" class="empty-state">
        <div class="empty-icon">📭</div>
        <p>该专栏暂无文章，试试创建或同步内容。</p>
        <button class="btn btn-outline" @click="onRefreshArticles" :disabled="isArticleLoading">重新载入</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
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
import { useLoading } from "../../utils/use-loading";

const emit = defineEmits(["on-update-categories"]);

const props = defineProps({
  allCategories: {
    type: Array,
    required: true,
    default: () => [],
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const errorMessage = ref("");
const categoryMgt = ref({ newCategoryName: "", category: "", articles: [] });

const { isLoading: isArticleLoading, start: startArticleLoading, stop: stopArticleLoading } = useLoading("admin.category.articleList");
const { isLoading: isCreatingCategory, start: startCreatingCategory, stop: stopCreatingCategory } = useLoading("admin.category.create");

const hasCategorySelected = computed(() => Boolean(categoryMgt.value.category));
const categories = computed(() => props.allCategories || []);

function sortBySerialNo() {
  categoryMgt.value.articles = [...categoryMgt.value.articles].sort((a, b) => (a.serialNo ?? 0) - (b.serialNo ?? 0));
}

function normalizeArticle(article) {
  const match = article.path?.match(/([^/]+)\.md$/);
  return {
    ...article,
    path: match ? match[1] : article.path,
  };
}

async function fetchArticlesByCategory(category, { showFeedback = true } = {}) {
  startArticleLoading();
  try {
    const res = await getArticlesByCategory(category);
    if (Array.isArray(res)) {
      categoryMgt.value.articles = res.map(normalizeArticle);
      sortBySerialNo();
      errorMessage.value = "";
      if (showFeedback) {
        Toast.success("文章数据加载成功");
      }
      return true;
    }
    throw new Error("获取文章失败");
  } catch (error) {
    console.error("获取文章失败:", error);
    categoryMgt.value.articles = [];
    errorMessage.value = "获取文章失败，请稍后再试";
    Toast.error("获取文章失败，请稍后再试");
    return false;
  } finally {
    stopArticleLoading();
  }
}

async function onSelectArticleCategory() {
  if (!categoryMgt.value.category) return;
  await fetchArticlesByCategory(categoryMgt.value.category);
}

async function onRefreshArticles() {
  if (!categoryMgt.value.category) return;
  await fetchArticlesByCategory(categoryMgt.value.category, { showFeedback: true });
}

async function onNewCategory() {
  if (!categoryMgt.value.newCategoryName) {
    errorMessage.value = "请输入分类名称";
    Toast.error("请输入分类名称");
    return;
  }

  if (categories.value.includes(categoryMgt.value.newCategoryName)) {
    errorMessage.value = "分类名称已存在，请使用其他名称";
    Toast.error("分类名称已存在，请使用其他名称");
    return;
  }

  const regex = /^[a-zA-Z0-9_]+$/;
  if (!regex.test(categoryMgt.value.newCategoryName) || categoryMgt.value.newCategoryName.startsWith("_")) {
    errorMessage.value = "分类名称只能包含字母、数字和下划线，且不能以下划线开头";
    Toast.error("分类名称只能包含字母、数字和下划线，且不能以下划线开头");
    return;
  }

  startCreatingCategory();
  try {
    const res = await addCategory(categoryMgt.value.newCategoryName);
    if (res) {
      Toast.success("新分类创建成功");
      categoryMgt.value.newCategoryName = "";
      emit("on-update-categories");
    } else {
      throw new Error("新分类创建失败");
    }
  } catch (error) {
    console.error("新分类创建失败:", error);
    errorMessage.value = "新分类创建失败，请稍后再试";
    Toast.error("新分类创建失败，请稍后再试");
  } finally {
    stopCreatingCategory();
  }
}

function onEditArticle(articleId) {
  window.location.href = `/edit/${articleId}`;
}

async function onEditTitle(id, title) {
  if (!confirm(`确定要修改文章: ${id} 的标题为 ${title} 吗？`)) return;
  const res = await editTitle(id, title);
  if (!res) {
    errorMessage.value = "标题更新失败，请稍后再试";
    Toast.error("标题更新失败，请稍后再试");
  } else {
    Toast.success("标题更新成功");
  }
}

async function onEditFileName(articleId, filename) {
  if (!confirm(`确定要修改文章: ${articleId} 的文件名为 ${filename} 吗？`)) return;
  const isExist = await editIsExist(categoryMgt.value.category, filename);
  if (isExist) {
    errorMessage.value = "文件名已存在，请使用其他名称";
    Toast.error("文件名已存在，请使用其他名称");
    return;
  }

  const res = await renameArticleFile(articleId, filename);
  if (!res) {
    errorMessage.value = "文件名更新失败，请稍后再试";
    Toast.error("文件名更新失败，请稍后再试");
  } else {
    const index = categoryMgt.value.articles.findIndex((article) => article.id === articleId);
    if (index !== -1) {
      categoryMgt.value.articles[index].id = res;
    }
    Toast.success("文件名更新成功");
  }
}

async function onEditSerialNo(article) {
  if (!confirm(`确定要修改文章: ${article.id} 的序号为 ${article.serialNo} 吗？`)) return;
  const res = await editSerialNo(article.id, article.serialNo);
  if (!res) {
    errorMessage.value = "序号更新失败，请稍后再试";
    Toast.error("序号更新失败，请稍后再试");
  } else {
    sortBySerialNo();
    Toast.success("序号更新成功");
    errorMessage.value = "";
  }
}

async function onDeleteArticle(articleId) {
  if (!confirm(`确定要删除文章: ${articleId}吗？`)) return;
  const res = await deleteArticle(articleId);
  if (res) {
    await onRefreshArticles();
    Toast.success("文章删除成功");
  } else {
    errorMessage.value = "删除文章失败，请稍后再试";
    Toast.error("删除文章失败，请稍后再试");
  }
}

async function onSyncArticleDiff(articleId) {
  if (!confirm(`确定要将文章: ${articleId} 保存到源文件吗？`)) return;
  const res = await syncArticleToFile(articleId);
  if (!res) {
    errorMessage.value = "保存文章到源文件失败，请稍后再试";
    Toast.error("保存文章到源文件失败，请稍后再试");
  } else {
    Toast.success("文章保存成功");
  }
}

async function onDownLoadMDFile(id, title) {
  const res = await getArticleText(id);
  if (res) {
    const blob = new Blob([res], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    Toast.success("下载文章成功");
  } else {
    errorMessage.value = "下载文章失败，请稍后再试";
    Toast.error("下载文章失败，请稍后再试");
  }
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.article-row {
  display: grid;
  grid-template-columns: minmax(240px, 2fr) minmax(240px, 2fr) auto auto auto;
  align-items: center;
  gap: 12px 16px;
}

.article-row .field-label {
  min-width: 48px;
  text-align: right;
}

.article-row .field.field-compact {
  min-width: auto;
  flex: 0 0 auto;
  gap: 8px;
}

.article-row .field.field-compact .field-label {
  min-width: auto;
  text-align: left;
}

.article-title {
  gap: 12px;
}

.article-title .article-link {
  display: inline-flex;
  align-items: center;
  flex: 1 1 auto;
  min-width: 0;
  color: #1d4ed8;
  cursor: pointer;
  text-decoration: underline;
  line-height: 1.4;
  word-break: break-word;
}

.article-title .article-link:hover {
  color: #1e40af;
}

.inline-actions {
  margin-left: 0;
  justify-self: end;
}

.field-input.field-input--xs {
  text-align: center;
}

@media (max-width: 1200px) {
  .article-row {
    grid-template-columns: minmax(200px, 2fr) minmax(200px, 2fr) auto auto;
  }

  .inline-actions {
    grid-column: 1 / -1;
    justify-self: flex-start;
  }
}

@media (max-width: 768px) {
  .article-row {
    display: flex;
    flex-direction: column;
    align-items: stretch;
  }

  .article-row .field-label {
    min-width: auto;
    text-align: left;
  }
}
</style>
