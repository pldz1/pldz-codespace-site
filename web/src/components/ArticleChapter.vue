<template>
  <div class="catalog-card">
    <div class="catalog-card-header">
      <div>
        <span>目录</span>
      </div>
      <span class="progress">{{ progress }}</span>
    </div>

    <div class="catalog-content">
      <div
        v-for="title in titles"
        :key="title.id"
        @click="scrollToView(title.scrollTop)"
        :class="['catalog-item', currentTitle.id === title.id ? 'active' : 'not-active']"
        :style="{ marginLeft: title.level * 20 + 'px' }"
        :title="title.rawName"
      >
        {{ title.name }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, onUnmounted, nextTick } from "vue";

// 接收文章内容选择器
const props = defineProps({
  articleClass: {
    type: String,
    default: ".content .article-content",
  },
});

const currentTitle = reactive({ id: null, level: 0 });
const progress = ref("0%");
const titles = ref([]);

function getTitles() {
  const list = [];
  const levels = ["h1", "h2", "h3"];
  const blogEl = document.querySelector(props.articleClass);
  if (!blogEl) return list;

  const elements = Array.from(blogEl.querySelectorAll("*"));
  const tagNames = new Set(elements.map((el) => el.tagName.toLowerCase()));
  const used = levels.filter((lv) => tagNames.has(lv));
  const serials = used.map(() => 0);

  elements.forEach((el, idx) => {
    const tag = el.tagName.toLowerCase();
    const lvl = used.indexOf(tag);
    if (lvl === -1) return;

    serials[lvl]++;
    const node = {
      id: `${tag}-${idx}-${el.innerText.slice(0, 20)}`,
      level: lvl,
      rawName: el.innerText,
      scrollTop: el.offsetTop,
      name: `${serials.slice(0, lvl + 1).join(".")}\. ${el.innerText}`,
    };
    list.push(node);
  });

  return list;
}

function handleScroll() {
  const st = window.scrollY;
  const sh = document.documentElement.scrollHeight;
  const ch = window.innerHeight;
  const maxScroll = sh - ch;
  progress.value = maxScroll > 0 ? `${Math.floor((st / maxScroll) * 100)}%` : "0%";

  // 倒序查找当前活动标题并更新
  for (let i = titles.value.length - 1; i >= 0; i--) {
    const t = titles.value[i];
    if (t.scrollTop <= st) {
      if (currentTitle.id !== t.id) {
        currentTitle.id = t.id;
        currentTitle.level = t.level;
      }
      break;
    }
  }
}

function scrollToView(pos) {
  window.scrollTo({ top: pos, behavior: "smooth" });
}

onMounted(() => {
  titles.value = getTitles();
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

.catalog-icon {
  font-size: 18px;
  margin-right: 10px;
  color: dodgerblue;
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
}

.catalog-item {
  margin: 5px 0;
  line-height: 28px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  font-size: 14px;
  padding: 2px 6px;
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
}

.catalog-item:hover {
  color: #409eff;
}

.active {
  font-size: 16px;
  font-weight: 800;
}
</style>
