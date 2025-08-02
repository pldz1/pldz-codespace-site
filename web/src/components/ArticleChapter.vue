<template>
  <div class="catalog-card">
    <div class="catalog-card-header">
      <div>
        <span>目录</span>
      </div>
      <span class="progress">{{ progress }}</span>
    </div>

    <div class="catalog-content">
      <MdCatalog :editorId="props.editorId" :scrollElement="props.scrollElement" :theme="props.theme" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";
import { MdCatalog } from "md-editor-v3";

// 接收文章内容选择器
const props = defineProps({
  editorId: {
    type: String,
    default: "md-editor",
  },
  scrollElement: {
    type: Object,
    default: () => document.documentElement,
  },
  theme: {
    type: String,
    default: "light",
  },
});

const progress = ref("0%");

function handleScroll() {
  const st = window.scrollY;
  const sh = document.documentElement.scrollHeight;
  const ch = window.innerHeight;
  const maxScroll = sh - ch;

  // 更新进度条
  progress.value = maxScroll > 0 ? `${Math.floor((st / maxScroll) * 100)}%` : "0%";
}

onMounted(() => {
  window.addEventListener("scroll", handleScroll);
  nextTick(() => handleScroll());
});

onUnmounted(() => {
  window.removeEventListener("scroll", handleScroll);
});
</script>

<style scoped>
.catalog-card {
  padding: 8px 24px;
}

.catalog-card-header {
  text-align: left !important;
  margin-bottom: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  border-bottom: 1px solid #e4e6ea;
}

.catalog-card-header div > span {
  font-size: 17px;
  color: var(--text-color);
}

.progress {
  color: #a9a9a9;
  font-style: italic;
  font-size: 140%;
}

.catalog-content {
  overflow-y: auto;
  max-height: 286px;
  position: relative;
}

@media (max-width: 768px) {
  .catalog-content {
    max-height: unset;
  }
}
</style>
