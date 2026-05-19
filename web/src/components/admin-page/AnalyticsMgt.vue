<template>
  <div class="content-container analytics-container">
    <div class="content-header analytics-header">
      <div>
        <h1>数据统计</h1>
        <p>查看站点访问量、文章点击量和 Live Demo 按钮点击量。</p>
      </div>

      <div class="toolbar">
        <label class="toolbar-field">
          <span>时间范围</span>
          <select v-model="selectedRange" @change="loadDashboard">
            <option value="7d">最近 7 天</option>
            <option value="30d">最近 30 天</option>
            <option value="90d">最近 90 天</option>
            <option value="180d">最近 180 天</option>
          </select>
        </label>

        <label class="toolbar-field">
          <span>聚合维度</span>
          <select v-model="selectedGranularity" @change="loadDashboard">
            <option value="day">按天</option>
            <option value="week">按周</option>
            <option value="month">按月</option>
          </select>
        </label>

        <button class="btn btn-outline refresh-button" :class="{ 'is-loading': isLoading }" :disabled="isLoading" @click="loadDashboard">刷新</button>
      </div>
    </div>

    <div class="error-banner" v-if="errorMessage">{{ errorMessage }}</div>

    <div class="stat-grid">
      <article class="stat-card">
        <span>PV</span>
        <strong>{{ formatNumber(overview.summary.pv) }}</strong>
      </article>
      <article class="stat-card">
        <span>UV</span>
        <strong>{{ formatNumber(overview.summary.uv) }}</strong>
      </article>
      <article class="stat-card">
        <span>文章点击</span>
        <strong>{{ formatNumber(totalArticleClicks) }}</strong>
      </article>
      <article class="stat-card">
        <span>Live Demo 点击</span>
        <strong>{{ formatNumber(cta.clicks) }}</strong>
      </article>
    </div>

    <div v-if="isLoading" class="loading-stack">
      <div v-for="n in 3" :key="`analytics-skeleton-${n}`" class="loading-card chart-loading-card"></div>
    </div>

    <div v-else class="stats-layout">
      <section class="stats-panel stats-panel--wide">
        <div class="panel-header">
          <h2>访问量统计</h2>
          <p>PV / UV</p>
        </div>
        <div v-if="hasTrafficData" class="chart-shell">
          <canvas ref="trafficCanvas"></canvas>
        </div>
        <div v-else class="empty-state stats-empty">
          <p>当前区间暂无访问数据。</p>
        </div>
      </section>

      <section class="stats-panel">
        <div class="panel-header">
          <h2>文章点击 Top 10</h2>
          <p>点击次数</p>
        </div>
        <div v-if="hasArticleData" class="chart-shell">
          <canvas ref="articleCanvas"></canvas>
        </div>
        <div v-else class="empty-state stats-empty">
          <p>当前区间暂无文章点击数据。</p>
        </div>
      </section>

      <section class="stats-panel">
        <div class="panel-header">
          <h2>Live Demo 点击</h2>
          <p>曝光 / 点击</p>
        </div>
        <div class="chart-shell cta-chart-shell">
          <canvas ref="ctaCanvas"></canvas>
        </div>
        <div class="cta-counts">
          <span>曝光 {{ formatNumber(cta.impressions) }}</span>
          <span>点击 {{ formatNumber(cta.clicks) }}</span>
          <span>点击率 {{ cta.ctr || 0 }}%</span>
        </div>
      </section>

      <section class="stats-panel stats-panel--wide article-table-panel">
        <div class="panel-header">
          <h2>文章点击明细</h2>
          <p>点击 / UV</p>
        </div>

        <div v-if="articleRows.length" class="article-table">
          <div class="article-table-head">
            <span>排名</span>
            <span>文章</span>
            <span>点击</span>
            <span>UV</span>
          </div>
          <a v-for="item in articleRows" :key="item.article_id" class="article-row" :href="`/article/${item.article_id}`" target="_blank" rel="noopener noreferrer">
            <span class="rank">{{ item.rank }}</span>
            <span class="article-title" :title="item.title">{{ item.title }}</span>
            <span>{{ formatNumber(item.clicks) }}</span>
            <span>{{ formatNumber(item.uv) }}</span>
          </a>
        </div>
        <div v-else class="empty-state stats-empty">
          <p>当前区间暂无文章点击明细。</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import Chart from "chart.js/auto";
import { getAnalyticsCta, getAnalyticsOverview, getAnalyticsTopArticles } from "../../utils/apis";

const selectedRange = ref("30d");
const selectedGranularity = ref("day");
const isLoading = ref(false);
const errorMessage = ref("");

const overview = ref({
  summary: { pv: 0, uv: 0 },
  series: { labels: [], pv: [], uv: [] },
});
const topArticles = ref([]);
const cta = ref({
  impressions: 0,
  clicks: 0,
  ctr: 0,
  sources: [],
});

const trafficCanvas = ref(null);
const articleCanvas = ref(null);
const ctaCanvas = ref(null);

let trafficChart = null;
let articleChart = null;
let ctaChart = null;

const totalArticleClicks = computed(() => topArticles.value.reduce((sum, item) => sum + Number(item.clicks || 0), 0));
const hasTrafficData = computed(() => overview.value.series.pv.some((item) => Number(item) > 0) || overview.value.series.uv.some((item) => Number(item) > 0));
const hasArticleData = computed(() => topArticles.value.length > 0);
const articleRows = computed(() =>
  topArticles.value.map((item, index) => ({
    ...item,
    rank: index + 1,
    clicks: Number(item.clicks || 0),
    uv: Number(item.uv || 0),
  }))
);

const articlePalette = ["#2563eb", "#0f766e", "#f59e0b", "#db2777", "#7c3aed", "#0891b2", "#65a30d", "#ea580c", "#475569", "#9333ea"];

function destroyCharts() {
  trafficChart?.destroy();
  articleChart?.destroy();
  ctaChart?.destroy();
  trafficChart = null;
  articleChart = null;
  ctaChart = null;
}

function baseOptions() {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
          pointStyle: "circle",
          boxWidth: 8,
        },
      },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.92)",
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      x: {
        grid: { display: false },
      },
      y: {
        beginAtZero: true,
        ticks: { precision: 0 },
        grid: { color: "rgba(148, 163, 184, 0.16)" },
      },
    },
  };
}

function renderCharts() {
  destroyCharts();

  if (trafficCanvas.value && hasTrafficData.value) {
    trafficChart = new Chart(trafficCanvas.value, {
      type: "line",
      data: {
        labels: overview.value.series.labels,
        datasets: [
          {
            label: "PV",
            data: overview.value.series.pv,
            borderColor: "#2563eb",
            backgroundColor: "rgba(37, 99, 235, 0.12)",
            borderWidth: 2,
            tension: 0.32,
            fill: true,
          },
          {
            label: "UV",
            data: overview.value.series.uv,
            borderColor: "#0f766e",
            backgroundColor: "rgba(15, 118, 110, 0.1)",
            borderWidth: 2,
            tension: 0.32,
            fill: true,
          },
        ],
      },
      options: baseOptions(),
    });
  }

  if (articleCanvas.value && hasArticleData.value) {
    articleChart = new Chart(articleCanvas.value, {
      type: "bar",
      data: {
        labels: topArticles.value.map((item) => shortenLabel(item.title)),
        datasets: [
          {
            label: "点击次数",
            data: topArticles.value.map((item) => item.clicks),
            backgroundColor: topArticles.value.map((_, index) => articlePalette[index % articlePalette.length]),
            borderRadius: 999,
            barThickness: 12,
            maxBarThickness: 12,
            categoryPercentage: 0.62,
            barPercentage: 0.72,
          },
        ],
      },
      options: {
        ...baseOptions(),
        indexAxis: "y",
        plugins: {
          ...baseOptions().plugins,
          legend: { display: false },
        },
      },
    });
  }

  if (ctaCanvas.value) {
    const remaining = Math.max((cta.value.impressions || 0) - (cta.value.clicks || 0), 0);
    ctaChart = new Chart(ctaCanvas.value, {
      type: "doughnut",
      data: {
        labels: ["点击", "未点击曝光"],
        datasets: [
          {
            data: [cta.value.clicks || 0, remaining],
            backgroundColor: ["#2563eb", "#e2e8f0"],
            borderColor: "#ffffff",
            borderWidth: 3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: "68%",
        plugins: baseOptions().plugins,
      },
    });
  }
}

async function loadDashboard() {
  isLoading.value = true;
  errorMessage.value = "";
  destroyCharts();
  try {
    const [overviewRes, topRes, ctaRes] = await Promise.all([
      getAnalyticsOverview(selectedRange.value, selectedGranularity.value),
      getAnalyticsTopArticles(selectedRange.value, 10),
      getAnalyticsCta(selectedRange.value, "live_demo"),
    ]);

    overview.value = overviewRes || overview.value;
    topArticles.value = topRes?.items || [];
    cta.value = ctaRes || cta.value;
  } catch (error) {
    console.error("load analytics stats error:", error);
    errorMessage.value = "统计数据加载失败，请稍后再试。";
  } finally {
    isLoading.value = false;
    await nextTick();
    renderCharts();
  }
}

function shortenLabel(value) {
  const text = String(value || "");
  return text.length > 14 ? `${text.slice(0, 13)}...` : text;
}

function formatNumber(value) {
  return new Intl.NumberFormat("zh-CN").format(Number(value || 0));
}

onMounted(() => {
  loadDashboard();
});

onBeforeUnmount(() => {
  destroyCharts();
});
</script>

<style scoped>
@import url("../../assets/components/admin-content.css");

.analytics-container {
  gap: 20px;
}

.analytics-header {
  flex-direction: row;
  align-items: end;
  justify-content: space-between;
  gap: 18px;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: end;
  justify-content: flex-end;
  gap: 10px;
}

.toolbar-field {
  display: grid;
  gap: 6px;
  min-width: 150px;
}

.toolbar-field span {
  font-size: 11px;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.toolbar-field select {
  min-height: 38px;
  padding: 0 10px;
  border: 1px solid #dbe5f0;
  border-radius: 8px;
  background: #fff;
  color: #0f172a;
}

.refresh-button {
  min-height: 38px;
  border-radius: 8px;
}

.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  display: grid;
  gap: 8px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #ffffff;
}

.stat-card::before {
  content: "";
  position: absolute;
  inset: 0 auto 0 0;
  width: 4px;
  background: var(--stat-color, #2563eb);
}

.stat-card:nth-child(1) {
  --stat-color: #2563eb;
}

.stat-card:nth-child(2) {
  --stat-color: #0f766e;
}

.stat-card:nth-child(3) {
  --stat-color: #f59e0b;
}

.stat-card:nth-child(4) {
  --stat-color: #db2777;
}

.stat-card span {
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.stat-card strong {
  color: #0f172a;
  font-size: 30px;
  line-height: 1;
}

.stats-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.72fr);
  gap: 16px;
}

.stats-panel {
  --panel-accent: #2563eb;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 340px;
  padding: 18px;
  border: 1px solid #e2e8f0;
  border-top: 3px solid var(--panel-accent);
  border-radius: 8px;
  background: #ffffff;
}

.stats-panel:nth-child(1) {
  --panel-accent: #2563eb;
}

.stats-panel:nth-child(2) {
  --panel-accent: #f59e0b;
}

.stats-panel:nth-child(3) {
  --panel-accent: #db2777;
}

.stats-panel:nth-child(4) {
  --panel-accent: #0f766e;
}

.stats-panel--wide {
  grid-column: 1 / -1;
}

.article-table-panel {
  min-height: auto;
}

.panel-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 14px;
}

.panel-header h2 {
  margin: 0;
  color: #0f172a;
  font-size: 17px;
}

.panel-header p {
  margin: 0;
  color: #64748b;
  font-size: 13px;
}

.chart-shell {
  position: relative;
  flex: 1;
  min-height: 300px;
}

.chart-shell canvas {
  width: 100% !important;
  height: 100% !important;
}

.cta-chart-shell {
  min-height: 230px;
}

.cta-counts {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.cta-counts span {
  padding: 10px;
  border: 1px solid #e8eef5;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
  font-size: 12px;
  font-weight: 700;
  text-align: center;
}

.article-table {
  overflow: hidden;
  border: 1px solid #e8eef5;
  border-radius: 8px;
}

.article-table-head,
.article-row {
  display: grid;
  grid-template-columns: 64px minmax(240px, 1fr) 110px 100px;
  align-items: center;
  gap: 14px;
}

.article-table-head {
  min-height: 42px;
  padding: 0 16px;
  background: #f8fafc;
  color: #64748b;
  font-size: 12px;
  font-weight: 700;
}

.article-row {
  min-height: 54px;
  padding: 9px 16px;
  color: #0f172a;
  text-decoration: none;
  border-top: 1px solid #e8eef5;
}

.article-row:hover {
  background: #f8fafc;
}

.rank {
  color: #94a3b8;
  font-weight: 800;
}

.article-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 700;
}

.stats-empty {
  justify-content: center;
  min-height: 180px;
  padding: 18px;
}

.chart-loading-card {
  min-height: 220px;
}

@media (max-width: 1120px) {
  .analytics-header {
    align-items: stretch;
    flex-direction: column;
  }

  .toolbar {
    justify-content: flex-start;
  }

  .stat-grid,
  .stats-layout {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .stat-grid,
  .stats-layout {
    grid-template-columns: 1fr;
  }

  .toolbar,
  .toolbar-field,
  .refresh-button {
    width: 100%;
  }

  .article-table-head {
    display: none;
  }

  .article-row {
    grid-template-columns: 44px 1fr;
    gap: 8px 12px;
  }

  .article-title {
    grid-column: 2;
  }

  .article-row span:nth-child(3)::before {
    content: "点击 ";
    color: #64748b;
  }

  .article-row span:nth-child(4)::before {
    content: "UV ";
    color: #64748b;
  }
}
</style>
