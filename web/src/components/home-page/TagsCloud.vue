<template>
  <div class="tag-cloud-container">
    <div class="tag-cloud-title">标签</div>
    <div class="tag-content">
      <div :class="['tag-item', { active: activeTag === tag.text }]" v-for="tag in tagCounts" :key="tag.text" :style="tag.style" @click="onClickTag(tag.text)">
        {{ tag.text }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getTagCounts } from "../../utils/apis";
import { randomColorWordCloud } from "../../utils/word-cloud.js";

const emit = defineEmits(["toggle-tag-filter"]);

const props = defineProps({
  activeTag: {
    type: String,
    default: "",
  },
});

/**
 * 标签统计数据
 * @type {Array<{ text: string, style: object }>}
 * @description 用于存储标签统计数据，包含标签文本和样式
 */
const tagCounts = ref([]);

/**
 * 点击标签时触发事件，传递标签文本
 * @param tagText 标签文本
 * @description 点击标签时触发事件，传递标签文本
 */
function onClickTag(tagText) {
  emit("toggle-tag-filter", tagText);
}

/**
 * 在组件挂载时获取标签统计数据并生成词云图
 * @description 在组件挂载时调用getTagCounts获取标签统计数据，并使用randomColorWordCloud生成词云图
 */
onMounted(async () => {
  // tag标签的统计生成词云图
  const tagCountsRes = await getTagCounts();
  if (!tagCountsRes) return;
  tagCounts.value = randomColorWordCloud(tagCountsRes);
});
</script>

<style scoped>
.tag-cloud-container {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
}

.tag-cloud-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding: 8px;
  border-bottom: 1px solid #e4e6ea;
}

.tag-content {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  font-size: 16px;
  font-weight: 500;
  transition: transform 0.3s ease;
  cursor: pointer;
}

.active {
  text-decoration: underline;
}

.tag-item:hover {
  transform: scale(1.2);
}
</style>
