<template>
  <div class="content-container">
    <div class="content-header">
      <h1>新增文章</h1>
    </div>
    <div class="content-body">
      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>
      <div class="content-item">
        <span>文件名称</span>
        <input type="text" placeholder="请输入文件名称" v-model="newArticleMgt.title" />
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
      <!-- 新增文章的button -->
      <div class="content-item">
        <button class="btn btn-primary" @click="onNewArticle">新增文章</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { editIsExist, addArticle } from "../../utils/apis";
import Toast from "../../utils/toast.js";
import { useRouter } from "vue-router";

const router = useRouter();

const props = defineProps({
  allCategories: {
    type: Array,
    required: true,
  },
});

const errorMessage = ref("");

// 用于存储新文章的标题和分类
const newArticleMgt = ref({ title: "", category: "" });

/**
 * 新增文章
 * @param category {string} 文章分类
 * @param title {string} 文章标题
 */
async function onNewArticle() {
  // 检查文章标题是否符合规范
  const regex = /^(?!-)[\p{Script=Han}\p{L}\p{N}_-]+$/u;
  if (!regex.test(newArticleMgt.value.title)) {
    errorMessage.value = "文章标题只能包含汉字、字母、数字、下划线和中划线，且不能以中划线开头";
    Toast.error("文章标题只能包含汉字、字母、数字、下划线和中划线，且不能以中划线开头");
    return;
  }

  // 检查标题和分类是否填写
  if (!newArticleMgt.value.title || !newArticleMgt.value.category) {
    errorMessage.value = "请填写文章标题和选择专栏";
    Toast.error("请填写文章标题和选择专栏");
    return;
  }

  const isexist = await editIsExist(newArticleMgt.value.category, newArticleMgt.value.title);
  if (isexist) {
    errorMessage.value = "文章标题已存在，请更换标题";
    Toast.error("文章标题已存在，请更换标题");
    return;
  }

  // 清除错误信息
  errorMessage.value = "";

  const res = await addArticle(newArticleMgt.value.category, newArticleMgt.value.title);
  if (typeof res === "string" && res !== "") {
    newArticleMgt.value.title = "";
    newArticleMgt.value.category = "";
    router.push({ path: `/edit/${res}` });
  } else {
    errorMessage.value = "新增文章失败，请稍后再试";
    Toast.error("新增文章失败，请稍后再试");
  }
}
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");
</style>
