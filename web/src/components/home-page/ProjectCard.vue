<template>
  <article class="project-card">
    <div class="project-cover">
      <img :src="project.cover" :alt="project.title" />
    </div>

    <div class="project-body">
      <h3>{{ project.title }}</h3>
      <p>{{ project.description }}</p>

      <div class="tag-list">
        <span v-for="tag in project.tags" :key="tag" class="tag-chip">{{ tag }}</span>
      </div>
    </div>

    <div class="card-actions">
      <a class="button-primary button-small" :href="project.tutorialLink">查看教程</a>
      <a class="button-ghost button-small" :href="project.repoLink" target="_blank" rel="noopener noreferrer">查看源码</a>
    </div>
  </article>
</template>

<script setup>
defineProps({
  project: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped>
.project-card {
  display: grid;
  gap: 20px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid #eef3f8;
  border-radius: 24px;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.018);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, background-color 0.2s ease;
}

.project-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.028);
  border-color: #e2e8f0;
  background: rgba(255, 255, 255, 0.9);
}

.project-cover {
  border-radius: 18px;
  overflow: hidden;
  aspect-ratio: 16 / 9;
  background: #f8fafc;
}

.project-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.project-body {
  display: grid;
  gap: 12px;
}

.project-body h3 {
  margin: 0;
  color: #0f172a;
  font-size: 20px;
  line-height: 1.35;
}

.project-body p {
  margin: 0;
  color: #475569;
  line-height: 1.75;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  border: 1px solid #e6edf5;
  background: #fbfcfd;
  color: #475569;
  font-size: 12px;
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.button-primary,
.button-ghost {
  height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  font-weight: 600;
  transition: transform 0.2s ease, background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease;
}

.button-small {
  height: 38px;
  padding: 0 14px;
  font-size: 14px;
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

@media (max-width: 640px) {
  .project-card {
    padding: 14px;
  }
}
</style>
