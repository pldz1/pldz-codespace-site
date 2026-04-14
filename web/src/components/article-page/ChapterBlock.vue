<template>
  <div class="catalog-card">
    <div class="catalog-card-header">
      <div>
        <span>目录</span>
      </div>
      <span class="progress">{{ progress }}</span>
    </div>

    <div class="catalog-content">
      <div v-if="props.headings.length" class="catalog-list">
        <button
          v-for="item in props.headings"
          :key="item.id"
          type="button"
          :class="['catalog-link', `catalog-link--depth-${item.depth}`, { 'is-active': activeId === item.id }]"
          @click="scrollToHeading(item.id)"
        >
          {{ item.text }}
        </button>
      </div>
      <div v-else class="catalog-empty">暂无目录</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from "vue";

const props = defineProps({
  headings: {
    type: Array,
    default: () => [],
  },
});

const progress = ref("0%");
const activeId = ref("");

function handleScroll() {
  const st = window.scrollY;
  const sh = document.documentElement.scrollHeight;
  const ch = window.innerHeight;
  const maxScroll = sh - ch;

  // 更新进度条
  progress.value = maxScroll > 0 ? `${Math.floor((st / maxScroll) * 100)}%` : "0%";

  let currentActiveId = "";
  for (const item of props.headings) {
    const element = document.getElementById(item.id);
    if (!element) continue;

    if (element.getBoundingClientRect().top <= 140) {
      currentActiveId = item.id;
    } else {
      break;
    }
  }

  activeId.value = currentActiveId;
}

function scrollToHeading(id) {
  const element = document.getElementById(id);
  if (!element) return;

  const targetTop = element.getBoundingClientRect().top + window.scrollY - 96;
  window.scrollTo({ top: targetTop, behavior: "smooth" });
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
  padding: 2px 0 0;
}

.catalog-card-header {
  text-align: left !important;
  margin-bottom: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}

.catalog-card-header div > span {
  font-size: 13px;
  color: #64748b;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.progress {
  color: #94a3b8;
  font-size: 13px;
  letter-spacing: 0.08em;
}

.catalog-content {
  overflow-y: auto;
  max-height: calc(100vh - 150px);
  position: relative;
  padding-right: 4px;
}

.catalog-list {
  display: grid;
  gap: 4px;
}

.catalog-link {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  color: #6b7280;
  border-radius: 0;
  border-left: 1px solid #e2e8f0;
  padding: 4px 0 8px 8px;
  cursor: pointer;
  transition: color 0.2s ease, border-color 0.2s ease, transform 0.2s ease;
  font-size: 12px;
  line-height: 1.25;
}

.catalog-link:hover {
  color: #0f172a;
  transform: none;
  border-left-color: #94a3b8;
}

.catalog-link.is-active {
  color: #0f172a;
  font-weight: 600;
  border-left-color: #0f172a;
}

.catalog-link--depth-1 {
  font-weight: 700;
}

.catalog-link--depth-2 {
  padding-left: 24px;
}

.catalog-link--depth-3 {
  padding-left: 34px;
}

.catalog-link--depth-4,
.catalog-link--depth-5,
.catalog-link--depth-6 {
  padding-left: 42px;
}

.catalog-empty {
  color: #94a3b8;
  padding: 8px 0;
}

.catalog-content::-webkit-scrollbar {
  width: 4px;
}

.catalog-content::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 999px;
}

.catalog-content::-webkit-scrollbar-track {
  background: transparent;
}

@media (max-width: 768px) {
  .catalog-card {
    padding-top: 0;
  }

  .catalog-content {
    max-height: unset;
    padding-right: 0;
  }
}
</style>
