<template>
  <article class="demo-card">
    <div class="demo-main">
      <div v-if="demo.thumbnail || demo.previewgif" class="demo-thumb demo-thumb--image" aria-hidden="true">
        <img :src="demo.thumbnail || demo.previewgif" :alt="demo.title" loading="lazy" decoding="async" />
      </div>
      <div v-else class="demo-thumb" aria-hidden="true">{{ demo.title.slice(0, 2).toUpperCase() }}</div>

      <div class="demo-copy">
        <div class="demo-title-row">
          <h3>{{ demo.title }}</h3>
          <span :class="['status-pill', `status-pill--${demo.status}`]">{{ statusText }}</span>
        </div>
        <p>{{ demo.description }}</p>
      </div>
    </div>

    <div class="demo-actions">
      <a class="button-primary button-compact" :href="demo.demoLink" target="_blank" rel="noopener noreferrer">在线体验</a>
      <a class="button-ghost button-compact" :href="demo.repoLink" target="_blank" rel="noopener noreferrer">GitHub</a>
    </div>
  </article>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  demo: {
    type: Object,
    required: true,
  },
});

const statusTextMap = {
  done: "已完成",
  building: "开发中",
  experimental: "实验",
};

const statusText = computed(() => statusTextMap[props.demo.status] || props.demo.status);
</script>

<style scoped>
.demo-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 16px 18px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 18px;
  box-shadow: 0 6px 18px rgba(15, 23, 42, 0.03);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.demo-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
  border-color: #d7dfe8;
}

.demo-main {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 14px;
}

.demo-thumb {
  width: 52px;
  height: 52px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, #eff6ff, #f8fafc);
  border: 1px solid #dbe3ef;
  color: #2563eb;
  font-size: 13px;
  font-weight: 700;
  overflow: hidden;
}

.demo-thumb--image {
  background: #f8fafc;
  border-color: #e2e8f0;
}

.demo-thumb--image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.demo-copy {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.demo-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.demo-title-row h3 {
  margin: 0;
  color: #0f172a;
  font-size: 17px;
  line-height: 1.3;
}

.demo-copy p {
  margin: 0;
  color: #64748b;
  line-height: 1.6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 26px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid #e5e7eb;
}

.status-pill--done {
  color: #0f766e;
  background: #ecfeff;
}

.status-pill--building {
  color: #b45309;
  background: #fffbeb;
}

.status-pill--experimental {
  color: #7c3aed;
  background: #f5f3ff;
}

.demo-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.button-primary,
.button-ghost {
  height: 36px;
  padding: 0 13px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: transform 0.2s ease, background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.button-primary {
  background: #2563eb;
  color: #ffffff;
  border: 1px solid #2563eb;
}

.button-primary:hover {
  background: #1d4ed8;
  border-color: #1d4ed8;
  transform: translateY(-1px);
}

.button-ghost {
  background: #ffffff;
  color: #334155;
  border: 1px solid #e5e7eb;
}

.button-ghost:hover {
  background: #f8fafc;
  transform: translateY(-1px);
}

@media (max-width: 840px) {
  .demo-card {
    align-items: flex-start;
    flex-direction: column;
  }

  .demo-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}

@media (max-width: 640px) {
  .demo-copy p {
    white-space: normal;
  }
}
</style>
