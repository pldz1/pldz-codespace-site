<template>
  <li class="timeline-item">
    <a :href="item.link" class="timeline-link">
      <span class="timeline-type">{{ item.type }}</span>
      <span class="timeline-title">{{ item.title }}</span>
      <span class="timeline-date">{{ formattedDate }}</span>
      <span class="timeline-action">阅读更新</span>
    </a>
  </li>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  item: {
    type: Object,
    required: true,
  },
});

const formattedDate = computed(() => (props.item.date || "").replaceAll("-", "."));
</script>

<style scoped>
.timeline-item + .timeline-item {
  border-top: 1px solid #eef2f7;
}

.timeline-link {
  min-height: 58px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto auto;
  align-items: center;
  gap: 14px;
  padding: 14px 0;
  text-decoration: none;
}

.timeline-type {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 68px;
  height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  background: #f1f5f9;
  color: #475569;
  font-size: 12px;
  text-transform: lowercase;
}

.timeline-title {
  color: #0f172a;
  line-height: 1.5;
}

.timeline-date {
  color: #94a3b8;
  font-size: 14px;
}

.timeline-action {
  color: #2563eb;
  font-size: 14px;
  font-weight: 600;
}

@media (max-width: 840px) {
  .timeline-link {
    grid-template-columns: auto minmax(0, 1fr);
    align-items: start;
  }

  .timeline-date,
  .timeline-action {
    margin-left: 82px;
  }
}

@media (max-width: 640px) {
  .timeline-link {
    gap: 10px;
  }

  .timeline-date,
  .timeline-action {
    margin-left: 0;
  }
}
</style>
