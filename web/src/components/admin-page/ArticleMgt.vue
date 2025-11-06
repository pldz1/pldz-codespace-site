<template>
  <div class="content-container">
    <div class="content-header">
      <h1>新增文章</h1>
      <p>选择目标专栏并创建新的文章草稿</p>
    </div>

    <div class="content-body">
      <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

      <div v-if="isLoading" class="loading-stack">
        <div v-for="n in 3" :key="`article-skeleton-${n}`" class="loading-card">
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-80" style="margin-top: 12px"></div>
        </div>
      </div>

      <template v-else>
        <div class="content-item">
          <span>文章专栏</span>
          <div class="select-wrapper">
            <select v-model="newArticleMgt.category" :disabled="isLoading || !categories.length">
              <option value="" disabled>请选择专栏</option>
              <option v-for="category in categories" :key="category" :value="category">
                {{ category }}
              </option>
            </select>
          </div>
        </div>

        <div class="content-item" v-if="newArticleMgt.category">
          <span>文件名称</span>
          <input type="text" placeholder="请输入文件名称" v-model.trim="newArticleMgt.title" maxlength="80" />
        </div>

        <div class="content-item actions" v-if="newArticleMgt.category">
          <div class="inline-actions">
            <button class="btn btn-outline" type="button" @click="onGenerateTitle" :disabled="isCreating">快速生成标题</button>
            <button class="btn btn-primary" :class="{ 'is-loading': isCreating }" type="button" @click="onNewArticle" :disabled="isCreating || !canSubmit">
              新增文章
            </button>
          </div>
          <small class="helper-text">文章标题可包含汉字、字母、数字、下划线与中划线，且不得以中划线开头</small>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { editIsExist, addArticle } from "../../utils/apis";
import Toast from "../../utils/toast.js";
import { useRouter } from "vue-router";
import { useLoading } from "../../utils/use-loading";

const router = useRouter();

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
const newArticleMgt = ref({ title: "", category: "" });
const { isLoading: isCreating, start: startCreating, stop: stopCreating } = useLoading("admin.article.create");

const canSubmit = computed(() => Boolean(newArticleMgt.value.category && newArticleMgt.value.title));
const titleSuggestions = ["新的文章", "灵感记录", "创作草稿", "最新动态"];
const categories = computed(() => props.allCategories || []);

async function onNewArticle() {
  if (!canSubmit.value) return;

  const regex = /^(?!-)[\p{Script=Han}\p{L}\p{N}_-]+$/u;
  if (!regex.test(newArticleMgt.value.title)) {
    errorMessage.value = "文章标题只能包含汉字、字母、数字、下划线和中划线，且不能以中划线开头";
    Toast.error("文章标题只能包含汉字、字母、数字、下划线和中划线，且不能以中划线开头");
    return;
  }

  startCreating();
  try {
    const isexist = await editIsExist(newArticleMgt.value.category, newArticleMgt.value.title);
    if (isexist) {
      errorMessage.value = "文章标题已存在，请更换标题";
      Toast.error("文章标题已存在，请更换标题");
      return;
    }

    errorMessage.value = "";
    const res = await addArticle(newArticleMgt.value.category, newArticleMgt.value.title);
    if (typeof res === "string" && res !== "") {
      const articleId = res;
      Toast.success("文章创建成功，正在跳转编辑器");
      newArticleMgt.value.title = "";
      router.push({ path: `/edit/${articleId}` });
    } else {
      errorMessage.value = "新增文章失败，请稍后再试";
      Toast.error("新增文章失败，请稍后再试");
    }
  } catch (error) {
    console.error("新增文章失败:", error);
    errorMessage.value = "新增文章失败，请稍后再试";
    Toast.error("新增文章失败，请稍后再试");
  } finally {
    stopCreating();
  }
}

function onGenerateTitle() {
  if (!newArticleMgt.value.category) return;
  const suffix = newArticleMgt.value.category.replace(/[-_]/g, " ").slice(0, 12);
  const random = titleSuggestions[Math.floor(Math.random() * titleSuggestions.length)];
  newArticleMgt.value.title = `${suffix || "文章"}-${random}`.replace(/\s+/g, "-");
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.actions {
  flex-direction: column;
  align-items: flex-start;
  gap: 12px;
}

.helper-text {
  color: #6b7280;
  font-size: 12px;
}
</style>
