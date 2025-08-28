<template>
  <div class="article-related-container">
    <div class="article-related-title">相关文章</div>
    <div class="article-related-list">
      <div class="article-related-item" v-for="item in relatedArticles" :key="item.id">
        <a :href="`/article/${item.id}`">
          {{ item.title }}
        </a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { getArticlesByCategory, getArticlesByTag } from "../../utils/apis";

const props = defineProps({
  article: {
    type: Object,
    required: true,
  },
});

// 定义一个响应式变量来存储相关文章
const relatedArticles = ref([]);

/**
 * 更新相关文章列表
 * @param article 文章对象
 */
function updateRelatedArticles(article) {
  const id = props.article.id;
  // 排除当前文章
  if (article.id === id) {
    return;
  }

  // 如果已经存在，则不添加
  if (!relatedArticles.value.some((item) => item.id === article.id)) {
    relatedArticles.value.push(article);
  }
}

watch(
  () => props.article,
  async () => {
    const { article } = props;
    const category = article.meta.category;
    const tags = article.meta.tags;

    // 获取相关文章
    if (!category && !tags) {
      return;
    }

    // 如果有分类，则获取分类相关的文章
    const allCategoryArticles = await getArticlesByCategory(category);
    allCategoryArticles.forEach((item) => {
      updateRelatedArticles(item);
    });

    // 如果有标签，则获取标签相关的文章
    tags.forEach(async (item) => {
      const tmpArticles = await getArticlesByTag(item);
      tmpArticles.forEach((tmpItem) => {
        updateRelatedArticles(tmpItem);
      });
    });
  },
  { deep: true }
);
</script>

<style scoped>
.article-related-container {
  padding: 8px 24px;
}

.article-related-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding: 8px;
  border-bottom: 1px solid #e4e6ea;
}

.article-related-list {
  max-height: 186px;
  overflow-y: auto;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.article-related-item {
  font-size: 16px;
}

.article-related-item a {
  text-decoration: none;
  color: unset;
}

.article-related-item:hover {
  color: #409eff;
  cursor: pointer;
  transition: color 0.3s ease;
  text-decoration: underline;
}
</style>
